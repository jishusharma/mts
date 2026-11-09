# Malkan level short, div 3-10 close arm: testnet forward pre-registration (context-only, paper outcome)

**Result: the arm is pinned and the kill is fixed before any forward trade: BTCUSDT 4h, div_window (3, 10), price_mode close, target 2R, 60-bar stop, fee BINANCE_TAKER; FAIL = after 30 closed paper trades net R <= 0 (operator-set, OURS). Count it rests on: n=126, +0.104 R net per trade (COUNT.json), not significant (SE 0.12 R).**

Card `malkan-level-short-testnet-forward-1109`. Source: `REPORT.md` and `COUNT.json` of this folder (card `malkan-level-short-4h-count-1109`). Forward data is the only clean test left: the sealed windows are burned. Labels: SOURCED = Malkan (WEB_RESEARCH.md, SEVEN_STAR_CAPTIONS.md), OURS = this project's choice.

## 1. What is frozen (change any line = a new pre-registration, new params_id)
| Pin | Value | Where |
|---|---|---|
| Symbol, timeframe | BTCUSDT, closed 4h bars | live_runner_cli registry key `malkan\|level_short\|4h` |
| Arm | `div_window` (3, 10), `price_mode` close, `structure` div (the SOURCED 3-10 bar window; the count's best and only positive-sign divergence arm) | `malkan_level_short_live.ARM` |
| Layers | level + structure (divergence) + trigger, as defined in the docstring of `malkan_level_short.py`: level = pivot high/low tagged from below within 0.5 % (OURS proxy); structure = bearish RSI divergence (price higher high, RSI lower high); trigger = RSI crosses under its 14 SMA, RSI < 60, RSI was >= 60 in the last 10 bars (SOURCED 60 line) | `malkan_level_short.signals` (imported, nothing copied) |
| Not layers of this arm | WaveTrend and HTF (daily/weekly RSI vs 60). HTF history must still exist (>= 30 closed dailies, >= 20 closed weeklies, >= 400 4h bars, else no signal). The 5-layer agreement at the same bar is logged as `full_stack`, never used as a gate | `malkan_level_short_live.events` |
| Entry | a stop-sell under the trigger bar's open within the next 3 bars (fill there, or at the open on a gap) | `signals()` |
| Stop | highest high of the last 8 bars through the fill bar, +5 bps | `signals()` |
| Target | 2R | `M.TARGET_R` |
| Time stop | 60 bars (close of bar 60), stop wins a bar that touches both | `M.MAX_BARS`, `outcome()` |
| Fee | `fees.BINANCE_TAKER`, each side, charged in R | `outcome()` |
| One trade at a time | a trigger within 6 bars of a filled signal is skipped | `signals()` skip rule |

Sample the count gave: **n=126, hit 1R 0.49, win 2R 0.365, gross +0.148 R, net +0.104 R per trade, total +13.1 R net, 2017-2026** (COUNT.json). The task text quotes +0.11; the file says 0.104, this pre-registration uses the file. Rough SE 1.4 R / sqrt(126) = 0.12 R: the edge is **not significant** (0.9 SE). Trades per year in the count: 5 to 17, 9 in 2026 so far.

## 2. The kill (FAIL rule)
- After **30 closed paper trades**, if the sum of net R <= 0 (equivalently the mean) the arm FAILS: verdict `KILL`, the live layer stops emitting alerts, one `kill` row is journaled. (Operator-set, OURS: not derived from a power calculation.)
- Closed = stop, target or 60-bar time exit on real later bars. A trigger that never fills (no bar under the open within 3 bars, or skipped by the 6-bar rule) is `no_fill` and does not count. A trigger that left the history window unresolved is `unresolved`, does not count, and is listed.
- Before 30 closed trades: verdict `RUNNING`, no early stop and no early pass. At >= 30 with sum > 0: `PAST_30` = survived the kill, **not** an edge claim.
- Honest odds, information only: at a true +0.10 R and SE 1.4 R per trade the SE of a 30-trade mean is 0.26 R (0.10 is 0.4 SE), so a true-edge arm still hits `KILL` about 35 % of the time; at ~14 trades a year the 30 trades take about 2 years. The test is a kill test, not a power test.

## 3. What runs (no order, ever)
- Alert: one `malkan|level_short|4h` alert per new closed 4h trigger bar, `collection_only` + `shadow_side` "short", **no `side`**, no layer_rules entry: the auto-trader cannot map it, so no order exists. It carries `entry_ref` (the trigger bar's open), the provisional `stop`, `target_r`, `full_stack`.
- Paper outcome: on later closed bars `outcome()` settles the trade (stop, target, net R) and appends a row to `runtime_data/malkan_level_short_forward.jsonl` (git-ignored; rows kind signal / outcome / no_fill / unresolved / kill). No exchange call, no account, no key.
- Parity (test): `signals()` run once on the whole history equals the one-bar-at-a-time live feed; the 5-layer C3 bar (2026-10-22) fires exactly once.

## 4. Context (phase-first; all OURS)
Phase: post-bottom recovery inside a 75.4-80.9k range (too short to count, which is what the forward run is for). The count's regime split for this arm: bull +0.11 R (n=70), bear +0.13 R (n=49). Invalidation per trade is the stop above; the trade is a counter-trend fade of a failed level test.

## 5. Not done
Long side, other symbols, WaveTrend/HTF as gates (the +0.07 R arms each lift the base only about +0.1 R, n=148/201), sizing, any order path. A move to real orders needs its own card and a new pre-registration.
