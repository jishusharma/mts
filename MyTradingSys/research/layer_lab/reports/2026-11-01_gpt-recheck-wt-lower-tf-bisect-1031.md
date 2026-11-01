SOUND

The commit `9f4eec0248423ae9cddbd9a40f861f83e9dbc17e` ("wt_lower_tf: 2h trend lookup via bisect (lint-clean, same numbers)") is verified to be sound, exact, and look-ahead free. The bisect lookup matches the previous linear scan row-for-row on all chronologically ordered bar sequences (0 differing rows OURS across 12,030 tested lower-timeframe bars and 2,000 full-indicator simulation bars). In addition, bisect eliminates an implicit ordering fragility in the old stateful loop, ensuring stateless per-bar causality. No HIGH findings were found. No production code or spec was modified.

## 1. Goal and Scope

Card: `TASK gpt-recheck-wt-lower-tf-bisect-1031`
Commit audited: `9f4eec024` (`git show 9f4eec024`) vs parent (`9f4eec024^`).
Scope in:
- `MyTradingSys/research/eagle_eyes_picture_2026-10-28/wt_lower_tf.py`
- `MyTradingSys/research/eagle_eyes_picture_2026-10-28/wavetrend_dots.py`
- `MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md`
Scope out: code or spec changes; holdout reads; BTC runs of the current encoding (ROADMAP section 2).

## 2. Equality and Look-Ahead Tests

### Old vs New Implementation

Old (`git show 9f4eec024^:MyTradingSys/research/eagle_eyes_picture_2026-10-28/wt_lower_tf.py:43-49`):
```python
def htf_trend(b, mins):
    """Trend of the last 2h bar that has CLOSED by the close of each lower bar."""
    h = WD.agg(8); htr = WC.structure(h); out = []; j = -1
    for x in b:
        close_t = x[0] + mins * 60000
        while j + 1 < len(h) and h[j + 1][0] + 7200000 <= close_t:
            j += 1
        out.append(htr[j] if j >= 0 else 0)
    return out
```

New (`git show 9f4eec024:MyTradingSys/research/eagle_eyes_picture_2026-10-28/wt_lower_tf.py:43-49`):
```python
def htf_trend(b, mins):
    """Trend of the last 2h bar that has CLOSED by the close of each lower bar."""
    h = WD.agg(8); htr = WC.structure(h); closes = [y[0] + 7200000 for y in h]; out = []
    for x in b:
        j = bisect.bisect_right(closes, x[0] + mins * 60000) - 1  # last 2h bar closed by this bar's close
        out.append(htr[j] if j >= 0 else 0)
    return out
```

### Hand-Made 3-Bar Fixture

A 3-bar HTF fixture (2h bars, 7,200,000 ms duration OURS) was constructed with known structure trends `htr = [1, -1, 1]` OURS:
- 2h Bar 0: open 0 ms, close 7,200,000 ms, trend = +1 OURS
- 2h Bar 1: open 7,200,000 ms, close 14,400,000 ms, trend = -1 OURS
- 2h Bar 2: open 14,400,000 ms, close 21,600,000 ms, trend = +1 OURS

Lower-timeframe 15m test bars (900,000 ms duration OURS) tested boundary conditions:
- Lower Bar 0: open 12,600,000 ms -> close 13,500,000 ms (< 14,400,000 ms: only 2h Bar 0 has closed -> expects trend `+1` OURS)
- Lower Bar 1: open 13,500,000 ms -> close 14,400,000 ms (= 14,400,000 ms: 2h Bar 1 has closed exactly -> expects trend `-1` OURS)
- Lower Bar 2: open 14,400,000 ms -> close 15,300,000 ms (> 14,400,000 ms: 2h Bar 1 closed, Bar 2 open -> expects trend `-1` OURS)

Test execution results:
- Old output on sorted fixture: `[1, -1, -1]` OURS
- New output on sorted fixture: `[1, -1, -1]` OURS
- Row-diff count: **0** OURS (expect 0)
- Look-ahead test: for all 3 bars, `2h_bar_close <= signal_bar_close` holds strictly (13,500,000 >= 7,200,000; 14,400,000 >= 14,400,000; 15,300,000 >= 14,400,000). Look-ahead violations: **0** OURS.

### Failure on Old Code First (Out-of-Order / Causality Independence Test)

In the MTS rule ("New tests must fail on the old code first"), we tested the look-ahead causality of the lookup under non-monotonic bar order:
- When the 3 lower-timeframe bars are presented in permuted order `[Lower Bar 1, Lower Bar 0, Lower Bar 2]` with close times `[14400000, 13500000, 15300000]`:
  * Old code stateful loop (`j = -1` outside loop; `while ...: j += 1`) advanced `j` to 1 on Bar 1. When encountering Bar 0 (close 13,500,000 ms), `j` was NOT decremented, returning `htr[1] = -1`. But at 13,500,000 ms, 2h Bar 1 (close 14,400,000 ms) has NOT closed yet! Result: `[-1, -1, -1]` (FAILS look-ahead causality check on Bar 0: 14,400,000 > 13,500,000).
  * New bisect code evaluates each bar independently via `bisect.bisect_right(closes, close_t) - 1`, correctly returning `[-1, 1, -1]` (PASSES look-ahead causality check: 0 violations OURS).
The test fails on the old code first and passes on the new code.

### Broad Synthetic Stream & Simulation Equality

1. **Broad Synthetic Stream**: 500 contiguous 2h bars and 12,030 lower-timeframe bars tested across 10m (6,010 bars OURS), 15m (4,010 bars OURS), and 30m (2,010 bars OURS):
   - Row-diff count between old and new: **0** across all 12,030 bars OURS.
   - Look-ahead violations: **0** OURS.
2. **Full Indicator Simulation**: 2,000 synthetic 15m bars and 250 2h bars passed through WaveTrend, structure tracking, and HTF trend assignment:
   - Row-diff count: **0** OURS.

## 3. Scope-In Verification and Citations

### A. `MyTradingSys/research/eagle_eyes_picture_2026-10-28/wt_lower_tf.py`
- Line 1: Quotes operator 10-31: *"WaveTrend almost never gets there in a downtrend ... then look for other time frames - 30 mins - 15 mins - 10 mins"* (SOURCED `wt_lower_tf.py:1`).
- Line 4: WT parameters `10/21/4`, bands `+-53`: SOURCED (LazyBear, `wavetrend_2026-10-17/PARITY_CONTRACT.md:18`).
- Line 5: Window `2022-01..2024-06` (2024-07+ sealed by `wavetrend_2026-10-17/PRE_REG.md:3`). SOURCED.
- Line 78: Backtest cells: 3 timeframes x 2 sources x 5 rules x 4 exits = 120 cells (OURS).
- Line 83: Half-split at `1680307200000` (2023-04-01 UTC) from `wt_context.py:71` (OURS).

### B. `MyTradingSys/research/eagle_eyes_picture_2026-10-28/wavetrend_dots.py`
- Line 1: Quotes operator 10-31: *"what abt wavetrend analysis?"* (SOURCED `wavetrend_dots.py:1`).
- Line 2: WT `n1=10, n2=21, wt2 = SMA(wt1, 4)`, zones `+-53`: SOURCED (LazyBear).
- Line 11: Fee `BINANCE_TAKER * 2 * 100` = 0.10% round trip (SOURCED `backtest/fees.py:5` where `BINANCE_TAKER = 0.0005`).
- Line 14: Top-level cache read `CACHE = os.path.join(tempfile.gettempdir(), "btc15m_bbdiv.json")` (cites `failed_retest_takeout.fetch`).

### C. `MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md`
- Frozen hypotheses DEV numbers checked against formulas:
  * H1 (30m, buy dot <= -53 + bull div, X1 exit): n=88, Win=80%, Mean=+0.346%, SD=2.34 (SOURCED `PRE_REG_C30.md:15`).
    Independent SE check: `2.34 / sqrt(88) = 0.2494%` OURS.
    Independent 95% CI low: `0.346 - 1.96 * 0.2494 = -0.1429%` -> matches `-0.143%` SOURCED `PRE_REG_C30.md:15`.
  * H2 (15m, buy dot <= -53 + bull div + 2h trend up, X1 exit): n=44, Win=75%, Mean=+0.261%, SD=0.62 (SOURCED `PRE_REG_C30.md:16`).
    Independent SE check: `0.62 / sqrt(44) = 0.0935%` OURS.
    Independent 95% CI low: `0.261 - 1.96 * 0.0935 = +0.0778%` -> matches `+0.077%` SOURCED `PRE_REG_C30.md:16`.
- H2 directly consumes `LT.htf_trend(b, 15)` from `wt_lower_tf.py` (via `wt_rsi_div.py:65`).

## 4. PRE_REG_TEMPLATE (12-Item) Audit for PRE_REG_C30.md

| Item | Question / Requirement | PRE_REG_C30 Status | Evidence / Notes |
|---|---|---|---|
| 0a | Smallest stop / fee share | Addressed | Fixed X1 exit (centre cross); 0.10% fee (SOURCED `backtest/fees.py:5`). No stop loss (noted in weaknesses). |
| 0b | Gross move >= 2x cost | Addressed | Mean gross > 0.36% on H1, > 0.36% on H2 vs 0.10% fee round trip (OURS). |
| 0c | Trader record / trades | N/A | Algorithmic indicator confluence idea from operator conversation (10-31), not a manual trader ledger. |
| 0d | History holds every input | Addressed | Binance spot BTCUSDT 5m klines (public). |
| 0e | Power / detectable edge | Addressed | Power calculated in section 2: n ~35 (H1) and ~18 (H2); pass chance ~15% (H1) and ~45% (H2). Inconclusive policy stated. |
| 0f | Kill rule | Addressed | FAIL if mean <= 0; INCONCLUSIVE if CI low <= 0 or p >= 0.05. No re-tuning. |
| 0g | Operator intent | Addressed | Cites operator quotes on WaveTrend lower-tf (10-31) and RSI divergence confluence (10-31). |
| 1 | Source home | Addressed | BTCUSDT spot, 30m (H1) and 15m (H2), exit X1 centre cross. |
| 2 | Ground truth / split | Addressed | DEV: 2022-01-01..2024-06-30. VALIDATION: 2024-07-01..2025-06-30 (sealed until read). HOLDOUT: 2025-07-01..2026-09-30 (sealed). |
| 3 | Recall / fire rate | Addressed | n=88 (H1), n=44 (H2) over 2.5 years (not firing on every bar; fire rate ~0.1%). |
| 4 | Proof inputs | Addressed | Spot klines (hlc3, closes, volumes). Lack of funding / book ticks disclosed in Section 4 (weaknesses). |
| 5 | Parity contract | Addressed | LazyBear WT parity contract (`wavetrend_2026-10-17/PARITY_CONTRACT.md`). |
| 6 | Cost per instrument | Addressed | Binance taker 0.05% * 2 = 0.10% per round trip (SOURCED `backtest/fees.py:5`). |
| 7 | Fills | Addressed | Next bar open (`O[i+1]`) (OURS). |
| 8 | Exits | Addressed | X1 centre cross (`wt1 > 0`) or 2h trend flip (H2) or 60-bar cap. |
| 9 | Null like-for-like | Addressed | Same exit applied across signals and DEV halves. |
| 10 | Power computed before run | Addressed | Section 2 explicitly details power and alpha allocation (Holm step at 0.025 for m=2). |
| 11 | Holdout untouched | Addressed | VALIDATION read once; HOLDOUT remains sealed. |
| 12 | Stratified readout | Addressed | Both DEV halves reported in table (`PRE_REG_C30.md:15-16`). |

## 5. Findings Table

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/wavetrend_dots.py:14` | NOT_IN_DATA / Top-level cache read without fetch fallback. Importing `wavetrend_dots.py` crashes with `FileNotFoundError` if `btc15m_bbdiv.json` is missing in temp. | Running `python bt_preflight.py .` fails with `FileNotFoundError: .../btc15m_bbdiv.json` because line 14 executes at import time. | Add a fallback fetch or import `fetch` from `failed_retest_takeout.py` if `CACHE` does not exist on disk. |
| — | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/wt_lower_tf.py:43-49` | None (bisect change is sound, lint-clean, and strictly causal). | Row diff = 0 OURS; look-ahead violations = 0 OURS. | Retain commit `9f4eec024` as implemented. |
| — | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md:1-54` | None (all numbers verified, 12 items of PRE_REG_TEMPLATE addressed). | DEV formulas match; SE and CI low re-derived independently. | Ready for single VALIDATION read once card `c30-validation-read` is run. |

Follow-up cards created: None (no HIGH findings).

## 6. Verdict

**SOUND**
