# ADVERSARIAL AUDIT t1 (2026-11-14, DEV build, study.py as frozen at d87d6d24e)

**Verdict: no blocking issue.** No look-ahead found; fees, exits and the one-position rule re-derived independently and match. Five low-severity items and some notes below.

## What was poked (real caches, not only synthetic)
| Probe | Result |
|---|---|
| Truncate bars at 3 dates (2021-03, 2022-06, 2023-11) for ZEC, EOS, BTC; compare every causal array (P, R1, S1, atr, vw, hm, ph, cy, 1h OHLC) on the common bars | 0 differences |
| Same, but future bars multiplied by random 0.8-1.2 (O/H/L/C/V) | 0 differences |
| coin_candidates rows (trigger, HM, VWAP, entry, D, gross, exit offset) on full vs truncated vs poked data for signals whose windows complete before the cut | identical |
| DEV-only load (bars cut at 2024-01-01) vs full load, DEV signals | 0 value differences on shared rows; full load has 7 (ZEC) / 9 (BTC) extra signals, all the last DEV days whose 24 h window crosses the split (DEVIATIONS item 3). DEV never sees a VAL bar. |
| Independent re-simulation of ALL 5320 DEV primary main trades from raw 15m bars (fresh code: prior-day pivots, trigger priority, ATR14, D, stop/target/gap/tie, time exit, gross R) | 5320 / 5320 match (9 flagged only by the CSV rounding of D to 8 decimals on 4e-5-priced VET/ZIL; exit reason and R agree to 5 digits) |
| Overlap check on the independently simulated exits (one position per coin) | 0 overlaps |
| Sample of 250 trades: phase label from table, HM sell state (own RSI(9)/EMA3/WMA21 loop on 30m closes), VWAP through signal close | 0 mismatches |
| Timestamps: all primary and secondary files are ms, max t < 2e12, 14-23 15m gaps per coin, no unsorted rows | OK |
| Frozen-check logic read; test_runs.txt shows STUDY_BUG=1 fails 7 tests, PHASE_LAG=0 fails the phase test | OK |

## Checked and found correct (read + poked)
- Phase: table row for day d is lag 1 (close_used equals prior close, 0 mismatches); every table MARKDOWN day passes the independent d-1 test (434 / 434).
- Pivots: prior complete UTC day only (study.py:185-195); poke of the signal day does not move them.
- 1h/30m/15m alignment: HM read at the 30m bar opening th+30m (closes with the signal bar) (study.py:202); VWAP includes the 15m bar opening th+45m (study.py:211); ATR uses the closed signal bar; entry is next 1h open (study.py:259-260). Partial last buckets are dropped (resample cnt == k).
- Exits: stop touch fills at max(stop, open), target at the level, same bar stop wins, time exit at close of bar j0+23 (study.py:227-240). Hand tests agree.
- Fee: cost R = 0.0012 x entry / D (study.py:268), at the 1.2% floor = 0.10 R, matches verify_trades. Placebo cost uses 0.0012 / D% (same value).
- One-position: exit bar = i+1+offset, next signal allowed when i' >= exit bar (study.py:274-283); skipped signals never open a position; independent overlap check 0.
- Bootstrap, ex-best-5, verdict logic (study.py:331-363, 435-440) agree with PRE_REG bars.

## Issues
| # | Sev | File:line | Issue | Effect | Suggested handling |
|---|---|---|---|---|---|
| 1 | Low | study.py:393 vs 261, 412 | Placebo pool requires the ENTRY bar's UTC day to be MARKDOWN; real trades are gated on the SIGNAL bar's day. Differs only for signals at 23:00 UTC (entry 00:00, next day). | About 1/24 of trades see a slightly different eligible pool; direction of bias unknown, tiny. | State in RESULT; do not edit (frozen). |
| 2 | Low | study.py:262-270, 485-490 | Maker row: limit at signal close fills if next high > close, but the stop/target scan starts at the same bar, so a target touched BEFORE the fill inside that bar is credited; stop exits are charged the maker 6 bp. | Maker row optimistic. Row is not pass-bearing. | Label "optimistic upper bound" in RESULT. |
| 3 | Low | study.py:659-679 (check_frozen) | Freeze hashes code and PRE_REG only. `phase_daily.csv` and the npz caches are not hashed; VAL reads whatever is on disk then. A regenerated phase table (new thresholds, revised history) would silently change VAL labels. | Reproducibility risk, not a look-ahead. | Record sha256 of phase_daily.csv and npz meta sha256 in RESULT at VAL time; compare the DEV rows of the table with dev_tables.json mix (434 / 198 MARKDOWN days). |
| 4 | Low | study.py:59-65, 185-195 | A day with any missing 15m bar has no pivot, so the next day yields no signals. Gaps cluster on exchange outages, i.e. disorderly days. | Small selection of signal days (14-23 gaps per coin over 7 years). | Disclose. |
| 5 | Low | study.py:240 (px), 268 | Cost is charged on entry notional; a gap-up stop fill at a worse price carries a slightly larger exit notional. Also no slippage/funding. | Under a basis point on average; PRE_REG states the limits. | None. |

## Notes (not defects)
- Gate: prereg_gate.py = BLOCK (MDE 0.339 R vs 0.30 plausible, n needed 598 vs 434 days). Spec says the run continues and RESULT says BLOCK. DEV result is already FAIL on its own (primary net -0.063 R, CI [-0.141, 0.014], placebo EXCESS -0.010, p 0.73).
- When both R1 and P are rejected, R1 wins (spec). If the bar also closed below P, the P target sits above the close and is dropped by the target >= entry skip (tested).
- Placebo ignores the one-position rule and the HM/VWAP/trigger conditions by design (PRE_REG baseline a). Placebo mean-of-means p-value is the spec's.
- EOS data ends 2025-05-26, so VAL for EOS is partial; count it in RESULT's VAL coin list.
- load_npz decides s/ms/us from t[0] only (study.py:498-501); all current files are pure ms, verified.
- DEV drops 7-9 signals per coin at the split edge by design; VAL one-position state restarts at 2024-01-01.
- Tests do not exercise real-cache edge cases (gaps, zero-volume bars: 14-294 per coin, VWAP NaN if a whole day has zero volume gives a False VWAP flag, safe direction).

ok = true (no blocking issue). Scratch probes: scratchpad poke.py and indep.py (not committed).
