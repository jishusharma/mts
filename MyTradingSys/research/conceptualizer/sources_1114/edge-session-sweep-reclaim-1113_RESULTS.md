# edge-session-sweep-reclaim-1113 RESULTS (2026-11-13 ~16:30Z)
VERDICT: FAIL (12 cells, none passes; power gate BLOCK recorded: MDE ~0.25 R, so a small edge is not excluded).
Pooled Bybit 5m BTC+ETH+SOL, weekdays, Europe-low sweep in US window, reclaim <=60 min, long at next open (+ mirror short).
- Taker cells, VALIDATION (n 331-384): fee-net mean R -0.23 to -0.32, every CI upper bound below 0 or touching it (e.g. long 2R taker n 384 -0.259 [-0.412,-0.090]).
- Maker-limit cells, VALIDATION (n 148-173): -0.12 to +0.11, all CIs span 0 (best long HIGH maker n 173 +0.105 [-0.298,+0.577]; short 2R maker n 148 +0.094 [-0.150,+0.331]). BH 10 %: no cell rejected.
- Placebo (random US-window bar, same stop % and target R): -0.54 to -0.69 R, events beat it, but it is a tight-stop loser; beating it is not an edge.
- DEV taker cells -0.13 to -0.36; maker DEV -0.18 to +0.06. RECENT maker cells +0.03 to +0.25 (n 207-231, CIs span 0): only a lead, not a result.
- Best next test: maker-limit retest entry at the reclaimed level with a wider stop (>=0.8 %), RECENT-style forward on testnet; needs ~1600 maker events.
Files: MyTradingSys/research/eur_low_sweep_reclaim_pooled_2026-11-13/{PRE_REG,REPORT}.md in worktree <worktree>
