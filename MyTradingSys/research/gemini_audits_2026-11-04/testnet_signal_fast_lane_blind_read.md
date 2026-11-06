FOUND=16 DIFF=0 NOT_IN_DATA=2  (18 rows; source DESIGN.md read in full, checked against repo files on this machine)

Reader: Claude Builder (card labelled Gemini). Model output is not a source; every FOUND row quotes the line it matched.

| # | Fact in DESIGN.md | Matched source line | Result |
|---|---|---|---|
| 1 | runner files `backtest/layers/alerts/live_runner_cli.py` + `live_runner_core.py` exist | both in MyTradingSys/backtest/layers/alerts/ | FOUND |
| 2 | runner alert-only, public klines, no execution imports | live_runner_cli.py l.4 "fetches closed Binance klines over public REST, wires two registered layers"; imports l.9-20 contain no execution module; no key/secret strings in either file | FOUND |
| 3 | `rsi_events` is a layer event function | rsi/rsi_events.py l.19 `def rsi_events(rsi, ts, level, tolerance, ...)` | FOUND |
| 4 | `cvd_absorption_events` is a layer event function | fabio/fabio_cvd_absorption.py l.45 `def cvd_absorption_events(bars, ...)` | FOUND |
| 5 | runner has a registry of layers (core logic unchanged by a new concept) | live_runner_core.py l.58 required_keys {"layer","sub","tf","fn","params_id"} | FOUND |
| 6 | `--concept` flag exists | no such flag in live_runner_cli.py; design lists it as later card (a) | NOT_IN_DATA (proposed, correctly marked OURS) |
| 7 | `alerts/live_validation.py` is the verdict store / doubts | live_validation.py l.1 "per-category verdict store, doubts list, signal-to-chart hook" | FOUND |
| 8 | category = symbol, tf, type, side | live_validation.py l.4 "(symbol, tf, type regular|hidden, side bull|bear)" | FOUND |
| 9 | fail closed to DOUBT/PENDING | live_validation.py l.9 "all end as DOUBT / PENDING, never as a verdict" | FOUND |
| 10 | decision `d-live-validation` dated 2026-10-28: confirm once per category, look-alikes inherit, DOUBTS, no auto-verdict | OPERATOR_DECISIONS.md l.1309 "decided 2026-10-28"; l.1311 decision text same wording | FOUND |
| 11 | decision `d-cotrade-testnet-carveout` dated 2026-10-31: testnet, by name, only via cotrade.py, journaled, never mainnet | OPERATOR_DECISIONS.md l.1608; MOVED_RULES.md l.16 exception wording | FOUND |
| 12 | cotrade: stop mandatory, caps, HALT check | cotrade.py l.11 "a stop is mandatory", l.12 "no HALT / HALT_DAILY_LOSS file", l.13 "risk_guard cap, loss at stop <= $500 (OURS)" | FOUND |
| 13 | cotrade testnet only, journaled; `place --said ... --stop` | cotrade.py l.10, l.6, l.21 usage line | FOUND |
| 14 | no scheduler (SCHEDULING_POLICY) | system/SCHEDULING_POLICY.md l.3 "no more schedulers in any device" | FOUND |
| 15 | `.mts_live` live tree not used by runner / deploy only via runbook | MOVED_RULES.md l.16 "changes only by a manual or coordinator-run deploy" | FOUND |
| 16 | `lookahead_lint.py --new` | scripts/dev/lookahead_lint.py l.4 and l.354 `--new` | FOUND |
| 17 | trailing `1m | 5m` legend, operator ask 11-02 | research/eagle_eyes_picture_2026-10-28/LIVE_AID_REQUIREMENTS.md l.20 "(ask 11-02)"; EAGLE_EYES_BIBLE.md l.157 | FOUND |
| 18 | "Never drawn: entry/size/exit calls (Eagle_Eyes rule)" | no line in eagle_eyes.md / EAGLE_EYES_BIBLE.md found by grep for that rule | NOT_IN_DATA |

Count: FOUND 16 (rows 1-5, 7-17), NOT_IN_DATA 2 (rows 6, 18), DIFF 0.
