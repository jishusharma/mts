# INDICATOR MAP: what MTS reads, what each read measures, the role it plays, and which reads go together

Card indicator-map-1108 (from indicator-map-1107), spec `SPEC_INDICATOR_MAP.md` step 2. Documentation only: no rule, threshold,
signal or engine change. Every threshold named here is the source's (SOURCED) or marked OURS and untested. Phase-first rule
(11-06): every read is a CONTEXT column, never a signal alone. Test: `MyTradingSys/tests/test_indicator_map.py`.
DECISION (OURS, 11-08): `USAGE_adx.md` does not exist yet (card tvfav-usage-adx-1107 still ready); the ADX row rests on
FAVORITES_2026-11-07.md and Wilder (SOURCED) only and is marked so. LAYERS.md ids are unchanged.
Regime mix: not applicable (no backtest, no number measured here).

## 1. Dimension table (rows = what is measured)
Sources for the indicator columns: `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md`, `USAGE_squeeze.md`, `USAGE_vfi.md`,
`MyTradingSys/research/tv_favorites_2026-11/FAVORITES_2026-11-07.md`, `MyTradingSys/system/LAYERS.md`. Price, volume, levels and
time are rows although LAYERS.md lists no such families (operator 11-07).

| Dimension | Indicators / engines (path) | Analysts who read it | MTS layer id (LAYERS.md) | TV favourite |
|---|---|---|---|---|
| Price action (candles, wicks, swing structure, trend lines) | `MyTradingSys/backtest/layers/trendlines/`, `MyTradingSys/backtest/layers/wlow_bounce/`, `MyTradingSys/backtest/layers/pitchfork/`, `MyTradingSys/backtest/layers/pizzino/`, `MyTradingSys/backtest/layers/cryptocred/` | Habib, Brando (price action), CryptoCred, Jason and Michael (Pizzino) | pitchfork, pizzino, cryptocred, krown | no |
| Levels and volume profile (VAH/VAL/POC, LVN, balance, session highs/lows) | `MyTradingSys/backtest/layers/session_levels/`, `MyTradingSys/backtest/layers/krown/`; Tom's profile code is Java (`SetupCandidatesBuilder.java`), not under layers/ | Tom (levels, LVN/POC, balance), Fabio, Krown | tom, krown, session_timing | no |
| Volume / participation (effort behind a move) | `MyTradingSys/backtest/layers/vfi/`, `MyTradingSys/backtest/layers/fabio/` (order-flow bars, CVD, escalation), `MyTradingSys/backtest/layers/tick/` | Fabio (order flow), Tom | fabio, volume_candles_ma | VFI yes |
| Momentum (where in the swing) | `MyTradingSys/backtest/layers/wavetrend/`, `MyTradingSys/backtest/layers/rsi/`, `MyTradingSys/backtest/layers/kurisko/` (stochastic rotation), squeeze histogram | Malkan (RSI 40/60), Kurisko, Krown (hidden divergence) | wavetrend, rsi | WaveTrend yes, Squeeze histogram yes |
| Volatility / compression | `MyTradingSys/backtest/layers/squeeze/` (Bollinger inside Keltner); Bollinger live reads under `MyTradingSys/backtest/layers/alerts/` | Tom (balance before the move), the operator's BB range-to-range claim | none own id (guidance family holds BB/LVN) | Squeeze yes |
| Trend strength / direction | `MyTradingSys/backtest/layers/adx/` (Wilder DMI) | Steve / CCU (2d DI cross), CBP calls | none own id | ADX and DI yes |
| Time / cycles / sessions | `MyTradingSys/backtest/layers/session/`, `MyTradingSys/backtest/layers/turn_of_candle/`, `MyTradingSys/backtest/layers/timeframe/`, `MyTradingSys/backtest/layers/session_levels/` | Fabio (sessions), the mts_bible cycle clock | session_timing | no |
| Positioning (funding, OI, whales) | `MyTradingSys/backtest/layers/positioning/` | Coinglass-style reads, FlowHorse | positioning | no |
| Calls (posted trade calls) | none under layers/ (scored in `MyTradingSys/research/analysts/`) | Qriptal, RLinda, Bennett, Crypto Chase, Roman | callers | no |

## 1b. Engine inventory (every directory under backtest/layers/ has one row; the test enforces it)
Role: C = context (phase), S = setup (where), K = confirmation (go/no-go), I = infrastructure (measures nothing itself).

| Engine path | Dimension | Role | Status in one phrase |
|---|---|---|---|
| `MyTradingSys/backtest/layers/adx/` | trend strength | C | engine built 11-07; TradingView cross-check pending |
| `MyTradingSys/backtest/layers/alerts/` | live emitters (Bollinger top reversal, RSI divergence, candle close, levels confluence) | S, K | live feed of other layers' reads |
| `MyTradingSys/backtest/layers/consensus/` | cross-layer agreement writer | I | writes consensus rows; not a measure |
| `MyTradingSys/backtest/layers/cryptocred/` | price action (setups, structure, retest, HTF count) | S | setups from CryptoCred; no edge claimed |
| `MyTradingSys/backtest/layers/fabio/` | volume / order flow | K | v3 OOS FAIL 10-04; being redefined (LAYERS.md) |
| `MyTradingSys/backtest/layers/krown/` | levels, zones, candles, averages | S | TA 101 events and fire counts |
| `MyTradingSys/backtest/layers/kurisko/` | momentum (stochastic quad rotation) | C | golden-file tested |
| `MyTradingSys/backtest/layers/pitchfork/` | price action (median-line structure) | S | detector with review fixes |
| `MyTradingSys/backtest/layers/pizzino/` | price action (bar count, nested swing states) | C | indicators and spec tests |
| `MyTradingSys/backtest/layers/positioning/` | positioning | C | funding/CVD fade; trade-cost helper |
| `MyTradingSys/backtest/layers/promotion/` | promotion registry and gate | I | decides what may trade; not a measure |
| `MyTradingSys/backtest/layers/rsi/` | momentum | C, K | Malkan 40/60, divergence, reclaim, MA events |
| `MyTradingSys/backtest/layers/session/` | time (session momentum) | C | Shen-Urquhart-Wang adaptation; 24/7 session start is a parameter (OURS) |
| `MyTradingSys/backtest/layers/session_levels/` | levels and time (prev-day, Asia, EU extremes) | S | observation layer, failed first break |
| `MyTradingSys/backtest/layers/squeeze/` | volatility / compression | C | context column for W2 and the range detector |
| `MyTradingSys/backtest/layers/tick/` | volume / tick-sourced delta extremes | K | flag logic and tiers |
| `MyTradingSys/backtest/layers/timeframe/` | time (resampling registry) | I | closed bars only |
| `MyTradingSys/backtest/layers/trendlines/` | price action (causal trend lines) | S | contract v1, FORMULAS s19 |
| `MyTradingSys/backtest/layers/turn_of_candle/` | time (minute-of-quarter stats) | C | statistics only |
| `MyTradingSys/backtest/layers/vfi/` | volume / participation | K | M5 volume column |
| `MyTradingSys/backtest/layers/wavetrend/` | momentum | C | parity contract 10-17; crosses come before a bounce, no edge after (census 11-04) |
| `MyTradingSys/backtest/layers/wlow_bounce/` | price action (W-low bounce) | S | detector and status |

## 2. Role table per dimension (context -> setup -> confirmation) and the gate column each feeds
Gate names are the phase-first columns in FAVORITES_2026-11-07.md: CENSUS M4 (2d DI-cross cascade), wick W2, volume M5,
scenario_ledger (scored A/B maps). Role assignments are OURS (proposed in FAVORITES), untested unless stated.

| Dimension | Context (phase) | Setup (where) | Confirmation (go / no-go) | Gate column fed |
|---|---|---|---|---|
| Trend strength (ADX/DI) | ADX bucket at a 2d DI cross: below 20 no trend, 20-40 trend, above 40 stretched (Wilder 20/25 SOURCED; 40 OURS) | none | none | CENSUS M4 |
| Momentum (WaveTrend, RSI) | WT OB/OS zone (60/53, -60/-53, LazyBear SOURCED) as where-in-the-swing | none | RSI divergence at a level (Krown/Malkan, tested separately) | CENSUS cascade; live-aid page card |
| Volatility (Squeeze) | squeeze ON for 6 or more bars = stored energy (Carter, SOURCED); OFF = expansion on | squeeze ON at a Tom/Fabio level = wait for release (OURS) | momentum sign at release gives direction (Carter, SOURCED; crypto use OURS) | wick W2, range detector |
| Volume / participation (VFI, order flow) | VFI sign: above 0 net accumulation (Katsanos, SOURCED) | none | VFI into a level test: falling = no buyer effort, divergence at a sweep = bought back (OURS) | volume M5 |
| Levels / profile | balance vs trend day (Tom) | VAH/VAL/POC/LVN, prior-day and session extremes | acceptance (2x30m closes) vs rejection | scenario_ledger |
| Price action | swing structure, trend lines | wick, W-low, pitchfork, CryptoCred retest | rejection speed and volume ratio (wick note) | wick W2 |
| Time | session and cycle clock | session opens, turn of candle | none measured | scenario_ledger |

## 3. Connected sets (ordered read per setup family; read order is OURS, nothing here is a tested rule)
Each set is a reading checklist. "If they disagree" says what a session reports; it does not block or place an order.

| Setup family | 1 Context | 2 Setup | 3 Confirmation | If they disagree |
|---|---|---|---|---|
| Cycle-bottom long | 2d ADX/DI bucket + WT zone (oversold); mts_bible cycle clock | Tom/Krown level or trend line under price | VFI turning up and volume ratio on the reclaim | report "context only", no entry; log the disagreement column |
| Session trade | session momentum and ADX of the higher frame | session extreme or failed first break (`MyTradingSys/backtest/layers/session_levels/`) | VFI sign and order-flow bars (Fabio) | skip the session; note which slot was missing |
| Level test | squeeze state (ON = balance, OFF = move on) | Tom VAL/POC/LVN or analyst cluster | VFI into the test, wick rejection speed | treat as untested level |
| Range to range | squeeze ON for multiple bars (compression) | Bollinger band edges (operator's BB range-to-range claim) | release direction from squeeze momentum | stay flat until release |

## 4. Gaps
- Price, volume, levels and time have no own LAYERS.md id; they sit inside tom, fabio, krown and session_timing.
- Trend strength and volatility have an engine but no LAYERS.md id (adx, squeeze).
- ADX has no `USAGE_adx.md` (card tvfav-usage-adx-1107 not done) and no TradingView cross-check yet.
- Callers (analysts' posted calls) have no engine under layers/; they are scored only in `MyTradingSys/research/analysts/`.
- Consumers: squeeze and vfi are declared in `MyTradingSys/system/wiring_registry.json` as WIRE (built, no live consumer yet). Per
  the wiring_registry rule a producer needs a consumer; the first connected set that reads them is the consumer, and none is wired.
- No engine reads the mts_bible cycle clock or Tom's profile in Python; both are prose or Java.
- Time has no confirmation-role engine.

## 5. Mechanism
No sentence in this map states as a rule that one read verifies another: sections 2 and 3 are read-order proposals (OURS,
untested). When a connected set is promoted to a testnet-forward test, its claim becomes a `scenario_ledger.py add` row the same
ship (feedback 11-04). The test fails if this file claims a mechanical verification outside quoted sources.
