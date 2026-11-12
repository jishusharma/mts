# Malkan RSI level layer: fact sheet for slide deck (read-only research, 2026-11-12)

Conventions. All paths are under `MyTradingSys/` unless they start with `raw_transcripts_canonical/` (repo root). SOURCED = from the trader (quote exists in a transcript/extract) or a repo file. OURS = our parameter/choice/result. T3 = a quote shows what he teaches, not an edge. No account/order data used.
Trader: Vishal B Malkan (@Malkansview), Indian equities (Nifty examples), Daily/Weekly/Monthly charts (SOURCED: `research/malkan_universe_2026-10/UNIVERSE_POWER.md:12`, quoting `extract_Wvq1TZh8aF0.md:284-287`).
Quote verification state (ran `python scripts/dev/verify_extract_quotes.py` 2026-11-12): extracts `extract_cQ-y1oULkBw.md`, `extract_Wvq1TZh8aF0.md`, `extract_2HcJ3NeZmEQ.md` = PASS (0 problems). `research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md` = 9 quotes NO-TRANSCRIPT (videos v8pCR_bA0_0, 5Aoyw_sG_88, hGPqIpWRUMQ: transcripts not in repo, so UNVERIFIED), the rest OK. Timestamps in that table are as stated there; most raw files are one line with no per-line stamps, only `GbXnw_tNMtw_raw.txt` has [mm:ss] stamps (used below). Hindi quotes: the verifier's normaliser breaks on Hindi (`research/malkan_hindi_2026-11-04/REVIEW_MALKAN_WINDOW_GEMINI_1104.md:48`), so Hindi quotes were checked by substring (`WINDOW_RECONCILE_1104.md` spot-check section).

**Correction to the memory note "divergence = closes, 12/18 bars":** closes = SOURCED (his words). 12/18 is NOT sourced: relabelled OURS by `system/OPERATOR_DECISIONS.md:1755` (`d-malkan-window-label-1105`) after `research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md` found 3-10 SOURCED, 12 appears only as a "diluting" count (Hindi), 18 is never a bar threshold. The running default is still 3-10 (`backtest/layers/rsi/params/malkan_divergence_default.json`). BUT the live feed docstring and the div-flag report header still say "12/18 SOURCED" (stale label, see H).

---
## A. CONCEPTS (7)

### A1. Grandfather-Father-Son (GFS) higher-timeframe gate = "5-star"
- Teaches: trade only in the direction of the higher timeframes. Monthly = grandfather, weekly = father, daily = son. 5-star long = monthly RSI above 60 + weekly above 60 + daily RSI pulls back to the 40 support. Short mirror = monthly below 40, weekly below 40, daily at the 60 resistance. Higher TF seeks 60 support, lower TF 40 support (Hindi, `fgN6QBFY3Ss`).
- Quote (VERIFIED PASS): "...which is five star setup with monthly about 60 weekly about 60 and daily at 40 support was the trend" - video `2HcJ3NeZmEQ` (RSI 5 Star Set Up #1, Sell Setup, published 2019-01-20), GPS BEGIN, table stamp 00:00:33; extract `research/malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md:22`.
- 2nd quote (table stamp 00:06:27, `MALKAN_RULES_2026-10-31.md`): "son will definitely not try to go against the father or the grandfather" (2HcJ3NeZmEQ).
- Diagram: three stacked RSI panes (M, W, D). M and W lines sitting above the 60 line (shaded "green zone"); D pane RSI dips to the 40 line and a green candle forms; arrow up. Mirror: M, W under 40, D rejects at 60.

### A2. RSI 40/60 level = range shift (support/resistance on RSI itself)
- Teaches: bullish regime = RSI cannot fall below 40 (40 acts as support); bearish regime = RSI cannot rise above 60 (60 acts as resistance); 40-60 = sideways; "40 pe support leta hai = bullish range shift" (Hindi `sPu2SnAFEIY`, `HINDI_CONCEPTS.md`).
- Quote (VERIFIED PASS): "we can go to daily and look for 60 rise just to sell" - `2HcJ3NeZmEQ`, GPS MIDDLE, table stamp 00:03:20. Web summary: `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:39-62,84-89` (secondary).
- Hindi (substring-checked, `HINDI_CONCEPTS.md`): "बिलो 40 इज बेरिश बिटवीन 40 60 साइड वेज अबोव 60 इज बुलिश" (`raw_transcripts_canonical/sPu2SnAFEIY_raw.txt:8`).
- Diagram: single RSI pane with horizontal lines at 40 and 60; three shaded bands (below 40 bear, 40-60 range, above 60 bull); RSI line bouncing off 40 from above.

### A3. Signal candle (alert candle) entry, stop, target
- Teaches: at the 40 support, the candle that forms the support is the "alert candle"; buy above its high, initial stop below its low. Target = RSI back at 60 (long) / 40 (short) per web research only.
- Quote (SECONDARY presenter, not Malkan, `COMPARE.md` s1.2): "entry abodh this candle" and "stop loss will be below the candle" - `W1HrDl70Lhk` (Trader Insights presenter, Hindi audio + machine translation), `extract_W1HrDl70Lhk.md:339,350`. Malkan's own wording (UNVERIFIED, no transcript): "the high of that is your entry and initial stop loss" - `5Aoyw_sG_88` table stamp 00:04:35.
- Diagram: price candle chart with a green candle at the RSI-40 touch; horizontal buy-stop line at that candle's high, stop line at its low, dashed target where RSI hits 60.

### A4. Regular divergence: closes, 3-10 bars
- Teaches: compare closing prices at two swing points (RSI is built on closes). Minimum 3 bars, "between three and 10", fewer bars = stronger; 15, 20, 25, 30, 40 bars = diluted. Decimals count. RSI = speedometer: price makes new extreme, speed (RSI) lower, then U-turn.
- Quote (VERIFIED PASS): "I will say that less than 10 bars is the most powerful divergence. It should be between three and 10." - `Wvq1TZh8aF0` (RSI Divergence Explained Simply), GPS BEGIN, `extract_Wvq1TZh8aF0.md:133`.
- Quote (VERIFIED PASS): "As the number of bars increases, you see 15, 20, 25, 30, 40 bars. The divergence gets diluted completely and it has not worked." - `cQ-y1oULkBw`, GPS MIDDLE, `extract_cQ-y1oULkBw.md:146` (also "15 to 20 times, this is still fine" at :200, contradicts a hard cutoff). Closes: "Now what do we have to compare? Close to close. Because RSI is based on closing price." `extract_Wvq1TZh8aF0.md:75`.
- Diagram: line chart of closes with two lower lows A (close) and B (close) joined by a line, RSI pane below with two higher lows joined by a line; bracket "A..B = 3-10 bars"; a second bracket "15+ = diluted" greyed.

### A5. Reverse divergence (PRD / NRD) = trend continuation
- Teaches: in an uptrend price makes a higher low while RSI makes a lower low = Positive Reverse Divergence (PRD, buy the pullback); NRD mirror in a downtrend. Trend marker = both RSI points above 60 (PRD) / below 40 (NRD). Bar count matters; stop below the swing low.
- Quote with stamps (raw transcript `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt`, VERIFIED present, "Reverse Divergence - Positive & Negative Divergence"): [21:54]-[21:59] "should be between five to fifty and both the point should be about sixty if it's a positive edge divergence and of course if it's a negative reverse divergence it..." (conflicts with [18:10] "number of bars which are less than 15", and [16:53]-[17:00] "within seven eight bars ... more than fifteen twenty bars so I that dilutes"). 60-zone filter: [17:13]-[17:15] "both the points are about 60".
- Diagram: uptrend price chart, higher low; RSI pane with RSI line above 60 making a lower low (both points above the 60 line, shaded); green arrow after B.

### A6. Bar-count dilution (Hindi series)
- Teaches (Hindi, `HINDI_CONCEPTS.md`): fewer bars between the two points = stronger; minimum 3; above 10 dilutes progressively; "must be under 15"; "12 15 20 25 30 40 diluted"; Class A/B/C divergences, B and C best near RSI 60/40.
- Quote (Hindi, substring-checked): "दो पॉइंट के बीच में वो बहुत जरूरी है कि 15 से कम हो ..." - `TrZQ4Xat_sQ` (`raw_transcripts_canonical/TrZQ4Xat_sQ_raw.txt:8`); "जैसे जैसे नंबर ऑफ बर्स बढ़ते जाते 12 15 20 25 30 40 वो बिल्कुल डाइल्यूट हो जाता है" - `TO3pLafk7Us` (`..._raw.txt:8`). 12 is a diluting count, 18 is NOT_IN_DATA (`WINDOW_RECONCILE_1104.md` threshold table).
- Diagram: strength-vs-bars curve falling from 3 bars to 50; marks at 3, 10 (sourced edge), 15 (his "under 15"), 50.

### A7. Star grades 3 / 5 / 7 (confluence grade, conditions mostly withheld)
- Teaches: a grade of conviction. Only stated 7-star recipe (English): monthly RSI above 60 + daily RSI below 40 + a divergence on the daily; double the target, same stop. In Hindi `A-CQiV_UFB4` he claims 7-star runs "80-90", 5-star "60-70" and withholds the conditions. (Separate: `XFO49JlODxI` "Spinning Top 7 Star Setup" is a candle setup, a different 7-star; `malkan_level_shorts_2026-11-09/SEVEN_STAR_CAPTIONS.md`.)
- Quote (VERIFIED PASS): "RSI monthly above 60 and RSI daily below 40 and there is divergence visible, that is one of the best trades" - `Wvq1TZh8aF0`, GPS END, `extract_Wvq1TZh8aF0.md:395`; "...then double the target. The stop loss will remain the same." `:403`.
- Caveat: "above 60" and "at 60" both said (`COMPARE.md` s2.2); strike rates are a claim with no sample shown (`COMPARE.md` s2.1).
- Diagram: grade ladder 3-star (loose) < 5-star (GFS gate + daily 40 bounce) < 7-star (5-star + divergence at the daily low, target x2).

---
## B. OUR RULE per concept (code + parameters)

| Concept | One-line rule as coded | Code |
|---|---|---|
| A1 GFS gate | Weekly AND monthly RSI >= 60 = band "bull", both <= 40 = "bear", else "mid"; regime = band AND daily close vs SMA200 side (bull: above, bear: below) | `backtest/research_kit.py: rsi_band` (l.215), `regime_tag` (l.240), `weekly_regimes` |
| A1 older gate | 20-bar window: BULL if min RSI >= 40 and max >= 60; BEAR if max <= 60 and min <= 40 | `backtest/layers/rsi/malkan_40_60.py: malkan_regime`; composed in `malkan_mtf.py: malkan_mtf_bull / malkan_mtf_bear` |
| A2 level events | RSI within +-tol of 40 (support) or 60 (rejection) via tolerance-band state machine | `layers/rsi/rsi_events.py: rsi_events` (FORMULAS s6) |
| A3 entry | Signal-only: support at 40 in BULL + green candle -> long; rejection at 60 in BEAR + red candle -> short. No entry price/stop/target in the layer | `malkan_40_60.py: malkan_setup_bull / malkan_setup_bear` (rule ids MLK-S1/S2) |
| A4 regular div | Strict-local-extreme closes, two ADJACENT pivots A,B, price lower low + RSI higher low (mirror for bearish), bars A..B inclusive 3-10, any RSI difference > 0; event stamped bar b+1 (causal) | `layers/rsi/rsi_divergence.py: rsi_divergence(kind="bullish"/"bearish")` |
| A5 reverse div | PRD: price higher low, RSI lower low, RSI >= 60 at both; NRD mirror <= 40; bars 5-14 | same function, kind "prd"/"nrd" |
| A6 window arms | Studies tile bars into S3_10 / B11_12 / C13_18 / D19_50 | `research/malkan_window_dev_2026-11/study.py`, `malkan_window_wide_2026-11/wide.py` |
| A7 stars | LABEL only: mlk_g02 (monthly within 2 of 60 + daily divergence), mlk_g03 (monthly > 60, daily < 40, divergence) | `malkan_mtf.py: seven_star`; study `research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades` |
| Derived: level short | 5-layer stack read from the operator's 5 BTC 4h shorts: level tag, structure (div 3-10 close or sweep), trigger (RSI < 14-SMA of RSI, < 60, was >= 60 in 10 bars), WaveTrend, HTF 60-fail | `layers/rsi/malkan_level_short.py`, live paper alert `malkan_level_short_live.py` |

Parameter table (label per value):

| Parameter | Value | Label | Where |
|---|---|---|---|
| RSI period, Wilder | 14 | SOURCED (Malkan/TradingView default; WEB_RESEARCH:35) | `rsi_core.py`, FORMULAS s1 |
| RSI levels 40 / 60 | 40, 60 | SOURCED | `params/malkan_40_60_default.json`, `research_kit.RSI_BEAR/RSI_BULL` |
| GFS gate: weekly AND monthly | >= 60 bull / <= 40 bear | SOURCED | `research_kit.py:190-191`; `MALKAN_RULES_2026-10-31.md` |
| Daily SMA200 side in regime tag | 200 | OURS (SOURCED-in-repo meta.py trend_d) | `research_kit.MA_N` |
| Regime = band AND side | combination | OURS | `research_kit.py` header |
| Regime lookback (older malkan_regime) | 20 bars | OURS | `malkan_40_60_default.json` |
| Level tolerance | 2.0 RSI pts (layer); 0.5 (live confluence feed) | OURS | json; `live_confluence_feed.py` |
| Candle colour required | yes | OURS reading of "candle forms" | json |
| Divergence compare | close to close | SOURCED | `malkan_divergence_default.json` |
| Divergence min bars | 3 | SOURCED ("minimum three") | json |
| Divergence max bars (regular) | 10 | SOURCED ("between three and 10") | json |
| Min RSI diff | 0 | SOURCED ("decimals count") | json |
| Reverse div bars | 5 - 14 | min 5 SOURCED, max 14 OURS (sources conflict: <15 vs 5-50) | json "reverse" |
| PRD/NRD RSI levels | >= 60 / <= 40 | SOURCED level, strict compare OURS | `rsi_divergence.py:PRD_MIN_RSI/NRD_MAX_RSI` |
| 12 STRONG / 13-18 OK / >18 WEAK window | 12 / 18 | OURS (relabelled 11-05; was called SOURCED) | `OPERATOR_DECISIONS.md:1755` |
| Swing definition | strict close extreme, adjacent pivots | OURS | `rsi_divergence.py` (v1 limit) |
| Studies' exit | 10 bars after event close | OURS, NO-SOURCE | `rsi_divergence_mtf_gated_2026-11-04/PRE_REG.md` |
| Studies' cost | 0.14 % round trip (older run 0.10 %) | OURS/SOURCED research_kit, fees.py | `research_kit.TAKER_RT_PCT` |
| Bear proxy P40 | weekly RSI14 <= 40 alone, below SMA200 | OURS, "never Malkan's" | `OPERATOR_DECISIONS.md:1694-1698` |
| Level-short target / time stop | 2R / 60 bars | OURS | `malkan_level_short.py` |
| Level-short level proxy | pivot 5/5 within 60 days, tag within 0.5 % | OURS | `READING.md`, code |
| 5-star daily trigger "RSI near 40, green candle" | 40 | host-recap (secondary), T3 | `COMPARE.md` s1.6 |
| Star hit rates 5-star 60-70 %, 7-star 80-90 % | claims | SOURCED claim, no sample, UNVERIFIED | `COMPARE.md` s2.1 |

---
## C. FIDELITY (his version vs ours)

| Aspect | Verdict | How |
|---|---|---|
| Closes not wicks | MATCHES | SOURCED, coded close-to-close; one wick variant tested in level short (no difference at 5-50 bars: -0.05 vs -0.03 R) |
| Regular divergence 3-10 bars | MATCHES the words | `malkan_divergence_default.json` |
| 40 / 60 levels, RSI 14 | MATCHES | |
| Market | DISTORTED | His home = Indian equities daily/weekly/monthly; we test BTC 24/7 at 15m, 1h, 4h, 1d (UNIVERSE_POWER.md:12; `rsi_divergence_mtf_2026-10-09/RESULT.md` ran 1m-2d). No Indian equity series in repo (HOME_FIT_AUDIT_MALKAN.md:33 via UNIVERSE_POWER). |
| Timeframe | DISTORTED | He says daily/weekly/monthly only and "read one higher and one lower" (`RSI_2A_SPEC.md` answers table). Sub-hour tests have no source. His 3-10 bars came from lower-TF and daily examples; the operator's 4h hand reads span 15-19 bars (`malkan_level_shorts_2026-11-09/READING.md`). |
| GFS gate | SIMPLIFIED / DRIFTED | Two implementations: `malkan_mtf.py` uses a 20-bar min>=40,max>=60 window per TF (not "RSI above 60"; COMPARE s0 item 5); `research_kit.rsi_band` is the level test = closer. Live/sim layers use the older same-TF regime, not monthly/weekly (see D). On BTC the gate is true ~19-20 % of weeks and bear never (monthly RSI14 never <= 40 since 2017-08, min 40.4 on 2023-01). |
| Bear (short) leg | UNTESTABLE on BTC | 0 bear weeks in 360-479 weeks; OURS proxy P40 gives 57 weeks (not his). |
| Entry/stop/target | SIMPLIFIED | Layer = signal only. His entry above candle high, stop below low is only secondary-source for 40-bounce; target "C between A and B", partial 50 % and trailing not exactly stated (`RSI_2A_SPEC.md`: "exact definition NOT in the words"). Studies exit at a fixed 10 bars (OURS) so they do not test his exit (`RSI_2A_SPEC.md` conflicts section). |
| Divergence pairing | SIMPLIFIED | Only adjacent same-kind pivots (strict 1-bar extremes); he reads swing-to-swing by eye across non-adjacent swings; consecutive strict-close pivots almost never sit > 10 bars apart (`malkan_window_dev_2026-11/RESULT.md`: 4 events total in 11-50 bar arms). |
| Reverse div window | CONFLICT unresolved | 5-14 used; his words: <15, 5-50, "7-8 bars good, 15-20 dilutes" (`GbXnw_tNMtw_raw.txt` [16:53], [18:10], [21:54]). |
| Stars | NOT IMPLEMENTED | Only label; 5-star partially (gate + 40 bounce); 3-star and 7-star conditions withheld (paid course); `edge_hunt eh-h2` coded the stated 7-star recipe + 5-star. |
| Discretion | DISTORTED | He eyeballs, adds "certain conditions" he does not state ("I think if I give so much together then you will feel over whelm", `extract_A-CQiV_UFB4.md:450`). 0 dated trades/calls exist, so no ledger to score (`malkan_ledger_2026-10/LEDGER_PARITY.md`: 0 dated calls, 6 parity points, verdict HYPOTHESIS, below the 20-call gate). |
| Caption quality | RISK | English auto captions of Hindi speech (garbled stops/targets in `W1HrDl70Lhk`); Hindi 6 videos: first extraction NOT_IN_DATA (policy), later Hindi re-read gave window evidence only. |
| Operator-added extras | OURS | Wide-pivot bands 11-12 / 13-18 / 19-50; 12 STRONG / 18 OK; P40 proxy; cushion bands (c 1-5); fake-out filters. |

---
## D. SUPPORT LAYERS (how, wired or not)

| Layer | How it supports Malkan | Wired? |
|---|---|---|
| Regime tag (`research_kit.regime_tag`) | As-of regime = weekly+monthly RSI band (60/40) x daily SMA200 side; used as GATE and as `Regime mix:` line in every RESULT since 11-04 (`LESSONS_DIGEST.md:33` context rule). Mix on BTC 2017-08..2024-06: bull 20 %, bear 0 %, range 62 %, n/a 18 %. | Research only (only file using it outside research/ is research_kit itself, grep). NOT in live runner, sim desk, or Live Aid. |
| Bear gate (strict + P40 proxy) | Strict = never fires. P40 (OURS, operator kept it: "Keep proxy", `OPERATOR_DECISIONS.md:1697-1698`). Per-context tuning study found no default (0 of 7 cells; hit rate of proxy weeks 0.376 vs 0.423 all weeks = gate marks bounces, `bear_proxy_context_tuning_2026-11-04/RESULT.md`). | Research only. |
| Phase label (OURS, eh-o2) | Cycle phase x weekly RSI zone; finds 112 of 358 DEV weeks BEAR/BOTTOM_WINDOW vs 0 in regime tag (`edge_hunt_2026-11-09/results/eh-o2-phase-lens/RESULT.md`). | Research only. |
| CBP context | Analyst calls (Crypto Bike Plan store) are CONTEXT, never signals (`research/cbp/README.md`). No Malkan link; used for altcoin plan, sister notes; `sister_signals.json` consumed by `live_runner_cli.py:668`. | Wired to live runner for sister signals; NOT to Malkan layer. |
| Bollinger Bands | Malkan has his own BB "Father-Son" video (`fgN6QBFY3Ss`, Hindi; not extracted in English; `SEVEN_STAR_CAPTIONS.md` row: no star grade). Our BB studies test the OPERATOR's range-to-range idea, not Malkan's rule (F). BB(20,2) is OURS. | Studies only; Live Aid shows %B, BBw (display). |
| Levels (S/R) | Operator's hand-drawn levels are layer 1 of the level short; proxy = confirmed pivot (OURS). Live Aid has a level ladder/registry (`live_aid_map_2026-11-09/RESULT.md`). | Level short layer: paper alert. Live Aid: levels yes, Malkan no. |
| Order flow (CVD/OI/volume) | Operator asked to add one by one (wlow_bounce request); value-area rules (`btc_untested_rules_1112`, from other analysts) FAIL; volume fake-out filter at 15m only trims loss 0.03 pt. Not a Malkan input. | Not wired to Malkan. |
| WaveTrend + HTF 60-fail (level short layers 4, 5) | Each lifts base about +0.1 R (n 201 / 148) mostly in bear regime; full 5 = n 37, +0.13 R (0.6 SE). | Counted; not gates in the forward arm. |

Live path facts (code):
- `backtest/layers/alerts/live_confluence_feed.py`: Malkan divergence flags (R-BULL, R-BEAR, PRD, NRD) + RSI 40/60 events as ALERT-ONLY, no side, no layer_rules entry, so the auto-trader cannot map them (fail closed). Windows there = 12 (STRONG) / 18 (OK) labelled SOURCED (stale), legacy 3-10 column suffix _OLD.
- `live_layers.py: malkan_bull_layer / malkan_bear_layer` on 1h, same-TF 20-bar regime (not monthly/weekly). `execution/auto_trader_config.json` carries them as "grandfathered pre-pipeline testnet calibration, operator decision pending", review_by 2026-10-23 (testnet only).
- `live_rsi_divergence.py`: 1h regular divergence 3-10, events carry `"sampling": True` (RSI-DIV-MTF failed).
- `malkan_level_short_live.py`: context-only paper alert on BTC 4h, no order, kill after 30 paper trades if net R <= 0 (`malkan_level_shorts_2026-11-09/FORWARD_PREREG.md`).

---
## E. TESTS (fee-net; cost 0.14 % round trip unless stated; "CI" = day-clustered 95 %)

| Study (path under research/) | Date | n | Fee-net result | Verdict | Lesson |
|---|---|---|---|---|---|
| `rsi_divergence_mtf_2026-10-09` (T089, BTC 1m-2d, 2022-01..2026-10, cost 0.10 %) | 10-09 | 32 cells >= 300 events | 31 of 32 net negative; 1h Malkan bearish n 531 net -0.280 % t -3.43; 1h bullish n 458 -0.036 % t -0.43 | no edge on any TF with n >= 300 | Raw divergence is drift; fees eat it. Leads (6h operator bullish n 54 +1.57 % t 2.99; 7h n 46 +1.09 %) are small-n, anchor-dependent (epoch 7h: n 41 +0.47 %) |
| `rsi_divergence_mtf_gated_2026-11-04` run 1 (DEV 2022-01..2024-06, futures, gate = monthly+weekly 60/40 + SMA200) | 11-04 | 164 aligned 15m bull | net -0.176 % [-0.307, -0.045]; ungated -0.161 % (n 973); 1h aligned n 43 +0.111 % [-0.394, +0.615]; 1d n 1 | INCONCLUSIVE (power BLOCK); 0/32 survivors | Gate removed 83 % of events and did not make the signal positive. Bear aligned: 0 events (0 bear weeks) |
| same, LONG window (spot 2017-08..2024-06, Holm m 48) | 11-04 | 482 aligned 15m bull | -0.080 % [-0.216, +0.055]; P40 shorts n 434 -0.158 % [-0.278, -0.039]; 1h n 125 -0.066 %; 4h n 36 +0.185 % | INCONCLUSIVE; 0/48 survivors | 3x history still cannot test the full gate; "more symbols, not another BTC read" |
| `malkan_window_dev_2026-11` (BTC+ETH, 1h/4h, arms S3_10 / B11_12 / C13_18 / D19_50) | 11-06 | 1h S3_10 bear 550, bull 517; 4h 132 / 129; OURS arms 4 events total | 1h bear -0.246 % [-0.443, -0.049]; 1h bull -0.161 %; 4h bear -0.048 %; 4h bull +0.041 % | INCONCLUSIVE (needs ~3227 days, has 405) | The detector cannot test 12/18 (adjacent pivots) |
| `malkan_window_wide_2026-11` (10 symbols, pivot strength 3, count + gate only) | 11-06 | 1h S3_10 2359; B11_12 443; C13_18 487; D19_50 140 | no return read; MDE + cost 0.416 % vs 0.30 % ceiling | BLOCKED | More symbols cannot fix power; lever = fewer repo-wide DEV variants (Holm m 238) or lower-variance exit |
| `rsi_40_60_line_behaviour_2026-11-04` (BTC+ETH spot, DEV 544 trials, VAL 6 picks) | 11-04 | hold/break events 105-6222 per cell; play cells n >= 30: 214 | hold 25-58 %, break 15-51 %; real hold only +1.5 pp vs random walk; 15 of 214 play cells CI > 0 (7 %, chance 5 %); 6 picks on VAL n 2-9 | NO DEFAULT PLAY; all INCONCLUSIVE | RSI 40/60 = coin with a lean, not a wall. Other TF at same line: hold +7 pp (1h) to +18 pp (12h). HTF-aligned bounce holds LESS (-10 to -14 pp) |
| `edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence` (T11/T12, 1h+4h BTC+ETH, 2.5R/48 bars) | 11-09 | 1588 / 1477 | net -0.146 R [-0.228, -0.064] / -0.133 R | FAIL (adequate power, MDE 0.117) | Confluence did not help (no-confluence -0.078 R n 3347). Loses in range weeks (-0.236 R n 1069) |
| `eh-h2-malkan-star-grades` (T02 7-star / T03 5-star, daily BTC+ETH) | 11-09 | 7 / 8 trades | +1.058 R (SE 1.01) / +0.072 R (SE 0.51) | INCONCLUSIVE (n < 30) | Grades too rare on daily BTC+ETH; 7-star driven by 2 winners (2020-09-09 BTC +3.81 R, 2021-06-26 ETH +3.98 R) |
| `eh-o2-phase-lens` T15 (MLK-S1 4h RSI-40 long, accumulation/bull) | 11-09 | 51 | +0.016 R (SE 0.247) | INCONCLUSIVE | Phase label found bears but no edge for the 40 bounce |
| `eh-h5-rsi-ma-cross-trigger` T06 (RSI14 vs its SMA14 cross, 4h) | 11-09 | 1322 | +0.048 R [-0.029, +0.126]; long +0.105 R, short -0.002 R | INCONCLUSIVE (screen fail) | Best leftover on the sim desk; the trigger inside the level-short stack |
| `malkan_level_shorts_2026-11-09` count (BTC 4h, 2017-08..2026-11, target 2R, fee 0.05 % per side) | 11-09 | base 529; div 3-10 close 126; FULL 5 layers 37 | base -0.04 R; div 3-10 close +0.10 R (0.9 SE, 10 arms tried); div 5-50 -0.05 R; FULL +0.13 R (0.6 SE) | no proven edge; paper forward under kill rule | Only his SOURCED 3-10 window is positive; widening to 5-50 kills it; sweep layer filters nothing (482 of 529) |
| `rsi_divergence_mtf_gated` blind read of charts (`REVIEW.md`) | 11-06 | 5 display defects | trades unaffected (diff 0) | n/a | Chart draws only W18 arm; BEFORE=30 dead code |
| `layer_lab/TRIALS.md` rows 10-31: Malkan reverse div WITH the trade, next lower TF (tf_break 15m/1h/4h) | 10-31 | 274 / 131 / 52 | -0.110 % / -0.180 % / -0.384 % | FAIL (Holm p 1.0) | No better than unflagged trades |
| `bear_proxy_context_tuning_2026-11-04` (A: 24 settings x 7 cells; B: 4 TF fake-out filters) | 11-04 | A 69 of 168 rows n >= 30 | 0 CI > 0; 15m picked filter VAL net -0.183 % [-0.312, -0.053] n 642; 4h htf_rsi +0.203 % DEV (n 170) / +0.747 % VAL (n 27), spans 0 | A: no default; B 15m FAIL; others underpowered | Fake-out rate 44-54 % with or without filter |
| `krown_malkan_g3_2026-10-16/EVENT_COUNTS.md` (counts only, BTC daily DEV) | 10-16 | MAL-2 7; MAL-5 25; MAL-10 6; MAL-16 42; MAL-17 35 | none computed; MDE 0.62-1.63 R; +0.10 R needs ~1655 events | THIN | Gate (monthly+weekly > 60) true in few bull stretches; weekly rows < 40 events |
| `malkan_universe_2026-10/UNIVERSE_POWER.md` | 10-18 | n/a (arithmetic) | Nifty 100 recommended phase 1; Nifty 500 for full test; single stock = INCONCLUSIVE in advance | HYPOTHESIS | Data-source table UNVERIFIED (no fetch evidence) |
| `malkan_ledger_2026-10/LEDGER_PARITY.md` | 10-18 | 0 dated calls | cannot score | HYPOTHESIS | He publishes no dated trade record |
| `layer_lab/TRIALS.md` 10-17 `malkan_rsi_event_table` (descriptive) | 10-17 | 132 events (59 long, 73 short) | gross 24-bar MFE 3.18 R vs MAE 3.06 R, no fees | descriptive | MFE about equals MAE |

---
## F. OPERATOR IDEAS (not Malkan's rules): failed vs promising

| Idea (operator words) | Source | Result | Status |
|---|---|---|---|
| "Always calculate divergence properly, the Malkan way: 12 bar, 18 bar, after 18 weaker, closing not wicks" | `OPERATOR_DECISIONS.md:1685-1686` | 12/18 had no Malkan source; relabelled OURS 11-05; arms untestable with adjacent pivots; wide pivots fill bands but power-blocked | Unresolved, not failed |
| BB range-to-range: "when it is ranging, from one end to another repeats; higher ranges as per Tom, by session" (`:1680`) | `bb_range_to_range_2026-11-04/RESULT.md` | 15m range gate, asia/london/ny: 0 of 6 cells > 0, nets -0.12 to -0.15 % CI wholly below 0, target hit 17-28 %; range gate = 80 % of weeks so it does nothing (difference t -0.5) | FAIL (powered) |
| BB long window (3x history, spot) | `bb_long_window_2026-11-04/RESULT_LONG.md` | A: n 9008 / 1560 d net -0.128 % [-0.155, -0.102] ("gate effect -0.010 %, t -1.4"); all six cells -0.115 to -0.165 %, Holm p < 0.001 negative | FAIL again |
| BB retest arm (real return-to-band entry, k x ATR) | `bb_range_retest_2026-11-04/RESULT.md`; ETH pool `bb_range_retest_eth_pool_2026-11/RESULT.md` | fill 59-74 %; nets -0.07 to -0.20 % (BTC), -0.044 to -0.156 % (pool); ETH ny k0.5 +0.011 % one of 27 cells, Holm 1.0 | INCONCLUSIVE (power BLOCK) |
| Bear gate: weekly-only proxy P40; "keep proxy" | `OPERATOR_DECISIONS.md:1694-1698`; `bear_proxy_context_tuning` | proxy marks weeks followed by bounces (0.376 vs 0.423 lower-close rate) | Kept as OURS arm, no default |
| "Cushion/clearance around 40/60 on different TFs; bounce or break? what are other TFs doing?" (`:1725`) | `rsi_40_60_line_behaviour_2026-11-04/RESULT.md` | confluence only factor with consistent effect (+7 to +18 pp hold) but T11 trade -0.146 R | Looks promising as description; FAIL as trade |
| Level shorts at hand-drawn levels (5 marks C1, C2, V1, V2, C3) | `malkan_level_shorts_2026-11-09/READING.md` | all 5 reached >= 1R in hindsight; only V1 fits repo divergence rule; counted base catches 1R only 48 % | Pattern not edge; best arm div 3-10 close +0.10 R (0.9 SE) -> paper forward, kill at 30 trades |
| 2a / 2a': RSI cross above 40 with dwell, RSI-MA support, BB + CVD/OI for shorts (`RSI_2A_SPEC.md`) | `rsi_2a_2026-10-09/RSI_2A_SPEC.md` | spec only; operator Case A / B dwell not in Malkan | Hypothesis |
| RSI deep-buy (buy RSI lows on 1m/15m/1h; confirmations, divergence at lows) | `rsi_deep_buy_2026-10-19/CONFIRMATIONS.md`, `DIVERGENCE_REPORT.md` | 0 of 150 DEV and 0 of 80 VAL rows CI > 0 (chance ~3.8 / ~2.0); raw touch 60m abs20 N=16 +0.565 % [-0.71, +1.84] on 41 days | No confirmation gives a fee-net edge |
| MAL-BB-MID-ENGULF (5m BB midline bounce, bearish engulf, second break) | `mal_bb_mid_engulf_2026-10-16/RESULT.md` | A1 n 1179 net -0.1276 % t -6.02; A2 n 807 -0.1257 % t -4.89; controls no better | FAIL |
| Weekly-low break, bounce, hold under RSI 60 at upper BB (`wlow_bounce_bbrsi60`) | `wlow_bounce_bbrsi60_2026-10-16/RESULT.md` | n = 8 events (< 10), event 4 h net long -0.433 % vs baseline | INCONCLUSIVE |
| Four value-area rules on BTC (acceptance, return-to-liquidity, thin close, naked POC) | `btc_untested_rules_1112/RESULT.md` (found: `research/btc_untested_rules_1112/`) | A n 139 -28.8 bp t -2.75; B n 885 -12.2 bp t -3.90; C n 462 -2.6 bp; D n 50 +4.5 bp t 0.06 (fee 10 bp) | 3 FAIL, 1 INCONCLUSIVE; analyst order-flow rules, NOT Malkan; context only |
| Operator's long-range divergence 11-60 bars (T091) | `rsi_divergence_mtf_2026-10-09/RESULT.md` | no better than Malkan's; 6h/7h bullish leads at n 46-54 only | Lead for multi-symbol rerun |

---
## G. SIM VERIFY (click path)

| Concept | Where / path | Documented? |
|---|---|---|
| A2/A3 RSI 40/60 bounce | Sim desk: `python MyTradingSys/research/sim_desk/desk.py` (opens browser) -> studies list -> "RSI 40/60 (Malkan)" (`sim_desk/studies/rsi.py`) -> choose Chart 1d (trader) / 4h / 1h (ours), Entry BREAK (above signal candle high, trader) or CLOSE (ours), Exit LEVEL (RSI reaches 60/40, trader) or R (ours), tolerance, trend-check bars, fees, dates (window 2022-04-01..2024-06-30 DEV only) -> Run -> numbers strip (win rate, PF, max DD, gross / fee / net) -> breakdown table (year, side, 4-hour UTC block) -> click a trade for the candle chart -> CONDITIONS panel (A vs B on equity curve). Source: `sim_desk/GUIDED_SESSION_PLAN_2026-11-10.md` s2-3; `sim_desk/HANDOVER_SIMV2.md` (daily RSI: 5 setups, 2 filled, both lost; 4h 20 trades, 1h 75, about 0 R net). | Yes |
| A1 GFS gate | Not a desk study; the desk RSI study uses same-TF `malkan_regime`, no monthly/weekly gate. | Not documented as a click path |
| A4/A5 divergence | Not a sim-desk study (only `rsi` study carries Malkan). Divergence charts: `research/malkan_div_flags_2026-11-04/charts/BTCUSDT_1d.png`, `_1w.png` and tables `BTCUSDT_divergences.md` (1d 23 events, 1w 15); per-trade charts `rsi_divergence_mtf_gated_2026-11-04/malkan_div_trade_charts.py` (W18 arm only). Operator wanted the chart to draw lines used (`OPERATOR_DECISIONS.md:1686`; raw card rsi-divergence-chart-draws-used-pivots). | Partial (static charts) |
| A7 stars | Operator's 5 marked shorts appear in the sim page via `sim_desk/census_1109.py` (Malkan level shorts, per-trade candle charts, why-it-failed line; `OPERATOR_DECISIONS.md:2131`). Star grades studies T02/T03 are census rows with "too few events" text. | Partial |
| Live Aid | No Malkan or 40/60 element. RSI14 per timeframe table with <30 / >70 chips; Map verdict uses 3 of 6 votes (VWAP, RSI 1h, RSI 4h vs 50) (`live_aid_review_2026-11-11/RESULT.md:12`; `live_aid_map_2026-11-09/RESULT.md`; `tools/live_aid/live_aid.html`). Live alert side: `live_confluence_feed.py` flags. | Malkan: not documented |
| Guided session | "RSI study on the 4-hour chart" is idea #1 for the guided session (nearest to best leftover T06 +0.048 R n 1322; `GUIDED_SESSION_PLAN_2026-11-10.md` s7). 0.25 R / 30 trades / above luck line = CANDIDATE (s4). | Yes |

---
## H. GAPS, ranked (top 3 marked)

1. **[TOP 1] Universe and timeframe mismatch / power.** His edge claim lives on Indian equities D/W/M; BTC D/W/M gates give n 1-37 per cell (daily MAL rows 6-42), bull weeks 19-20 %, bear 0; +0.10 R needs ~1655 events; every BTC verdict is INCONCLUSIVE. No Indian equity data in repo; Nifty 100/500 basket recommended but the data-source table is UNVERIFIED. Lever stated: fewer repo-wide variants (Holm m) or lower-variance exit; more symbols alone does not clear the gate (`malkan_window_wide_2026-11/RESULT.md`).
2. **[TOP 2] Divergence detector and window fidelity.** Adjacent strict-close pivots only (cannot reproduce hand-read swings; 4 events in OURS windows on BTC+ETH 1h/4h); regular window 3-10 SOURCED but operator's 4h reads are 15-19 bars; 12/18 relabelled OURS yet live feed (`live_confluence_feed.py`) and flag report header still say SOURCED; reverse window (5-14) rests on conflicting quotes; chart marks cover W18 only.
3. **[TOP 3] Gate wiring and exit not his.** The correct level-test gate (`research_kit.regime_tag`) is research-only; live/sim layers use a same-TF 20-bar regime (`live_layers.py`, `studies/rsi.py`) and the testnet calibration entry is "grandfathered, operator decision pending, review_by 2026-10-23" (past). Studies exit after 10 bars (OURS), not his target "C" with 50 % partial and trail, so his exit is untested; bear leg never fires (P40 proxy is OURS).
4. Star grades: 3-star and 7-star conditions withheld; 5-star = secondary-source recap; no dated record (0 calls) so no ledger score.
5. 9 quotes in `MALKAN_RULES_2026-10-31.md` unverifiable (3 videos with no transcript); Hindi verifier broken (non-ASCII normaliser).
6. `rsi_40_60_line_behaviour` finds confluence is the one factor with effect, but no trade version beats zero; HTF-aligned bounce holds less than opposed (unexplained, measured on 2 symbols).
7. Sim desk has no divergence study and no monthly/weekly gate toggle; Live Aid has no Malkan element.
8. Context gap: CBP analyst context and order flow not linked to Malkan layer; phase label (OURS, 112 bear weeks) not wired to any live path.
9. Scenario ledger: no Malkan rows (`research/eagle_eyes_picture_2026-10-28/SCENARIO_LEDGER.md` grep count 0).
10. Costs: studies used 0.10 % (10-09) and 0.14 % (11-04 on); equities delivery trading cost differs.
