// Narrow-wrap probe: flags text blocks that wrap to >= 2 lines in a column much narrower than the space
// their container offers, with nothing beside them in the gap. Framework-agnostic; runs in the page.
//
//   Playwright:  const problems = await page.evaluate(`${readFileSync(thisFile, 'utf8')}\nnarrowWrapProbe()`);
//   Console:     paste, then call narrowWrapProbe() (options: { ratio, minGap, minChars })
//
// Returns strings like: p "Manage the templates every channel…" wraps to 2 lines in 810px of 1136px (71%)
// Exempt: tables, out-of-flow boxes (fixed/absolute dialogs, popovers), items of a multi-column grid, a whole
// column centred in its container (a login card), and anything inside [data-narrow-ok="<reason>"].
function narrowWrapProbe({ ratio = 0.85, minGap = 96, minChars = 20 } = {}) {
  const BLOCK = new Set(['block', 'list-item', 'flow-root', 'inline-block', 'table-caption']);
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const contentBox = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    const left = r.left + parseFloat(s.borderLeftWidth) + parseFloat(s.paddingLeft);
    const right = r.right - parseFloat(s.borderRightWidth) - parseFloat(s.paddingRight);
    return { left, right, width: right - left };
  };
  const lineCount = (el) => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const s = getComputedStyle(el);
    const lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.2;
    const tops = [...range.getClientRects()]
      .filter((r) => r.width > 0 && r.height > 0)
      .map((r) => r.top)
      .sort((a, b) => a - b);
    let n = tops.length ? 1 : 0;
    for (let i = 1; i < tops.length; i++) if (tops[i] - tops[i - 1] > lh / 2) n++;
    return n;
  };
  const outOfFlow = (el) => ['fixed', 'absolute'].includes(getComputedStyle(el).position);
  const multiColumnGrid = (el) => {
    const s = getComputedStyle(el);
    return s.display.includes('grid') && s.gridTemplateColumns.trim().split(/\s+/).length > 1;
  };

  const problems = new Set();
  const seen = new Set();
  for (const el of document.querySelectorAll('body *')) {
    if (!visible(el) || !BLOCK.has(getComputedStyle(el).display)) continue;
    if (el.closest('table, .sr-only, [aria-hidden=true], [data-narrow-ok]')) continue;
    if ((el.textContent || '').trim().length < minChars) continue;
    // Leaf text block only: inline children are fine, block children are measured on their own.
    if ([...el.children].some((c) => visible(c) && getComputedStyle(c).display !== 'inline')) continue;
    const lines = lineCount(el);
    if (lines < 2) continue;

    // Climb to the effective column: the outermost ancestor no wider than this text's box.
    let box = el;
    let container = el.parentElement;
    while (container && container !== document.body && !outOfFlow(box)) {
      if (contentBox(container).width > box.getBoundingClientRect().width + 2) break;
      box = container;
      container = container.parentElement;
    }
    if (!container || container === document.body || outOfFlow(box) || seen.has(box)) continue;
    if (multiColumnGrid(container)) continue;
    seen.add(box);

    const c = contentBox(container);
    const b = box.getBoundingClientRect();
    if (b.width >= ratio * c.width || c.width - b.width < minGap) continue;
    // A whole column centred on purpose is layout; a centred text element capped narrow is not exempt.
    const leftGap = b.left - c.left;
    const rightGap = c.right - b.right;
    if (box !== el && leftGap > 8 && Math.abs(leftGap - rightGap) <= 4) continue;
    // Something beside the column (actions, an aside, a sibling card) uses the gap.
    const occupied = [...container.children].some((s) => {
      if (s === box || !visible(s)) return false;
      const r = s.getBoundingClientRect();
      return r.top < b.bottom - 1 && b.top < r.bottom - 1 && (r.right > b.right + 1 || r.left < b.left - 1);
    });
    if (occupied) continue;
    const text = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 50);
    problems.add(
      `${el.tagName.toLowerCase()} "${text}" wraps to ${lines} lines in ${Math.round(b.width)}px of ` +
        `${Math.round(c.width)}px (${Math.round((100 * b.width) / c.width)}%)`,
    );
  }
  return [...problems];
}
