# Eagle_Eyes session map, 10-29 to 10-30

Every topic the operator raised in this Eagle_Eyes session, with where it now lives. Nothing here is a call: the probabilities are measured base rates (fee-free, descriptive) unless marked otherwise.

## 1. The agreed order of work (operator 10-30)

Decisions `d-map-before-backtest`, `d-setup-review-before-backtest` and `d-storybook-v2` in OPERATOR_DECISIONS.md.

| Step | What | Card | Waits on |
|---|---|---|---|
| 1 | The book he learns from: storybook v2 (regime, timeframe ladder, proof checklist, BB chapter, measured boxes) | `storybook-v2-living-book` | none |
| 2 | Review every catalogued setup with him (16 Tom, 7 Fabio); he picks 2-3 | `setup-review-with-operator` | none |
| 3 | Descriptive map: BB state x prior candle x regime x timeframe close | `bb-state-regime-tf-map` | none |
| 4 | Pre-reg and fee-net DEV test of his picks, starting with his BB-mid candle rule | `bb-mid-reject-candle-rule-test` | steps 2 and 3 |

Steps 1-3 can run at the same time. Step 4 is the first backtest under the new order.

## 2. Topic by topic

| Topic (operator ask) | Where it lives | State |
|---|---|---|
| Pitchfork: prepare the layer; his method is copy-paste of the same fork | `d-pitchfork-keep-and-prepare`; cards `pitchfork-operator-charts-prep` (waits for his shots), `pitchfork-live-4h-bars-too-few` (JIS-NB, Lab_Guy review first); EAGLE_EYES_BIBLE.md "Level prep and Pitchfork" | live switch inert; no orders from PF |
| Why the 78.3k low formed; bounce strength; is the buying real | `drop_bounce_2026-10-29/RESULT.md` (n=813: break 44%, hold 45%; bounce buying made no difference) | done |
| BB odds: fall through, come back, test the low, sideways | same RESULT.md (next hour: 5% below the lower band, 43% lower half, 52% upper half) | done |
| Fractals like the green box | `drop_bounce_2026-10-29/fractal.py` (n=511, coin flip on direction, move size about ±0.8%) | done |
| The bounce failed back near the low | `followup.py` (n=116: break in 1h 16%, in 4h 43%; selling into the fade did not raise it) | done |
| Footprint view of the rally; alignments and misalignments | CARD_SPECS.md U1-U4 (absorption, OI, wicks, 5m vs 1m); card `level-approach-prep` | open ledger rows |
| Everything Fabio and friends say on CVD | `fabio_cvd_2026-10-30/CVD_CONCEPTS.md` (F-CVD1-16, 24 quotes verified) | done |
| More videos with ROI | CVD_CONCEPTS.md section 3c (5 ranked); card `fabervaale-cvd-sweep` (DSA-NUC, Gemini low) | waits for the NUC run |
| Test Fabio's CVD claims on BTC | card `cvd-coil-and-absorption-u7-u8` (U7, U8) | ready |
| Previous-close break idea | `prev_close_break_2026-10-29/RESULT.md`: every-candle version loses fee-net on 5m/15m/1h (negative baseline) | done |
| His real rule: green candle at the BB mid, short on a cross of its close, stop prior high, TP with clearance | same RESULT.md (walked on shot 8faf2cac14be); card `bb-mid-reject-candle-rule-test` | waits on steps 2-3 |
| "Decide scenarios before backtesting" (candle states, BB path, phase, timeframe) | `d-map-before-backtest`; card `bb-state-regime-tf-map` | ready |
| "Setups were never extracted from Tom or reviewed" | `d-setup-review-before-backtest`: the extraction exists (SETUP_CATALOG.md), his review never happened; card `setup-review-with-operator` | ready |
| "Is the storybook written for me?" | `d-storybook-v2`; card `storybook-v2-living-book`; old deck https://claude.ai/artifact/2DXWotLraL8te3xNqo4hWV | ready |
| Keep refining probabilities from screenshots | SCENARIO_LEDGER.md (now 3 maps scored, 2 of 3 right); shots classified with shot.py | ongoing, every Eagle_Eyes reply |
| Missed click-boxes | `d-eagle-eyes-missed-boxes-defaults`; no more click-boxes | done |

## 3. Peer asks (Malkan RSI divergence session)

| Ask | State |
|---|---|
| Revert or fix the CI-red commit | re-landed with the look-ahead allowlist |
| Raw cards pass `tasks.py check` | done (7 cards READY) |
| Level-approach-prep card | done |
| Unknowns as ledger rows | CARD_SPECS.md U1-U6, CVD_CONCEPTS.md U7-U8 |
| Absorption shots 451c4523247f, bca9025ce84f, 45dbcb33e4ca | answered in chat; measuring is U1 in `level-approach-prep` |

## 4. Not for builders

- Arming orders from Pitchfork (live-tree change): operator only.
- Any mainnet or money step: operator only.
