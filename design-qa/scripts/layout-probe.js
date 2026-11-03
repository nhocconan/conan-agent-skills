// Layout probe: COUNTS the composition defects a screenshot review keeps missing, so a critique cites
// numbers instead of adjectives. Framework-agnostic; runs in the page. Report-only; never edits.
//
//   Playwright:  const r = await page.evaluate(`${readFileSync(thisFile, 'utf8')}\nlayoutProbe()`);
//   Console:     paste, then call layoutProbe() (options below)
//
// Returns { findings: string[], metrics: {...} }. A finding is a lead for the human/agent reviewer,
// not a verdict: confirm it on the screenshot. Exempt a subtree with [data-probe-ok="<reason>"].
//
// Checks
//   bar-*     every horizontal bar (header, nav, [role=toolbar|menubar|tablist]): controls of mixed
//             heights, icon glyphs of mixed sizes, uneven gaps, icon-only controls whose glyph is small for the box,
//             one control styled unlike all its siblings (reads as a badge or an error)
//   scale-*   in main: how many distinct control heights / font sizes / small-icon sizes are used
//   ragged-row card-like siblings on one row whose bottom edges differ
//   overflow  horizontal page scroll; text cut by overflow (ellipsis or clip)
//   wall      a run of prose with no heading, figure, list or table to break it
//   links     prose where links outnumber the sentences around them (a link farm)
//   panel     an open menu/dialog/popover listing many items with no grouping
function layoutProbe({
  wallWords = 160,
  linkPer100Words = 6,
  panelItems = 9,
  minGlyphRatio = 0.4,
  gapSpread = 2,
} = {}) {
  const findings = [];
  const exempt = (el) => !!el.closest('[data-probe-ok]');
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity !== 0;
  };
  const label = (el) =>
    (el.getAttribute('aria-label') || el.textContent || el.tagName).trim().replace(/\s+/g, ' ').slice(0, 28);
  const CONTROL = 'button, a[href], [role="button"], [role="tab"], [role="menuitem"], input:not([type="hidden"]), select';
  const tally = (values) => values.reduce((m, v) => ((m[v] = (m[v] || 0) + 1), m), {});
  const look = (el) => {
    const s = getComputedStyle(el);
    const bordered = parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none';
    const filled = s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent';
    return `${bordered ? 'border' : '-'}/${filled ? 'fill' : '-'}`;
  };

  // ── Bars ────────────────────────────────────────────────────────────────
  const bars = [...document.querySelectorAll('header, nav, [role="toolbar"], [role="menubar"], [role="tablist"]')]
    .filter((b) => visible(b) && !exempt(b))
    .filter((b) => b.getBoundingClientRect().width > b.getBoundingClientRect().height * 3);
  const metrics = { bars: [] };
  for (const bar of bars) {
    const top = [...bar.querySelectorAll(CONTROL)].filter(
      (c) => visible(c) && !exempt(c) && !c.parentElement.closest(CONTROL),
    );
    if (top.length < 3) continue;
    // Controls on the same row as the bar's middle, left to right.
    const bb = bar.getBoundingClientRect();
    const row = top
      .map((c) => ({ c, r: c.getBoundingClientRect() }))
      .filter(({ r }) => r.top < bb.top + bb.height * 0.75 && r.bottom > bb.top + bb.height * 0.25)
      .sort((a, b) => a.r.left - b.r.left);
    if (row.length < 3) continue;
    const name = `${bar.tagName.toLowerCase()}${bar.getAttribute('aria-label') ? `[${bar.getAttribute('aria-label')}]` : ''}`;
    const heights = row.map(({ r }) => Math.round(r.height));
    const glyphs = row
      .map(({ c, r }) => {
        const g = c.querySelector('svg, img');
        if (!g || !visible(g)) return null;
        const gr = g.getBoundingClientRect();
        const iconOnly = !(c.innerText || '').trim();
        return { c, size: Math.round(Math.max(gr.width, gr.height)), box: Math.min(r.width, r.height), iconOnly };
      })
      .filter(Boolean);
    const gaps = row.slice(1).map(({ r }, i) => Math.round(r.left - row[i].r.right)).filter((g) => g >= 0 && g < 64);
    const looks = row.map(({ c }) => look(c));
    const entry = { bar: name, controls: row.length, heights: tally(heights), glyphs: tally(glyphs.map((g) => g.size)), gaps };
    metrics.bars.push(entry);
    if (Object.keys(entry.heights).length > 2)
      findings.push(`bar-heights ${name}: ${Object.keys(entry.heights).length} control heights ${JSON.stringify(entry.heights)}`);
    if (Object.keys(entry.glyphs).length > 1)
      findings.push(`bar-glyphs ${name}: icon sizes ${JSON.stringify(entry.glyphs)} — one size per bar`);
    for (const g of glyphs)
      if (g.iconOnly && g.size / g.box < minGlyphRatio)
        findings.push(`bar-glyph-small ${name}: "${label(g.c)}" glyph ${g.size}px in a ${Math.round(g.box)}px control (<${minGlyphRatio * 100}%)`);
    if (gaps.length > 2 && Math.min(...gaps) >= 0 && Math.max(...gaps) > gapSpread * Math.max(4, Math.min(...gaps)))
      findings.push(`bar-gaps ${name}: gaps ${gaps.join(',')}px — uneven rhythm (cluster or equalize)`);
    const lookCount = tally(looks);
    const odd = row.filter(({ c }, i) => lookCount[looks[i]] === 1 && looks[i] !== '-/-');
    if (row.length >= 4 && odd.length === 1)
      findings.push(`bar-odd-one ${name}: "${label(odd[0].c)}" is the only ${looks[row.indexOf(odd[0])]} control — reads as a badge/alert unless it is THE primary action`);
  }

  // ── Scales in main ──────────────────────────────────────────────────────
  const main = document.querySelector('main') || document.body;
  const controls = [...main.querySelectorAll(CONTROL)].filter((c) => visible(c) && !exempt(c));
  const ctlH = tally(controls.map((c) => Math.round(c.getBoundingClientRect().height)).filter((h) => h >= 20 && h <= 64));
  const textEls = [...main.querySelectorAll('*')].filter(
    (el) => !exempt(el) && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) && visible(el),
  );
  const fonts = tally(textEls.map((el) => getComputedStyle(el).fontSize));
  const icons = tally(
    [...main.querySelectorAll('svg')]
      .filter((s) => visible(s) && !exempt(s) && !s.parentElement.closest('svg'))
      .map((s) => Math.round(s.getBoundingClientRect().width))
      .filter((w) => w > 0 && w <= 32),
  );
  Object.assign(metrics, { controlHeights: ctlH, fontSizes: fonts, iconSizes: icons });
  const sig = (t) => Object.entries(t).filter(([, n]) => n >= 2).length;
  if (sig(ctlH) > 4) findings.push(`scale-controls: ${sig(ctlH)} control heights in use ${JSON.stringify(ctlH)} — snap to the kit's sizes`);
  if (sig(fonts) > 6) findings.push(`scale-type: ${sig(fonts)} font sizes in use ${JSON.stringify(fonts)} — collapse to the type scale`);
  if (sig(icons) > 3) findings.push(`scale-icons: ${sig(icons)} icon sizes in use ${JSON.stringify(icons)}`);

  // ── Ragged rows: card-like siblings on one row with different bottom edges ──
  let ragged = 0;
  for (const box of main.querySelectorAll('*')) {
    if (ragged >= 5 || exempt(box) || !visible(box)) continue;
    const d = getComputedStyle(box).display;
    if (!/grid|flex/.test(d) || getComputedStyle(box).flexDirection.startsWith('column')) continue;
    const cards = [...box.children].filter((c) => visible(c) && look(c) !== '-/-');
    if (cards.length < 2) continue;
    const rows = {};
    for (const c of cards) {
      const r = c.getBoundingClientRect();
      (rows[Math.round(r.top / 4)] ||= []).push(r);
    }
    for (const row of Object.values(rows)) {
      if (row.length < 2) continue;
      const bottoms = row.map((r) => Math.round(r.bottom));
      if (Math.max(...bottoms) - Math.min(...bottoms) > 4) {
        ragged++;
        findings.push(`ragged-row: ${row.length} cards side by side end at ${[...new Set(bottoms)].join('/')}px — share one bottom edge`);
      }
    }
  }

  // ── Overflow ────────────────────────────────────────────────────────────
  if (document.documentElement.scrollWidth > window.innerWidth + 1)
    findings.push(`overflow-page: page scrolls sideways (${document.documentElement.scrollWidth}px > ${window.innerWidth}px)`);
  const cut = textEls
    .filter((el) => {
      const s = getComputedStyle(el);
      return s.overflow !== 'visible' && el.scrollWidth > el.clientWidth + 1 && !el.closest('table');
    })
    .map((el) => `"${label(el)}"`);
  if (cut.length) findings.push(`overflow-text: ${cut.length} cut text(s) outside tables: ${cut.slice(0, 6).join(', ')}`);

  // ── Prose: walls and link farms ─────────────────────────────────────────
  const BREAK = /^(H[1-6]|FIGURE|IMG|PICTURE|SVG|TABLE|UL|OL|PRE|BLOCKQUOTE|DETAILS|VIDEO|HR)$/;
  let run = [];
  const flush = () => {
    const words = run.reduce((n, el) => n + el.innerText.split(/\s+/).filter(Boolean).length, 0);
    if (words >= wallWords) findings.push(`wall: ${words} words in ${run.length} paragraph(s) from "${label(run[0])}" with no heading, figure, list or table`);
    run = [];
  };
  const flow = [...main.querySelectorAll('p, h1, h2, h3, h4, h5, h6, figure, img, picture, table, ul, ol, pre, blockquote, details, video, hr')].filter(
    (el) => visible(el) && !exempt(el) && !el.parentElement.closest('p, li, table, figure, blockquote'),
  );
  for (const el of flow) (el.tagName === 'P' ? run.push(el) : BREAK.test(el.tagName) && flush());
  flush();
  const paras = [...main.querySelectorAll('p, li')].filter((el) => visible(el) && !exempt(el) && !el.closest('nav'));
  const proseWords = paras.reduce((n, el) => n + el.innerText.split(/\s+/).filter(Boolean).length, 0);
  const proseLinks = paras.reduce((n, el) => n + el.querySelectorAll('a[href]').length, 0);
  metrics.prose = { words: proseWords, links: proseLinks };
  if (proseWords > 80 && (proseLinks / proseWords) * 100 > linkPer100Words)
    findings.push(`links: ${proseLinks} links in ${proseWords} words of prose (> ${linkPer100Words}/100) — a link farm, not guidance`);

  // ── Open panels ─────────────────────────────────────────────────────────
  for (const p of document.querySelectorAll('[role="menu"], [role="dialog"], [role="listbox"], [popover], [data-state="open"]')) {
    if (!visible(p) || exempt(p)) continue;
    const items = [...p.querySelectorAll('[role="menuitem"], [role="option"], a[href], button')].filter(visible);
    const groups = p.querySelectorAll('[role="group"], [role="separator"], hr, h2, h3, h4, [role="heading"], fieldset').length;
    if (items.length >= panelItems && groups === 0)
      findings.push(`panel: "${label(p)}" lists ${items.length} items with no group heading or separator in markup (check the shot: visual-only groups are also invisible to screen readers)`);
  }
  return { findings, metrics };
}
