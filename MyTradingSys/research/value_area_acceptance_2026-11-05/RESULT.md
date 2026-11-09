# Value-area acceptance on BTC (Tom/Fabio "accepted back inside / outside value")

Operator ask 2026-11-05: "Tom talks abt price moving in levels b/w buyers and sellers - he talks abt price acceptance and direction - so is MTS capturing those and able to trade them?"

Method (`accept80.py`): prior UTC day value area = 70% of 1m volume around the POC, $50 bins, closes binned (OURS). 666 days, 2024-12-02..2026-09-28, F:/MTS/data/orderflow_1m (Binance spot 1m). Acceptance = two consecutive 30m closes (Dalton; count OURS).

| Event | n | Result | 95% CI |
|---|---|---|---|
| R: outside prior VA, then accepted back inside -> reaches far VA edge same day ("80% rule") | 493 | 44% | 40..49% |
| A: accepted below VAL -> trades a further half VA width lower same day | 300 | 77% | 72..81% |
| A: accepted below VAL -> back to POC same day | 300 | 42% | - |

Read: the 80% rule is 44% on BTC, not 80%. Acceptance below value tends to extend a little (half-width is small, so part of the 77% is plain volatility; no placebo yet). Descriptive only, no fees, no trade rule.

Dalton 80% rule on BTC = 44% [40..49], n=493 (Event R, the row above). The 77% (Event A) is a same-day half-VA-width drift, not a win rate; placebo pending in card placebo-for-the-77-acceptance-claim-rand. Census ACCEPTED at 1R = -0.096 R gate-pass (n=2798).

Live state: no Tom/Fabio balance layer runs live (tom_core STOP, Tom v2 cards T3-T8 blocked, Fabio v3 OOS FAIL). Card live-aid-balance-acceptance-1105 adds the read to live_aid.
