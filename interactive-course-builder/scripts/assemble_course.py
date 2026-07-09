#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble a house-standard course from module fragments + a JSON contract.

Usage:
    python3 assemble_course.py <contract.json>

Why this exists: hand-editing a 300–500KB single-file course is where builds
go wrong (duplicate ids, broken LESSONS↔DOM sync, missed placeholder). This
script makes assembly deterministic so authors — human or model — only write
*lesson fragments* and a small contract. Pairs with validate_course.py (run
automatically at the end).

CONTRACT (contract.json) — minimal example:
{
  "out": "/abs/path/courses/my-course.html",
  "slug": "my-course",
  "title": "Course title (used as COURSE_TITLE + <title>)",
  "lang": "vi",
  "theme": "teal",
  "metaDescription": "One good sentence for <meta description>.",
  "fragmentsDir": "/abs/path/to/fragments",
  "hero": {
    "kicker": "Khoá học tương tác · 2026",
    "h1Html": "<span class=\\"grad-text\\">Big idea</span> — subtitle",
    "subHtml": "Who this is for and the concrete outcome.",
    "startLabel": "Bắt đầu học →", "curriculumLabel": "Xem chương trình"
  },
  "sidebarBrandHtml": "My <em>Course</em>",
  "completion": { "h2": "Hoàn thành khoá học", "pHtml": "…", "backLabel": "Về trang đầu" },
  "footerHtml": "My Course · 2026",
  "moduleIntros": { "1": "Framing paragraph for module 1.", "2": "…" },
  "glossary": [["Term", "Meaning as used in this course"], ...]   // optional
}

FRAGMENTS (in fragmentsDir), per module N:
  module-N.html       — ONLY <article class="lesson" id="mN-lK" data-lesson> blocks,
                        each ending with an EMPTY <div class="lesson-nav" data-navfor="mN-lK"></div>.
                        All svg internal ids MUST be prefixed mNlK- (collision-proof).
  module-N-meta.json  — {"module": N, "moduleTitle": "…", "part": "Phần I · …",
                         "lessons": [{"id": "mN-lK", "title": "…", "desc": "…",
                                      "minutes": 6, "level": 2, "takeaway": "…"}]}

Chrome localization: lang == "vi" applies the built-in Vietnamese table below.
Other languages: provide "chromeOverrides": {"english string": "replacement", …}
covering at least the VI table's keys (validate_course.py checks leftovers).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = SKILL_DIR / "template.html"

# Every user-visible English string in the template chrome + engine.
VI_CHROME = {
    '<a href="#main" class="skip-link">Skip to content</a>':
        '<a href="#main" class="skip-link">Bỏ qua, tới nội dung chính</a>',
    'aria-label="Open navigation"': 'aria-label="Mở menu điều hướng"',
    'aria-label="Course navigation"': 'aria-label="Điều hướng khoá học"',
    'aria-label="Lessons"': 'aria-label="Danh sách bài học"',
    'aria-label="Course progress"': 'aria-label="Tiến độ khoá học"',
    '<div class="progress-meta"><span>Progress</span>': '<div class="progress-meta"><span>Tiến độ</span>',
    '<span class="mono" id="tb-crumb">Overview</span>': '<span class="mono" id="tb-crumb">Tổng quan</span>',
    '>← → navigate<': '>← → chuyển bài<',
    '>⌂ Overview<': '>⌂ Tổng quan<',
    'aria-label="Switch to dark mode"': 'aria-label="Chuyển sang chế độ tối"',
    '<div class="section-head"><h2>Curriculum</h2>': '<div class="section-head"><h2>Chương trình học</h2>',
    '>click any lesson<': '>bấm vào bài bất kỳ<',
    "{id:'complete',title:'Finish course'}": "{id:'complete',title:'Hoàn thành khoá học'}",
    '<span class="nl-label">← Previous</span>': '<span class="nl-label">← Bài trước</span>',
    '<span class="nl-label">Start</span><span class="nl-title">First lesson</span>':
        '<span class="nl-label">Bắt đầu</span><span class="nl-title">Bài đầu tiên</span>',
    '<span class="cl">Mark complete</span>': '<span class="cl">Đánh dấu hoàn thành</span>',
    '<span class="nl-label">Next →</span>': '<span class="nl-label">Bài tiếp →</span>',
    "l.textContent=done?'✓ Completed':'Mark complete'":
        "l.textContent=done?'✓ Đã hoàn thành':'Đánh dấu hoàn thành'",
    "crumb='Overview'": "crumb='Tổng quan'",
    "crumb='Complete'": "crumb='Hoàn thành'",
    "(ok?'✓ Correct. ':'✗ Not quite. ')": "(ok?'✓ Chính xác. ':'✗ Chưa đúng. ')",
    "'Switch to light mode':'Switch to dark mode'":
        "'Chuyển sang chế độ sáng':'Chuyển sang chế độ tối'",
    '<a class="btn btn-primary" href="#overview">Back to start</a>':
        '<a class="btn btn-primary" href="#overview">Về trang đầu</a>',
}


def esc_js(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    c = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    tpl = Path(c.get("template", DEFAULT_TEMPLATE)).read_text(encoding="utf-8")
    frags_dir = Path(c["fragmentsDir"])
    out = Path(c["out"])
    lang = c.get("lang", "en")

    # ---- load fragments ----
    mods = {}
    for meta_path in sorted(frags_dir.glob("module-*-meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        n = int(meta["module"])
        html = (frags_dir / f"module-{n}.html").read_text(encoding="utf-8")
        mods[n] = (html, meta)
    if not mods:
        print(f"ERROR: no module-*-meta.json in {frags_dir}")
        return 1
    order = sorted(mods)
    n_lessons = sum(len(mods[n][1]["lessons"]) for n in order)
    total_min = sum(l.get("minutes", 7) for n in order for l in mods[n][1]["lessons"])
    hours = round(total_min / 60 * 2) / 2

    # ---- head / theme ----
    tpl = tpl.replace('<html lang="en">', f'<html lang="{lang}">')
    tpl = re.sub(r"<title>.*?</title>", f"<title>{c['title']}</title>", tpl, count=1, flags=re.S)
    if re.search(r'<meta name="description"', tpl):
        tpl = re.sub(r'<meta name="description" content="[^"]*">',
                     f'<meta name="description" content="{c["metaDescription"]}">', tpl)
    else:
        tpl = tpl.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                          '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                          f'<meta name="description" content="{c["metaDescription"]}">')
    tpl = re.sub(r'<body data-theme="[^"]*">', f'<body data-theme="{c.get("theme", "navy")}">', tpl)

    # ---- sidebar brand ----
    tpl = re.sub(r'<div class="sidebar-brand-title">.*?</div>',
                 f'<div class="sidebar-brand-title">{c.get("sidebarBrandHtml", c["title"])}</div>',
                 tpl, count=1, flags=re.S)
    sub = c.get("sidebarSub") or (f"{n_lessons} bài · phiên bản 2026" if lang == "vi"
                                  else f"{n_lessons} lessons · 2026 edition")
    tpl = re.sub(r'<div class="sidebar-brand-sub">.*?</div>',
                 f'<div class="sidebar-brand-sub">{sub}</div>', tpl, count=1, flags=re.S)

    # ---- hero ----
    h = c["hero"]
    chips = h.get("chips") or ([f"⏱ ~{hours:g} giờ", "📶 L1 → L5", f"🧩 {n_lessons} bài",
                                "✅ Quiz + takeaway mỗi bài"] if lang == "vi" else
                               [f"⏱ ~{hours:g} hours", "📶 L1 → L5", f"🧩 {n_lessons} lessons",
                                "✅ Quizzes + takeaways"])
    chips_html = "\n            ".join(f'<span class="chip">{x}</span>' for x in chips)
    hero_new = f'''          <span class="hero-kicker">{h["kicker"]}</span>
          <h1>{h["h1Html"]}</h1>
          <p class="hero-sub">{h["subHtml"]}</p>
          <div class="hero-meta">
            {chips_html}
          </div>
          <div style="margin-top:28px;display:flex;gap:12px;flex-wrap:wrap">
            <a class="btn btn-primary" id="start-btn">{h.get("startLabel", "Start learning →")}</a>
            <a class="btn btn-ghost" href="#curriculum">{h.get("curriculumLabel", "See curriculum")}</a>
          </div>'''
    tpl = re.sub(r'          <span class="hero-kicker">.*?</div>\n        </div>\n      </div>',
                 hero_new + "\n        </div>\n      </div>", tpl, count=1, flags=re.S)

    # ---- glossary (optional) ----
    if c.get("glossary"):
        rows = "\n".join(f"            <tr><td><b>{t}</b></td><td>{d}</td></tr>"
                         for t, d in c["glossary"])
        head = ("Bảng thuật ngữ", "nghĩa dùng trong khoá này", "Thuật ngữ", "Nghĩa (như dùng trong khoá)") \
            if lang == "vi" else ("Glossary", "as used in this course", "Term", "Meaning (as used here)")
        glossary = f'''
      <div class="container section-pad" id="glossary">
        <div class="section-head"><h2>{head[0]}</h2><span class="line"></span><span class="mono" style="font-size:11px;color:var(--ink-3)">{head[1]}</span></div>
        <div class="table-wrap"><table>
          <thead><tr><th style="width:220px">{head[2]}</th><th>{head[3]}</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table></div>
      </div>
'''
        tpl = tpl.replace('        <div id="toc-body"></div>\n      </div>\n    </section>',
                          '        <div id="toc-body"></div>\n      </div>\n' + glossary + '    </section>')

    # ---- modules ----
    blocks = []
    intros = {int(k): v for k, v in c.get("moduleIntros", {}).items()}
    for n in order:
        html, meta = mods[n]
        intro = intros.get(n, "")
        blocks.append(f'''    <!-- ============ MODULE {n} ============ -->
    <div class="container">
      <header class="module-header" data-module="{n}">
        <span class="eyebrow">Module {n:02d} · {meta["part"]}</span>
        <h2>{meta["moduleTitle"]}</h2>
        <p>{intro}</p>
      </header>
{html.strip()}
    </div><!-- /container module {n} -->''')
    start = tpl.index("    <!-- ============================================================\n         MODULE 1")
    end_marker = "</div><!-- /container module 1 -->"
    end = tpl.index(end_marker) + len(end_marker)
    tpl = tpl[:start] + "\n\n".join(blocks) + tpl[end:]

    # ---- completion ----
    comp = c.get("completion", {})
    if comp:
        tpl = re.sub(r"        <h2>Course complete</h2>\n        <p>.*?</p>",
                     f"        <h2>{comp['h2']}</h2>\n        <p>{comp['pHtml']}</p>",
                     tpl, count=1, flags=re.S)
        if comp.get("backLabel"):
            tpl = tpl.replace('<a class="btn btn-primary" href="#overview">Back to start</a>',
                              f'<a class="btn btn-primary" href="#overview">{comp["backLabel"]}</a>')
    if c.get("footerHtml"):
        tpl = re.sub(r'<footer class="site">.*?</footer>',
                     f'<footer class="site">{c["footerHtml"]}</footer>', tpl, count=1, flags=re.S)

    # ---- engine config + LESSONS ----
    tpl = re.sub(r"const COURSE_SLUG\s*=\s*'[^']*';",
                 f"const COURSE_SLUG  = '{c['slug']}';", tpl, count=1)
    tpl = re.sub(r"const COURSE_TITLE\s*=\s*'[^']*';",
                 f"const COURSE_TITLE = '{esc_js(c['title'])}';", tpl, count=1)
    rows = []
    for n in order:
        _, meta = mods[n]
        for l in meta["lessons"]:
            rows.append(f"  {{id:'{l['id']}', mod:{n}, part:'{esc_js(meta['part'])}', "
                        f"title:'{esc_js(l['title'])}', desc:'{esc_js(l.get('desc', ''))}'}},")
    tpl = re.sub(r"const LESSONS = \[.*?\n\];",
                 "const LESSONS = [\n" + "\n".join(rows) + "\n];", tpl, count=1, flags=re.S)
    # sidebar strips the part prefix for the group label — accept localized prefixes too
    tpl = tpl.replace("part.replace(/^Part [IVX]+ · /,'')",
                      "part.replace(/^(?:Part|Phần) [IVX]+ · /,'')")

    # ---- chrome localization ----
    table = dict(VI_CHROME) if lang == "vi" else {}
    table.update(c.get("chromeOverrides", {}))
    for old, new in table.items():
        tpl = tpl.replace(old, new)
    if lang == "vi":
        tpl = re.sub(r'<span class="eyebrow">Lesson (\d+)\.(\d+)</span>',
                     r'<span class="eyebrow">Bài \1.\2</span>', tpl)

    out.write_text(tpl, encoding="utf-8")
    print(f"WROTE {out} ({len(tpl):,} bytes · {len(order)} modules · {n_lessons} lessons · ~{total_min} min)")

    # ---- hand off to the validator ----
    validator = SKILL_DIR / "scripts" / "validate_course.py"
    if validator.exists():
        r = subprocess.run([sys.executable, str(validator), str(out)])
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
