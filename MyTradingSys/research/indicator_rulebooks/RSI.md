# Rule book: RSI (Relative Strength Index, Wilder 1978)

Sources: FORM = `backtest/layers/FORMULAS.md` s1; CEN = `rsi_range_census_2026-11-13/REPORT.md`; EXT = `rsi_extreme_confirm_2026-11-13/RESULT.md`; DIV = `rsi_divergence_mtf_2026-10-09/RESULT.md`; GATE = `rsi_divergence_mtf_gated_2026-11-04/RESULT.md`; DEEP = `rsi_deep_buy_2026-10-19/CONFIRMATIONS.md`; L4060 = `rsi_40_60_line_behaviour_2026-11-04/RESULT.md`; MAL = `malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md`; NKR = NK_RSI_RESULTS.md (side-session notes, NOT in the repo yet: `...\side-session-notes\local_0cb8bd0b-848b-4df7-b685-6a6d0f12ab98\NK_RSI_RESULTS.md`); WIKI = https://en.wikipedia.org/wiki/Relative_strength_index (fetched 2026-11-13; the fetch tool returns a summary, so short quotes below are UNVERIFIED as exact wording). Wilder's book itself was NOT opened.

**Result: RSI says how stretched the last closes are, on a scale of 0-100. Our data shows no fee-net edge in any RSI rule we tested (extreme+confirm 0/384, divergence 31 of 32 net negative, NK rules 0/42). Use it as a "how rare is this" gauge and a context line, never as an entry.**

## 1. What it measures
Average size of up-closes against down-closes over the last 14 bars, Wilder-smoothed, scaled 0-100. FORM s1 (Wilder = TradingView `ta.rsi`; one deliberate deviation: flat series returns 50). Code `backtest/layers/rsi/rsi_core.py`. VERIFIED-TV: not marked for RSI in FORMULAS (grep of the file found no RSI VERIFIED-TV line); Live Aid uses RSI 14 as the operator's chart setup (`tools/live_aid/live_aid_indicators.js:2`, SOURCED operator).

## 2. Developer's own rules (SOURCED via WIKI, UNVERIFIED wording)
| Item | What is stated | Source |
|---|---|---|
| Who | J. Welles Wilder Jr., *New Concepts in Technical Trading Systems*, 1978 | WIKI |
| Period | "Wilder recommended a smoothing period of 14" | WIKI |
| Levels | "tops and bottoms are indicated when RSI goes above 70 or drops below 30" | WIKI |
| Divergence | "divergence between RSI and price action is a very strong indication that a market turning point is imminent" | WIKI |
| Failure swings | Wilder "thought that failure swings above 50 and below 50 are strong indications of market reversals"; the page cites StockCharts for this, not the book | WIKI |
| Cardwell (not Wilder) | uptrends trade between RSI 40 and 80, downtrends between 60 and 20; bearish divergence confirms an uptrend (and bullish a downtrend) | WIKI |
Open: Cardwell/Brown's own books and Brown's 40-90 / 10-60 ranges were not found on this page; no primary source opened. Gemini card `gemini-rulebook-rsi-1113` (filed) is to open Wilder/Cardwell/Brown primary sources and crypto-trader material.

## 3. What the internet and crypto traders say
| Claim | Source | Grade |
|---|---|---|
| 70/30 are the standard OB/OS lines, "typically" | WIKI | anecdote (convention) |
| In strong trends RSI stays pinned; a 30 is not a buy | not opened | none (UNVERIFIED, general knowledge, not a source) |
Our own census is the only measured evidence here (section 5). No crypto-trader source with costs and sample was opened in this pass.

## 4. What our analysts say
| Analyst | Rule | Pointer |
|---|---|---|
| Malkan | 5-star buy: monthly about 60, weekly about 60, daily RSI at 40 support; sell mirror 40-40-60 at daily 60 resistance | MAL rows 5-Star Buy/Sell (v8pCR_bA0_0 00:05:27, 00:10:02) |
| Malkan | Bearish zone: monthly RSI under 40 | MAL (2HcJ3NeZmEQ 00:03:00) |
| Malkan | Divergence: compare swing points on CLOSES only, ignore intraday spikes | MAL (cQ-y1oULkBw 00:03:40) |
| Krown | Oscillators give constant false signals in low volatility (KR-Q08); trade mode first, indicators last (KR-T09) | `krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md` lines 24, 140 |
| Operator (his chart rule) | RSI at an extreme + confirming candle = entry | tested as EXT |
| NK StockTalk | RSI 70/30 at session close, Hilega Milega flips (formula is OURS-EXTERNAL, NK never states it) | NKR |

## 5. OUR measurements (BTC unless stated)
| Study | What | n | Fee-net result | Verdict |
|---|---|---|---|---|
| CEN | Where RSI lives, 5m-1w, Bybit 2020-26, gross, descriptive | 1h 58,030 bars | 1h p1 = 22.3, p5 = 30.4; 1h below 20: 144 episodes; 1h below 10: 6 episodes (2020:1, 2021:2, 2023:2, 2026:1) | CONTEXT ONLY (rarity map) |
| CEN | 1h touch of <=20, forward 24h | 138 pooled | median +0.2%, 51% positive; median further drop within 24h -2.8% (2.5 hourly ATRs) | not a bounce signal |
| EXT | Hourly RSI extreme + confirming candle, 10 coins, fixed stops, 2 x taker + funding | 384 cells | 0 of 384 pass; 0 BH-significant on DEV or VALIDATION; best DEV cell long T20 pct1 time24 DEV +0.284 R, VAL -0.061, RECENT -0.486 | DO NOT USE (1h) |
| DEEP | Confirmations at an RSI low, 60m/15m/1m | 150 DEV, 80 VAL rows | 0 of 150 and 0 of 80 net CI above 0 | DO NOT USE |
| DIV | RSI divergence, every TF, 2022-2026 | 32 cells n>=300 | 31 of 32 net negative; best 1h operator bearish n 332 net +0.038% t 0.39 | DO NOT USE; 6h/2d UNDERPOWERED (n 6-54) |
| GATE | Divergence under Malkan monthly/weekly gate | 15m aligned n 164 | net -0.176% [-0.307, -0.045]; 0 of 32 survive; bear regime 0 weeks in DEV | UNDERPOWERED, 15m negative |
| L4060 | RSI 40/60 line behaviour, BTC+ETH spot | 214 play cells n>=30 | 15 with DEV CI above 0 (7%, chance ~5%); default play null; real lines hold +1.5 points more than chance | CONTEXT ONLY; "another TF at the same line" is the one factor with a hold-rate effect (+7 points 1h, +12 4h) |
| NKR | NK R1-R4, 10 perps, 5m, 10 bp round trip | 42 cells | 0 of 42 pass; R3 closest +1.16% CI -0.15..+2.41, p 0.047, fails BH, RECENT -0.17% | DO NOT USE |
Not yet on trunk: structural-stop grid `edge3-rsi-deep-extreme-grid-1113` (running). Operator said "1h <= 10 five times since 2020"; CEN counts 6 episodes (8 bars) for BTC 1h below 10. Check the count rule before quoting "five".

## 6. How to read it now on Live Aid
Panel "Momentum" (columns RSI, SMA of RSI, per timeframe) and the Timeframe strip. RSI 14, closes. Read: below 22 on 1h = the rarest 1% since 2020 (CEN), above about 80 on 1h = rarest 1% high. It tells you "stretched", not "turn".

## 7. Confluence role: EXHAUSTION
May add confidence to a level-based or divergence-based setup that already exists ("price at a level AND 1h RSI in the rarest 5%"), and to a veto: do not chase a move with RSI in the rarest 1%. It does not add an entry. Today: CONTEXT ONLY, no fee-net out-of-sample pass exists.

## 8. Open tests
| Test | Status |
|---|---|
| Structural-stop grid on deep extremes | `edge3-rsi-deep-extreme-grid-1113`, running |
| Another TF at the same 40/60 line as a gate (L4060 factor) | not filed |
| Cardwell ranges 40-80 / 60-20 as a regime gate | not tested; needs a primary source first |
| Wilder failure swing | not tested |
