# EDGE WAVE 2 DESIGN, T4-T6 (2026-11-14, Fable)

**Decision: T4-T6 are three single-cell replications on FRESH coins of the only three leads whose sign held in both DEV and VAL and where the fee is under 0.06 R. No new idea, no grid. The lever is sample size and coin independence, because every one of these leads failed only on CI width or multiplicity, never on sign or fees.**

## Why not the four lines named in the brief

Checked trunk (`origin/fast-track`) before designing. The laptop already ran and killed them today:

| Brief line | Already tested as | Result | So |
|---|---|---|---|
| Buy-zone ladder (HL_BREAK) | `buyzone_test1_ladder_2026-11-14`, 22 coins | UP+BASE VAL +0.037 R, n 97, placebo pct 81 | dead, not repeated |
| Capitulation signature long | `buyzone_test4_capitulation` (reverted for CI, result stands) + 7 washout studies + T2 running | VAL -0.077 R, n 221; DEV +0.125 | T2 owns the cycle split; episodes cannot be powered (about 15-18 market flushes since 2017) |
| Big trades at bottoms | `buyzone_test5_flowlead` | KILL, top-bottom quintile spread CI spans 0 | dead |
| Daily trend with phase gate | edge7, edge8, T3 running | below buy-and-hold | T3 owns it |

What trunk also shows, and the postmortem did not have: `buyzone_test3_bear4h` (bear-phase 4h bearish-divergence short) is positive in DEV (+0.107 R, n 287), VAL (+0.090, n 211) and RECENT (+0.238, n 127, CI [0.01, 0.52], placebo pct 99.5); pooled +0.100 R, CI [-0.01, 0.21], placebo pct 99.2. It was killed on the VAL CI only.

## The three picks

| | T4 squeeze long | T5 bear divergence short | T6 deep-drawdown dip long |
|---|---|---|---|
| Source cell (frozen, definitions unchanged) | combo miner named T3: FUND_LO and NB_ABS and BRK5 onset, 4h, long, non-bear phases, RIDE exit | `buyzone_test3_bear4h` PRE_REG, BEAR flag true, 4h, short | edge9 weekly-streak row DD20 E1 X2: weekly close <= 0.80 x max weekly close of prior 8 weeks, buy Monday open, exit close 2 weeks later, 8-week cooldown |
| Seen result on the old coins | DEV +2.675 R (n 45), VAL +2.420 R (n 72), CI [0.217, 5.887], placebo p 0.047; T3R exit row +0.399 / +0.220 | DEV +0.107, VAL +0.090, RECENT +0.238, pooled CI [-0.01, 0.21] | DEV +3.0%, VAL +2.6% (n 391), CI low -0.2%, placebo p 0.053, ex-best-3-weeks +1.3% |
| Timeframe / hold | 4h, days to 60 days | 4h, up to 7 days | weekly entry, 14 days |
| Stop distance | max(2.5 ATR14 4h, 2%), typically 4-6% | pivot high + max(0.6 ATR14, 0.5%), typically 2-5% | none on the primary row (time exit); secondary row stop = 2.5 ATR14 1d, typically 10-15% |
| Fee at 12 bp in R | 0.02-0.03 R | 0.03-0.06 R | 0.01 R (0.12% against a +2.6% mean) |
| Gross needed to pass | about +0.10 R | about +0.10 R | about +0.5% per trade |
| Gross seen | +0.25 to +2.4 R (exit dependent) | about +0.15 R | +2.7% (about +0.25 R on the stop row) |
| Active today | BTC MIX_L by the miner label: yes if a signal prints | yes (BTC BEAR / MARKDOWN) | yes (BTC -21% from the 8-week high, 6 red weeks) |
| Differs from failed studies | edge-crowding, ratio-fade: faded positioning with no price trigger and short holds. This needs a breakout bar and rides | htf-divergence (BTC only, 400 cells, ungated) and test3 (22 coins). Same rule, new coins | edge9 streak rows (momentum in bear, failed); capitulation longs (intraday bars, one crash date). This is weekly, 213 + 391 events |
| Honest weak point | RIDE profit is tail-shaped: DEV TRAIL row was -0.017 R. The T3R row carries the ex-best-5 gate | gross is +0.15 R, below the +0.30 R line; it can only pass by count | no stop on the primary; coins fall together, so weeks, not trades, are the sample |

Fee maths in one line: the postmortem's +0.30 R gross line assumed a 0.5% stop (fee 0.21-0.24 R). These three use stops of 2-15%, so the fee is 0.01-0.06 R and the break-even gross is about +0.05 to +0.10 R. Fees cannot decide any of them; the count of independent weeks does.

## Fresh-coin rule (all three)

- Universe = Binance spot USDT coins NOT in the source study's list, taken from one frozen candidate list (the T3 study's 49-coin list, already cached with funding, plus the source study's exclusions). Delisted coins kept where the archive has them. No coin dropped for performance.
- Primary sample = fresh coins only. The rule was frozen on other coins, so every fresh-coin trade is out of sample by coin. It is NOT out of sample by calendar time (same weeks as the old coins). That is why the split by time stays: DEV <= 2023-12-31, VAL >= 2024-01-01, by signal bar.
- Old + fresh pooled is a descriptive row only.

## Pass bars (same for all three, fixed now, at 12 bp + funding where a perp is implied)

1. VAL fresh: n >= 30 trades and >= 20 entry weeks, else UNDERPOWERED.
2. VAL fresh mean net > 0 and week-cluster bootstrap 95% CI low > 0 (clusters = ISO entry week over all coins, 2000 resamples, seed 1114).
3. DEV fresh mean net > 0 (sign agreement).
4. Excess over random entries: 1000 draws, same coin, same phase flag, same split, same stop distance and exit; real mean above the 97.5th percentile.
5. Ex-best-5 entry weeks mean > 0 (T4: on the T3R row, because RIDE is tail-shaped by design).
6. Buy-and-hold baseline: T4, T6 mean net daily return in position >= equal-weight fresh basket over the same eligible days; T5 >= short-and-hold of the basket over BEAR days.
7. Top-coin removal keeps the mean > 0, else FRAGILE (reported, blocks PASS).
One cell per test, family m = 3 across T4-T6; Holm over the three VAL one-sided p-values is reported next to each verdict (a PASS that fails Holm is labelled MULTIPLICITY-FLAGGED).

## Kill criteria

| Test | KILL the line if |
|---|---|
| T4 | fresh VAL mean <= 0 on RIDE, or T3R row ex-best-5 <= 0, or excess over same-phase random <= 97.5th pct with n >= 60. Then "squeeze long" was a tail of 20 old coins |
| T5 | fresh pooled (DEV+VAL) mean <= 0, or fresh VAL placebo pct < 90 with n >= 200. Then the +0.10 R was the old-coin sample. If fresh mean is +0.05 to +0.15 with CI spanning 0 again: verdict REPLICATED-WEAK, not KILL, and the next step is size (all listed perps), not a new rule |
| T6 | fresh VAL mean <= 0, or the stop row (secondary) mean R <= 0, or ex-best-5 weeks <= 0. Then DD20 was drift plus survivorship |

## Process per study (Workflow, one worktree each under <local-path>)

1. One shared fetch (4h + 1d spot with taker volume, funding) into `F:\MTS\data_cache\binance\wave2-1114\`, sidecar meta, reuse of the T3 cache read-only.
2. PRE_REG frozen and committed before any outcome (`## Context`, `Regime mix:`, SOURCED / OURS on every parameter, `prereg_gate.py` output pasted; a BLOCK is reported, the run is ordered).
3. Coder: study code with uniquely prefixed module names (`t4_*.py`; bare `lib.py` broke CI today), synthetic-bar tests only (look-ahead, stop-wins-ties, fee arithmetic from `fees.py`, planted edge), mutation check. Step A writes the trade list, no pooled statistics.
4. Independent recompute of 3 dated trades from raw klines and FORMULAS.md, and an adversarial look-ahead / fee audit, in parallel, before statistics.
5. Statistics, RESULT.md, notes file `T<n>_RESULT_1114.md`; a final checker re-derives the verdict from the summary numbers against the PRE_REG bars.
6. Ship one study at a time when CI is green; CI checked per sha; revert at once if red.

All agents Sonnet (CLAUDE.md cost rule), BelowNormal priority, no orders, public data only. Any PASS stops that line: blind review and a testnet-forward card need the operator's go.

Labels: every threshold above is OURS or copied unchanged from the named source PRE_REG; none is a trader's.
