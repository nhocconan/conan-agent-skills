# Retrofit a codebase to the baseline

A counted job, separate from feature work. Read the project rulebook first; its rules win.

1. **Count each tell** with a search over rendered source, and keep the numbers:
   `transition-all` / `transition: all`; Enter key handlers with no `isComposing` check;
   `outline: none` with no `:focus-visible` replacement; modal, drawer and sheet components
   without `overscroll-behavior: contain` or an inert background; no `touch-action` base rule;
   no root `color-scheme` / `theme-color`; `type="number"` on codes and identifiers; form
   buttons with no `type`; a lazy-loaded largest image.
2. **Fix at the shared layer first**: base stylesheet, kit component, layout. A page-level patch
   is the last resort and is listed as such.
3. **Keep the look**: name the transition properties an element animates today; a visual change
   is allowed only where the tell is the visual bug.
4. **Guard each class** the way the project guards recurring bugs (type or schema, behavioural
   test at the shared component, static audit with a baseline that only shrinks), and add one
   rule line to the project rulebook in its own format, inside its size budget.
5. **Report** before/after counts per tell, the files changed, the guard added, conflicts with
   project rules (kept, not overridden) and what was skipped.
