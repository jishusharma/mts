# NOT_IN_DATA (card btc-native-orderflow-map-1112)

Verdict: FAIL / NOT_IN_DATA for a paper slot; no rule passes DEV |z|>=2 vs placebo net of the 10 bp fee.

Missing feeds:
- Liquidation history: no public feed, so liquidation-cascade events cannot be tested.
- Full-DEV aggTrades (only 60 sampled event days): A1 large prints on all DEV is NOT_RUN; A2 sits at n=170 (<180) INSUFFICIENT_N and needs more DEV days or a longer window.
- VALIDATION stays sealed; the forward paper run is the only out-of-sample test and no rule is frozen for it.
