#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical validator for house-standard interactive courses.

Usage:
    python3 validate_course.py <course.html> [--strict] [--sensitive terms.txt]

Turns the reference.md ship checklist into executable checks so ANY model
(or human) can loop until clean instead of relying on taste. Exit code 0 =
no errors (warnings allowed unless --strict).

ERRORS  = objective violations of the standard (must fix).
WARNINGS = judgment calls surfaced for review (fix or consciously accept).

--sensitive terms.txt : for PUBLIC courses. Newline-delimited banned terms
(client names, internal repos, real figures; '#' comments allowed). Any hit
anywhere in the file is an ERROR — see reference.md §7 / PLAYBOOK Phase 1.
"""
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

MAX_FILE_BYTES = 3_500_000
MAX_IMG_BYTES = 280_000          # ~200KB binary ≈ 280KB base64
MAX_LESSON_WORDS = 1_900
PROSE_WALL_WORDS = 450           # max words between two visual/interactive breaks

# Empty-intensifier lexicon (EN + VI). Word-boundary matched, case-insensitive.
SLOP = [
    "powerful", "seamless", "seamlessly", "revolutionary", "cutting-edge",
    "game-changing", "world-class", "state-of-the-art", "unlock the power",
    "in today's fast-paced", "delve into", "elevate your",
    "mạnh mẽ", "toàn diện", "tối ưu hoá trải nghiệm", "đột phá",
    "trong thế giới ngày nay", "trong thời đại số", "chìa khoá thành công",
    "nâng tầm", "vượt trội",
]

# English chrome strings that must be localized when <html lang> is not en.
EN_CHROME = [
    "Mark complete", "← Previous", "Next →", "Finish course", "First lesson",
    ">Overview<", ">Curriculum<", "Skip to content", "✓ Completed",
    "'Overview'", "'Complete'", "✓ Correct. ", "✗ Not quite. ",
    "Course progress", "Course navigation",
]

TEMPLATE_PLACEHOLDERS = [
    "A concrete lesson title", "Course Title", "template-course", "Course Name",
    "What this lesson delivers", "Module title in plain language",
    "One or two sentences on who this is for",
    "the one sentence you want the learner to repeat back",
]

VISUAL_BREAKS = re.compile(
    r'<(?:figure|table|svg|details|div class="(?:compare|callout|steps|takeaway|quiz|'
    r'prompt-card|code-card|objectives|concept))', re.I)


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def word_count(html: str) -> int:
    return len(strip_tags(html).split())


def main() -> int:
    argv = sys.argv[1:]
    sensitive_file = None
    if "--sensitive" in argv:
        i = argv.index("--sensitive")
        if i + 1 >= len(argv):
            print("--sensitive requires a terms file")
            return 2
        sensitive_file = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("--")]
    strict = "--strict" in argv
    if not args:
        print(__doc__)
        return 2
    path = Path(args[0])
    html = path.read_text(encoding="utf-8")
    # comment-stripped view for checks that HTML comments would false-trigger
    html_nc = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    errors: list[str] = []
    warns: list[str] = []

    # ---------- file-level ----------
    size = len(html.encode("utf-8"))
    if size > MAX_FILE_BYTES:
        errors.append(f"file is {size:,} bytes (> {MAX_FILE_BYTES:,}) — cut/downscale images")
    lang_m = re.search(r'<html\s+lang="([^"]+)"', html_nc)
    if not lang_m:
        errors.append('<html lang="…"> missing')
    lang = lang_m.group(1) if lang_m else "en"
    if not re.search(r'<body[^>]*data-theme="', html):
        errors.append("<body> missing data-theme")
    if re.search(r"@media[^{]*prefers-color-scheme", html_nc):
        errors.append("@media prefers-color-scheme found — house rule is light default + toggle only")
    if not re.search(r'<meta name="description" content=".{20,}"', html):
        warns.append("meta description missing or too short")

    # external RESOURCE loads: only Google Fonts allowed. Content hyperlinks
    # (<a href>) are fine — the ban is on network requests the page performs.
    for m in re.finditer(r'<(?:script|img|iframe|video|audio|source)\b[^>]*\bsrc="(https?://[^"]+)"', html):
        errors.append(f"external resource load not allowed: {m.group(1)[:90]}")
    for m in re.finditer(r'<link\b[^>]*\bhref="(https?://[^"]+)"[^>]*>', html):
        url = m.group(1)
        if "fonts.googleapis.com" in url or "fonts.gstatic.com" in url:
            continue
        errors.append(f"external <link> not allowed: {url[:90]}")
    scripts = re.findall(r"<script\b[^>]*>", html_nc)
    if any("src=" in s for s in scripts):
        errors.append("external <script src> found — engine must be inline, no JS libs")
    if len(scripts) > 1:
        warns.append(f"{len(scripts)} <script> blocks (house norm: 1 engine block)")

    # embedded images
    for m in re.finditer(r'src="data:image/[^;]+;base64,([^"]+)"', html):
        if len(m.group(1)) > MAX_IMG_BYTES:
            errors.append(f"embedded image ~{len(m.group(1))//1000}KB base64 (> 200KB binary budget)")

    # ---------- engine / LESSONS ----------
    slug_m = re.search(r"const COURSE_SLUG\s*=\s*'([^']+)'", html)
    if not slug_m or slug_m.group(1) in ("template-course", ""):
        errors.append("COURSE_SLUG not set")
    lessons_m = re.search(r"const LESSONS\s*=\s*\[(.*?)\n\];", html, re.S)
    lesson_ids: list[str] = []
    if not lessons_m:
        errors.append("LESSONS array not found")
    else:
        body = re.sub(r"^\s*//.*$", "", lessons_m.group(1), flags=re.M)  # drop commented rows
        lesson_ids = re.findall(r"\bid:\s*'([^']+)'", body)
        if len(lesson_ids) < 12:
            warns.append(f"only {len(lesson_ids)} lessons — under the 12-lesson course floor")
        if len(lesson_ids) > 30:
            warns.append(f"{len(lesson_ids)} lessons — consider splitting (>30)")
        if len(set(lesson_ids)) != len(lesson_ids):
            errors.append("duplicate ids in LESSONS array")
        for lid in lesson_ids:
            if not re.fullmatch(r"m\d+-l\d+", lid):
                errors.append(f"LESSONS id '{lid}' not of form mN-lK")
        # every LESSONS row needs title + desc
        rows = re.findall(r"\{[^}]*\}", body)
        for r in rows:
            if "desc:" not in r or re.search(r"desc:\s*''", r):
                warns.append("a LESSONS row has empty desc (TOC card loses its subtitle)")
                break

    for key in ("lms:progress", "lms:lesson-change"):
        if key not in html:
            errors.append(f"LMS postMessage contract broken: '{key}' missing")

    # node --check the engine
    engine_m = re.search(r"<script>\n(.*?)</script>\s*</body>", html, re.S)
    if engine_m:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(engine_m.group(1))
            tmp = f.name
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"node --check failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'syntax error'}")
    else:
        warns.append("could not isolate engine <script> for node --check")

    # ---------- DOM ↔ LESSONS ----------
    dom_ids = re.findall(r'<article class="lesson" id="([^"]+)"', html)
    for lid in lesson_ids:
        if lid not in dom_ids:
            errors.append(f"LESSONS has '{lid}' but no <article class=\"lesson\"> card")
        if f'data-navfor="{lid}"' not in html:
            errors.append(f"'{lid}' missing empty lesson-nav placeholder")
    for did in dom_ids:
        if did not in lesson_ids:
            errors.append(f"lesson card '{did}' in DOM but not in LESSONS (unreachable)")

    all_dom_ids = re.findall(r'\bid="([^"]+)"', html)
    dupes = sorted({i for i in all_dom_ids if all_dom_ids.count(i) > 1})
    if dupes:
        errors.append(f"duplicate DOM/SVG ids (fragment collision?): {dupes[:12]}")

    # ---------- placeholders / hex / slop ----------
    for p in TEMPLATE_PLACEHOLDERS:
        if p in html_nc:
            errors.append(f"template placeholder left in file: {p!r}")

    head_end = html.find("</head>")
    body_html = html[head_end:] if head_end != -1 else html
    body_no_script = re.sub(r"<script\b.*?</script>", "", body_html, flags=re.S)
    hexes = re.findall(r'(?:fill|stroke|color|background|stop-color)\s*[:=]\s*"?(#[0-9a-fA-F]{3,8})\b',
                       body_no_script)
    if hexes:
        errors.append(f"hardcoded color in markup (use tokens/dgm-*): {sorted(set(hexes))[:8]}")
    funcs = re.findall(r'(?:fill|stroke|color|background|stop-color)\s*[:=]\s*"?((?:rgba?|hsla?)\([^)]*\))',
                       body_no_script)
    if funcs:
        errors.append(f"hardcoded rgb()/hsl() color in markup (use tokens/dgm-*): {sorted(set(funcs))[:6]}")
    if re.search(r'aria-label="\s*"', body_no_script):
        errors.append('empty aria-label="" found — give a real name or remove the attribute')

    # sensitive-terms pass (PUBLIC courses)
    if sensitive_file is not None:
        if not sensitive_file.exists():
            errors.append(f"--sensitive file not found: {sensitive_file}")
        else:
            low_all = unicodedata.normalize("NFC", html).lower()
            for raw in sensitive_file.read_text(encoding="utf-8").splitlines():
                term = raw.split("#", 1)[0].strip()
                if not term:
                    continue
                n = low_all.count(unicodedata.normalize("NFC", term).lower())
                if n:
                    errors.append(f"SENSITIVE term in public course ({n}×): {term!r}")

    low = unicodedata.normalize("NFC", strip_tags(body_no_script)).lower()
    hits = sorted({s for s in SLOP if s.lower() in low})
    if hits:
        warns.append(f"slop lexicon hits (run anti-slop pass): {hits}")

    if lang != "en":
        leftovers = [s for s in EN_CHROME if s in html_nc]
        if leftovers:
            errors.append(f"lang='{lang}' but English chrome strings remain: {leftovers[:6]}")

    # ---------- per-lesson mandates ----------
    cards = re.findall(r'(<article class="lesson" id="[^"]+".*?</article>)', html, re.S)
    takeaway_texts: dict[str, list[str]] = {}
    quiz_corrects: list[int] = []
    lesson_titles: dict[str, list[str]] = {}
    for card in cards:
        lid = re.search(r'id="([^"]+)"', card).group(1)

        def need(pattern, label, bucket=errors):
            if not re.search(pattern, card, re.S):
                bucket.append(f"{lid}: missing {label}")

        need(r'class="level-badge"', "level badge")
        need(r"⏱", "reading-time chip", warns)
        need(r'class="objectives"', "objectives block")
        obj_m = re.search(r'class="objectives".*?</ul>', card, re.S)
        if obj_m:
            n_obj = len(re.findall(r"<li", obj_m.group(0)))
            if not 2 <= n_obj <= 4:
                warns.append(f"{lid}: {n_obj} objectives (standard: 2–4 verb-first)")
        title_m = re.search(r"<h3[^>]*>(.*?)</h3>", card, re.S)
        if title_m:
            t = strip_tags(title_m.group(1)).strip().lower()
            lesson_titles.setdefault(t, []).append(lid)
        if not VISUAL_BREAKS.search(card.replace('class="objectives"', "")):
            errors.append(f"{lid}: no figure/comparison/steps/table (visual mandate)")
        n_take = len(re.findall(r'class="takeaway"', card))
        if n_take != 1:
            errors.append(f"{lid}: {n_take} takeaway blocks (need exactly 1)")
        tk_m = re.search(r'class="takeaway".*?<p>(.*?)</p>', card, re.S)
        if tk_m:
            tk = re.sub(r"\s+", " ", strip_tags(tk_m.group(1))).strip()
            takeaway_texts.setdefault(tk.lower(), []).append(lid)
            if len(tk) < 25:
                warns.append(f"{lid}: takeaway is only {len(tk)} chars — too thin to be quotable")
            if 'class="hl"' not in tk_m.group(0):
                warns.append(f"{lid}: takeaway has no <span class=\"hl\"> gold phrase")
        quizzes = re.findall(r'class="quiz"[^>]*data-correct="(\d+)"', card)
        if not quizzes:
            errors.append(f"{lid}: missing quiz with data-correct")
        quiz_corrects.extend(int(q) for q in quizzes)
        need(r'data-explain="..', "quiz data-explain")
        for ex in re.findall(r'data-explain="([^"]*)"', card):
            if len(ex.strip()) < 40:
                warns.append(f"{lid}: data-explain is {len(ex.strip())} chars — must teach why "
                             f"wrong options are wrong, not just confirm")
        opts = len(re.findall(r'class="quiz-opt"', card))
        if quizzes and opts < 3:
            errors.append(f"{lid}: quiz has {opts} options (<3)")
        for q in quizzes:
            if int(q) >= max(opts, 1):
                errors.append(f"{lid}: data-correct={q} out of range for {opts} options")
        # svgs inside a <figure> are content diagrams: role+label mandatory.
        # svgs elsewhere are decorative icons: aria-hidden mandatory (warn).
        for fig in re.findall(r"<figure.*?</figure>", card, re.S):
            for svg in re.findall(r"<svg\b[^>]*>", fig):
                if 'role="img"' not in svg:
                    errors.append(f"{lid}: figure <svg> without role=\"img\"")
                if "aria-label" not in svg:
                    errors.append(f"{lid}: figure <svg> without aria-label")
                if "viewBox" not in svg:
                    errors.append(f"{lid}: figure <svg> without viewBox (must scale fluidly)")
        card_no_fig = re.sub(r"<figure.*?</figure>", "", card, flags=re.S)
        for svg in re.findall(r"<svg\b[^>]*>", card_no_fig):
            if "aria-hidden" not in svg and 'role="img"' not in svg:
                warns.append(f"{lid}: decorative <svg> icon without aria-hidden=\"true\"")
                break
        tiny_warned = False
        for fig in re.findall(r"<figure.*?</figure>", card, re.S):
            if "<figcaption" not in fig:
                errors.append(f"{lid}: figure without figcaption")
            else:
                cap_m = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", fig, re.S)
                cap = re.sub(r"\s+", " ", strip_tags(cap_m.group(1))).strip() if cap_m else ""
                if len(cap) < 20:
                    warns.append(f"{lid}: figcaption {len(cap)} chars — must state the picture's point")
            # mobile legibility: tiny SVG text scales to unreadable at 375px
            vb_m = re.search(r'viewBox="0 0 (\d+)', fig)
            if not tiny_warned and vb_m and int(vb_m.group(1)) >= 700:
                tiny = re.findall(r'font-size="([0-8](?:\.\d+)?)"', fig)
                if tiny:
                    warns.append(f"{lid}: svg text font-size {sorted(set(tiny))} with "
                                 f"viewBox width {vb_m.group(1)} — unreadable at 375px "
                                 f"(min 9; fewer, bigger labels)")
                    tiny_warned = True

        wc = word_count(card)
        if wc > MAX_LESSON_WORDS:
            warns.append(f"{lid}: ~{wc} words (> {MAX_LESSON_WORDS}) — split the lesson")
        # prose-wall heuristic: words in gaps between visual/interactive breaks
        # table/steps CONTENT is not prose — blank it before the wall check
        card_prose = re.sub(r"<table\b.*?</table>", "<table></table>", card, flags=re.S)
        card_prose = re.sub(r"<ol\b.*?</ol>", "<ol></ol>", card_prose, flags=re.S)
        for gap in VISUAL_BREAKS.split(card_prose):  # segments between visual breaks
            if gap and word_count(gap) > PROSE_WALL_WORDS:
                warns.append(f"{lid}: a prose stretch of ~{word_count(gap)} words with no visual break")
                break

    # ---------- cross-lesson checks ----------
    for tk, lids in takeaway_texts.items():
        if len(lids) > 1 and tk:
            errors.append(f"identical takeaway pasted into {len(lids)} lessons ({', '.join(lids[:4])}) "
                          f"— each lesson has ONE core idea of its own")
    for t, lids in lesson_titles.items():
        if len(lids) > 1 and t:
            warns.append(f"duplicate lesson title {t!r} ({', '.join(lids[:4])})")
    if len(quiz_corrects) >= 6:
        top = max(set(quiz_corrects), key=quiz_corrects.count)
        share = quiz_corrects.count(top) / len(quiz_corrects)
        if share > 0.7:
            warns.append(f"{share:.0%} of quizzes share correct index {top} — learners game the "
                         f"pattern; vary data-correct")
    if lang == "vi" and cards and 'id="glossary"' not in html:
        warns.append("vi course without an overview glossary section (reference.md §4)")
    if cards:
        last_title = list(lesson_titles)[-1] if lesson_titles else ""
        tail = strip_tags(cards[-1][:800]).lower()
        if not any(k in tail or k in last_title for k in
                   ("tổng kết", "cheat", "recap", "tóm tắt", "summary")):
            warns.append("no recap/cheat-sheet closing lesson detected (reference.md §4 learner tooling)")

    # ---------- report ----------
    print(f"validate_course: {path.name} · lang={lang} · {len(lesson_ids)} lessons · {size:,} bytes")
    for e in errors:
        print(f"  ERROR   {e}")
    for w in warns:
        print(f"  warning {w}")
    if not errors and not warns:
        print("  CLEAN — mechanical checks all pass. Now do the human pass:")
    if not errors:
        print("  → remaining (cannot be automated): keyboard walk, 375px pass, BOTH color "
              "modes, fact check vs source digests, does-each-diagram-earn-its-caption.")
    print(f"RESULT: {len(errors)} errors, {len(warns)} warnings")
    return 1 if errors or (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
