# Fable confluence map: 13 layer families x (role, inputs, outputs, overlaps)

Card `fable-confluence-integration-map`. One map, no discards: what each family outputs
(signal / filter / veto / sizing), what it needs as input, and which families it overlaps —
so the later confluence review starts from the map. No verdicts here; nothing keeps,
drops, demotes or parks a layer.

Sources (every non-UNKNOWN cell cites one of these):
- `li:<id>` = MyTradingSys/system/layer_index.json, families.<id> (plain / status / layers / path notes).
- `LAYERS:<id>` = MyTradingSys/system/LAYERS.md, family section <id>.
- `PRE:§n` = MyTradingSys/research/krown_audit_2026-10-22/PRE_REG_CONFLUENCE.md section n.
- Role words are the confluence pre-reg role set: trend > volatility > structure > momentum
  (PRE:§8 parameter row "Role order trend > volatility > structure > momentum", SOURCED).
- No source names a runtime **veto** for any family; "do not wire cross-guidance"
  (li:guidance status) is a kill of a wiring idea, not a veto output.

| Family | Role | Inputs | Outputs | Overlaps |
|---|---|---|---|---|
| tom | structure (order flow) — li:tom plain "oversized push into thin volume... real order flow" | footprint bars on JIS-NUC from 2024-12 — li:tom path.inputs | signal: flag-gated BTC detector, entry paths A1-A3 + stop — LAYERS:tom card `tom-btc-encode`; DAX smoke only — li:tom path.built | fabio (order flow) — li:fabio plain; guidance (its triggers) — li:guidance plain; CVD rows shared — LAYERS:fabio `PRICE-CVD-DIV-1M5M` |
| fabio | structure (order flow) — li:fabio plain "order-flow pressure and absorption at the New York open" | BTC footprint and aggressor side (orderflow_bars.py) — li:fabio path.inputs | signal: v3 escalation / cvd_absorption / volume_fvg / of variants; all L1 no-edge, OOS FAIL, no live integration — li:fabio status + layers | tom (order flow) — li:tom plain; guidance filters stacked on its triggers — li:guidance plain |
| guidance | filter (BB, LVN, regime) — li:guidance plain | Tom/Fabio trigger events + BB/LVN/regime levels — li:guidance plain + code matrix_q33.py | filter: 336 cells, 0 survivors, "do not wire cross-guidance" (Q34 skipped) — li:guidance status + path.dev | tom, fabio (their triggers are its inputs) — li:guidance plain |
| rsi | momentum / regime (RSI 40/60) — li:rsi plain + PRE:§8 role words | OHLC; RSI 40/60 levels, multi-TF; Kurisko quad rotation + stoch — li:rsi path.inputs + code | filter: 40/60 tolerance study done; signal: divergence, no edge any TF — li:rsi status + layers | krown ("RSI 40/60 zones as confirmation") — li:krown plain; malkan_rsi, rsi_reclaim, rsi_divergence_1h/4h joined in the pre-reg pool — PRE:§3.4 |
| cryptocred | structure (price-structure swings) — li:cryptocred plain "S/R flip, failed market-structure break, fib pullback" | price only: klines — li:cryptocred path.inputs | signal: 15m brackets FAIL after trade-through rerun; daily/4h untested — li:cryptocred status + path.dev | BIGTRADE-EXIT and FIRES-B1 rows shared with fabio, rsi, session_timing, volume_candles_ma — LAYERS:cryptocred backtest lines |
| positioning | UNKNOWN (no role word in li:positioning plain; funding/OI/whale are data sources, not role words) | Binance funding, OI, long/short ratios 2020-09.. (gap G5, being fetched) — li:positioning path.inputs | filter: funding_cvd_fade FAIL closed; oi_delta descriptive only — li:positioning layers + status | CVD component overlaps tom/fabio order flow — li:positioning layer funding_cvd_fade + LAYERS:fabio `PRICE-CVD-DIV-1M5M` "CVD adds nothing over price alone" |
| session_timing | momentum ("session momentum") — li:session_timing plain | price + session clock/levels — li:session_timing plain + path.inputs | signal: session_momentum FAIL, turn_of_candle no edge but still 79 % of testnet trades, session_levels T087 FAIL — li:session_timing status + path.testnet; sizing study LC-SIZING-QUICK, exploratory negative — LAYERS:session_timing backtest lines | session_momentum joined in the pre-reg pool (5m, 48-bar horizon) — PRE:§3.4 |
| volume_candles_ma | UNKNOWN (li:volume_candles_ma plain names content only; "intensity, not direction" is a result, not a role word — LAYERS:volume_candles_ma `VOLUME` line) | OHLCV: volume, candle closes, MA inputs, big-trade fires — li:volume_candles_ma plain + path.inputs | signal + filter: volume flags, candle patterns, daily MA, bigtrade fires; no validated edge, HOLDOUT sealed — li:volume_candles_ma status | krown ("volume at 2x its average", "four candle patterns") — li:krown plain; bigtrade rows shared — LAYERS:volume_candles_ma backtest lines |
| live_engine | infra, no strategy role ("infrastructure, not a strategy") — li:live_engine kind + plain | live market feeds, screenshots, executor state — li:live_engine spec (live_session_protocol, screenshot_intake) | feeds every layer: execution + live-market reads; testnet HALT since 2026-10-12 — li:live_engine plain + status | all 12 strategy families (its plain says "feeds every layer") — li:live_engine |
| callers | UNKNOWN (posted calls carry entry/stop/targets but no role word — li:callers plain) | posted call transcripts (Qriptal 22 staged) + Binance klines for scoring — li:callers path.inputs | signal: posted calls; filter: kline scorecard scores the record before anything is traded — li:callers status + plain | scores calls on the same klines every backtest uses — li:callers path.inputs |
| krown | trend + volatility + structure + momentum — li:krown plain ("trend state", "volatility (BBWP) regime", "levels", "RSI 40/60 zones") + PRE:§8 role words | OHLCV 1d/1w only (Binance spot krown_daily; basis note F17) — li:krown path.inputs + PRE:§1 | context/filter: D1/D2/D3 context factors — PRE:§1/§3; signal: T2 compression breakout, T4 sweep-reclaim — PRE:§3.5/§3.6; sizing: vol-target arm — PRE:§3.2; "a close, not a wick, is the verdict" — li:krown plain | rsi (RSI 40/60 confirmation) — li:krown plain; volume_candles_ma (volume, candles) — li:krown plain; its context is pooled over the 13 joined layers incl. rsi, tom/fabio, session_momentum, volume, candle — PRE:§3.4 |
| wavetrend | UNKNOWN (li:wavetrend plain says "causal BTC context layer"; oscillator states, no role word) | BTCUSDT USD-M DEV bars 2022-01-01..2024-06-30 — li:wavetrend path.inputs | signal: oscillator states W01-W09; 4 FAIL, 5 INCONCLUSIVE, W07/W08 invalid C1; no validated edge or live integration — li:wavetrend status | UNKNOWN (no source names an overlap) |
| pitchfork | structure (channels/breakout) — li:pitchfork plain "dynamic equilibrium channels... median line reach (80% rule) and Hagopian failure breakout" | 4H/1D klines on BTC — li:pitchfork path.inputs | signal: pitchfork_swing detector built with tests; event study planned — li:pitchfork status + path.built | UNKNOWN (no source names an overlap; structure zones in subject with krown/cryptocred only) |

Overlaps at a glance (each pair above is what a later confluence review must deduplicate):
- Order flow: tom <-> fabio, both feed guidance; CVD rows shared by fabio/positioning
  (li:fabio, li:positioning, LAYERS:fabio `PRICE-CVD-DIV-1M5M`).
- RSI 40/60: rsi family is the implementer; krown uses it as confirmation (li:rsi, li:krown plain).
- Volume + candle patterns: volume_candles_ma and krown (li:krown plain, li:volume_candles_ma plain).
- Pre-reg pool already joins: bb_top_reversal, malkan_rsi, rsi_reclaim, cc_msb, fabio_escalation,
  session_momentum, rsi_divergence_1h/4h, candle_pattern_1h/4h, volume_1h/4h, wlow_bounce
  (PRE:§3.4, s2 Holm family) — the concrete dedup list for that read.
- Infrastructure: live_engine feeds all families; callers scores against the same klines
  (li:live_engine, li:callers).
