# Do Tom and Fabio guide each other's trade? (code audit 2026-10-12, origin/fast-track 830c1d5)

## Answer: NO. They are wired to run side by side, never to read or gate each other.

| Question | Evidence |
|---|---|
| Does Fabio read Tom state? | No. Fabio v3 may import only stdlib, orderflow_bars and its own siblings; "nothing from execution, layers.alerts, Tom/core" is a test: `tests/test_b127_fabio_v3_isolation.py:1-8`. `htf_context_live.py:3` says "nothing here gates Tom". |
| Does Tom read Fabio state? | No. Tom core is Java (`src/main/java/datafeed/SetupCandidatesBuilder.java`, `MarketDataSnapshot.java`) and writes `runtime_data/last_alert.json`; no Java file reads `runtime/alerts/*.jsonl`. The only Python that touches Tom's card is auto_trader and the consensus hook. |
| Is there a confluence / gating module? | `backtest/layers/consensus/` exists but is observation only: "never gates, vetoes or delays a core" (`consensus/hook.py:8-9`, `consensus/README.md:4`). It writes one row per poll when either core fired, with both sides' entry/stop/target. Nothing reads that row back. |
| Architecture rule | `backtest/layers/test_layer_boundaries.py:3-9`: layers are alert-only, "Tom core is never filtered by layers". A Fabio-gates-Tom wire contradicts this test and needs an operator ruling first. |
| Backtest | `backtest/tom_bt.py:280-290` `fabio_tag` tags a Tom signal when a same-side Fabio event closed within n bars: "DESCRIPTIVE ONLY ... Never a filter". Used by `tom_bt_run.py:63-80` with frozen Fabio params. |
| Live runner, both fire | `execution/auto_trader.py:719-775` `cycle`: Tom signal first, then layer alerts in arrival order. Each source maps to an account (`auto_trader.py:85` `{"layer:fabio:": "fabio"}`); a slot is busy only per account (`:753-757`). So a Tom trade and a Fabio trade can be open at once on different testnet accounts, same side or opposite sides, with no awareness of each other. If the fabio account file is missing, both share the default slot and the second is logged `skipped_busy`. |

## Context indicators: computed vs wired into Tom / Fabio

| Indicator | Where computed | In Tom? | In Fabio? |
|---|---|---|---|
| Bollinger bands | nowhere in code (research docs only) | no | no |
| RSI(14), 40 level events | `layers/alerts/live_layers.py:146-166`, `layers/rsi/` | no (not in Java) | no, separate layer ("rsi") |
| RSI 40-60 regime | not computed; only the 40 level and malkan bull/bear (`live_runner_cli.py:292-293`) | no | no |
| CVD / delta | Java snapshot `cvd_slope`; Python `fabio_cvd_absorption.py`, `orderflow_bars.py` | yes (`SetupCandidatesBuilder.java:240-250` trend healthy/unhealthy) | yes (delta in v3 signals, `signals.py:216,237`) |
| Open interest | `MarketDataSnapshot.java:342,405` `oi_trend`, `oi_breakdown`; `runtime/oi_live/oi_recorder.py`; `quad_classify.py` price x CVD x OI | snapshot only, not in a Tom gate found | no |
| Long/short ratio | `MarketDataSnapshot.java:1541-1562` retail/whale/top ratios | snapshot only | no |
| Funding | `MarketDataSnapshot.java:256-259,341,384`; `live_layers.py:79-100` funding layer | `funding_extreme` condition only | no (own "positioning" layer) |
| VWAP + bands | `MarketDataSnapshot.java`, `SetupCandidatesBuilder.java:240,291-298,432` | yes (zones, pullback entries) | no |
| Volume profile POC/VAH/VAL, naked POC | Java `buildVp`; `NakedPocTracker.java`; Fabio `signals.py:98-170` | yes (zones, targets TOM-018) | yes (S1 balance, value area, premium/discount `signals.py:371`) |
| LVN / HVN | Java `MarketDataSnapshot.java:654-673` (3 each, daily VP only); Fabio `signals.py:158-176` | HVN as targets (`SetupCandidatesBuilder.java:143-145`); LVN not used | LVN for model A (`select_lvn`) |
| Squeeze / ATR compression | ATR in Fabio `signals.py:91`; `quad_classify.py` squeeze is a CVD/OI label, not a vol squeeze | no | ATR scales balance only |
| Multi-timeframe | Tom: tfRank zones (`SetupCandidatesBuilder.java:23,193`); Fabio: `htf_context_live.py` (4H balance, separate layer) | yes | no (not wired) |

## Gap list (short)
1. No Tom<->Fabio signal path: no shared state, no gate, no sizing link; consensus rows are never read.
2. Tom core may not be filtered by layers (test rule), so cross-guidance needs an explicit operator ruling.
3. No Bollinger bands, no RSI 40-60 regime, no vol squeeze/ATR-compression state anywhere.
4. OI and long/short ratio exist in the live snapshot but nothing tests them as a direction or sizing filter.
5. LVN is computed (Java daily VP, Fabio v3) but Tom uses only HVNs; no "fast move through LVN / void" detector for either layer.
6. Same-side / opposite-side simultaneous Tom + Fabio trades are not tracked as a pair, so there is no data on whether agreement helps.
