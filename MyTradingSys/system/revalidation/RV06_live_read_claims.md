# RV06 [MED] Live-read findings: HALT, Tom direction-health, VWAP/CVD mismatch (e911cfb, 6fc967c, 4870539)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV06. Report: `MyTradingSys/research/revalidation/RV06_<UTC date>.md`.

Scope in: MyTradingSys/research/screenshots/ (reads: 2026-10-12_BTCUSDT_set_5b0e17d24d71.md, 2026-10-12_BTCUSDT_8h_f3ba42e7e7d6.md,
2026-10-12_BTCUSDT_30m_15m_8ff150f93dfc.md, engine/5b0e17d24d71.json, engine/9580843f8e7b.json), MyTradingSys/research/observations/
2026-10-12_layer_observations.md, cards exec-halt-entry-10031, state-machine-vwap-cvd-vs-klines, tom-direction-health-vs-sources,
MyTradingSys/observation/capture.py (TF_MINUTES 8h change), 1m klines (Dumps/backtest/raw_1m_2022 or F:/MTS/data/bigtrade/spot_raw).
Scope out: edits, the live path, mirror refresh, HALT files.
Why: each read ends in MATCH/MISMATCH claims; a MISMATCH becomes a card and may change engine code. The reader and the
engine-state script were both written by Claude, the screenshots are the only independent witness.
Checks: for every MATCH / MISMATCH line, recompute the number from the engine JSON or klines (print both values and the source line);
check the HALT claim against the cited log/state lines; check the VWAP and CVD definitions the engine uses vs the vendor chart
(session anchor, UTC vs exchange day, spot vs perp volume); confirm each finding card's text restates its read faithfully.
Already known: 6fc967c states 7 MATCH, 1 MISMATCH (label), 1 NOT_IN_DATA for the 8h CoinGlass shot.
