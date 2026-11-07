---
name: backtest-integrity
description: >-
  Use when writing or reviewing a backtest, factor study or trading-system
  evaluation, investigating suspicious Sharpe/CAGR/drawdown results, or assessing
  a strategy before live trading ("backtest", "edge", "chiến lược"). Catches result
  inflation from annualization, look-ahead, survivorship and ignored costs; enforces
  out-of-sample evaluation and auditable provenance. Excludes standalone definitions
  and formula explanations.
---

# Backtest Integrity

## The prime heuristic

**When a result looks great — Sharpe > 1.5, MaxDD < 5%, smooth equity — suspect a bug FIRST,**
before celebrating, before tuning further, and before showing the user. Great results must
survive this whole checklist and reproduce from a clean re-run.

## Bug classes that inflate results (audit each)

1. **Annualization**: use the frequency of the sampled return series and its market
   calendar, not the trading/rebalance frequency. Daily marked-to-market returns
   remain daily even with monthly rebalances. Compute CAGR from elapsed years;
   document the assumptions behind Sharpe scaling, especially serial correlation.
2. **Causal features and warm-up**: retain enough pre-period history for rolling features,
   using only information available at each bar. Fit scalers, feature selection and models
   on each training fold only, never the full sample; then slice evaluation outputs by date.
   [Preprocessing leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)
   can inflate scores even when the final estimator uses a proper split.
3. **Point-in-time everywhere**: fundamentals as-published (with reporting lag), universe
   membership as-of-date, prices unadjusted for information not yet known. Any join on
   "current" attributes (today's sector, today's shares outstanding) is quiet look-ahead.
4. **Survivorship**: test it empirically: add delisted/blown-up names and re-run WITH vs
   WITHOUT, using point-in-time membership and delisting returns. A stop-loss does not
   guarantee executable exits. Delisted names auto-exclude from LIVE signals.
5. **Costs & capacity**: fees + slippage per market; size capped by liquidity (e.g. % of
   ADTV). Evaluate net results at the intended venue, size and execution costs.
6. **Silent data degradation**: verify the data layer actually loaded (a data package
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
  not exist. Any quoted figure (an edge percentage, a hit rate, a confluence number) that
  does not come back byte-for-byte from a clean re-run is deleted from the write-up — not
  rounded, not caveated.
- **Report full-period AND a recent window** side by side — a bubble sub-period must not
  flatter the headline (a strategy that made everything 2020–2022 and nothing since is
  flat, not "14% CAGR").
- Parameter sweeps: report the neighborhood, not the peak. A config whose CAGR swings widely
  across nearby params is overfit noise.

## Provenance (every published number is auditable)

Every backtest result surfaced to a UI/report carries: config hash, data-store fingerprint/
version, code version, run date, and the full-span ledger (no truncated last-N-rows chart
that makes 9 years of equity look like 11 months). If any of those are missing, the number
is a draft, not a result.

## Promotion gate (before live money)

Checklist clean and costs-on OOS edge positive, plus: risk controls tested (stop behavior,
regime brake, max drawdown budget), paper/canary period defined, decision-log entry (what
was promoted, why, what would falsify it). Record negative results too.

## Output

Report: what was audited, bugs found (class → file → impact on the numbers), corrected
before→after metrics, and the honest bottom line — including "no robust edge" when that's
the truth. Never soften a corrected number back toward the buggy one.
