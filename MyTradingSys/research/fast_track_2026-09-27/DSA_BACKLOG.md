# DSA BACKLOG - tasks the cheap feeder packs into the DSA lane (created 2026-09-30, supervisor)

Feeder rule: keep `incoming_dsa` at >= 1 task. Take the top unchecked item whose "needs" are met, write a spec to
Dumps/workers/NUC-QUEUE/specs/<id>-dsa-<slug>.md (TASK / SCOPE / OUTPUT / OUTPUT_TOKENS header like 998-dsa-fabio-rulebook.md;
prompt <= 90k chars; split by file if larger), `python scripts/worker/queue_tool.py pack --lane dsa <spec>`, then tick the box
with the task id. Gate each reply: extraction/rulebook -> `verify_extract_quotes.py` where quotes exist; code -> write
the file as .new, spec-derived tests (feeder writes them BEFORE reading DSA's code), run in a scratch copy, commit on pass;
research text -> spot-check one claim, commit.
Backtest drivers: once a driver is committed, the feeder runs it on the full history (Dumps/backtest/raw_1m_2022 + raw;
order-flow bars on F:\MTS\data\orderflow_1m when built) and commits the report next to the driver. A layer with a
passing verdict goes live on testnet as an alert layer (supervisor wires + restarts), never as a Tom filter. Never pack anything touching MyTradingSys/execution/ or a live-imported file
except as a .new proposal. Tom is core; every other system is a separate layer, never a Tom filter.

## A. Rulebooks (long-context reading)
- [x] 998 Fabio rulebook (all Fabio extracts -> FR table, class, data needed, Tom overlap)
- [x] 999 Tom master rulebook merge: the 16 new T- rules (extracts/processed/tom/WQ_OAdz-PJ8, zAwEX_tRUfE) into the Tom master list; flag conflicts only (never edit Tom logic) - DSA output lost; redone 2026-09-30 by cloud Sonnet: TOM_RULEBOOK_MERGE_999.md (4 NEW, 12 MATCH, 2 CONFLICT)
- [x] Cross-trader rulebook: extracts/processed/cryptocred + flowhorse -> same table format as 998; mark which are already built as layers - cloud Sonnet 2026-09-30: CROSS_TRADER_RULEBOOK.md
- [x] T054 research brief (cloud Haiku 2026-09-30: T054_US_SESSION_BRIEF.md): US session / correlation / news effects on BTC - from on-disk research only; list claims needing verified sources (web research is done by a Sonnet worker under playbook Part I, not DSA)

## B. Specs + code (DSA writes code from a spec; tests come from the feeder)
- [x] (cloud Opus 2026-09-30: FABIO_V3_SPEC.md, 97-103 trials, T01-T50) (needs 998 + FABIO_OF_REPORT) Fabio trade model spec: location -> context -> trigger -> management from the rulebook's testable core, as a layer module spec with FORMULAS.md-style definitions
- [ ] (NUC specs 2201-2203 + pending_test_fabio_v3.py written 2026-09-30; awaiting pack) (needs spec above) Fabio trade model implementation (backtest module under MyTradingSys/backtest/layers/fabio/, offline only)
- [x] (cloud Sonnet 2026-09-30: layers/rsi/run_rsi_backtest.py, 35 tests; desktop runs it) Backtest driver for malkan_40_60 regime-gated setups + malkan_mtf 5-star (Grandfather/Father/Son) - same verdict rule as FABIO_L1 (IS/OOS 70/30, fees 0.10% RT, PBO); never tested historically
- [x] (same driver, --family rsi_ma_events) Backtest driver for rsi_ma_events (RSI x RSI-MA cross/events), same method
- [x] (cloud Sonnet 2026-09-30: layers/run_bracket_grid.py, 27 tests, 54-cell grid incl 0.3/0.75% stops; desktop runs it) Q1 per-layer bracket grid driver: for each layer's historical events, grid stop {0.5,1,1.5,2}% x target {1,2,3}R x time exit {4,8,16} bars; IS/OOS + PBO; output the best frozen bracket per layer or "fixed 1%/2% default stands"

## C. Reviews / audits (instead of the hot NUC)
- [x] (cloud Sonnet 2026-09-30: FORMULA_AUDIT_2026-09-30.md, 39 MATCH / 2 MISMATCH / 2 UNTESTABLE) Formula audits 083/084 (FORMULAS.md vs code) - the NUC versions are thermally paused
- [x] (cloud Sonnet 2026-09-30: TOM_CORE_BT_REVIEW_2026-09-30.md, 2 HIGH / 9 MED / 6 LOW) Review of TOM_CORE_BT.md method (once it lands): look-ahead, fill assumptions, cost model - list defects only
- [x] Review of FABIO_OF_REPORT.md (once it lands): same - done in FABIO_BTC_RESEARCH_2026-09-30.md section 2

## D. Trade reconstructions (cloud-written specs, 2026-09-30; template MISSING_PIECES_2026-09-30.md 3.2)
Hold lifted by operator 2026-09-30: run as planned; Opus EXTRACTION_METHOD_V2 may add a later re-extraction.
- [x] 2101-2104 Fabio recon: 0KyIEdvVKMQ, LQvv5xgy_ik, fZlNGWvd2Ko, FawPrRUGNpk (specs in nuc_specs/)
- [x] 2105-2113 Tom recon: 7BQPMJ39WpI, 96iPFDpXEcU, HySZZSjMxF8, WQ_OAdz-PJ8, aursfDVYzUk, gWjHq5UMisY, hQ8sOq67x5o, pgdmKLJ0hhA, zAwEX_tRUfE

## E. Options module backtests (MyTradingSys/options/, 2026-10-09; read options/OPTIONS_PLAN.md first)
- [ ] 2301 (packed 2026-10-09) Independent audit of the options backtest engine (look-ahead, fills, fees, stats) -> options/research/BT_AUDIT_DSA_2301.md; defects only
- [ ] 2302 (packed 2026-10-09) Spec-derived hand-computed tests for R1/R2/R3/R4 -> options/tests/pending_test_bt_independent.py; feeder runs them against strategies.py and files failures as defects
- [ ] 2303 (packed 2026-10-09) Specs R8-R13 (wheel, skew filter, max pain, DVOL regime, basis carry, gamma scalp) from practitioner chatter -> options/backtest/BT_SPEC_V2_CANDIDATES.md
- [ ] GROK channel (operator pastes): options/research/GROK_PROMPT_options_traders.md; save reply as options/research/GROK_REPLY_options_traders_<date>.md, then feed it to 2303 as SCOPE
- [ ] (after 2301 verdict and data backfill to 2021) feeder runs `python MyTradingSys/options/backtest/run_grid.py --strategy all` and commits the report with IS/OOS + PBO; no profitability claim before then
