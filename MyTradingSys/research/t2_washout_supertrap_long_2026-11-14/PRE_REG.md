# PRE_REG: T2 washout Supertrap LONG, split by cycle state (2026-11-14)

Source: `EDGE_POSTMORTEM_1114.md` section 4 T2 (notes folder). Frozen BEFORE any trade, R or placebo number is computed (only outcome-free counts may be looked at). SOURCED = trader's words or repo source; OURS = our choice, stated here.

## Context

Question: is NK's Supertrap (1h candle at least half outside the lower Bollinger band, then price back above the VWAP anchored at that candle) a profitable long after a market washout, in BULL/BASE cycle state but not in BEAR? This is the one thing 7 earlier washout studies never split on (their DEV/VAL sign flips: DEV negative, VAL positive 6 of 6; DEV holds the 2022 bear). Not a trade instruction; nothing is an edge until a fee-net out-of-sample result passes.
Regime: cycle state BULL / BASE / BEAR from `F:\MTS\data_cache\mts_brains\phase_daily.csv` column `cycle` (MTS brain; row of the signal's UTC day, which the brain builds from closes through the prior day; the audit verifies this via `close_used`). BULL+BASE = the hypothesis cell, BEAR = control. Never pooled.
Phase: the brain's 6-phase `label` (CAPITULATION, RELIEF, ACCUM-RANGE, MARKUP, DISTRIBUTION, MARKDOWN) is reported as a descriptive cut only, not a gate.
Session: none, because 1h bars run 24/7 and the washout gate is BTC 4h; no session gate is tested.
Entry: 1h candle with at least 50% of its range below the lower BB(20,2), BTC 4h RSI14 at or below 40 at that candle, then the first 1h close above the trap-anchored VWAP within 12 bars; fill at the next 1h open.
Regime mix: filled in RESULT from the data (DEV / VAL tables, cycle share of signals and of calendar days). Expected from `phase_daily.csv` calendar days 2019-2026: BEAR about 47%, BULL about 24%, BASE about 29% of days; 2022 is almost all BEAR, 2024-2025 mostly BULL, 2026 mostly BEAR. VAL (2024+) holds BEAR days (2025 Q4, 2026), so the BEAR control is testable out of sample.

## Power gate (recorded, overruled)
`prereg_gate.py --n 40 --sd 1.5 --cost 0.10 --m 2` exits BLOCK (MDE 0.73 R; n 100 gives 0.46 R; needs about 534 independent episodes). Decision (OURS): run anyway because the operator ordered T2 (2026-11-14); a FAIL is read as UNTESTED/underpowered, never as proof of no edge. A PASS would still need the blind review. sd 1.5 R is the GATE_AUDIT Q1 range, not measured; the measured sd is reported in RESULT.

## Data (public Binance spot klines, local cache `F:\MTS\data_cache`; the research script reads it, committed tests use synthetic bars only)
- Core universe (20 coins, 15m from listing, 2019-01 on): ADA ALGO ATOM AVAX BCH BNB BTC DOGE DOT ETC ETH FIL LINK LTC NEAR SOL TRX UNI XLM XRP (`binance_spot/*_15m.npz`, array `a` rows t,o,h,l,c,v; layout checked in code). Used in earlier studies, so their earlier peeks count.
- Fresh-8 (not in the 20): AAVE ENJ GRT HBAR MANA SAND THETA XTZ (`binance_fresh/nk5_nyasia/*_5m.npz`, resampled to 1h).
- 1h bars = UTC-aligned aggregation of 15m (or 5m); a bar needs all its sub-bars, else it is dropped. BTC 4h bars likewise from BTC 15m.
- History starts 2019-01 (not 2018): the 2022 bear and 2019-2020 are in; 2018 is not available locally. Caveat stated.
- Survivorship: all coins still list; delisted coins absent (bias unknown).

## Rules

| Item | Rule | Label |
|---|---|---|
| Washout gate | BTC 4h RSI14 (Wilder, on 4h closes) at or below 40, using the last 4h bar fully closed at or before the trap candle's close time | SOURCED (Malkan 40/60, layers/rsi/malkan_40_60.py); 4h frame and BTC as market proxy OURS |
| Trap candle | 1h candle of the coin with high > low and (min(lowerBB, high) - low) / (high - low) >= 0.5. BB = SMA20 of 1h closes minus 2 x population sd (ddof 0), including this candle's close | SOURCED (AKZ-7zvDxpY 00:25:49; 1h at 00:27:58); band 20,2 OURS |
| Gate timing | washout gate and cycle state are read at the trap candle (its close time / its UTC day) | OURS |
| VWAP | anchored at the trap candle open, cumulative sum(typical x volume) / sum(volume), typical = (h+l+c)/3, through the current bar | SOURCED (00:27:07 VWAP of the trap); typical price OURS |
| Entry signal | first 1h bar within the next 12 bars after the trap candle whose close is above the anchored VWAP; entry = the following 1h bar's open | SOURCED idea; 12-bar window OURS |
| One position | one open or armed (waiting for its entry signal) trade per coin; a trap candle is ignored while one is open or armed (first trap wins) | OURS |
| Stop | stop = entry - D, D = max(entry - trap candle low, 1.0 x ATR14(1h, Wilder, at the signal bar), 0.012 x entry). Skip if D > 0.10 x entry | SOURCED (stop hunt low / VWAP); floor and cap OURS |
| Exit | first of: stop (checked from the entry bar; stop first inside a bar; a gap below the stop fills at the open), time exit at the open of the 24th bar after the entry bar | exit time OURS (NK gives none; 12-24h came from seen data) |
| R, fee | R = (exit - entry) / D. Fee-net R = R - fee_rt x entry / D. fee_rt 12 bp primary = 2 x (BINANCE_TAKER from `fees.py` + 0.0001 slippage per side). 6 bp = sensitivity row only (no fill model, optimistic), never used for a verdict | SOURCED fees.py; slippage OURS |
| Splits | DEV = trap candle time <= 2023-12-31; VAL = trap candle time >= 2024-01-01 | task |
| Episode | all trades (any coin) whose entry signal falls within 72h of the first one; a gap of more than 72h with no new entry signal starts a new episode. Episode R = mean fee-net R of its trades. Verdict statistics are on episodes. Episode cycle state = state of its first trade | OURS |
| Seed | 1114 | OURS |

One frozen cell. No grid, no second pass on parameters.

## Verdict cells (family m = 2, own cells only): BULL+BASE (verdict) and BEAR (control)
PASS of BULL+BASE requires ALL, at 12 bp, DEV+VAL pooled episodes unless stated:
1. at least 30 episodes;
2. mean episode fee-net R > 0 and the 95% bootstrap CI low > 0 (2000 resamples of episodes, seed 1114); Holm over m = 2 reported next to it, a PASS that fails Holm is labelled MULTIPLICITY-FLAGGED;
3. ex-best-5 episodes mean fee-net R > 0;
4. excess over random same-state longs > 0: for every real trade draw a random 1h bar of the same coin, same cycle state, same period (DEV/VAL), not inside a position, apply the same stop/exit rule with the real trade's stop distance in percent; 1000 draws of the full matched set; real mean >= 97.5th percentile of the draw means, and excess = real mean minus placebo mean > 0;
5. DEV episode mean > 0 AND VAL episode mean > 0 (sign agreement); VAL < 10 episodes = UNDERPOWERED and cannot PASS;
6. Fresh-8 trades alone: mean > 0 if they have at least 10 episodes (else reported only).
Otherwise FAIL (reason per bar). Reported, not gates: buy-and-hold of the equal-weight coin basket per year and per cycle state; time in market; gross R; by symbol (top-coin removal, FRAGILE if it makes the mean <= 0), by year, by phase label, by cycle state; 6 bp row; sd of R.
Registered prediction (reported as CONFIRMED / REFUTED): BULL+BASE mean > 0 and BEAR mean <= 0. If BEAR also passes bars 1-5 it is reported as the tradable result, labelled by itself (m = 2).

## Known weaknesses (before the run)
- Underpowered by the gate; episodes are few and clustered on crash dates.
- Cycle thresholds and the 12-bar / 24h / 1.2% numbers are OURS, one specification, nothing tuned.
- Spot prices, no funding, 12 bp flat, no fill model; coins correlated inside an episode (the episode unit handles it).
- Core 20 coins were seen in earlier washout studies.

## Protocol
Code (`lib.py`, `trades.py`, `stats.py`, synthetic tests) is committed with this PRE_REG. Step A: `trades.py` writes the trade list (no pooled statistics). Step B: an independent recompute of 3 dated trades and an adversarial look-ahead/fee audit run on that list. Step C: only if both are clean, `stats.py` computes RESULT. A found mechanical bug is fixed and logged in RESULT; rules are never changed after step A.
