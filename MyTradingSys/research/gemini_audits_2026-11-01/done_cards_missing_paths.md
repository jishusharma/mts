# Cards scanned: 169, Paths checked: 300, Paths missing: 29

# Audit of Repository Paths in Closed Task Cards (Closed >= 2026-10-31)

Systematic scan of every task card in `MyTradingSys/system/tasks/*.json` marked `done` with `closed` or `refreshed` on or after 2026-10-31.
All path-like references in `result` and `done_when` were extracted and checked against `git ls-files`.

## Summary Statistics

- **Task Cards Scanned**: 169
- **Path References Checked**: 300
- **Paths Found in Working Tree**: 271 (90.3%)
- **Paths Missing from Tree**: 29 (9.7%)
- **Tokens Skipped (Status Enums / Placeholders)**: 0

---

## Missing Repository Paths

| Card ID | Named Path | Nearest Existing File | Reason / Category |
| :--- | :--- | :--- | :--- |
| `aibridge-reply-drop-4-blocks-generation-` | `test.js` | `scripts/aibridge/tests/loop.test.js` | File moved, renamed, or omitted from commit |
| `ask-p0-45-tf-break-event-study` | `sim_desk/results/ask-p0-45-tf-break-event-study.json` | `MyTradingSys/system/tasks/ask-p0-45-tf-break-event-study.json` | Uncommitted sim_desk result card |
| `ask-p0-65-setup-alpha-beta-backtest` | `sim_desk/results/ask-p0-65-setup-alpha-beta-backtest.json` | `MyTradingSys/system/tasks/ask-p0-65-setup-alpha-beta-backtest.json` | Uncommitted sim_desk result card |
| `bug-conflict-6a20d35469` | `gate_timing.jsonl` | `.claude/settings.json` | Runtime uncommitted log / data stream |
| `bug-conflict-ea7682bf74` | `backtest/layers/wavetrend/test_wavetrend_spec.py` | `MyTradingSys/backtest/layers/wavetrend/test_wavetrend.py` | File moved, renamed, or omitted from commit |
| `bug-conflict-ea7682bf74` | `py.txt` | `MyTradingSys/research/layer_lab/gpt-g3-pack-audit/probe.py.txt` | File moved, renamed, or omitted from commit |
| `c30-validation-read` | `verdict.json` | `MyTradingSys/research/layer_lab/candle_close_2026-10-14/verification.json` | File moved, renamed, or omitted from commit |
| `control-room-page-nan-false-positive-1031` | `mts_control_room.html` | `scripts/dev/control_room.tpl.html` | Generated HTML artifact |
| `cryptocred-4h-1d-dev-s3` | `MyTradingSys/research/cryptocred_s3_2026-11/RESULT.md` | `MyTradingSys/research/no_source_sweep_2026-10-09/RESULT.md` | File moved, renamed, or omitted from commit |
| `cryptocred-4h-1d-dev-s3` | `sim_desk/results/cryptocred-4h-1d-dev-s3.json` | `MyTradingSys/system/tasks/cryptocred-4h-1d-dev-s3.json` | Uncommitted sim_desk result card |
| `fabio-v3-l3-is-only-flag` | `out/is_only.json` | `MyTradingSys/research/indicator_audit_2026-10-14/klines_pool.json` | File moved, renamed, or omitted from commit |
| `fabio-v3-l3-is-only-flag` | `selection.json` | `MyTradingSys/options/backtest/selection.py` | File moved, renamed, or omitted from commit |
| `fabio-v3-model-b-unmanaged-scored-zero` | `NOT_MEASURED.md` | `MyTradingSys/research/self_heal_2026-10-28/MEASURE.md` | File moved, renamed, or omitted from commit |
| `fractal-hurst-regime-gate-f2` | `f2/RESULT.md` | `MyTradingSys/research/no_source_sweep_2026-10-09/RESULT.md` | File moved, renamed, or omitted from commit |
| `gpt-audit-formulas-vs-positioning-layer` | `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-positioning-layer.md` | `MyTradingSys/research/layer_lab/reports/2026-10-31_gpt-audit-formulas-vs-positioning-layer.md` | Report date drift (report committed under 2026-10-31_ date prefix) |
| `gpt-audit-formulas-vs-trendlines-layer` | `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-trendlines-layer.md` | `MyTradingSys/research/layer_lab/reports/2026-10-31_gpt-audit-formulas-vs-trendlines-layer.md` | Report date drift (report committed under 2026-10-31_ date prefix) |
| `gpt-audit-formulas-vs-turn_of_candle-layer` | `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-turn_of_candle-layer.md` | `MyTradingSys/research/layer_lab/reports/2026-10-31_gpt-audit-formulas-vs-turn_of_candle-layer.md` | Report date drift (report committed under 2026-10-31_ date prefix) |
| `gpt-audit-formulas-vs-wavetrend-layer` | `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-wavetrend-layer.md` | `MyTradingSys/research/layer_lab/reports/2026-10-31_gpt-audit-formulas-vs-wavetrend-layer.md` | Report date drift (report committed under 2026-10-31_ date prefix) |
| `gpt-audit-formulas-vs-wlow_bounce-layer` | `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-wlow_bounce-layer.md` | `MyTradingSys/research/layer_lab/reports/2026-10-31_gpt-audit-formulas-vs-wlow_bounce-layer.md` | Report date drift (report committed under 2026-10-31_ date prefix) |
| `gpt-audit-live-aid-indicators-vs-formulas` | `_gpt-audit-live-aid-indicators-vs-formulas.md` | `MyTradingSys/system/tasks/gpt-audit-live-aid-indicators-vs-formulas.json` | Template artifact filename |
| `gpt-recheck-aibridge-07x-tests-1031` | `py.txt` | `MyTradingSys/research/layer_lab/gpt-g3-pack-audit/probe.py.txt` | File moved, renamed, or omitted from commit |
| `gpt-rederive-tom-vp-return-to-value` | `_gpt-rederive-tom-vp-return-to-value.md` | `MyTradingSys/system/tasks/gpt-rederive-tom-vp-return-to-value.json` | Template artifact filename |
| `live-aid-macro-calendar-cors-snapshot` | `live_aid/ff_calendar_snapshot.js` | `scripts/dev/ff_calendar_snapshot.py` | File moved, renamed, or omitted from commit |
| `opus-fractals-btc-deep-research-1031` | `MyTradingSys/research/fractals_2026-10-31/PRE_REG.md` | `MyTradingSys/research/context_factors_pit_2026-10-16/PRE_REG.md` | File moved, renamed, or omitted from commit |
| `opus-fractals-btc-deep-research-1031` | `MyTradingSys/research/fractals_2026-10-31/REPORT.md` | `MyTradingSys/research/layer_lab/rsi_reclaim_event_table/REPORT.md` | File moved, renamed, or omitted from commit |
| `ship-gate-keep-per-step-failure-output` | `runtime_data/gate_fail_logs` | `MyTradingSys/research/mts_doctor/heal_log.jsonl` | Runtime uncommitted log / data stream |
| `tom-v2-gross-first-dev-ext` | `sim_desk/results/tom-v2-gross-first-dev-ext.json` | `MyTradingSys/system/tasks/tom-v2-gross-first-dev-ext.json` | Uncommitted sim_desk result card |
| `where-is-index-redo` | `role/CLAUDE.md` | `CLAUDE.md` | File moved, renamed, or omitted from commit |
| `wire-binanceliquidationaccumulator-into-` | `runtime_data/liq_events/BTCUSDT.jsonl` | `MyTradingSys/data/klines/BTCUSDT_5m.json` | Runtime uncommitted log / data stream |

---

Noticed: (1) Out of 300 concrete file and repository paths named across the 169 task cards closed since 2026-10-31, 271 paths (90.3%) exist and are tracked in the git tree. (2) Exactly 29 paths (9.7%) are absent from `git ls-files`. (3) The missing paths fall into five distinct categories: (a) Date drift: five GPT formula audit cards cited layer lab reports with date prefix `2026-10-30_`, but the deliverables were committed under `2026-10-31_`. (b) Runtime data: `runtime_data/gate_fail_logs` and `runtime_data/liq_events/BTCUSDT.jsonl` are uncommitted execution/gate caches. (c) Simulator cards: four cards cited pending or uncommitted `sim_desk/results/<card-id>.json` files. (d) Generated web pages: `mts_control_room.html` is generated on demand from `control_room.tpl.html`. (e) Partial path references or subfolder relocations (e.g. `role/CLAUDE.md` vs root `CLAUDE.md`, and fractal `PRE_REG.md` / `REPORT.md` located in sub-study folders `p1_split/`). (4) No critical source code files are missing; all production scripts, backtest layers, and core test suites are present.
