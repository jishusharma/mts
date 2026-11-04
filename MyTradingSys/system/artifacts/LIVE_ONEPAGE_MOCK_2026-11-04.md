Live one-page mock v2 (operator style: 16px, KPI tiles, Δ box, date x symbol grids, mono ladder, 1m|5m legend). Data per tab; defaults taken, no questions.
- Market now: runtime/orderflow_live/*.csv (newest 2026-10-03, header chip shows age; no market_guide.md, feeds stale here). Live: live_mirror.py brief on desktop-f7iu69n.
- Signals: research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json (30m bottom-buy backtest, VALIDATION), not live flags; needs a runtime flag export.
- Positions/testnet: SAMPLE-POS, all numbers invented; order data stays out of the public repo, so it needs a local-only mirror feed.
- News & calls: habib_plan_imbalance_2026-10-20/PLAN_LEDGER.csv (calls, ladder); hack timeline rows hand-copied from news_feeds_2026-10-30/REPORT.md s2.
- Layers: system/LAYERS.md dated verdict lines (grid + Δ) and scripts/dev/market_guide_verdicts.json (tags), parsed at build.
- Health: research/STATUS.md parsed at build (CI, pages stale, digest, commits, gate board); its age is shown, it can lag trunk CI.
- Generators to change for live: mts_home generator (registry slug mts_home), live_mirror.py brief, STATUS generator.
- SAMPLE badges: SAMPLE-POS.
- Build: python MyTradingSys/system/artifacts/_gen_live_onepage_mock.py [--fragment <artifact copy>]; artifact https://claude.ai/artifact/DBQFxH79QsFSCVxmGqvSU9
