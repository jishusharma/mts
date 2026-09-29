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
- [x] 999 Tom master rulebook merge: the 16 new T- rules (extracts/processed/tom/WQ_OAdz-PJ8, zAwEX_tRUfE) into the Tom master list; flag conflicts only (never edit Tom logic)
- [ ] Cross-trader rulebook: extracts/processed/cryptocred + flowhorse -> same table format as 998; mark which are already built as layers
- [ ] T054 research brief: US session / correlation / news effects on BTC - from on-disk research only; list claims needing verified sources (web research is done by a Sonnet worker under playbook Part I, not DSA)

## B. Specs + code (DSA writes code from a spec; tests come from the feeder)
- [ ] (needs 998 + FABIO_OF_REPORT) Fabio trade model spec: location -> context -> trigger -> management from the rulebook's testable core, as a layer module spec with FORMULAS.md-style definitions
- [ ] (needs spec above) Fabio trade model implementation (backtest module under MyTradingSys/backtest/layers/fabio/, offline only)
- [ ] Backtest driver for malkan_40_60 regime-gated setups + malkan_mtf 5-star (Grandfather/Father/Son) - same verdict rule as FABIO_L1 (IS/OOS 70/30, fees 0.10% RT, PBO); never tested historically
- [ ] Backtest driver for rsi_ma_events (RSI x RSI-MA cross/events), same method
- [ ] Q1 per-layer bracket grid driver: for each layer's historical events, grid stop {0.5,1,1.5,2}% x target {1,2,3}R x time exit {4,8,16} bars; IS/OOS + PBO; output the best frozen bracket per layer or "fixed 1%/2% default stands"

## C. Reviews / audits (instead of the hot NUC)
- [ ] Formula audits 083/084 (FORMULAS.md vs code) - the NUC versions are thermally paused
- [ ] Review of TOM_CORE_BT.md method (once it lands): look-ahead, fill assumptions, cost model - list defects only
- [ ] Review of FABIO_OF_REPORT.md (once it lands): same
