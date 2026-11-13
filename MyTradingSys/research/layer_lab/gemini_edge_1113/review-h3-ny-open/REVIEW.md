# REVIEW: Blind Review of H3 NY-Open Studies (Pooled & 10-Symbol)

VERDICT: SOUND

## 1. Executive Summary & Verdict
- One-line verdict: **SOUND**
- Studies reviewed:
  - `MyTradingSys/research/h3_ny_open_pooled_2026-11/BLOCKED.md`
  - `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md` (and associated `count_10sym.py`, `test_count_10sym.py`)
- The headline event counts, usable days, and preregistration power gate calculations are mathematically and empirically sound. All 10 symbols DEV counts match the reported counts to the exact integer. Both studies are count-only pre-registration power assessments that correctly conclude the sample size is underpowered to proceed with strategy freezing or backtesting.

## 2. Headline Numbers Recount

| Claim / Metric | Claimed Value | Recounted Value | Status | Citation / Verification Method |
|---|---|---|---|---|
| BTCUSDT DEV Usable Days | 650 | 650 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:12`, confirmed via `count_10sym.py` |
| BTCUSDT DEV Events | 35 | 35 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:12`, confirmed via `count_10sym.py` & SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/test_count_10sym.py:42` |
| ETHUSDT DEV Usable Days | 650 | 650 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:13`, confirmed via `count_10sym.py` |
| ETHUSDT DEV Events | 28 | 28 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:13`, confirmed via `count_10sym.py` |
| SOLUSDT DEV Usable Days | 648 | 648 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:14`, confirmed via `count_10sym.py` (2 gap days dropped) |
| SOLUSDT DEV Events | 34 | 34 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:14`, confirmed via `count_10sym.py` |
| XRPUSDT DEV Usable Days | 648 | 648 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:15`, confirmed via `count_10sym.py` (2 gap days dropped) |
| XRPUSDT DEV Events | 22 | 22 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:15`, confirmed via `count_10sym.py` |
| LTCUSDT DEV Usable Days | 648 | 648 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:16`, confirmed via `count_10sym.py` (2 gap days dropped) |
| LTCUSDT DEV Events | 22 | 22 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:16`, confirmed via `count_10sym.py` |
| BNBUSDT DEV Usable Days | 650 | 650 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:17`, confirmed via `count_10sym.py` |
| BNBUSDT DEV Events | 27 | 27 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:17`, confirmed via `count_10sym.py` |
| ADAUSDT DEV Usable Days | 650 | 650 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:18`, confirmed via `count_10sym.py` |
| ADAUSDT DEV Events | 21 | 21 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:18`, confirmed via `count_10sym.py` |
| DOGEUSDT DEV Usable Days | 650 | 650 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:19`, confirmed via `count_10sym.py` |
| DOGEUSDT DEV Events | 27 | 27 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:19`, confirmed via `count_10sym.py` |
| AVAXUSDT DEV Usable Days | 650 | 650 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:20`, confirmed via `count_10sym.py` |
| AVAXUSDT DEV Events | 23 | 23 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:20`, confirmed via `count_10sym.py` |
| LINKUSDT DEV Usable Days | 650 | 650 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:21`, confirmed via `count_10sym.py` |
| LINKUSDT DEV Events | 24 | 24 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:21`, confirmed via `count_10sym.py` |
| Pooled 10-Symbol Usable Days | 6494 | 6494 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:22`, sum of usable days |
| Pooled 10-Symbol Events | 263 | 263 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:22`, confirmed via `count_10sym.py` |
| Pooled 2-Symbol Upper Bound n | 70 | 70 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_pooled_2026-11/BLOCKED.md:8`, 2 * 35 |
| Pooled 2-Symbol Power Gate (m=220) | MDE 0.812 R, n needed 1801 | MDE 0.812 R, n needed 1801 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_pooled_2026-11/BLOCKED.md:10`, confirmed with `prereg_gate.py --n 70 --sd 1.5 --m 220 --cost 0.14` |
| Pooled 10-Symbol Power Gate (m=223) | MDE 0.419 R, n needed 1804 | MDE 0.419 R, n needed 1804 | MATCH | SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:27`, confirmed with `prereg_gate.py --n 263 --sd 1.5 --m 223 --cost 0.14` |

*Note on dynamic `m auto`: When running `prereg_gate.py --m auto` on the current repo state, m resolves to 248 (as new cells/verdicts have since been committed), yielding `n needed 1825` vs the historical `m=220` (needed 1801) and `m=223` (needed 1804). The gate exits with code 1 BLOCK in all cases.*

## 3. Look-Ahead Hunt
- **Feature evaluated**: H3 low detection and holding window.
  - SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/count_10sym.py:22-29`
  - Evaluated bar timestamps: `start` = 00:00:00 UTC of `date` up to `end` = `ny_open_utc(date) + 180 * 60000` ms (exclusive).
  - Day low identification: `min(ts, key=lambda t: (lows[t], t))` over bars from 00:00 UTC through `open+180` minutes.
  - Condition: `120 <= (low_t - open) // 60000 <= 150`.
  - Holding criterion: Because the window searched for the minimum extends strictly through `open+180` minutes, if the lowest bar occurs between minute 120 and 150, by definition no lower bar was printed between minute 120/150 and minute 180 (held for at least 30 to 60 minutes).
- **Decision bar / Entry bar comparison**:
  - SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:7`: "Entry: none; no entry or outcome is defined or read."
  - SOURCED `MyTradingSys/research/h3_ny_open_10sym_2026-11/count_10sym.py:2`: "Only lows and bar times are read; no return or outcome column exists here."
  - Decision bar: Any prospective trade entering on this pattern would make its decision at or after `open+180` min (once the 30-min hold through minute 180 is observed). The feature uses bars strictly up to `open+180` min (`end = int(o.timestamp() * 1000) + 180 * MIN`).
  - **Verdict on look-ahead**: NO LOOK-AHEAD DETECTED. No future bars beyond the evaluation cutoff (`open+180`) are accessed, and no future price returns or outcome bars are read.

## 4. Fee and Slippage Hunt
- **Fee model**: SOURCED `MyTradingSys/research/h3_ny_open_pooled_2026-11/BLOCKED.md:9` and `MyTradingSys/research/h3_ny_open_10sym_2026-11/RESULT.md:26` use `--cost 0.14`.
- **Cost parameter**: 0.14 R standard round-trip friction hurdle parameter in `prereg_gate.py`.
- **Execution / Returns**: Neither study executes trades, calculates PnL, or measures gross/net returns. They are count-only gates prior to pre-registration freeze.
- **Verdict on fees/slippage**: NO FEE OR SLIPPAGE ERRORS DETECTED. Friction is appropriately included in the pre-registration power gate hurdle (`MDE R + cost 0.14`).

## 5. Conclusion
Both research directories correctly identified that the proposed H3 pattern produces insufficient sample size during DEV (n=35 for BTC alone, n=70 upper bound for 2 symbols, n=263 across 10 symbols) against the ~1800+ required events under Holm multiple-testing corrections. The studies appropriately halted before freezing or testing.
