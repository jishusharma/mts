# B146 - No minimum stop width exists since 0c34a2d removed the NO-SOURCE 0.1 % floor and nothing replaced it: Tom backtest median stop 0.082 %, planned gross R:R 79, fees dominate

Status: CLOSED. Severity: HIGH. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

No minimum stop width exists since 0c34a2d removed the NO-SOURCE 0.1 % floor and nothing replaced it: Tom backtest median stop 0.082 %, planned gross R:R 79, fees dominate.

## Evidence

- 0c34a2d (2026-10-06) deleted MIN_STOP_PCT 0.001 and the 0.2 % fallback in SetupCandidatesBuilder.java (T3 ruling, correct on provenance). Grep of Python, Java and PowerShell finds no other gate that rejects a stop that is too tight relative to fees; SetupCandidatesBuilderStopT3Test.tightSwingStopIsNotWidened pins a 0.05 % stop as KEPT.
- research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06_full.md:109: median stop 0.082 % of price, mean fee 2.76 R, mean planned gross R:R 79.46; line 6: sensitivity n=2880 net R -2.91 [-4.35, -1.89], holdout n=181 net -2.80. Before the floor was removed (TOM_CORE_BT_RERUN_2026-10-06.md:19) median stop was 0.200 %, net -0.30, fee about 0.23 R.
- backtest/tom_bt.py:177 fee_r = (entry_fee*entry + exit_fee*px)/risk, i.e. fee divided by stop distance. The -2.76 R magnitude is dominated by tiny stops (mean of 1/stop); the NEGATIVE SIGN is robust: gross R is -0.15 [-0.29, 0.04] before any fee, and random-entry null gross is +0.223 (report line 121). backtest/fees.py:22-23 DERIBIT_MAKER is 0.0 (the 0.0002 maker rate is the Binance profile, fees.py:27): confirm the Deribit maker assumption against the live schedule.
- The only remaining guards are the net_rr fee term and floor 1.25 (a 79:1 planned R:R passes easily) and the per-plan max-loss caps. A far target next to a tiny stop is exactly what looks best to the net_rr test and worst after fees.

## Fix shape

Do NOT re-add 0.1 % (NO-SOURCE). Measure instead, pre-registered: net R by stop-width bucket (<0.1, 0.1-0.2, 0.2-0.4, >0.4 %), maker vs taker legs, holdout read once. Derive a fee-based admission rule (reject when round-trip fee > an agreed fraction of the stop distance) from that measurement and flag any constant NO-SOURCE. Also check the Deribit maker fee assumption. Live path: stage, test, supervisor deploys.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-09 consolidate session: measured (research/fast_track_2026-09-27/TOM_STOP_WIDTH_2026-10-09.md): sub-0.10 % stops = 57 % of trades, 3.8-7.6 R fee drag each; gross R negative in every bucket. Staged auto_trader tom.max_fee_to_stop (default off) + test_b146_fee_to_stop. Open: operator enables it (recommend 0.3) and Java SetupCandidatesBuilder still builds tiny stops (F-BT-01 path).

2026-10-09 supervisor session: the fee-to-stop gate (tom.max_fee_to_stop, default OFF, fails closed on a bad value) is on origin and in the live tree; enabling it is Control Room decision D08. Measured: cut 0.3 keeps 161 hist / 34 dev trades at net -0.29 / -0.33 R (still negative, protective only). Java SetupCandidatesBuilder still builds tiny stops; the fix path is T081 (stop = structure +/- k x ATR, walk-forward, BT-TUNED), report research/fast_track_2026-09-27/T081_STOP_BUFFER_WF_2026-10-09.md.

# END
2026-10-09 CI/CD session: operator D09 = switch on at 0.3. auto_trader_config.json tom.max_fee_to_stop = 0.3 (code default stays off). test_shipped_config_has_the_gate_on_at_0_3 fails without it. auto_trader reads the config at start: it needs a restart to pick it up (loop-supervisor revives it).

2026-10-10 close: gate verified in the quick gate (step 1 lists test_b146_fee_to_stop); value 0.3 is the operator number from D09, not invented. Remaining Java-side tiny stops are tracked by T081 (walk-forward stop buffer).
