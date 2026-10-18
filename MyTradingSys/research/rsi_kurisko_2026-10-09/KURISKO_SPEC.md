# John Kurisko "Quad Rotation" scalp - sourced spec (playbook Part I) - 2026-10-09

Operator ask (verbatim): "What abt John Kurisko strategies? he said there is one that you need to sit and wait patiently. It is a quick get in
and get out scalp - i remember it was 4 rsi indicators with certain params."
Status: layer candidate only. Separate layer, never a Tom filter (Tom is core, PROJECT_VISION). Nothing here is an MTS rule until the operator approves it
(playbook Part I "Consequences": a change backed only by T3 needs explicit operator approval) and our own backtest passes.

## 0. Answer in five lines

1. John Kurisko (DayTradingRadio) has exactly one multi-indicator scalp that fits your memory: the **Quad Rotation** (with the **Super Signal** = quad rotation + divergence).
   It is **four STOCHASTIC oscillators, not four RSIs.** No source I opened ties Kurisko to RSI. [MATCH: sources S1-S5 below; the transcript, the slide deck, the show notes and the AI summary were each checked for "RSI": none mentions it]
2. Settings stated by Kurisko-attributed sources: stochastic (9,3), (14,3), (40,4) or (44,?) [conflict], and (60,10,10). Levels 20 / 80. One position idea: wait for all four under 20, then the fast one turns up.
3. Timeframe 1-minute and 5-minute charts, micro E-mini S&P futures (MES). Patience is part of it: "less is more ... wait for the opportunities".
4. The spec is **not fully sourced** (section 5), so no backtest plan is written. Update 2026-10-18: the clean transcript (S8) closed the period conflict (40) and the stop / exit triggers; the exact stochastic smoothing and the numeric turn-up stay OPEN with labelled OURS defaults (section 5).
5. "4 RSI with params" stays **NO-SOURCE**. If you want the RSI version tested anyway, it has to be labelled "operator hypothesis", not Kurisko.

## 1. Method note (Part I step 1)

What would settle "does a quad-rotation scalp have an edge on BTC": our own pre-registered out-of-sample backtest on BTCUSDT 1m/5m klines with fees (taker 5 bp per side,
repo schedule; 14 bp round trip used in MARKET_GUIDE_RESULTS_2026-10-07.md:20) and funding, IS 70 / OOS 30 plus PBO, per CLAUDE.md gates. External sources here only say WHAT the rule is, never THAT it works.
Searches covered Kurisko-attributed content only. I did not search T1/T2 literature on stochastic-oscillator profitability: **no validated evidence searched or found**, so nothing below may be used as a universal claim.

## 2. Sources, tiers and verification (Part I step 3a: each opened 2026-10-09)

| ID | Source | What it is | Tier | Opened / matched |
|---|---|---|---|---|
| S1 | Desire To Trade podcast ep 472 "The 3 Scalping Setups That Make Me A Living - John Kurisko" (Etienne Crete interviews Kurisko; released 2024-09-16, 43 min), https://podcasts.apple.com/us/podcast/472-the-3-scalping-setups-that-make-me-a-living-john-kurisko/id1037685976?i=1000669724169 ; same recording on YouTube https://www.youtube.com/watch?v=PjigwAmhiT0 | Kurisko in his own words (primary speaker); chapters "quad rotation strategy" 13:22, "concept of divergence trading" 16:20, "Quad Super Signal: the perfect exit" 33:24 | T3 (practitioner, own words) | Apple page opened and title/date/chapters matched. YouTube page opened: title matched, description not retrievable |
| S2 | Auto-captions of S1: https://pickscribe.com/v/PjigwAmhiT0 (ytscribe redirects here) | Full transcript, auto-generated ("93 14344 and 6010", "mees" for MES) | T3, garbled numbers | Opened; title and channel matched to S1; the numbers in it are NOT clean, so they are only used to cross-check S3/S4 |
| S3 | Desire To Trade ep 538 "This Scalping Strategy Makes Me A Living (John Kurisko)", https://www.desiretotrade.com/538-this-scalping-strategy-makes-me-a-living-john-kurisko/ | Show notes of a second Kurisko interview (date not on page): "Deep dive on stochastics (9-3, 14-3, 44, 60-10)", "Quad rotation explained (all stochastics aligned)", "The super signal: quad rotation + divergence", "why the 9-3 at 80 is your cash-out signal", "Timeframes, expectations (1-5 min)" | T3 | Opened and matched. Topic list only; mechanics are not on the page |
| S4 | Slide deck, "John Kurisko's interview on Desire To Trade.pdf", re-host https://www.slideshare.net/slideshow/john-kurisko-s-interview-on-desire-to-trade-pdf/272299238 (uploader famosabazaar, i.e. not Kurisko) | Kurisko's chart blueprint: "Fast Stoch (9-,3)", "Fast Stoch (14,3)", "Fast Stoch (40,4)", "Full Stoch (60,10,10)"; divergence stage rules; stops; partial exits | T3 (re-host of a practitioner deck) | Opened and matched. The DTT original https://www.desiretotrade.com/wp-content/uploads/2020/07/Podcast-Interview-slide-show.pdf (46 pages, 89 images) opened but has no extractable text, so I could not match it page by page |
| S5 | Lilys AI note https://lilys.ai/en/notes/211149 | AI summary of S1 (states itself "garbled" numbers) | T3 secondary; cross-check only | Opened; it matches S2 where both are readable |
| S6 | https://home.daytradingradio.com/ | Kurisko's commercial site | Vendor page; no rule content | Opened: mentions "Quad Rotation" only as a scanner/alert feature for members |
| S7 | TradingView "JK Scalp" by nishith85441 (2025-12-16), https://kr.tradingview.com/script/1TTBunq7-JK-Scalp-Nishith-Rajwar | Third-party implementation: Fast (9,3), Medium (14,3), Slow (44,3), Trend (60,10,10) | T3 community, NOT Kurisko | Opened. Source code not shown; it does not name Kurisko or RSI in the text I read |

Findings are tagged `Tier | method | confidence` below. None of S1-S7 shows any backtest, so method quality is "none: stated rules only".

## 3. The rule as stated (what each source says)

| Element | Statement | Sources | Tag |
|---|---|---|---|
| Concept | Four stochastic "bands" on one chart. A **quad rotation** is when all four are oversold, under 20, at the same time: "when all each one of these bands get oversold under 20 at the same time that is what we call a quad rotation" | S2 (quote), S3, S4 | T3 / none / M |
| Super Signal | Quad rotation merged with a (price vs stochastic) divergence. Kurisko calls the combination his "Holy Grail" (win-rate claims such as "95%" are his own and have no data: REJECT as evidence) | S2, S3, S4 ("The Super Signal is a merger of a quad rotation and an" - truncated) | T3 / none / M |
| Stochastic 1 (fast) | (9,3); slide label "Fast Stoch (9-,3)" (OCR artefact for 9,3) | S4, S3 "9-3", S2 "nine candles", S7 | T3 / none / H for the pair 9,3 |
| Stochastic 2 | (14,3) | S4, S3, S2 "14 candles", S7 | T3 / none / H |
| Stochastic 3 | **CONFLICT**: (40,4) in S4 and S2 "40 candles"; "44" in S3 and in S2's digits ("14344"); (44,3) in S7 | S2-S4, S7 | T3 / none / L |
| Stochastic 4 (trend) | (60,10) in S3 / S2; (60,10,10), "Full Stoch", in S4 and S7. Role: it represents the 5-minute timeframe inside a 1-minute chart ("the 6010 is the five minute time frame") | S2, S3, S4, S7 | T3 / none / H for 60,10 |
| Levels | Oversold < 20, overbought > 80. In bull setups the 60/10 should be above 80, "preferably 90" ("above 85 preferably 90") | S2 | T3 / none / M |
| Entry (divergence / quad) | Enter right when the fast (9,3) turns back up: "you take that trade right when you see that turn back up". Divergence stage 1: stochastics under 20; the low bounces them back above 20; price then makes a lower low / double bottom while the stochastic makes a higher low | S2, S4 ("Stage 1 on the divergence should have the stochastics under the 20") | T3 / none / M |
| Entry (bull flag, a separate third setup) | After a strong push off the 20 EMA, 60/10 stays above 80, buy when the fast stochastic hits 20 | S2 ("you buy when the 93 hits the 20"), S4, S5 | T3 / none / M |
| Higher-timeframe confirmation | "5 Min and/or 60 Min stochastics should be moving up (preferred) off oversold"; chart legend lists 1 Min, 5 Min, 60 Min, D | S4 | T3 / none / L |
| Stop | S2: "one to two ticks under the pattern low candle"; S4: "1 tick under the divergence candle". Tick-based on MES (0.25 index point); no percent or ATR form is given | S2, S4 | T3 / none / M (1 vs 1-2 ticks conflict) |
| Exit | Sell each fast (9,3) rotation above 80 ("you need to sell every rotation of the 93 above 80"); partial profit when the fast stochastic crosses back above 80, stop moved up. Chapter "Quad Super Signal: the perfect exit" (S1 33:24) | S2, S3, S4 | T3 / none / M |
| Timeframe / market | 1-minute and 5-minute charts for scalps; micro E-mini S&P (MES) mainly; daily charts for longer trades. Context tools named in S5: 20/50/200 EMA, VWAP, hand-drawn support/resistance | S2, S3, S5 | T3 / none / M |
| Waiting | "less is more you know wait for the opportunities"; "you got to only take the Divergence setups"; slide: "You have to be ready when the trade appears" and "Most of the great setups appear in channels" | S2, S4 | T3 / none / M |
| Shorts | The mirror (all four above 80) is described only by community text (S7: "below 20 or above 80"). Kurisko's own words I read give long examples plus "sell every rotation above 80" as an exit | S7 | community only: treat the short side as NO-SOURCE until his words are matched |

## 4. About the "4 RSI" memory

- NOT_IN_DATA: no opened source says Kurisko uses RSI. The full transcript text (S2), the slide deck text (S4), the show notes (S3) and the AI note (S5) do not contain "RSI".
- Closest RSI link on the open web: the TradingView script "Multi Stochastic Alert" by IMStockwala (2025-01-30), https://cn.tradingview.com/script/SSUHdyuV-Multi-Stochastic-Alert/ . It uses the same four stochastics (9,3), (14,3), (40,4), (60,10), says "Trade entry become active when all of these goes below 20 or above 80", and adds "we wait for RSI Divergence and we enter". Its author is IMStockwala, not Kurisko; the name Kurisko appears only as a page tag. This is a plausible origin of "four indicators + RSI" in memory (hypothesis, not established).
- Therefore: "4 RSI indicators with certain params" = NO-SOURCE. Do not create RSI parameters and attribute them to Kurisko.

## 5. Gaps after the transcript extract (task kurisko-transcript-extract, 2026-10-18)

New primary source (S8): the full auto-caption transcript of S1, `raw_transcripts_canonical/PjigwAmhiT0_raw.txt` (8,940 words; body is line 8, one line, no timestamps; fetched with `fetch_captions.py` on the 3rd try after two RATELIMIT runs). Quote-gated extract: `extracts/processed/kurisko/QUAD_ROTATION.md` (44 quotes, rules R1-R11; `verify_extract_quotes.py` exits 0; a copy with one doctored quote exits 1). "R-ids" below point to that extract; every quote there carries its character offset.
S8 supersedes S2 (the summariser copy). **"RSI" and "relative strength" occur 0 times in S8**, so section 4 stands: "4 RSI with params" stays NO-SOURCE.

Label rule (CLAUDE.md "Numbers"): SOURCED = his words, quote in the extract. OURS = our judgement for the module card: chosen on DEV only, checked once on VALIDATION, holdout read once, every variant entered in the trial ledger. OURS is never called Kurisko's.

| # | Gap | Status | His words (SOURCED) | OURS default for the module card |
|---|---|---|---|---|
| 1 | Third band (40,4) vs 44 | **CLOSED for the period (40)**; **OPEN for the smoothing d** | R1: "These are 40 candles and these are 60 candles" in the list nine / 14 / 40 / 60, which matches the k periods of the other three bands. The caption digits "93143 444" and "9314344" read as 44, but they are also how "forty-four" (= 40,4) transcribes, so they do not prove 44. d = 4 is written only on slide S4 (re-host, unmatched). | Third band (40,4). Variant (44,4) as a sensitivity run in the ledger. |
| 2 | Exact stochastic formula | **CLOSED for the concept**; **OPEN for k / d / slowing roles** | R8: close inside the high-low range over a lookback, scale 0-100; "here I'm using the D line. And the D line is the signal line" (he plots D); platform NinjaTrader. Nothing on slowing or smoothing. | Raw K_n = 100 * (C - LL_n) / (HH_n - LL_n); plotted line = D = SMA_d(K_n) for (9,3), (14,3), (40,4); for 60,10 (his words give two numbers): D = SMA_10(K_60). Variant: slide's (60,10,10) as slowing 10 + D 10. FORMULAS.md needs a stochastic section with a hand-computed example before any code. |
| 3 | "Turns back up" | **PARTLY CLOSED**: it is the 9,3 line, a visual turn; **OPEN** as a number | R3: "a visual confirmation of the upward return of the Stoastic 93 which triggers the divergent signal"; "Take that position right when you see that retracement"; Super Signal stage 3: "the stochastics on the 93 rise above the 20 line". | Signal bar t: all four D_i[t-1] < 20 and D9[t] > D9[t-1]; enter at the close of t. Variant: D9 crosses up through 20 (the stage-3 wording). |
| 4 | Divergence rule | **CLOSED for the structure**; **OPEN for swing detection** | R3: stage 1 all four under 20; stage 2 price and the 9,3 "bounce a little bit"; stage 3 price "drops back to or below the last price of the first phase" while the 9,3 rises above 20. No bar counts. | Module v1 = plain quad rotation, no divergence. Super Signal card later: L1 = lowest low while all four < 20; bounce = D9 closes above 20 once after L1; stage 3 = a later bar with low <= L1 and D9 > 20, within 60 bars of L1 (OURS, tune on DEV only). |
| 5 | Stop, exit, BTC translation | **CLOSED for stop and exit trigger**; **OPEN for translation, size, caps** | R4: "place your stop one or two ticks below the low candlestick of the pattern" (the 1-vs-2-ticks conflict is his own: "one tick" appears too). R5: when the 60,10 is stuck low "you need to sell every rotation of the 93 above 80"; no clock ("Sometimes it moves fast, sometimes slow"). R7: "three setups a day" is a remark inside a question, not a cap. No sentence on position size, partial profit, stop trailing, or what to do when the 60,10 is above 80. | Stop = pattern low minus 1 tick of the traded symbol; skip the trade if that stop distance is under the 14 bp round trip (F-BT-22; OURS gate). Exit = close of the first bar with D9 >= 80; variant: only while D60 < 80. No time exit, no daily cap, no partial exit in v1; fixed notional per trade; report trades per day. |
| 6 | Short side | **CLOSED that shorts exist**; **OPEN for the numeric mirror** | R10: "take your short and put your stop right at the highs"; "The same thing goes for the downside here"; naked flag (60,10 low, price under the 200 EMA): "simply selling every time it goes up there". He never states "all four above 80". | Mirror arm: all four D > 80 and D9 turns down, stop 1 tick above the pattern high, exit at D9 <= 20. Separate arm in the ledger, reported apart from the long arm. |
| 7 | Primary text quality | **CLOSED** | S8 is in the repo and quote-gated. Caveats: auto-captions garble digits and names ("Stoastic", "square rotation" = quad rotation, "MEES" = MES); no timestamps, so the Apple chapters (13:22 / 16:20 / 33:24) cannot be mapped to lines. | none needed |

Not in S8 (stay T3-unverified, from S4 only): the 5 min / 60 min confirmation row and the partial-exit wording in section 3. They are not Kurisko-sourced until the slide image is matched. His win-rate claims ("it will work 95% of the time", "eliminate 50% of the losers") are REJECT as evidence (R11, R5).

Next step for the module card: add the stochastic section to FORMULAS.md (hand-computed example), then write the card with the OURS defaults above; the long arm of the plain quad rotation can be pre-registered first.

## 6. Fit to MTS (analysis, not a plan)

- Market mismatch: Kurisko's stops are 1-2 ticks on MES during US cash hours; the repo's cost model is taker 5 bp per side. A few-bp stop on BTC 1m is under the 14 bp round-trip cost, the situation the roadmap already calls fee-dominated ("49-100 % fee-dominated (stop under round-trip fee, F-BT-22)", research/CONSOLIDATED_ROADMAP_2026-10-09.md:27-28). Expect the same problem unless the trade targets more than a few bp.
- Closest sibling already tested: generic RSI/volume events NO-EDGE (RSI_HISTORY.md section 4). A stochastic quad rotation is untested in the repo (grep "stochastic" over .md/.py found only DIVERGENCE_AUDIT, VVP-001 "Stochastic: Not a Tom concept", BT_SPEC and a Krown note).
- Isolation: if built, it is a new layer under `backtest/layers/` with its own params file (`source` = "Kurisko S1-S4"), no import of Tom constants, no use as a Tom filter, alert-only first.
- Backtest plan: **not written** (condition "only if the spec is fully sourced" is not met). Preconditions to write one in under a page: close gaps 1-4 above, add a stochastic section to FORMULAS.md with a hand-computed example, and have the operator decide gap 5 items (stop, exit, BTC translation) as explicit operator parameters.

## 7. Rejected / not used (listed once so they are not researched again)

- forex.in.rs "John Kurisko's Trader Strategy" and companion article: seen only in search results, not opened (cannot be matched), and the snippet's "four stochastics on four timeframes" contradicts S2/S4. REJECT.
- cTrader "Stoch PRO Quad Rotation Signal" and the unattributed TradingView "Quad Rotation Stochastic": vendor listings, not opened, no Kurisko words. REJECT.
- Generic RSI scalping blogs (RSI 5/7/9 with 80/20, 75/25, etc.): no author tie to Kurisko. REJECT as Kurisko evidence.
- Kurisko's own performance claims ("95 percenter", "Holy Grail", "works 95% of the time"): win-rate claims without costs or method. REJECT.
- Spotify / Podbean / iHeart / Everand listings of the same episodes: duplicates of S1/S3, not needed.
