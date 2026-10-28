# MTS DICTIONARY
# Version: 1.0.0 | Date: 2026-09-15
# Authority: this file points. Named authority file defines. Do not duplicate.
# Boot-read: listed in SESSION_MANIFEST.json boot_supplemental.
# Rule 52: before answering any field-level question, read this file first.
# Maintained by: any session that resolves a field-level question. Rule 51 applies.
## HOW TO USE

1. Field question arrives.
2. Look up the field name below.
3. Read the authority file at the named section.
4. If authority is [NO EVIDENCE], open an L-item and stop.

## CANONICAL FIELDS

| Field | Source(s) | Authority | Notes |
|---|---|---|---|
| CVD (cumulative) | DSA snapshot `cvd.value`, `cvd.slope` | data_schema_v1.2.0.md §"DATA BLOCK — cvd (UPDATED)" | Session-anchored 00:00 UTC |
| CVD (recent) | DSA snapshot `cvd.cvd_recent.delta_1h / delta_4h / slope_1h / slope_4h` | data_schema_v1.2.0.md §"cvd_recent object fields" | Recent-window decomposition |
| CVD (CoinGlass) | CoinGlass CVD panel | heatmap_field_map.md §2b | Anchors at leftmost visible bar — never compare numerically to DSA |
| Volume Delta (per-bar) | CoinGlass Volume Delta panel; DSA `trade_flow.net_delta_1m` | heatmap_field_map.md §2b; data_schema_v1.2.0.md §"trade_flow" | DSA field name `net_delta_*` matches CoinGlass "Volume Delta", NOT their "Net Delta" |
| Volume Delta (multi-window) | DSA `trade_flow.net_delta_5m / 15m / 1h` | data_schema_v1.2.0.md §"trade_flow" | Sum of last N bars |
| Net Delta (CoinGlass) | CoinGlass Net Delta panel | heatmap_field_map.md §2b | POSITIONING family, not flow. Best proxy: Net Longs — Net Shorts (T3). Do NOT cross-validate with DSA CVD by sign |
| Open Interest | DSA `open_interest.direction`, `.change_1h_pct` | data_schema_v1.2.0.md §"DATA BLOCK — open_interest"; heatmap_field_map.md §2 | Direction from DSA; magnitude CoinGlass context |
| OI breakdown (retail/whale L/S) | DSA `oi_breakdown.retail.long_short_ratio`, `oi_breakdown.whale.long_short_ratio` | data_schema_v1.2.0.md §"oi_breakdown" | Proxy — account/position ratio, not absolute OI |
| OI breakdown (top trader accounts) | DSA `oi_breakdown.topAccounts.long_short_ratio` | data_schema_v1.2.0.md section "oi_breakdown" | Top trader account ratio (topLongShortAccountRatio). Sibling of retail/whale. No verdict consumer as of 2026-09-19. Gauge by design (matches B021/B022). |
| Funding rate | DSA `funding.current_rate`, `funding.extreme` | data_schema_v1.2.0.md §"funding" | Extreme = crowded side |
| Spot/perp basis | DSA `spot_perp_basis.basis_pct`, `.direction` | data_schema_v1.2.0.md §"spot_perp_basis" | Premium = longs pay |
| Book imbalance | DSA `conditions.book_imbalance`, `order_book_depth.bid_ask_ratio` | data_schema_v1.2.0.md §"order_book_depth" | bid_ask_ratio |
| Volume Profile | DSA `weekly_vp`, `daily_vp`, `post_funding_vp`, `intraday_4h_vp` | data_schema_v1.2.0.md §VP blocks; heatmap_field_map.md §1 | Approximated from 1m OHLCV — may deviate 0.2-0.5% from CoinGlass VPVR |
| VWAP | DSA `vwap.price`, `.slope`, `.bands` | data_schema_v1.2.0.md §"vwap" | HLC3 source, session anchor. Sigma bands are screener invention, NOT Tom |
| Liquidation clusters | DSA `liquidation_clusters.*` | heatmap_field_map.md §2 | DEPRECATED 2026-09-12 — emits 0.0/false unconditionally. Do not use |
| Trade flow (all windows) | DSA `trade_flow.net_delta_1m / 5m / 15m / 1h` | data_schema_v1.2.0.md §"trade_flow (updated 2026-09-11)" | — |
| Order flow speed | DSA `order_flow.trades_ratio`, `.volume_ratio`, `.speed_state` | data_schema_v1.2.0.md §"order_flow" | DSA_TASK_013 |
| State code | MyTradingSys/runtime/state_code.json | state_machine_design_2026-09-11.md §5 | Emitted every 60s by Java child. `signals.cvd_slope` may diverge from snapshot `cvd.slope` (aggTrade vs kline) |

## CROSS-CATEGORY WARNINGS

Three family confusions that recur:

1. **Flow vs Positioning.** CVD and Volume Delta are flow. Net Long/Short and CoinGlass "Net Delta" are positioning. Never cross-validate by sign — they measure different participant behaviors.
2. **Anchor mismatch.** DSA CVD anchors at 00:00 UTC. CoinGlass CVD anchors at leftmost visible bar. Values are not comparable unless anchors match.
3. **Same name, different source.** `cvd.slope` (snapshot, kline-based) vs `signals.cvd_slope` (state_code.json, aggTrade-based). Named differently on purpose. Do not equate.

## MAINTENANCE

When a session resolves a field-level question:
1. Update the authority file with the definition.
2. Add or update the row above.
3. Do not duplicate content — the row links, the authority file defines.
4. If a field has no authority, set the cell to `[NO EVIDENCE]` and open an L-item.

# END

## PLAIN LANGUAGE RULE (added 2026-09-16)

When giving the user an update, or when providing information:
- No internal codes. No letters, no numbers, no hashes, no byte counts
  unless the count itself is the point.
- No shorthand invented in a session. If a thing has a name, use its
  full name.
- Plain sentences first. Tables only when the table saves reading.
- Any term used twice in a session must exist in this dictionary or be
  replaced with a plain phrase.

## CORE TERMS (added 2026-09-16)

These were undefined before this entry.

| term | plain meaning |
|---|---|
| MTS | MyTradingSys, the decision system in this repo |
| DSA | dropped. Use "session" or "session prompt". |

| nrr | net reward to risk. Spell it out in logs and cards. |
| pd | prior day bias. Spell it out in logs and cards. |
| apparatus | dropped in favor of "the runtime loop". |
| L-items | dropped in favor of "open loops". |
| A / B / E | dropped. Name the actual file or folder. |

## END OF ADDITIONS

## LIVE FEED NAMES (added 2026-09-17)

Canonical naming scheme for the live-mode console feed. Applies to
commands (typed by the operator) and blocks (printed by the feed).
A name used in a session must resolve to one of these.

### Commands

| Name | What it does |
|---|---|
| mts-live | Start the live feed. Default cadence 30 seconds. |
| mts-live-fast | Same, 10-second cadence for fast tape. |
| mts-live-stop | Stop the feed cleanly. |
| mts-live-log | Tail the last 40 lines of the feed log. |
| mts-tape | Start the sidecar divergence classifier. |
| mts-dashboard | One-shot dashboard. Reads snapshot, state_code, apparatus_log, compiled math object. |
| mts-dashboard -Watch | Same, loops with Clear-Host every 30s. Ctrl-C to exit. |
| mts-loop | Loop lifecycle dispatcher. Args: start / stop / status. See COMMANDS.md LOOP LIFECYCLE. |

### Blocks (feed output, prefix MTS-)

| Prefix | Meaning |
|---|---|
| MTS-PROC | java / supervisor / wrapper / lock chain |
| MTS-SNAP | latest snapshot header |
| MTS-VWAP | vwap price and bands |
| MTS-SESS | session open/high/low/gap/sweep |
| MTS-COND | conditions block |
| MTS-SET | top setup candidates (up to 3) |
| MTS-STATE | state_code state letter |
| MTS-SIG | state_code signal votes |
| MTS-FRAME | regime label, confidence, cycles in state, entry time |
| MTS-FLOW | cvd, net_delta, oi, funding, basis |
| MTS-HSTOP | compiled hard stops (4 booleans) |
| MTS-PROOF | compiled proof direction |
| MTS-CAND | compiled rank-1 candidate |
| MTS-DELTA | change vs prior snapshot |
| MTS-CYCLES | apparatus verdict string tail |
| MTS-TAPE | sidecar classifier one-liner |
| MTS-SLOW | current_market_state.md tail |

### Modes

| Mode | Meaning |
|---|---|
| MTS-Live | Loop running, feed running. Reads and extends the feed. |
| MTS-Static | Loop not running. Disk reads only. |
| MTS-Replay | Past snapshots. No live data. |

Every live session runs mts-live. Every live session adds at least
one block or field to the feed. Version and changelog live in the
header of scripts/live/mts-watch.ps1.

## VERDICT WORDS (added 2026-09-18)

Written by scripts/core/start-trading-day.ps1 verdict block.

| Word | Meaning |
|---|---|
| WATCH | Setup observed, not at trigger. Proof 3-4, or direction contradicts. |
| WAIT_TRIGGER | Price not at zone. Tier conditional. |
| WAIT_RR | Net reward-to-risk below 2.0, or broken-value override fired. |
| WAIT_PROOF | Proof count below 3. |
| WAIT_FAR | Tier ignore. |
| SETUP_FORMING | All four gates: net_rr >= 2.0, tier trigger_ready, proof >= 5, proofDir != contradiction. |
| SETUP_CONFIRMED | Never written by the verdict function. Downstream check only. |


## CONFIDENCE GRADES (added 2026-09-18)

Set by src/main/java/datafeed/SetupCandidatesBuilder.java. Raw score bucket. No A tier exists.

| Grade | Raw score |
|---|---|
| B | >= 70 |
| C+ | >= 55 |
| C | >= 40 |
| D | < 40 |

## SOURCE TAGS (added 2026-09-19)

Every rule, field, or layer claim carries a source tag. Tag identifies origin.
This is the discovery-phase scheme. Add families; do not rename existing ones.

| Family | Tag | Source authority | Status |
|---|---|---|---|
| Tom core | [TOM-NNN] | raw_transcripts_canonical. 213 ids in TOM_VERBATIM_INDEX.md. | Live |
| Cross-trader rules | [CT-NNN] | Other analyst extracts (Flow Horse, CryptoCred, CrypNuevo). 19 ids in compiled_engine.md. | Live |
| Verdict tracking | [VERDICT-NNN] | Future analyst opinion pipeline (PROJECT_VISION layer 3). | Planned |
| MalkanView RSI | [MALKAN-NNN] | RSI 40-60 layer (PROJECT_VISION layer 1). | Planned |
| Event probability | [PROB-NNN] | Probability distribution layer (PROJECT_VISION layer 2). | Parked |
| Session frame | [SESSION-NNN] | Session-aware frame (PROJECT_VISION layer 4). | Design |
| Our invention | [SCREENER] | None. Must not be presented as sourced. | Live |

Rules:
1. No tag, no claim. If a rule has no source tag, treat it as SCREENER until proven.
2. [SCREENER] is a label of honesty, not a defect. Many fields are gauges by design.
3. Layer tags stay empty until the layer produces its first read. Do not pre-number.
4. Verifier: scripts/tools/verify_rule_citations.ps1 checks [TOM-NNN] resolve. Other families add to the verifier when they go live.
5. Source of layer names: MyTradingSys/PROJECT_VISION.md INTEGRATIONS TRACKED.

Corpus vocabulary note (2026-09-19): Tom speaks flow, absorption, aggression.
Hit counts: aggressive 53, absorption 17, order flow 18, footprint 45, buying 38, selling 33.
Zero or low: aggressor 0, open interest 0, OI 0, cumulative volume delta 0, net long 0, net short 0, taker 4, liquidation 1.
Consequence: OI, positioning, and net-long/short families have no Tom basis. They belong to no current layer.
## FLAGS (added 2026-09-19)

Files in runtime_data\ that a process reads as a stop signal. Distinct paths, distinct readers.

| Flag | Written by | Read by | Meaning |
|---|---|---|---|
| loop_stop.flag | Operator or stop-day.ps1 (mts-loop stop) | start-trading-day.ps1 each cycle top; loop-supervisor.ps1 each 30s check; removed by stop-day.ps1 after lock release | Wrapper exits, state-machine java shut down, lock released, supervisor exits |

| mts-paste | Continuous live snapshot writer. Writes Dumps/LIVE_PASTE.txt every 30s. |
| mts-paste-now | One-shot write and print LIVE_PASTE.txt to console. |
| mts-paste-stop | Stop the mts-paste loop. |

## DIVERGENCE (added 2026-09-22)

Defined per B063 (see MyTradingSys/items/B063_divergence.md). Current state: fragmented. Canonical definition pending B063.

Four detector implementations exist. No single source is authoritative.

| name | source | meaning |
|---|---|---|
| bearish_div | tape-watch.ps1 L59-60 | price up and cumulative volume delta down in one snapshot window. |
| bullish_div | tape-watch.ps1 L59-60 | price down and cumulative volume delta up in one snapshot window. |
| cvdDivergence | SetupScreener.java L54 | boolean input. Producer not shown on disk. |
| threshold rule | divergence_monitor.py | price move over 30 points and cumulative volume delta change over 200 and net delta change over 20 between snapshots at least 10 minutes apart. |

Live alerts do not fire on divergence. No condition-file rule reads any of the four. Reconciliation tracked in B063.

