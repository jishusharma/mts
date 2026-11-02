Cards scanned: 207 (state done, closed >= 2026-10-31); paths checked: 353; paths missing: 25

# Done cards naming files not in the tree (independent recount, DSA direct 2026-11-02)

Method: python over MyTradingSys/system/tasks/*.json, state==done and closed>=2026-10-31 (207 cards; the brief said 161 and the earlier Gemini file 169, both lower: the count moved as cards closed). Path-like tokens (extension py/md/json/jsonl/js/html/txt/csv/ps1/java/...) regex-extracted from result + done_when, de-duplicated per card, checked against `git ls-files` (exact, or with MyTradingSys/ prefix). Wildcard/URL tokens skipped.

Result: 353 tokens checked, 207 not an exact tracked path. Of those, 177 bare filenames (no directory; 5 more are partial paths that match a tracked suffix) exist elsewhere in the tree under that basename (e.g. sync.py -> scripts/dev/sync.py), so they are resolved by basename and NOT counted missing. 25 are truly missing (below). Earlier Gemini file said 300 checked / 29 missing: its checked count differs (it counted fewer cards); its 29 list is mostly a superset of mine because it also counted some basename-resolved names.

| card id | path | nearest by basename | reason |
|---|---|---|---|
| bug-conflict-6a20d35469 | gate_timing.jsonl | NONE | no file of that name anywhere |
| bug-conflict-ea7682bf74 | .py.txt | NONE | no file of that name anywhere |
| bug-conflict-ea7682bf74 | backtest/layers/wavetrend/test_wavetrend_spec.py | NONE | no file of that name anywhere |
| c30-validation-read | verdict.json | NONE | no file of that name anywhere |
| cbp-run-extractor-claude-p-fails-on-jis- | verdicts.json | NONE | no file of that name anywhere |
| control-room-page-nan-false-positive-1031 | mts_control_room.html | NONE | no file of that name anywhere |
| cryptocred-4h-1d-dev-s3 | MyTradingSys/research/cryptocred_s3_2026-11/RESULT.md | MyTradingSys/research/t090_7h_2026-10-09/RESULT.md | named dir path not in tree; same basename elsewhere |
| cryptocred-4h-1d-dev-s3 | sim_desk/results/cryptocred-4h-1d-dev-s3.json | MyTradingSys/system/tasks/cryptocred-4h-1d-dev-s3.json | named dir path not in tree; same basename elsewhere |
| fabio-v3-l3-is-only-flag | out/is_only.json | NONE | no file of that name anywhere |
| fabio-v3-l3-is-only-flag | selection.json | NONE | no file of that name anywhere |
| fabio-v3-model-b-unmanaged-scored-zero | NOT_MEASURED.md | NONE | no file of that name anywhere |
| gpt-audit-formulas-vs-cowen-band-phase-tag | MyTradingSys/research/layer_lab/reports/2026-11-01_gpt-audit-formulas-vs-cowen-band-phase-tag.md | NONE | no file of that name anywhere |
| gpt-audit-formulas-vs-positioning-layer | MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-positioning-layer.md | NONE | no file of that name anywhere |
| gpt-audit-formulas-vs-stochastic-rsi-chart-verify | MyTradingSys/research/layer_lab/reports/2026-11-01_gpt-audit-formulas-vs-stochastic-rsi-chart-verify.md | NONE | no file of that name anywhere |
| gpt-audit-formulas-vs-trendlines-layer | MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-trendlines-layer.md | NONE | no file of that name anywhere |
| gpt-audit-formulas-vs-turn_of_candle-layer | MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-turn_of_candle-layer.md | NONE | no file of that name anywhere |
| gpt-audit-formulas-vs-wavetrend-layer | MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-wavetrend-layer.md | NONE | no file of that name anywhere |
| gpt-audit-formulas-vs-wlow_bounce-layer | MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-wlow_bounce-layer.md | NONE | no file of that name anywhere |
| gpt-audit-live-aid-indicators-vs-formulas | _gpt-audit-live-aid-indicators-vs-formulas.md | NONE | no file of that name anywhere |
| gpt-recheck-aibridge-07x-tests-1031 | .py.txt | NONE | no file of that name anywhere |
| gpt-rederive-tom-vp-return-to-value | _gpt-rederive-tom-vp-return-to-value.md | NONE | no file of that name anywhere |
| live-aid-macro-calendar-cors-snapshot | live_aid/ff_calendar_snapshot.js | NONE | no file of that name anywhere |
| tom-v2-gross-first-dev-ext | sim_desk/results/tom-v2-gross-first-dev-ext.json | MyTradingSys/system/tasks/tom-v2-gross-first-dev-ext.json | named dir path not in tree; same basename elsewhere |
| where-is-index-redo | role/CLAUDE.md | CLAUDE.md | named dir path not in tree; same basename elsewhere |
| wire-binanceliquidationaccumulator-into- | runtime_data/liq_events/BTCUSDT.jsonl | NONE | no file of that name anywhere |

Note: sim_desk/results/*.json and 2026-11-01_gpt-audit-* reports are named by cards but absent; gpt-audit-*-2026-10-30_* names drifted to 2026-10-31_ files. Not classified as future outputs because the cards are done.

Command: python scan over system/tasks (see method), git ls-files.
