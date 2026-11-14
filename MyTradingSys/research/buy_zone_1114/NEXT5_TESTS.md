# NEXT 5 TESTS, buy zone 2026-11-14

Source: `BUY_ZONE_MAP.md` section 4 (ranked). Every test below is a pre-registered brief. Nothing here is an edge until a fee-net out-of-sample result passes. Rules are OURS, not the trader's, unless stated.

## Shared rules (all five tests)

| Rule | Setting |
|---|---|
| Phase split | Every result reported per phase (UP / DOWN / RANGE / post-peak bear / base), phase set from the daily bar of the previous day only (no lookahead) |
| Costs | Fee-net at 12 bp round trip (main row) AND a 6 bp row (sensitivity) |
| Stop | `max(0.6 x ATR, 0.5%)` from entry, pivot-based where the rule says so |
| Splits | DEV <= 2023-12-31; VAL >= 2024-01-01. RECENT reported separately, never used to pick a rule |
| Placebo | Random entries drawn from the SAME phase and the same hold length, same stop, N >= 1000 draws, reported as a percentile band |
| Lockout | 10 days between events on the same coin (no overlapping trades) |
| Bootstrap | Block bootstrap (block = hold length), 95% CI on mean R per trade |
| Causality | Indicators computed on closed bars only; no future-pivot fractals inside the signal |
| Data | Read from `F:/MTS/data_cache` (or the host's cache path). Never committed to the repo. Repo is PUBLIC |
| Pre-registration | `PRE_REG.md` with a `## Context` section and a `Regime mix:` line per phase, committed BEFORE any outcome is computed |
| Code | Test code committed BEFORE any outcome; a placebo that fails on pre-change code counts as a red flag |
| Ship | Each test ships with `python scripts/dev/sync.py ship --release <slug>`; commit message carries `Result:` and `Next:` |
| Verdict | PASS only if VAL fee-net 12 bp mean R > 0 with CI low > 0 AND beats the placebo band AND DEV sign agrees. Otherwise KILL with the number |

Labels: every parameter in the PRE_REG is tagged SOURCED (from a cited source) or OURS.

---

## Test 1: Causal confirmation ladder, long side (rank 1)

**Question:** does a causal, fee-net long entry on the confirmation ladder beat random same-phase entries?

**Candidates (pre-register ONE as primary, the other as secondary):**
- A. HL_BREAK: second swing low above the first; entry on close above the high between the two lows (1D).
- B. BULL_DIV: 1D bullish RSI or WaveTrend divergence on the second low, then close above the high between lows (1D).

**Universe:** BTC, ETH and 20 liquid coins. Binance spot 2017+. Bybit funding where needed.

**Phase:** long only in UP and base phases. Report DOWN and post-peak bear as a control (expected no edge).

**Entry:** next 1D open after the confirming close.
**Stop:** `max(0.6 x ATR14, 0.5%)` below the second low.
**Exit:** first of trailing stop (2 x ATR) or 30 days.

**Outputs:** table per coin and pooled: n, win %, mean R fee-net 12 bp, mean R fee-net 6 bp, CI, placebo percentile, DEV/VAL/RECENT columns.

**Abort rule:** if fewer than 30 events in VAL pooled, report "underpowered" and do not claim.

---

## Test 2: Multi-timeframe context rule, both sides (rank 2)

**Question:** does a phase filter (daily) + 1W/3D divergence as context + 4H/1D entry show edge when pooled across coins?

**Universe:** 20 coins, pooled.

**Phase filter:** daily phase from the previous day's bar only.
**Context:** 1W or 3D RSI/WT divergence present in the last 4 weeks (causal).
**Entry:** 4H close that breaks the 4H swing in the direction of the phase (long in UP/base, short in DOWN/post-peak bear).
**Stop:** `max(0.6 x ATR14 on 4H, 0.5%)` beyond the 4H pivot.
**Exit:** opposite 4H signal or 10 days.

**Placebo (mandatory on EVERY pooled table, not BTC only):** same phase, same side, same hold, entries at random 4H bars.

**Outputs:** pooled table by side and by phase; per-coin contribution so one coin cannot carry the pool (report the result with the top coin removed).

---

## Test 3: Bear-phase 4H divergence short, replication (rank 3)

**Question:** does the bear-phase split on 4H bearish divergence shorts (+1.03 R, n=28 on BTC) hold on 20 coins with funding?

**Universe:** 20 coins.
**Phase flag:** post-peak bear = previous day's close below 50-week SMA AND no base reclaim. Set from previous day only (ex-ante flag).
**Signal:** 4H bearish divergence outside the upper Bollinger band (RSI or WT), pivot-based.
**Entry:** short on next 4H open after the confirming close.
**Stop:** `max(0.6 x ATR14 4H, 0.5%)` above the divergence high.
**Exit:** first of 2 x ATR trailing or 7 days.
**Funding:** added as a cost line (actual funding paid while held). Report with and without funding cost.
**Fees:** 12 bp round trip main row; 6 bp sensitivity row.

**Decision:** the test either confirms (PASS per shared verdict rule) or removes the BTC-only result. A KILL is a valid, complete answer.

---

## Test 4: Capitulation signature at lows (rank 4, descriptive first)

**Question:** what does a real flush look like, and does it separate final lows from lows that kept falling?

**Signature (pre-registered, all causal):** funding negative at the low AND OI down >= 5% over the prior 7 days AND a failed breakdown (undercut of a swing low, close back above within 2 weeks).
**Data:** Bybit OI and funding from 2020-07. 38 anatomy lows from `BUY_ZONE_MAP.md` plus any new lows found by the same rule.

**Step 1 (descriptive, no verdict):** count how many lows meet the signature; forward return 1d, 3d, 7d median, and the share that made a lower low within 26 weeks.
**Step 2 (only if at least 6 lows meet the signature):** forward 1d to 7d fee-net test vs placebo of random lows-like bars in the same phase.

**Report today's state as a reading only:** funding positive, OI at 99.7th percentile of 365 days (from the map). Do NOT use today as a test sample.

**Verdict:** descriptive only unless Step 2 is reached. Step 2 uses the shared verdict rule.

---

## Test 5: Large-flow lead test with a proper lag (rank 5)

**Question:** does large-trade flow lead the next 24 h and 72 h return, or is it concurrent with price (correlation +0.45 same window, +0.05 next 24 h)?

**Data:** Binance daily large-trade dumps (>= $1M and >= $5M cutoffs, both reported). The 11-13 files are not yet published: rerun `fetch_hourly.py` for those dates when they appear, and record the gap in the PRE_REG. Coinbase premium as an extra feature.

**Design:** non-overlapping windows. Flow measured over window t, return measured over t+1 to t+24 h and t+1 to t+72 h. All days, not only low-centred windows.
**Test:** rank correlation and quintile spread (top-flow quintile minus bottom) for next-24 h and next-72 h, per phase, DEV/VAL split.
**Placebo:** shuffled flow across days within the same phase (1000 shuffles).

**Fee note:** this is a lead-signal test. If it passes, a separate fee-net trade test is pre-registered before any trade study. No trade result is claimed from this test alone.

**Verdict:** PASS only if the next-day spread holds in VAL and beats the shuffle band. Otherwise KILL with the number.

---

## Caveats carried forward (apply to all five)

- Small samples: about 4 real cycle bottoms; 38 lows with volume data.
- Anatomy tables pick lows with future bars. Any causal test must recompute the low causally.
- Binance futures was unreachable from the study machine: use Bybit for funding and OI, and say so in the result.
- 12 bp round trip eats most short-horizon edges. Wider stops and longer holds are where tests have a chance.
- Nothing in this file is a trade instruction.
