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
