# B151 - CryptoCred limit-fill backtest fills on touch and drops signals by a future event, so its PASS numbers are upper bounds; maker-entry fee refund applied on touch fills with a 0.1 % stop

Status: CLOSED. Severity: MED. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

CryptoCred limit-fill backtest fills on touch and drops signals by a future event, so its PASS numbers are upper bounds; maker-entry fee refund applied on touch fills with a 0.1 % stop.

## Evidence

- backtest/layers/cryptocred/run_cc_setups.py:102-118 find_limit_fill fills when low <= level (long) / high >= level (short): TOUCH, though the docstring and commit 37e34ba say 'trades through'. BACKTEST_PROTOCOL.md:51 requires trade-through by 1 tick, and fabio_of_model.py follows it. bt_engine.py targets also fill on touch.
- setup2_fib_pullback (cc_setups.py ~L115-175) emits a signal only if a bar's low lands inside the fib zone, so a bar that blows straight through the zone, fills the limit and hits the stop produces no signal and is never counted. Trades still open at the end of data are dropped (open_at_end -> None).
- Already acknowledged direction: CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:9-13 shows the earlier PASS (sr_flip hit 0.84, fib OOS +0.1687 %) was a fill-bias artefact; with touched limit all three setups FAIL. Worker found no layer with a passing pre-registered result (T055 C1/C2/C3 FAIL, BACKTEST_L1 only the 1h/40 cell clears PBO at +0.043 % OOS, below the 14 bp cost). Headline PASS numbers elsewhere (e.g. AUDIT_RERUNS_2026-10-06.md:12) should be read as upper bounds.

## Fix shape

Change the fill rule to trade-through by 1 tick; count a signal as unfilled/lost when its zone is traversed without a fill; report open-at-end trades; re-run the CC setups and update the rerun report. Keep every layer alert-only until a pre-registered, trade-through backtest passes (the parked blocklist is the opposite of that rule).

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md

2026-10-09 (JIS-NUC, sharma): PARTIAL. run_cc_setups.find_limit_fill now needs a trade-through by 1 tick (TICK=0.1); build_trades reports stats["open_at_end"] instead of dropping silently. 62 cryptocred tests pass (new test fails on old code; 3 touch-based tests moved one tick through).
STILL OPEN: (a) setup2_fib_pullback emits no signal when a bar blows through the zone, (b) bt_engine targets fill on touch, (c) rerun + update CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md. The rerun needs Dumps/backtest/raw_1m_2022 (1m klines) which is not on JIS-NUC (only raw_1h/1d/fund); run on JIS-NB or fetch 1m first.

2026-10-09 (JIS-NB): RERUN DONE (item c). Trade-through rerun on 1m data (research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md, appended section): all three setups FAIL on both fee variants. S/R flip OOS -0.038% maker / -0.107% taker (n 423); fib pullback OOS +0.042% maker (Sharpe 0.106, 1 of 2 positive years) / -0.030% taker (n 143); failed-MSB OOS negative. The earlier PASS verdicts do not survive (already withdrawn on 10-07; the tick rule moved S/R flip by <0.01 pp). Data window is 264 h longer than the 10-07 run. open_at_end is counted in stats but not printed in the report.
STILL OPEN: (a) setup2_fib_pullback no-signal on blow-through (its 0 unfilled is by construction, so its numbers stay an upper bound), (b) bt_engine targets fill on touch, (d) print open_at_end in the report.

## Receipt

2026-10-10 close (cc16a73): (a) setup2_fib_pullback: a bar that blows through the zone now fills the resting limit; its bear branch also built fib_zone descending so the touch condition could never be true: no short signal was ever emitted and the earlier fib numbers were long-only (found by the new test). (b) bt_engine.simulate_trade(target_through=0.1) used by run_cc_setups for entries and targets. (d) n_open_at_end printed. (c) rerun done here on F:/MTS/data/tom_raw 1m: setup1 OOS -0.1069 pct taker / -0.0382 maker (n 421), setup2 -0.0940 / -0.0275 (n 398), setup3 -0.2981 / -0.2408 (n 48): FAIL x6. Earlier PASS verdicts stay withdrawn. Layers stay alert-only.

# END
