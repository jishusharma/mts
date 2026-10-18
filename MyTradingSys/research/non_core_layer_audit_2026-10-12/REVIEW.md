# Second-eyes review of the layer audit (JIS-NUC, 2026-10-12)

Reviewed REPORT.md at fast-track tip 7a28721 (worktree jis-nuc/layer-audit-s1012). Scope: RSI and WaveTrend
findings, plus the unknowns that code or saved data could settle. Register: `EVIDENCE_REGISTER.md/.json`.

## Gate
- Run 1 (`gate_quick_receipt_run1_FAIL.txt`): FAIL, 2 steps (wiring gate, wiring check). Cause: this package's
  `package_report.py` and `verify_audit.py` were undeclared orphans. Everything else PASS (Maven and backtest SKIP under --quick).
- Fix: declared both in `system/wiring_registry.json` (REPRO, Q38). Run 2 receipt: see
  `gate_quick_receipt_run2.txt` (result recorded in the commit and NEXT_SESSION.md).
- The audit's own 505 tests re-pass on current fast-track (`verify_audit.py`: rsi 134, timeframe 18, cryptocred 69,
  positioning 21, session 9, turn_of_candle 36, session_levels 13, tick 49, consensus 52, alerts 104 = 505).

## Findings that hold (re-checked)
| Finding | Check I ran | Result |
|---|---|---|
| 92 divergence cells, 36 no-edge, 56 insufficient-n, 0 edge candidates | Recounted from summary.json and summary_T088.json, horizon 10, min_events 300 | Confirmed. 35 of the 36 powered cells net negative; the one positive is 1h operator bearish n=332, +0.038%, t=0.39 |
| WaveTrend not built | grep of .py/.java/.pine/.json on current fast-track | Confirmed: only audit files, control_room.json and groups.json (parked) |
| `rsi_events` rejects tolerance 0 while default.json says 0 | Read rsi_events.py:20 and default.json | Confirmed |
| CryptoCred 1.5R/2R role swap | Read extract line 82 and cc_setups defaults | Confirmed; the quote names the numbers as counter-trend minimum R:R |
| Tick delta mismatch | Read tiers_meta.json and build_tiers.py header | Confirmed (see sharpening below) |

## Where I would change the audit
1. **"Regime proxy" is overstated.** `malkan_regime` BULL = min>=40 and max>=60 over 20 values. A BULL regime with current
   RSI 45 is by design (a bull range holds 40 as support). The real defects are (a) lookback 20 has no source window
   (provenance R11 CONCEPT-ONLY) and (b) it is applied on intraday frames where the source works from daily. Do not describe
   it as a failed threshold gate.
2. **New: the live tolerance is an in-sample boundary pick.** Live `RSI_TOL = 0.5` (live_layers.py:143) equals the lowest
   value of the D3 grid 0.5..5.0 that was chosen by best in-sample return (R25, NO-SOURCE). Meanwhile the "sourced"
   malkan_40_60_default.json carries `event_tolerance: 2`. Two tolerances for one level, neither sourced as a number.
3. **Provenance Q3 is answered.** The LAYER_PROVENANCE_AUDIT open question "what does the live runner pass?" is 0.5;
   default.json tolerance 0 is read only by tests. The audit presents R04 as a new finding; it was known, and is harmless in production.
4. **Zero edge candidates is mostly a power-and-fee statement.** All 36 powered cells are on 1m-2h; gross spans
   -18..+14 bp against a 10 bp round-trip fee. 4h/1d cells never reach n=300, so the table says nothing about
   higher-timeframe divergence, which is where the source applies it.
5. **Timeframe finding sharpened.** The resampler already returns `gap_count` and `n_bars` on every bucket (REPRODUCED:
   gap_count=20, n_bars=40 for a half-empty hour). The defect is that `run_divergence_mtf` never reads them. The fix is a consumer filter, not a schema change.
6. **Tick finding narrowed.** `missing_in_klines = 2880` is exactly two whole days (2 x 1440), so the count is a clean
   gap, not scattered loss. The 68.25 BTC maximum is still unexplained; raw 1m klines are absent on this machine.

## WaveTrend: what can be settled now
- Formula and defaults are fully written in T061 (n1 10, n2 21, wt2 SMA 4, 0.015, +-60/+-53); T065 says the Pine source was
  opened and read on 2026-10-05, so "no fresh Pine verification" in REPORT means this session, not the repo.
- Candidate answers to the unknowns, from Pine semantics and NOT yet checked against a saved source: EMA seeded with the
  first source value; d=0 gives a division by zero (na in Pine). Treat both as hypotheses until a Pine snapshot is saved.
- Still blocked: saved Pine snapshot, chart exports for golden fixtures, module-path decision (layers/wavetrend/ per T061).
  Implementation stays parked by the Layer Board; nothing was built here.

## Not done (needs inputs I do not have)
Fresh mirror/deployment SHA, canonical ledger, Malkan video frames (P0-B), raw 1m klines for the tick reconciliation.
