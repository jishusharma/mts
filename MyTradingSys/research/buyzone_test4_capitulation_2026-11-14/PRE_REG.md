# PRE_REG: Test 4, capitulation signature at lows (frozen before any outcome is computed)

Source brief: `buy_zone_1114/NEXT5_TESTS.md` Test 4 and its Shared rules. Task from login C ask q-d8cd77. Nothing here is an edge until a fee-net out-of-sample result passes. Only data availability (first Bybit funding/OI timestamps, bar counts) was looked at while writing this file; no signature count, forward return or trade outcome has been computed. Every parameter is OURS unless marked SOURCED. Not a trade instruction.

## Context
Regime: none as a separate gate; the phase below (daily, previous day only) is reported per phase, not used to filter.
Phase: UP, BASE, RANGE, DOWN, POSTPEAK_BEAR, definitions copied unchanged from Test 1 (`buyzone_test1_ladder_2026-11-14/ladder.py::phases`), computed from closed daily bars through the bar before the entry bar. Label "" (not enough history) is reported as NOPHASE and kept in Step 1; in Step 2 it counts only in the all-phase pool.
Session: not applicable, daily bars (UTC day).
Entry (Step 2): next daily open after the signature day's closing bar (OURS).
Regime mix: reported in REPORT.md as share of signature events per phase per split; a split with more than 85% of events from one calendar year is flagged ONE-YEAR and cannot carry a PASS alone. Regime mix in UP: reported; BASE: reported; RANGE: reported; DOWN: reported; POSTPEAK_BEAR: reported; NOPHASE: reported.

## Data (OURS)
| Item | Choice |
|---|---|
| Price | Binance spot daily klines (public `data-api.binance.vision`), partial current day dropped. Cache `C:/Users/e-ngineers/mts_cache/buyzone_test4` (`F:/MTS/data_cache` does not exist on this host), never committed |
| Funding, OI | Bybit linear perpetual public API (`/v5/market/funding/history`, `/v5/market/open-interest` intervalTime 1d), as the brief says (Binance futures unreachable from the study machine). Funding of day d = mean of the 8h prints stamped in UTC day d. OI of day d = the 1d value stamped d (the state at the start of day d, known before day d closes, so conservative against lookahead) |
| Universe | BTC, ETH plus the 20 coins of Test 1 (BNB, XRP, ADA, DOGE, SOL, LTC, LINK, TRX, DOT, AVAX, ATOM, ETC, XLM, BCH, NEO, UNI, NEAR, FIL, ALGO, VET). A coin without a Bybit linear USDT market, or bars before its OI starts, contributes nothing (reported). Fixed now, none added or dropped after outcomes |
| Data start | Bybit OI starts 2020-08 for BTC (first stamp 1596585600000), 2020-10 for ETH and LTC and 2021-03 to 2021-10 for the others seen so far; so DEV is short (about 3.4 years for BTC, less for others). Reported honestly, not repaired |
| Fees | Not applicable to Step 1. Step 2: 12 bp round trip main row, 6 bp sensitivity (SOURCED, Shared rules). Funding paid or received while held is NOT modelled (a long entered at a negative-funding signature mostly receives funding; stated) |

## Signature (SOURCED shape from the brief; thresholds OURS), all causal
Swing low (as Test 1): bar i is a swing low if `Low[i] < Low[i-3..i-1]` and `Low[i] < Low[i+1..i+3]`; known only at the close of bar i+3.
For bar u (the undercut bar), S = the level of the most recent swing low known at the close of u-1 (index <= u-4) and no older than 120 bars (OURS). Failed breakdown: `Low[u] < S` AND there is a bar s in u..u+14 (within 2 weeks, SOURCED) with `Close[s] > S`; s = the first such bar.
Funding negative at the low: funding(day u) < 0 (SOURCED).
OI unwind: `OI[u] / OI[u-7] - 1 <= -5%` (SOURCED: OI down >= 5% over the prior 7 days; stamps u and u-7, both known at the open of u).
SIGNATURE at u (known at the close of s): all three. The signature DATE is s. Nothing after the close of s enters the signature. If u itself closes above S then s = u.
Partial flags (descriptive only): F (funding<0), O (OI unwind), B (failed breakdown); counts for each single and pair are reported next to the full count.

## Step 1: descriptive, no verdict
Lows population (the "38 anatomy lows" list is not in the repo, so recomputed by the same kind of rule on each coin, DECISION OURS): a low L is a swing low with k = 10 (`Low[L]` below `Low[L-10..L-1]` and `Low[L+1..L+10]`), with a fall of at least 25% from the max High of bars L-120..L-1 to Low[L], and with OI and funding available at L (OI[L-7] exists). Lows are ex-post labelled (future bars used), exactly as the anatomy tables; only descriptive.
For each low: sig = the SIGNATURE holds with u = L (the low bar is the undercut bar). Report per group (SIG, NOT-SIG, plus each partial flag): n, forward return 1d / 3d / 7d from Close[L] (median and mean), and the share that made a real lower low within 26 weeks: any `Low < 0.97 x Low[L]` in L+1..L+182 (the map's -3% definition); lows with fewer than 182 later bars are excluded from that share (censored; count shown). Also BTC alone. Fisher exact p for SIG vs NOT-SIG lower-low share when scipy is available.
Causal signature events (independent of the lows list): every (coin, u) with SIGNATURE, lockout 10 bars between kept signatures on a coin, date s: n, per-phase and per-split counts, forward return from Open[s+1] to Close[s+h], h = 1, 3, 7 (median, mean, win %), gross and net of 12 bp. Descriptive.
Today's state is reported as a reading only (BTC last closed day funding sign, OI percentile of the prior 365 days, signature flags on the last closed day); it is never a sample.

## Step 2 gate and test
Run only if at least 6 lows in the lows population meet the SIGNATURE (SOURCED, brief). Otherwise REPORT.md says "Step 2 not run" with the count, and the verdict is DESCRIPTIVE ONLY.
Test: the causal signature events of Step 1 as long trades. Entry Open[s+1]; stop `min(Low[u..s]) - max(0.6 x ATR14[s], 0.005 x min(Low[u..s]))` (SOURCED Shared stop, pivot-based = the failed-breakdown low); risk fraction r = (entry - stop)/entry, event dropped if entry <= stop (counted). Exit: first of stop (checked from the entry bar; exit at min(Open[t], stop)) or Close[e+h-1] with e the entry bar. Horizons h = 1, 3, 7 days; PRIMARY h = 7 (longest, because 12 bp eats the short ones; fixed now), 1d and 3d descriptive. R = (gross - fee) / r.
Lockout: 10 days between kept signatures on a coin, and no entry before the previous trade's exit (SOURCED).
Splits: DEV <= 2023-12-31 by entry date, VAL >= 2024-01-01, RECENT >= 2025-07-01 (subset of VAL, reported, never used to choose).
Placebo (2000 draws, seed 1114, SOURCED N >= 1000): each event replaced by an entry at the open of a random eligible day of the SAME coin, SAME split, phase at e-1 equal to the event's phase, same hold h, same r, same exit rule. PRIMARY placebo = any day in that phase (Shared rule). SECOND placebo = "lows-like" days: same phase and Close[e-1] <= 0.80 x max High[e-90..e-1] (a fall of 20% from the 90-day high, OURS, from the brief's "random lows-like bars in the same phase"). Band = 2.5th to 97.5th percentile of the draw means; percentile of the actual mean reported. No lockout on placebo draws (stated).
Bootstrap: block bootstrap of pooled per-trade R, blocks = 7-calendar-day windows of entry date (= hold length), 10000 resamples, seed 1114, percentile 95% CI.

## Verdict (applied to pooled all-phase events, VAL, h = 7, 12 bp R)
- UNDERPOWERED (do not claim) if VAL pooled n < 30 (OURS, as Test 1).
- PASS only if VAL mean R > 0 AND bootstrap CI low > 0 AND actual mean R is above the 97.5th percentile of BOTH placebos (conservative: lows-like is the stricter one, OURS) AND DEV mean R (12 bp) > 0 (sign agrees). A split flagged ONE-YEAR cannot carry a PASS alone.
- Otherwise KILL, stated with the VAL mean R, CI, placebo percentile and n.
- 6 bp row, RECENT, per coin, per phase, h = 1 and 3 are descriptive and cannot change the verdict. Rows with n < 30 are marked underpowered. One test (one primary h, one signature definition, no parameter grid), so no multiplicity correction applies.
- If Step 2 is not run, the verdict is DESCRIPTIVE ONLY with the Step 1 numbers.

## Output
`REPORT.md`, `summary.json` in this folder. Data files never committed. Code: `lib.py`, `run.py`, tests `test_lib.py`.
