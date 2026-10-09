# B146 - No minimum stop width exists since 0c34a2d removed the NO-SOURCE 0.1 % floor and nothing replaced it: Tom backtest median stop 0.082 %, planned gross R:R 79, fees dominate

Status: OPEN. Severity: HIGH. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

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

- MyTradingSys/research/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

# END
