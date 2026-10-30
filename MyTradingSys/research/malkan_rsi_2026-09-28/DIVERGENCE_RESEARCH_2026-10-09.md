# Malkan RSI divergence - research + audit of existing code (2026-10-09)

Status: RESEARCH ONLY. No code changed. Provenance rule applies: every rule below is tagged
[M] = Malkan's own words (transcript + video id), [3P] = third party, NOT Malkan, [?] = unresolved.
Only [M] items may become engine parameters.

Transcripts held (raw_transcripts_canonical/): cQ-y1oULkBw (Divergence Trading Strategy, 2023),
Wvq1TZh8aF0 (RSI Divergence masterclass, 2026-04), 2HcJ3NeZmEQ (5-star SELL setup, 2019; mislabeled
as reverse-divergence in the web shortlist), -CBvFi40sIQ (Samco screener video, secondary).
NOT held (YouTube 429 rate limit during this session): "RSI reverse divergence (best)", "Types of Divergences"
(M8Z3A6mcUmE), "3X3 Swing Trading RSI divergence" (gfr5n6B5QJk), mE1aeHulb-4, A-CQiV_UFB4, W1HrDl70Lhk.
A background fetch (scripts/dev/fetch_captions.py) keeps retrying; re-run it later.

## 1. Regular divergence - what Malkan says [M]

| Item | Rule | Source |
|---|---|---|
| Bullish (positive) | Price lower low (A to B), RSI higher low. Appears in a DOWNtrend, gives a BUY (contra-trend) | Wvq1TZh8aF0 |
| Bearish (negative) | Price higher high (A to B), RSI lower high. Appears in an UPtrend, gives a SELL (contra-trend) | Wvq1TZh8aF0 |
| Compare on | CLOSE to CLOSE (RSI is built on close). Uptrend: green candle to green; downtrend: red to red, at closing price | both |
| Which extreme | Down trend -> compare the LOWS (lowest RSI vs lowest close). Up trend -> compare the HIGHS. This is your remembered rule | both |
| Finding it | Mark the highest/lowest RSI in the window, then check whether price extreme is at the same bar; if not, divergence | Wvq1TZh8aF0 |
| Minimum length | 3 bars (up, down, up). Best 3/5/7, at most ~10 bars. 15-50 bars = diluted, will not work | both |
| Where | Most powerful: bullish near RSI 40, bearish near 60. 20-30 / 70-80 also occur but reverse divergences often negate them | Wvq1TZh8aF0 |
| Decimals | 37.7 vs 38.9 counts; small differences are acceptable | Wvq1TZh8aF0 |
| Confirmation (entry) | Bearish: wait for a red candle, short below its low. Bullish: bullish candle, buy above its high. Weekly divergence is confirmed/entered on the daily chart | Wvq1TZh8aF0 |
| Stop | Beyond the signal candle extreme incl. shadow (bearish: above high; bullish: below low) | Wvq1TZh8aF0 |
| Target | "C", a point between A and B. Exit when reached; at least 50% (said "50% to 35%") | Wvq1TZh8aF0 |
| Risk:reward | Take only if >= about 1:3 / 1:4 | both |
| Trailing | Trail stop under higher candle lows; do not extend past the divergence target | Wvq1TZh8aF0 |
| Repeat | If stopped and a 2nd/3rd divergence forms while higher-TF RSI holds, re-enter | Wvq1TZh8aF0 |
| 7-star | Buy: monthly RSI > 60 + daily RSI < 40 + bullish divergence on daily. Target = 2x the ABC target, same stop | Wvq1TZh8aF0 |
| 5-star (not divergence) | Long: monthly >= 60, weekly >= 60, daily RSI at 40 support, enter above signal-candle high, stop below its low. Short: monthly < 40, weekly < 40, daily near 60 | -CBvFi40sIQ, 2HcJ3NeZmEQ |

[?] Unresolved in Malkan's words: exactly what "C between A and B" is (midpoint of A-B, or the intervening
swing extreme between the two pivots, as in Kapil Mokashi's Cardwell projection); the mirror 7-star SELL
(monthly < 40 + daily > 60 + bearish divergence is implied, not stated); how Malkan counts "bars" (A to B inclusive?);
whether divergence is read on a weekly bar or only its daily confirmation; Class A/B/C divergences ("three different
types", promised for another video).

## 2. Reverse divergence ("reverse positive / reverse negative")

Malkan: says it exists and is a separate topic with its own videos ("there is another concept called reverse
divergence", Wvq1TZh8aF0) and that reverse divergences negate far-extreme (20/80) regular divergences. His course
outline lists "Reverse Divergences and Price targets". NO definition in the transcripts we hold. [?]

Third-party definition (the same one everyone uses; Malkan's names "positive/negative reverse" match it) [3P]:

| Name | Price | RSI | Trend context | Compare | Meaning |
|---|---|---|---|---|---|
| Positive reverse (bullish, "hidden bullish") | HIGHER low | LOWER low | UPtrend pullback (RSI often holds 40-45) | the LOWS | continuation up |
| Negative reverse (bearish, "hidden bearish") | LOWER high | HIGHER high | DOWNtrend bounce (RSI stalls 55-60) | the HIGHS | continuation down |

Sources: kapilmokashi.substack.com/p/rsi-reverse-divergences (entry = break of the intervening peak/trough,
target = Cardwell projection, stop = beyond second pivot, inferred); TradingView idea Jtju0Vxf (aks85, 2016).
This matches your memory: uptrend -> compare lows; downtrend -> compare highs. The two families:

    regular   bullish: DOWNtrend, compare lows, price LL / RSI HL  -> reversal up
    regular   bearish: UPtrend,   compare highs, price HH / RSI LH -> reversal down
    reverse   positive: UPtrend,  compare lows, price HL / RSI LL  -> continuation up
    reverse   negative: DOWNtrend, compare highs, price LH / RSI HH -> continuation down

Confusion to avoid: "positive/negative divergence" (Malkan: = bullish/bearish regular) vs "positive/negative reverse"
(= bullish/bearish hidden). Some TA writers call hidden "positive reversal". Keep the four names above as the enum.

## 3. Errors in our existing documents/code

1. WEB_RESEARCH.md lines ~190-191 define divergence WRONG: "positive: price lower low while RSI higher HIGH",
   "negative: price higher high while RSI lower LOW". Correct: positive = price LL + RSI higher LOW; negative = price HH +
   RSI lower HIGH. Fix before anyone codes from it.
2. WEB_RESEARCH.md "7-star = previous 3 days RSI > 60" is a Chartink user screener, not Malkan. Malkan's 7-star
   (Wvq1TZh8aF0) is monthly > 60 + daily < 40 + divergence. Treat the Chartink one as [3P].
3. No RSI divergence code exists in MyTradingSys/backtest/layers/rsi/ (only 40/60 bounce, level events, MA events,
   MTF gate). Divergence in the repo is CVD/OI only (positioning/funding_cvd_fade.py). So "implemented correctly?"
   = not implemented; the Malkan RSI layer covers the 5-star family only.
4. malkan_40_60.py self-contradiction (verified by running it): setup fires on rsi_events "support" with a +/-2 band
   (38-42), but the BULL regime gate requires min RSI over 20 bars >= 40. A real dip to 39.5 (the normal "RSI takes
   support at 40") is classed RANGE and the signal is dropped; only dips that stay >= 40 survive. Bear mirror has the
   same problem. Malkan's 40/60 words are about where RSI turns, not a 20-bar min/max window; lookback=20 and tolerance=2
   are NO-SOURCE (provenance rule).
5. malkan_mtf.py: gate uses weekly/monthly "regime" (20-bar window) but Malkan's gate is a LEVEL test: monthly RSI >= 60
   and weekly RSI >= 60 (bull) / both < 40 (bear). On monthly bars lookback=20 means 20 months of history. Docstring of
   malkan_mtf_bear says "resistance" but the event is "rejection" (docs only).
6. No entry/stop/target is emitted by the 5-star code: Malkan's entry above signal-candle high, stop below its low,
   daily target RSI 60 (blog) are not implemented.

## 4. Proposed divergence module (spec for the next step, not built)

- Pivots on CLOSE and on RSI(14) close; swing = bar whose close is lower (higher) than both neighbours [M: "one up, one
  down, one up"]. A and B pivots at least 2 bars apart.
- Regular bullish/bearish and reverse positive/negative as the four-value enum above; each event carries
  A_idx, B_idx, bars_between, rsi_A, rsi_B, rsi_at_B (zone flag near 40/60), strength tier (<=10 bars [M]).
- Trend context for the choice of lows vs highs must itself be sourced; Malkan only says "in a down/uptrend".
  Candidate sourced proxy: the 40/60 range-shift regime [M, range shift videos] - to be confirmed, otherwise explicit input.
- Confirmation candle, stop beyond signal candle (incl. shadow), target C, min R:R 1:3, higher-TF gate (7-star) as
  separate layer outputs. Params with no Malkan quote stay NO-SOURCE flags, not tuned numbers.
- Visual check before trust (VVP): plot price + RSI with A/B marks on real BTC 1h/4h/1d for ~20 hand-picked cases,
  compare with Malkan's chart examples from the videos.

## 5. Prompt for ChatGPT / Gemini / Grok (could not be sent from here: Chrome extension not connected, no logins)

"Vishal B Malkan (Malkansview, India) teaches RSI(14) divergence. Using only his own videos/courses (Hindi or English),
not generic TA, answer with video title + timestamp for each: (1) His exact definition of reverse positive divergence and
reverse negative divergence: price pivots, RSI pivots, which extremes (lows/highs) he compares in an uptrend vs a downtrend,
close vs wick. (2) Entry candle, stop, target (what is point C between A and B), and R:R for regular AND reverse
divergence. (3) The 5-star and 7-star setups, including the SELL mirror of 7-star. (4) Max bars between pivots, RSI zones
where each divergence is strongest (40/60), and Class A/B/C divergence definitions. (5) How reverse divergence negates
regular divergence at 20/80. Mark anything you cannot source as UNKNOWN; do not infer."

## 6. Next steps

1. Re-run fetch_captions for 2HcJ is done; still needed: M8Z3A6mcUmE, gfr5n6B5QJk, mE1aeHulb-4, A-CQiV_UFB4, W1HrDl70Lhk,
   kVIvcn7T44o, N7r3v7plqZM, plus "RSI reverse divergence (best)" id (find via his playlist) - after the 429 clears.
2. Fix WEB_RESEARCH.md items 1-2 (needs your OK; it is a research doc, not live path).
3. Run the prompt in section 5 through the three AIs and paste answers back; treat as [3P] until a Malkan quote confirms.
4. Then: extract quotes -> verify_extract_quotes.py -> test plan from FORMULAS.md-style definitions -> Sonnet builds divergence.py
   (staged .new) -> chart render check -> gates.
