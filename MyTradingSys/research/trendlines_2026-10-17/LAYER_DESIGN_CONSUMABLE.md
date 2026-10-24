# Trend-Line layer: status 2026-10-25 and the design every layer can consume

Written by Session_Planner on the operator's ask (2026-10-25). Design only: no code, no market data read, no outcome read. Labels: SOURCED = quote + file:line; OURS = judgement. Every parameter value stays in `TRENDLINE_CONTRACT.md` (v1); this file adds the consumption surface and the pattern catalogue.

## 1. Where it stands (verified against the repo this turn)
| Piece | State | Evidence |
|---|---|---|
| Source research (Fidelity, StockCharts, IG, TradingView, Krown TRL-04..24) | done, T3 practitioner definitions, no replicated BTC study | `REPORT.md` |
| Contract v1: 43 parameters, each SOURCED or OURS | done | `TRENDLINE_CONTRACT.md`, `FORMULAS.md` s19 |
| Causal detector: swing-pair lines, versioned, states proposed/touched/broken/retested/reclaimed/retired, 22 truncation tests | done | `backtest/layers/trendlines/trendline_core.py`, `test_trendline_core.py` |
| DEV count-only pass (1h/4h/1d) | done: only 3 of 18 cells powered (all 1h: arm A touch, arm A break, arm B break) | `PRE_REG_TRENDLINES.md` s3 |
| Audit 2026-10-18: 3 HIGH + 3 MED gaps | **open**: close-arm dead, pre-birth touches grant eligibility, a broken inner line bans its anchor for outer lines | `AUDIT_2026-10-18.md`; card `trendline-audit-gaps-disposition` (refined, goal over 400 chars, not ready) |
| G3 blind drawing test (40 windows, 2 readers) | **not done**: 0 of 40 marked, no kappa | `g3_pack/` |
| Outcome / event study (does a touch or break move price beyond cost) | **not started**: no verdict, no edge claim | `PRE_REG_TRENDLINES.md` s4 |
| Daily public-chart watch | running to 2026-10-24: 7 tracked posts, 0 recoverable line geometries | `daily/2026-10-24.md` |
| Registered in `layer_index.json`, `wiring_registry.json`, LAYERS.md | **no** (wiring row still says "nothing runs it yet") | audit Gap 6 |
| Live wiring / consumption by other layers | **none** |  |

Answer to "can we draw lines and identify breaks": yes for one pattern only: straight two-anchor swing lines (support/resistance) with touch, break, retest, reclaim. Everything else the operator listed is not built (section 3).

## 2. The consumption contract (one surface for all layers)
Principle: the layer does not trade. It publishes **line facts** per closed bar; other layers choose a role. Same shape as live layers today (`fn(bars) -> list of event dicts {t, event, side, ...}`, `live_layers.py:32`) plus a state snapshot.

**2.1 Snapshot `tl_state(tf, t)`** (one per closed bar, point-in-time, append-only):
- `lines[]`: `id, family, tf, side(support|resistance), transform, price_arm, anchors[(t,price)x2+], eq (L(t) value now), state, age_bars, contact_episodes, slope_atr, slope_log, anchor_volume_ratio, quality` (all fields exist in the detector or contract s2-6).
- `nearest_support`, `nearest_resistance` (contract L11 selector), each with `dist_atr = (close - L(t)) / ATR_b` signed.
- `horizontals[]` (flat pairs, L7) once built; `channel` object once built (section 3).
- `chain`: ordered confirmed pivots and whether highs/lows are rising or falling (trend structure used by CONTEXT).

**2.2 Event `tl_event`** (emitted once, at the bar close that causes it; `t` = that close, `known_at` = availability):
`touch, break, retest, reclaim, failed_break, channel_break, channel_exit_opposite` with `line_id, side, dist_atr, body_range, close_loc, volume_ratio, space_to_next_obstacle_atr`. Entry-safe features only; follow-through and snapback are outcome labels, never features (contract B5).

**2.3 Roles other layers take** (roles from `FABLE_DESIGN.md` s1; assignment is each consumer's pre-registration, not decided here):
| Role | Consumes | Example question (not a rule) |
|---|---|---|
| LOCATION | `dist_atr` to nearest line / horizontal | is a Tom, WT or RSI trigger firing at a line? |
| TRIGGER | `touch`, `break`, `retest`, `reclaim` events | first-return reaction; break then retest |
| CONTEXT / REGIME | `chain`, `slope_atr`, channel state | higher-low chain intact vs broken |
| RISK | line value and ATR | invalidation = close beyond L(t) (SOURCED B1); stop placement is the consumer's, OURS |
| JUDGE | `quality`: contacts, age, spacing, anchor volume | weight a line, never gate on it until it passed its own read |

Rules binding every consumer: use only `known_at <= decision bar`; one TF per line (no cross-TF pooling, F3); a consumer gates a trade only after the line facts passed their own standalone read (same rule as `PROJECT_VISION.md:262`); the layer stays a layer, not a core.

## 3. Pattern catalogue (what the masters teach vs what exists)
| # | Pattern | Causal definition (OURS unless noted) | Status |
|---|---|---|---|
| T1 | Swing-pair line, support/resistance (Fidelity, StockCharts, Krown "two points propose, three touches establish") | contract L1-L11, E1-E8 | built; HIGH gaps open |
| T2 | Break (close beyond line, SOURCED `E:` B1) | contract B1-B4 | built |
| T3 | Retest and role flip (broken support becomes resistance) | contract B6, B8 | built; never counted (audit Gap 4) |
| T4 | Reclaim / failed break (close back through within N bars) | state `reclaimed` exists; `failed_break` event name not defined | partial |
| T5 | Horizontal support/resistance ("most important", `E:167`) | flat pairs L7 are routed aside only | **not built**: no contact or break logic |
| T6 | Parallel channel (StockCharts): main line + parallel through a confirmed opposite pivot; boundary break vs failure to reach opposite side | offset anchor must be confirmed, never use future pivots | **not built** |
| T7 | Acceleration / fan / steeper inner line then outer line | needs audit Gap 3 fix first | **blocked** |
| T8 | Triangle, wedge, compression boundary | two converging lines + apex; Krown S8 compression is a separate Krown layer | **not built** |
| T9 | Volume-anchored line (two heavy-volume turns, ~2x recent bars) | arm V in contract E-section | built; underpowered at every TF |
| T10 | Close-based line (Krown looks at a line chart) | price_arm=close | **dead** (audit Gap 1) |
| T11 | Internal spike-tolerant line (StockCharts) | permitted violations must be declared | **not built**, by design deferred |
| T12 | Angle in degrees | not implemented; chart-scale dependent (`E:153`, KR-L07 BLOCKED) | rejected, slope_atr / slope_log used instead |
| T13 | Higher-timeframe line projected on a lower-TF trigger | `line_tf` vs `trigger_tf` fields (contract F4) | **not built** |

## 4. Build order (proposal; each step is a card, nothing ships without the one before)
1. **Fix v1.1** (audit gaps 1-3, `trendline-audit-gaps-disposition`, split it first: goal text over 400 chars). Gate: truncation tests still pass, new tests fail on old code.
2. **Count-only v2**: `first_touch` vs `all_touches`, `retested`/`reclaimed` counts, expanding slope terciles, pinned kline digests. Gate: PRE_REG v2 with `prereg_gate.py` MDE.
3. **G3 blind marks** (operator + one blind reader) to test whether the mechanical selector draws the "obvious" line. Gate: kappa reported; a low kappa means the selector is not Krown's line and is named so.
4. **Surface v0**: write `tl_state` / `tl_event` as an event table in the layer-lab format so other layers can join it offline, and register the family in `layer_index.json` and `wiring_registry.json`. No live wiring.
5. **Patterns in value order**: T5 horizontals, T4 failed break, T6 channel, then T13 cross-TF. T7 after step 1; T8/T11 only if T1-T6 show any effect.
6. **Outcome study** (`PRE_REG_TRENDLINES.md` s4): line vs placebo, then line + LOCATION from another layer. Only then does a verdict exist; VALIDATION is read once.
7. Live only after a fee-net out-of-sample pass, as an alert tag first (gates nothing).

## 5. Decisions taken (DECISION (OURS), nothing asked)
- The layer publishes facts and events; it never emits orders or a "buy/sell" side. Side is attached to an event only as "support|resistance".
- Pattern order T5 > T4 > T6 > T13 because horizontals and failed breaks reuse the existing state machine and are the sources' most-stressed concepts (`E:167`).
- No pattern is called an edge: the only result so far is counts (3 powered 1h cells).
- Parameter values live in the contract; a new pattern adds a contract section (SOURCED or OURS per row) before code.
