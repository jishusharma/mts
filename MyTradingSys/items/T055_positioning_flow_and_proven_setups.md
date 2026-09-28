# T055 - POSITIONING FLOW (NET/NEW LONGS & SHORTS) + PROVEN BTC SETUPS RESEARCH

Convention: one item, one doc. Verbatim ask at top. Updates appended, newest last.
Related: T040 (tick/delta extremes, OI/CVD tiers), T054 (US session anomalies), T053 (hedge scalping).
Rule: any setup found becomes a separate layer (PROJECT_VISION), never a Tom filter.

## VERBATIM ASK (operator, 2026-09-28)
WRT indicators - verify and research if :
	a. Net Shorts and Net Longs, and New Long and New Shorts - how professional trades use these indicators? Is there is a setup? Is there a hint that is used for confluence?
	If we have time frame wise delta of these indicators then can we identify trend bias in a meaningful and useful way? I am not sure there are many unknowns that you need to focus your research on.
	Also are there any other indicators that are clubbed with these above ones to make a trading setup?

	b. On internet - what/which are the most reliable and most valid BTC trading setups using any indicator that works best for a given task like Scalping, Intra Day or any trading style/methodology.
	Goal is fins something that actually works the best and is possible for us to implement and maybe back-test.

## STATE
2026-09-28 OPEN, on fast-track (operator). Research started (two Sonnet web-research workers, session 3).
Outputs: research/fast_track_2026-09-27/T055a_POSITIONING_FLOW.md, T055b_PROVEN_SETUPS.md.
Next: supervisor picks <=3 candidates -> formulas into FORMULAS.md -> Qwen specs -> backtest (verdict.py, PBO).

2026-09-28 research done (Sonnet x2), reports in research/fast_track_2026-09-27/T055a_*.md, T055b_*.md.
a) No vendor publishes its net/new long-short formula; standard = OI delta x price (or CVD) direction, 4 states.
   Testable: H1 OI-delta x CVD 4-state as entry filter on trend layers (needs OI history fetch - live Java feed
   has OI snapshots, backtest side has none); H2 CVD/price divergence + funding extreme fade (data exists);
   H3 taker imbalance -> 4-12h direction (grade-A order-imbalance paper).
b) Top 5: funding-extreme reversion; vol-scaled TSM (thin net of costs); intraday session momentum
   (Shen/Urquhart/Wang, Financial Review 2022); opening-range breakout (equities only so far); 21-23 UTC window.
   Weak/dead: BB/Keltner squeeze, VWAP bands, standalone RSI divergence, raw ICT OB/OTE, weekday seasonality.
Spot-check: T055a "no OI ingestion" only true for backtest (src/main/java/datafeed/BinanceClient.java fetches OI).
Pending operator pick (merge H2 + b#1 as one funding/CVD layer suggested).
2026-09-28 GATE CHECK (supervisor): T055a/b did NOT follow playbook Part I (no Step-1 methodology note, ad-hoc
A/B/C grades instead of T1/T2/T3/REJECT, preprints/SSRN graded "A", no Tier|Quality|Confidence tags, citations
not re-verified). Status of all findings above: UNVERIFIED ASSUMPTION - not usable for any rule until remediated.

2026-09-28 GATE REMEDIATED: both reports rewritten in place to playbook v3.0 (method notes, T1/T2/T3/REJECT
tiers, every citation opened/re-verified, discard list, formula candidates deferred to FORMULAS.md). Pre-gate
versions backed up as .pre_gate3. One citation was a wrong-paper mismatch (EuropePMC ppr602886, T055a) and one
was a claim mismatch (SSRN 7483658, T055b); both logged to 02b_DECISIONS_LOG.md and corrected. CME 24/7 claim
verified true. Surviving hypotheses: T055a H1 (OI-delta x CVD 4-state filter, T3 idea + our own weak-signal
internal backtest), H2 (funding+CVD divergence fade, T2 via whale_positioning_evidence), H3 (opening/quarter-
hour order-imbalance 4-12h, T2, corrected citation). T055b top candidates: turn-of-candle (T1), funding-extreme
reversion (T2), intraday session-momentum (T1), funding carry (T2, regime-flagged), order-flow imbalance scalp
(T2, low confidence). Next: operator picks <=3 for Qwen specs -> verdict.py backtest, PBO, OOS.

2026-09-29 FAST-TRACK OF C1/C2/C3 (operator-approved; supervisor pick): C1 funding-extreme reversion merged with CVD/price
divergence fade (T055a H2 + T055b funding-extreme), C2 intraday session momentum (Shen/Urquhart/Wang 2022, T1),
C3 turn-of-candle (Shanaev et al., T1). Definitions: FORMULAS.md sections 13-16 (backup FORMULAS.md.pre_t055).
NUC specs (queue ids sort ahead of 101-120): 0985 trade_costs.py (shared fee+slippage+funding), 0986 funding_cvd_fade.py (C1),
0987 session_momentum.py (C2), 0988 turn_of_candle.py (C3, MODEL gpt-oss:20b pilot). Tests already written next to the target
modules (layers/positioning/, layers/session/, layers/turn_of_candle/); they fail until the modules land.
Note: verdict.py is the Tom setup-verdict function and is NOT used for layers; layer candidates are judged by
layers/runner.forward_return_stats + bt/ref_pbo.ref_pbo_cscv, as in layers/fabio/run_backtest.py.

### Runbook (after 0985-0988 are verified and promoted)
1. Promote each .new (back up to .pre_t055, rename), then gate:
   `python scripts/worker/queue_tool.py verify 0985-t055-trade-costs 0986-t055-c1-funding-cvd-fade 0987-t055-c2-session-momentum 0988-t055-c3-turn-of-candle`
   `python -m unittest MyTradingSys.backtest.layers.positioning.test_trade_costs MyTradingSys.backtest.layers.positioning.test_funding_cvd_fade MyTradingSys.backtest.layers.session.test_session_momentum MyTradingSys.backtest.layers.turn_of_candle.test_turn_of_candle`
   `python scripts/dev/run_all_tests.py --quick`
2. Driver (NOT yet written; a Sonnet task, copy the structure of layers/fabio/run_backtest.py): `MyTradingSys/backtest/layers/run_t055.py --candidate c1|c2|c3`.
   Required behaviour: load klines with bt_data.load_klines (C2/C3: raw_1m_2022 + raw, 2022-2026; C1: raw only, funding starts 2025-09,
   load_funding), resample via tf_resample (C1 15m/1h with tbv merge as in fabio run_backtest; C2 5m; C3 1m); chronological 70/30 IS/OOS;
   grid search on IS only (C1: lookback {60,90,180}, n {20,50}, hi/lo {0.90/0.10,0.95/0.05,0.99/0.01}, use_divergence {T,F};
   C2: first_min {30,60}, entry_min {first_min, session_len-30}, session_start_min {0, 810}, min_abs {0,0.001};
   C3: lead_minutes {1,2}, side {long,short}); score each event with trade_costs.net_return (fee 10 bps RT + 2 bps slip + funding)
   at horizons per candidate (C1 4/16/48 bars of 15m, C2 to session end, C3 1/2/5 bars); PBO via ref_pbo_cscv on daily-bucketed IS net returns.
3. Commands (output to Dumps/backtest/runs/t055_<c>/):
   `python MyTradingSys/backtest/layers/run_t055.py --candidate c1 --out Dumps/backtest/runs/t055_c1`
   `python MyTradingSys/backtest/layers/run_t055.py --candidate c2 --out Dumps/backtest/runs/t055_c2`
   `python MyTradingSys/backtest/layers/run_t055.py --candidate c3 --out Dumps/backtest/runs/t055_c3`
4. PASS criteria (all must hold, on the IS-chosen params applied to OOS): OOS n_events >= 30; OOS mean NET return per trade > 0 after fees,
   slippage and funding; OOS net Sharpe (bt_stats) >= 0.3 (T055 kill threshold); PBO < 0.5; sign of the net edge the same in IS and OOS
   (C2/C3 additionally: positive in >= 2 separate OOS calendar years, per T055b). C1 caveat: only ~12 months of funding, so a single
   70/30 split; treat a pass as provisional and re-run as data accrues.
5. On a pass: register the layer in MyTradingSys/backtest/layers/alerts/live_runner_cli.py `build_default_registry`, ALERT-ONLY (no order path,
   never a Tom filter), gate with run_all_tests, then operator decides on any further use. On a fail: log the numbers in this item and
   close the candidate; do not tune parameters on OOS.
