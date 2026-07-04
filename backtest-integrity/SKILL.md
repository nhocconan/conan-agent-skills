---
name: backtest-integrity
description: Honesty checklist for quantitative strategy research — backtests, factor studies, trading-system evaluation in any market (stocks, crypto, futures). Catches the bugs that inflate results (wrong annualization, look-ahead via truncated features, survivorship, ignored costs), enforces out-of-sample discipline (walk-forward, champion/challenger, decay monitoring) and auditable provenance. Use when writing or reviewing any backtest, when a result looks great (high Sharpe, tiny drawdown), before promoting a strategy to production/live money, or when the user says "backtest", "Sharpe", "CAGR", "edge", "chiến lược".
---

# Backtest Integrity

Every celebrated backtest number deserves the null hypothesis: **it's a bug.** In one real
project, two quiet bugs inflated every result ~3× for weeks ("Sharpe 1.82 / CAGR 24%" was
really Sharpe 0.8 / 14%). The discipline below is what caught them.

## The prime heuristic

**When a result looks great — Sharpe > 1.5, MaxDD < 5%, smooth equity — suspect a bug FIRST,**
before celebrating, before tuning further, and before showing the user. Great results must
survive this whole checklist and reproduce from a clean re-run.

## Bug classes that inflate results (audit each)

1. **Annualization**: derive periods-per-year from the actual rebalance cadence
   (`ppy = 252 / rebalance_days`) or the real calendar span — never a hardcoded 52/252 that
   doesn't match the loop. Wrong ppy inflates BOTH CAGR and Sharpe multiplicatively.
2. **Look-ahead via truncated features**: never date-filter the raw price/fundamental data
   *before* computing features — a momentum/ADTV feature computed on truncated history ranks
   differently and flatters OOS probes. Build features on FULL history, then **slice the
   equity curve by date** to get period results.
3. **Point-in-time everywhere**: fundamentals as-published (with reporting lag), universe
   membership as-of-date, prices unadjusted for information not yet known. Any join on
   "current" attributes (today's sector, today's shares outstanding) is quiet look-ahead.
4. **Survivorship**: a current-listings universe biases results — but don't just *assert*
   doom either way: **test it empirically** by adding real delisted/blown-up names and
   re-running WITH vs WITHOUT. (Finding from VN large/mid-caps: with a stop-loss the damage
   is bounded and the bias was negligible — the experiment, not the textbook, settles it.)
   Delisted names auto-exclude from LIVE signals; they exist for honest history only.
5. **Costs & capacity**: realistic fees + slippage per market; position sizes capped by
   liquidity (e.g. % of ADTV); no fills at prices the size couldn't get. An edge that dies
   at 40bps round-trip was never an edge.
6. **Silent data degradation**: verify the data layer actually loaded (a paid-data package
   silently missing degrades to empty frames with no error; a mis-parameterized API call can
   masquerade as "fundamentals are broken"). Add a `doctor`/probe command and run it before
   trusting any research run.

## Out-of-sample discipline (what keeps you honest over time)

- **Walk-forward, not one split**: evaluate rank-IC / returns on rolling OOS windows; a
  single lucky split proves nothing.
- **Champion/challenger**: the production strategy is the champion; a challenger must beat
  it OOS (not in-sample) before promotion. Keep a decay monitor — factors rot; retire what
  decayed instead of re-tuning it back to life.
- **Headline must reproduce**: a number that can't be regenerated from config + data does
  not exist. If the "11.1% confluence" doesn't reproduce, it's gone from the story.
- **Report full-period AND a recent window** side by side — a bubble sub-period must not
  flatter the headline (a strategy that made everything 2020–2022 and nothing since is
  flat, not "14% CAGR").
- Parameter sweeps: report the neighborhood, not the peak. A config whose CAGR swings 3–42%
  across nearby params is overfit noise.

## Provenance ("không bịa" — every published number is auditable)

Every backtest result surfaced to a UI/report carries: config hash, data-lake fingerprint/
version, code version, run date, and the full-span ledger (no truncated last-N-rows chart
that makes 9 years of equity look like 11 months). If any of those are missing, the number
is a draft, not a result.

## Promotion gate (before live money)

Full checklist above clean + costs-on OOS edge still positive + risk controls tested (stop
behavior, regime brake, max drawdown budget) + paper/canary period defined + a written
decision-log entry (what was promoted, why, what would falsify it). Record negative results
too — "no edge found" findings prevent re-running the same dead end next quarter.

## Output

Report: what was audited, bugs found (class → file → impact on the numbers), corrected
before→after metrics, and the honest bottom line — including "no robust edge" when that's
the truth. Never soften a corrected number back toward the buggy one.
