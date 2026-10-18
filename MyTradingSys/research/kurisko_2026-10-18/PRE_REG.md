# PRE-REGISTRATION: Kurisko Quad Rotation, count-only, BTCUSDT perp DEV 1m/5m (2026-10-18)

Card `kurisko-prereg-fire-counts`. Status: COUNT-ONLY. **Frozen cells: 0 of 8 candidates.** Of the eight counted cells (1m and 5m only), every TF x arm x side is fee-dominated or underpowered by `prereg_gate.py` (BLOCK), so nothing is frozen and no outcome study may be built on these cells. Details of the BLOCK: `BLOCKED.md`.

## 0. Prior-verdict check (step 1)
`python scripts/dev/verdicts.py check "kurisko quad rotation stochastic"` (exit 0):
> check 'kurisko quad rotation stochastic': no prior row matches (need 3 of ['kuris', 'quad', 'rotat', 'stoch']). Safe to pre-register; append your row after RESULT.

## 1. What was read
- Data: Binance USDT-M BTCUSDT 1m klines `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2022-01.csv .. -2024-06.csv` (30 files, DEV, 1,313,280 1m bars). `count_events.py` checks each file sha256 against `gross_effect_screen_2026-10-15/DATA_MANIFEST.csv` and refuses any bar >= 2024-07-01. VALIDATION and HOLDOUT: zero reads. Fields used: open_time, high, low, close. 5m = `tf_resample` (FORMULAS 8), 262,656 bars, a bucket with a missing 1m bar is dropped.
- Events: kurisko module `quad_rotation.lines` + `detect`, module commit `dd001f2a7902f2de5c1b3821db7ea35bcb613624` (FORMULAS 24.4 rule), default bands (9,3),(14,3),(40,4),(60,10); the (44,x) variant was NOT run. RSI arm = same four lookbacks, Wilder RSI, levels 20/80.
- Computed: events, distinct UTC event-days (of the event bar close), side split, pattern stop width in bp. NOT computed anywhere: any return, MFE/MAE, hit rate, fee in P&L, or any bar after an event. No outcome column exists in `counts/counts.csv`.
- Reproduce: `python count_events.py --out counts`; tests `python -m pytest test_count_events.py` (7 pass; hand-derived from FORMULAS 24.5; they failed before the script existed).

## 2. Labels
SOURCED: bands, line D, levels 20/80 (params/kurisko_default.json). OURS: turn rule (FORMULAS 24.4), short mirror (NO-SOURCE, KURISKO_SPEC s5 gap 6), stop-width definition (pattern low to close for long, mirror for short; the sources give ticks on MES, KURISKO_SPEC s5 gap 5), cost 14 bp, gate parameters. OPERATOR-HYPOTHESIS: the whole RSI arm (RSI 20/80).

## 3. Cost and funding
Round trip 14 bp = 2 x 5 bp taker (SOURCED `backtest/fees.py` BINANCE_TAKER 0.0005, both legs) + 4 bp slippage (OURS). FORMULAS 13 carries 12 bp; I did not re-derive that figure, 14 bp follows the card and is the stricter number. Funding rule (OURS, for any later study): charge the realised 8h funding at each UTC 00/08/16 mark held, sign by side; not applied here because no outcome is read.

## 4. Counts (DEV, rule: one count per TF x arm x side; both sides reported apart)
| # | TF | Arm | Side | Events | Event-days | Median stop bp | Stops >= 14 bp | Fee as R (14 / median stop) | MDE (R at sd = 1 R placeholder, m=8; NOT a measured sd, not an R estimate, never add it to a cost) | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1m | stoch | long | 14317 | 912 | 6.67 | 22.1 % | 2.099 | 0.118 | BLOCK |
| 2 | 1m | stoch | short (NO-SOURCE mirror) | 15706 | 912 | 5.97 | 17.3 % | 2.345 | 0.118 | BLOCK |
| 3 | 1m | rsi | long | 19 | 18 | 114.28 | 89.5 % | 0.123 | 0.842 | BLOCK |
| 4 | 1m | rsi | short (NO-SOURCE mirror) | 15 | 14 | 66.97 | 100 % | 0.209 | 0.955 | BLOCK |
| 5 | 5m | stoch | long | 1646 | 678 | 23.43 | 68.8 % | 0.597 | 0.137 | BLOCK |
| 6 | 5m | stoch | short (NO-SOURCE mirror) | 2030 | 742 | 17.77 | 61.7 % | 0.788 | 0.131 | BLOCK |
| 7 | 5m | rsi | long | 3 | 3 | 452.2 | 100 % | 0.031 | 2.064 | BLOCK |
| 8 | 5m | rsi | short (NO-SOURCE mirror) | 4 | 4 | 169.32 | 100 % | 0.083 | 1.787 | BLOCK |

Gate command per row: `prereg_gate.py --n <event-days> --sd 1 --cost <fee R> --m 8` (sd = 1 is an unmeasured placeholder, OURS, since no outcome is read; the gate now refuses it without --sd-source, and measured sd of per-event R is 1.4-4.5 R per GATE_AUDIT Q1, which only raises every MDE below, so all 8 rows still BLOCK). Result: exit 1 for all 8. Cost alone exceeds the 0.30 R plausible-gross ceiling on every row (fee R 0.03 on the RSI 5m rows is only low because the stops are huge, 170-450 bp, and those have 3-4 days so the MDE is 1.8-2.1 SD).

## 5. Fee-floor verdict per TF x arm
- 1m stochastic: FEE-DOMINATED. Median stop 6.7 bp (long) / 6.0 bp (short) against a 14 bp round trip: the fee is 2.1-2.3 R. 78-83 % of events have a stop narrower than the fee.
- 5m stochastic: FEE-DOMINATED. Median stop 23.4 / 17.8 bp, fee 0.60 / 0.79 R; 31-38 % of events are narrower than the fee. Powered (678 / 742 days, MDE 0.13-0.14 SD) but the fee alone is above the ceiling.
- 1m RSI, 5m RSI: UNDERPOWERED (3-18 event-days; MDE 0.84-2.06 SD). The RSI 20/80 hypothesis almost never puts all four lookbacks (incl. RSI 60) below 20.

## 6. Selection rule (written before counting; no outcome enters)
Candidates = TF {1m, 5m} x arm {stoch, RSI} x side {long, short} = 8 (<= 12). A candidate is frozen iff `prereg_gate.py` exits 0 with n = event-days, cost = 14 / median stop bp in R, m = 8. If more than 12 candidates passed, rank by event-days. Outcome of the rule: 0 frozen.

## 7. If a later card revisits (not authorised here)
Outcome definitions, same-window random-clock control (matched on UTC hour slot and vol tercile, 200 draws), Holm plan over the frozen cells, trial ids and verdicts.py aliases {kurisko, quad rotation, quad_rotation, stochastic rotation} apply only to cells that pass a gate. Possible routes are each a new trial with its own pre-registration: a wider stop (5m+ TF, 15m/1h not counted here), a minimum-stop filter (>= 14 bp, OURS) which changes the sample and must be counted fresh, or dropping the card. Trial ids: KQ-T01 = this count pass (8 candidate cells, 0 frozen).

Kill scope (GATE_AUDIT Q4, gate-fix-4): FAIL/INCONCLUSIVE: stop; this BLOCK (count-only, no outcome read) covers only Quad Rotation on BTCUSDT 1m and 5m with bands (9,3),(14,3),(40,4),(60,10) D-line, the pattern-low stop and a 14 bp taker round trip; 15m and 1h, a minimum-stop filter, a maker entry or a tick stop are untested and need their own PRE_REG and gate.

## 8. Known weaknesses
1. The stop width is a pattern-low definition (OURS); a tick-based stop as in the sources would be far tighter on BTC.
2. 1m events cluster (about 16 per day): event-days saturate at 912 and the effective n is smaller.
3. Short side has no Kurisko source; RSI arm is the operator's hypothesis. Both reported only for completeness.
4. 15m and 1h were not counted (card scope is 1m/5m).

## Addendum 2026-10-19: RSI settings video search (no new arm)

Card kurisko-rsi-video-search (Gemini, reviewed by Claude): 26 Kurisko videos checked, `RSI_VIDEO_SEARCH.md`. Kurisko states NO RSI periods, levels or smoothing in any of them.
Reviewer spot-check: 4 quotes re-fetched from live YouTube captions (XNfOIzPYChA twice, LD_LOEeKzMs twice), all match.
- The RSI idea traces to a chatroom member's remark read aloud in XNfOIzPYChA ("the RSI ... using the same settings you're using in the stochastics"). That is a third party, not Kurisko.
- The TradingView difference the operator remembers is the stochastic, not RSI: TradingView's built-in is Full Stochastic, so Kurisko sets %K smoothing = 1 and hides the %K line (LD_LOEeKzMs). Our `qr.lines` (raw %K, SMA_d) is the same line; nothing to change in the stochastic arm.
- Result: the RSI arm stays OPERATOR-HYPOTHESIS (Wilder RSI 9/14/40/60 at 20/80). No SOURCED RSI setting exists, so NO new arm, no re-count, no ledger entry. Its 3-18 event-days stay as reported; it stays BLOCKED.
- Caption caveat: auto-captions read the third period as "44"; it is not resolved by captions whether that is (40,4) or another value. KURISKO_SPEC s5 keeps (40,4) as its existing label.
