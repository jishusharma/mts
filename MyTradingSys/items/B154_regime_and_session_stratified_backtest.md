# B154 - No regime-stratified and no session-stratified backtest verdict exists; every reported edge is one aggregate number

Status: OPEN. Severity: MED. Opened 2026-10-09.
Session: MTS-2026-10-09-DSA-COO. Source: external research pass 2026-10-09 under playbook PART I (method note written before searching, tier table fixed, per-source citation check, three sources rejected).

## Defect

Backtest verdicts in MTS are reported as one number each. No verdict is stratified by market regime, none by trading session, and none by both.

## Evidence

- Peer-reviewed regime division: hidden Markov model on log returns infers latent bull, bear and sideways states, with stated persistence and transition stability, and an out-of-sample window.
- Peer-reviewed session division: two complementary 12-hour sessions, 25 ordered rule combinations, chronological holdout, multiple-testing correction.
- MTS reports one aggregate number per run: TOM_CORE_BT_RERUN_2026-10-06.md, T055_BT_RERUN_FULLFUNDING_2026-10-07.md, CryptoCred rerun.
- Regime inputs untested: quad_classify, regime_classifier, update_market_state, StateCodeEmitter (TWO_CORES_READINESS_2026-10-01.md).
- Live log rg=RANGE every cycle; snapshot day_type UNKNOWN.
- Session inputs present but not reported: current_session, us_equity_open_window, funding_reset_window.
- Holdout 2026-06-26..2026-09-26 inside Rule 32 evidence; burned for Tom.
- Registry key not yet run_id + commit hash + config hash; FROZEN.md not written before the run.
- No source combines regime and session stratification with an out-of-sample result.

## Fix shape

Build one regime x session stratified backtest harness on committed data. Regime from a change-point or hidden-Markov detector with stated persistence. Sessions at the two 12-hour boundaries. Chronological holdout. Multiple-testing correction reported with every verdict. Report the first verdict per regime and per session, net of fees and funding.

## Related

- MyTradingSys/methodology/playbook.md PART I (research gate)
- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (B146-B153)

## Receipt