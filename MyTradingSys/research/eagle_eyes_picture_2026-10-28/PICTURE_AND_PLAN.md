# MTS picture and plan of actions (Eagle_Eyes, 2026-10-28)

Author: Eagle_Eyes (observer). Source of the ask: `MyTradingSys/system/EAGLE_EYES_BIBLE.md` (operator, verbatim). Tags: SOURCED = read in a file or on a page this session; OURS = my reading; NOT_IN_DATA = not seen.
This is a first draft for an independent review (an Opus session). Every claim below is to be re-checked against the repo and corrected in place.

## 1. What MTS is for (OURS, from CLAUDE.md, STATUS and the operator's words)

- Goal: a first mainnet BTC trade on whatever edge exists, even the simplest one. Today it is testnet only (Deribit BTC-PERPETUAL, SOURCED CLAUDE.md).
- Method: layers (indicators and flow series), fee-net out-of-sample results decide what trades; no fixed core (SOURCED CLAUDE.md).
- The operator's own live practice: take a bias, build a position, trade the setups Tom describes, read charts by screenshot (SOURCED operator 2026-10-28).

## 2. What is being built, and where the value is

| Part | State | Value |
|---|---|---|
| Simulator / desk (backtest, scenario replay) | running; E2 Krown S8 4h INCONCLUSIVE (SOURCED OPERATOR_DECISIONS d-krown-s8-e2-desk-crosscheck-go) | tests setups before money; shows what is not an edge |
| Layers (RSI divergence, WaveTrend, CVD, net delta, OI, top-trader ratios, liquidation) | WaveTrend card T061; flow concepts and CoinGlass usage research shipped today (`research/flow_layers_concepts_2026-10-28`, `research/coinglass_usage_2026-10-28`) | the ingredients; none has a validated edge |
| Live engine + alerts on desktop-f7iu69n | state on that host is NOT_IN_DATA here; mirror copy shows last alert #508 of 2026-10-20 15:05Z: NO_TRADE, no candidates (SOURCED `runtime_data/_mirror/.../last_alert.json`) | the loop that should tell the operator when a setup is live |
| Eagle_Eyes live reads | log in `research/live_reads`; screenshots classified | cross-check of engine against the chart; catches what the engine misses |
| Live dashboard v1 (WaveTrend strip, confluence panels, R01 to R10) | being built by session dash-designer | one screen for the 1m live read |
| CBP (analyst transcripts and views) | run needed for every analyst; status per item in the notes folder | bias context for the operator |

## 3. Alerts: what is known

- The alert popup is a Windows form (`scripts/core/show-alert.ps1`): fixed tool window 600x680, position cascaded by alert number modulo 6, not top-most, so it sits behind other windows and stacks up (SOURCED file read). This is the likely cause of the pile-up the operator reports (OURS).
- The only alert content seen (#508) is a state-change NO_TRADE card. Whether Tom setups fire as alerts today is NOT_IN_DATA from this host; the operator reports he sees none. T067 (alert improvements: event alerts, absorption at marked zones, "buy detection") has been OPEN since 2026-10-05 (SOURCED `items/T067_alert_improvements.md`); I found no sign it shipped (OURS, not exhaustively checked).
- Testnet trades fired by the engine (`execution/auto_trades.jsonl`): NOT_IN_DATA from this host. The operator's own Deribit log for 2026-10-28 (08:46 to 12:14Z): one short, 8,280 contracts at about 81,414, closed in three buys, net +0.00041 BTC after fees and funding (OURS sum of the log).

## 4. What is missing on the way to mainnet (OURS; each item is to be checked)

| # | Gap | Why it blocks |
|---|---|---|
| G1 | No validated edge: heatmap, OI, ratios, funding have "No validated evidence found"; E2 is INCONCLUSIVE | nothing to trade on mainnet yet |
| G2 | Operator's setups are not visible as live alerts; alert UI loses alerts behind windows | the bias-and-position method cannot be measured or supported live |
| G3 | The operator's discretionary testnet trades are not journaled with the layer state at entry and exit | no data to turn his method into rules; a Deribit log alone has no context |
| G4 | Series history missing: Binance keeps 30 days of ratio history; liquidation tape has no recorder host; legends unverified because Binance fapi times out from this host | layers cannot be studied or replayed |
| G5 | Trunk CI is RED, nothing deploys | no alert fix or dashboard can go live |
| G6 | C: drive about 7 GB free on the desktop | recorders and shot store at risk |

## 5. Plan of actions (OURS, for review)

1. Make alerts visible first: read what the live host fired in the last 7 days (alert counter, `live_alert_state.json`, `auto_trades.jsonl`) through its owner; list alert types and counts; report in one table.
2. Alert redesign card: study how current alert systems are designed (single notification center or toast stack with dedupe, severity, snooze, pin, one-click close, no window per alert, works while the IDE is focused), then spec a replacement for the cascading popup; the live path stays single-owner (staging and restart by the desktop supervisor).
3. Trade journal for testnet: each trade stored with time, side, size, the layer readings at entry and exit (from the dashboard feed) and the operator's stated reason; account data stays out of the public repo.
4. Simplest-edge path: take the operator's repeated setups (bias, confluence of top-trader ratios, OI, CVD, heatmap level), turn each into a rule written in plain words, run it in the simulator on DEV data only, keep what is fee-net positive out of sample.
5. Data capture: log top-trader and global ratios, liquidation tape and OI ourselves; name the recorder host.
6. Fix trunk CI red first so any of the above can deploy.
7. Eagle_Eyes keeps reading live shots and logging mismatches; the new CoinGlass definitions (Whale Index, Net Delta, Active Buy/Sell) are read from the Legend tooltips.

## 6. Open points for the operator

- Which Tom setups should fire as alerts first (his top two or three).
- Where the alerts should appear (screen corner, second monitor, phone).
- His invalidation levels for the live bias trades.
