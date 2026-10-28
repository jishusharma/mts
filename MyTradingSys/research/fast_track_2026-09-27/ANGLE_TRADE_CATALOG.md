# ANGLE: GROUND-TRUTH TRADE CATALOG (2026-09-30)

Purpose: collect the traders' ACTUAL trades as labeled examples so the engine can later be replayed
at those moments. Scope: all 102 files in raw_transcripts_canonical/. Script: scratchpad/catalog/rank.py
(marker-count ranking), then manual reading of every trade-rich transcript. Nothing in the repo was edited
except this file.

## 1. Headline answers

- Trader map (by extract membership): TOM = 57 files (48 in extracts/fresh/, 9 in extracts/processed/tom/new_selected_10/);
  FABIO = 7 (list given); OTHER = 38 (see section 5). Many OTHER files are Tom-style channel uploads (same voice, title
  "World Champion ...", speaker name garbled by auto-captions as Forgald/Forwald/Polwad) that are NOT in his extract set;
  they contain no trades taken, only sizing illustrations. Flagged as unverified.
- Concrete trades found (actually taken, per the speaker): TOM 21 unique rows, FABIO 9 rows. Plus 1 duplicate (same Avis
  trade told in two videos), 10 illustrative/plan rows (marked ILLUS, not counted).
- (a) LONG vs SHORT. TOM: 15 short, 6 long (29% long). Of the 6 longs, 2 are anti-examples (crude oil 2020 dip buy and a
  weekend gap loss, both told as his worst losses), 2 are the crude-oil long + re-entry in one live session, So his own described setups are
  ~70% short (counter-trend fades at highs / no-liquidity tops), and real longs are rarer and mostly pullback buys
  1 DAX Monday-gap pullback long and 1 buying-tail long. FABIO: 6 short, 1 long, 2 side-unstated/mixed (9 rows). Caveat: rows are
  trade-groups; Fabio's 0jM5Y31YJak alone covers ~5+ scaled short positions, so the true short share is higher.
  Conclusion: a short-only engine can in principle cover ~70-75% of described Tom trades and ~85% of Fabio's, but it
  cannot be scored on the Tom longs (6 of 21, or 4 of 21 if the two crude-oil anti-examples are dropped).
- (b) BTC with a replayable date: ZERO. No trader in these 102 transcripts describes taking a BTC trade. Tom uses Bitcoin only
  as a lead/risk-on indicator ("my leading indicator, which is currently Bitcoin"); Fabio's LQvv5xgy_ik and StaphlRH8NQ
  mention a BTC long-term accumulation model (MVRV), not trades. Instruments actually traded: DAX future (8 rows), AVIS stock
  (2), crude oil (4), Nasdaq (Tom 2, Fabio 5), S&P (1), not stated/unnamed (Tom 4, Fabio 2 of 9 rows). Dates: essentially none stated. Only date
  statements: Fabio "30 of December" (no year), Fabio "best session of December/October" (no year), Tom crude oil
  inferred 2020-04-20 (inference from the WTI negative-price event). Video publish dates (2025-11 .. 2026-07) are only an
  upper bound for "yesterday/last week" trades. So ground-truth replay against history is NOT possible from these
  transcripts; the exact dates would have to come from the traders' chart screenshots/trade logs.
- (c) Recurring setup names (videos mentioning / total mentions, Tom's 57 files, regex counts are approximate):
  liquidity-absence/"no liquidity at the top" (42/304), balance vs imbalance (44/189), counter trade / counter-trading (32/108),
  value area (26/73), pullback (27/58), footprint (28/59), VPOC/point of control (21/36), single prints (19/38),
  gaps (20/119), PBD logic (13/18), B profile/B setup (9/12), P profile/P setup (6/7), short squeeze (4/11), unfinished
  auction (3/12). Named entry setups he actually uses in taken trades: "B setup/B profile pullback" after a failed push
  into no-liquidity highs (zQTb, tS6Z, OUM9, k0zm5), "P profile" exhaustion short (T6hD), limit sell below the last
  volume step (yRvM), pullback to prior-day value/POC with buying tail for longs (4MoN, UOBg). Fabio's vocabulary:
  "big trades", "punch to the wall"/absorption, CVD distribution/accumulation, volume spread analysis, scale/reload with
  stop to break-even, "sell model day"/auction market theory.

## 2. Method and honesty notes
- Ranking: regex marker density (I'm in / stopped / stop / target / entry / ticks / points / risk / NR / long / short /
  4-5 digit prices / contracts / BTC) per 10k chars; top of the ranking was then read. Every transcript with any
  marker hit was scanned with a sentence extractor; the ~20 trade-rich ones were read in full or by windows.
- Line numbers are file lines; most Tom transcripts are 7-19 physical lines of several thousand characters, so position
  is given as L<line> ~<percent through the body> (the same thirds tag the verifier uses).
- "not stated" = the speaker does not give it (Tom refers to the chart: "here", "up here"). No price or date is
  invented. Inferences are marked "inferred". Prices like "690" are as spoken (leading digits dropped by captions).
- Tom rarely gives entry prices; Fabio gives level mentions and $ risk/reward rather than entries. Expect the
  replay to need trader-side chart data for exact levels.
- Row types: TOM/FABIO = trade actually taken; TOM-DUP = same trade as an earlier row (not counted);
  *-ILLUS = hypothetical or planned example (not counted).

## 3. Catalog (one row per trade; verbatim quotes in section 6, keyed R<n>)

| # | video | pos | trader | instr | date | side | entry | stop | target | outcome | setup |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | tS6ZEiHj8gQ | L19 ~55% | TOM | AVIS stock (Nasdaq) | not stated | short | 640 | 730 | ~250 (last big volume) | stopped out | short-squeeze fade; consolidation after exponential volume |
| 2 | tS6ZEiHj8gQ | L19 ~91% | TOM | AVIS stock (Nasdaq) | not stated; next day gap down | short (re-entry) | not stated | risk $35-40 | 250 | win ("that one worked") | B profile after gap down; smaller stop, bigger size |
| 3 | WSCIURybK3U | L19 ~28% | TOM-DUP | AVIS stock | not stated | short | 630 | 730 | 230 | risk math only (RRR 4); result not given | counter trade, 30% win-rate framing |
| 4 | kXhIAug0Gh8 | L19 ~31% | TOM | S&P future (ES inferred) | not stated (live session) | short | not stated | trailed to the high | taken (RRR ~4) | win, take profit hit | balance/value-high rejection after gap away from prior day; selling overhang |
| 5 | kXhIAug0Gh8 | L19 ~55% | TOM | Nasdaq future | same session | short (limit order; inferred: "same game as before") | not stated | not stated | hit | win, RRR 8 | second limit order after balance formed |
| 6 | kXhIAug0Gh8 | L19 ~76% | TOM | crude oil | same session | long | not stated | ~9246 (bad spot) | not stated | loss: stopped 2 ticks lower than stop | buy at prior-day value area / VPOC zone |
| 7 | kXhIAug0Gh8 | L19 ~85% | TOM | crude oil | same session | long (re-entry) | not stated | below last swing low | not stated | win, exited early (price ran much higher) | re-entry on buyer stability |
| 8 | zQTbdEweG3c | L19 ~69% | TOM | DAX future | not stated (week after DAX surge; publ. 2026-07-08 upper bound) | short | not stated | not stated | 24,400 first, then profile VPOC | result not stated (title: $4,720 in 15 min) | counter-trend; liquidity gap + B setup pullback + POC |
| 9 | ujedEcmvBMk | L13 ~29% | TOM | DAX future | not stated (today's session) | short | pre-market highs | ~18,257-258 area | ~411 range | stopped once, re-entered, partial take, rest running | weekly-profile short bias; VPOC; intraday gap as target |
| 10 | ujedEcmvBMk | L13 ~59% | TOM | DAX future | same session | short (re-entry) | at low volume | not stated | ~411 range | partial take, rest open | re-entry after stop flush |
| 11 | T6hDJcHrVBM | L13 ~59% | TOM | DAX future | "yesterday" (no date) | short | 690 (DAX level, leading digits cut) | moved to 650 | TP1 ~260 pts away; TP2 184 | open; 1 position taken, rest left to run | P-shape exhaustion at open spike; inside bar; PBD |
| 12 | UOBgXV20yCM | L7 ~36% | TOM | DAX future | "yesterday", a Monday | long | not stated | not stated | ~80 pts planned, RRR exactly 3 | target hit; market then ran 700 pts | gap + P profile + pullback buy signal |
| 13 | yRvMW6lgN1o | L19 ~12% | TOM | index future (S&P-like, levels ~6,763-6,768; not named) | not stated; publ. 2025-11-19 | short (sell limit) | limit below last volume step | 12 ticks risk | 97 ticks; 6,768 | win: $250 risk, ~$1,212 gain | smart S/R zone; inside day at ATH; limit below volume step |
| 14 | k0zm5NYn0IQ | L19 ~4% | TOM | DAX future | not stated; publ. 2026-02-04 | short | not stated | 20 points | below morning liquidity | stopped out | counter trade at highs, no liquidity above |
| 15 | k0zm5NYn0IQ | L19 ~40% | TOM | DAX future | same session | short (re-entry) | not stated | initial stop $500 (as said) | ~285 area; partial | partial profit, rest stop 310 area; good day | finished auction + liquidity gone |
| 16 | OUM9LYwL8eA | L19 ~78% | TOM | Nasdaq future (S&P alongside) | day after Nvidia earnings (no date) | short | not stated | not stated | RRR 1:6 and 1:4.5 | win (title: $20,500 in 2 hours) | B profile top after earnings gap; 2 outside + later short |
| 17 | 4MoNjEQ2Dd8 | L19 ~4% | TOM | not stated | not stated; publ. 2025-12-31 | long | not stated | ~100 ticks risk vs 161 | above highs (620 level) | win (title: $2,350 in 40 min) | buying tail + pullback to PC; order-flow breakout |
| 18 | n7ZSkjb7JXs | L19 ~26% | TOM | DAX future (+ gold future short) | this morning, pre-market; publ. 2026-01-14 | short | not stated | above volume bell | first TP at air pocket | partial take, rest open (title: $3,400 in 30 min) | no liquidity at top; pre-market |
| 19 | l8RZrBfzvp4 | L13 ~77% | TOM | not stated (gap product; DAX-like) | not stated | short | not stated | n/a | prior-day value area | first try stopped -1R; second won 4R | gap exaggeration close; route planning |
| 20 | wPMiyJXL0zU | L19 ~45% | TOM | not stated | not stated; publ. 2025-11-11 | short (inferred: counter-trade vs uptrend) | not stated | ~15 pts | current-day VAH, ~80 pts planned | closed early by design | counter trade held as "long-term trade" up to an hour |
| 21 | dh-ysRR8f-M | L19 ~42% | TOM | crude oil (WTI) | inferred 2020-04-20 (price 14-16, fell to minus $40) | long | 14-16 range | none | n/a | very large loss ("biggest loss") | buy-the-dip into storage crisis (anti-example) |
| 22 | dh-ysRR8f-M | L19 ~14% | TOM | crude oil | weekend after a Putin post (no date) | long | n/a | n/a | n/a | gap down loss | held long over weekend (anti-example) |
| 23 | WSCIURybK3U | L19 ~54% | TOM-ILLUS | DAX future (hypothetical) | n/a | short | n/a | 24,220 | 24,120 | illustration of position sizing | "trading idea" for risk table |
| 24 | BVpYGKz9PBU | L19 ~73% | TOM-ILLUS | not stated (plan) | n/a | short | 260 | ~305 (20 pts in tight case) | 140 | plan only | B profile in value area after rejection; counter trade |
| 25 | 3o1VVsfBmmU | L19 ~56% | TOM-ILLUS | not stated | n/a | n/a | n/a | 10 ticks | 70 ticks | RRR 7 example | footprint entry example |
| 26 | 0jM5Y31YJak | L4 ~43% | FABIO | NASDAQ | "30 of December" (year not stated) | short (pos 1) | at first volume follow-through candle | to break even quickly | ~1:3 to 1:5 | win | CVD distribution + big trades + price follow-through |
| 27 | 0jM5Y31YJak | L4 ~77% | FABIO | NASDAQ | same day | short (positions 2-5, trailed) | not stated | trailed | not stated | wins; half of profit re-risked | continuation in redistribution phase; sell model day |
| 28 | 0jM5Y31YJak | L4 ~90% | FABIO | NASDAQ | same day | short | not stated | not stated | took profit at day low | win | volume spread analysis: delta pressure, zero price result |
| 29 | 8CWKfoSJu3c | L31 ~12% | FABIO | NASDAQ | "best session of the month of December" | short, 10 contracts | not stated (levels ~25,650) | risk $3,150 | final 27,600 as said (1:19) | win, stop in profit ~+$23,000 on the position | absorbed buyers / punch to the wall / sellers control auction |
| 30 | 8CWKfoSJu3c | L33 ~13% | FABIO | NASDAQ | same day | side not stated (earlier trades) | n/a | n/a | n/a | +$27,500 from first trades | n/a |
| 31 | fZlNGWvd2Ko | L23 ~12% | FABIO | not stated (order-flow platform) | "best session of the month of October" (year not stated) | short (continuation), 2 tries | not stated | not stated | n/a | both failed (gave back ~$5,000 net with London gains) | continuation short |
| 32 | fZlNGWvd2Ko | L47 ~87% | FABIO | not stated | same session | long (loaded, reloaded x2) | not stated | risk $980 at best | potential $25,000 | win, closed above $25,000 day | failed auction of sellers, then buyer aggression; big trades |
| 33 | jasv3L-d8ZE | L? ~15% | FABIO | not stated (NQ inferred: level 24,932; unverified) | "precession of the 23" (ambiguous) | long/short mix: several stopped trend-following entries | n/a | "streak of stop-loss" | n/a | -$9,000 drawdown | trend-following model in absorption day |
| 34 | jasv3L-d8ZE | L152 ~71% | FABIO | same | same day | short (18 contracts) | from the top | scaled, stop to zero | 1:20 | win: +$12,000 locked, day +$2,330 | breakdown of consolidation range; long gamma warning |
| 35 | FawPrRUGNpk | L1123 ~93% | FABIO-ILLUS | Nasdaq (levels 27,910-912) | same-day example | short ("if I took a short from here") | n/a | n/a | below the low | hypothetical | liquidity heatmap absorption |
| 36 | UrZ4vpHJ97g | L7 ~58% | TOM-STYLE-ILLUS | DAX future | n/a | short | n/a | 20 pts | 100 pts | RRR 5 example | sizing example |
| 37 | zAwEX_tRUfE | L9 ~31% | TOM-ILLUS | S&P 500 (1-min) | n/a | long | 7,482 | below last low | 7,485 | shown as poor RRR 0.8 | P setup vs context breakout |
| 38 | pgdmKLJ0hhA | L7 ~50% | TOM-ILLUS | not stated | n/a | long (inferred from prices) | 406 | 394 | n/a | example | swing entry example |
| 39 | Wvq1TZh8aF0 | L8 ~59% | OTHER-Malkan-ILLUS | NSE (Nifty/Indian stocks) | n/a | long (bullish divergence) | candle confirmation | candle low | 2028 (Nifty long-term) | teaching | RSI divergence |

## 4. Per-video summary (videos with concrete trades)

| video | trader | trades | long/short | instrument | publ. |
|---|---|---|---|---|---|
| tS6ZEiHj8gQ | TOM | 2 | 0L/2S | AVIS stock | 2026-05-20 |
| WSCIURybK3U | TOM | 0 (dup of Avis + DAX illus) | - | AVIS/DAX | 2026-05-22 |
| kXhIAug0Gh8 | TOM | 4 | 2L/2S | ES, NQ, crude | 2026-04-17 |
| zQTbdEweG3c | TOM | 1 | 0L/1S | DAX | 2026-07-08 |
| ujedEcmvBMk | TOM | 2 | 0L/2S | DAX | 2026-06-03 |
| T6hDJcHrVBM | TOM | 1 | 0L/1S | DAX | n/a |
| UOBgXV20yCM | TOM | 1 | 1L/0S | DAX | n/a |
| yRvMW6lgN1o | TOM | 1 | 0L/1S | index (unnamed) | 2025-11-19 |
| k0zm5NYn0IQ | TOM | 2 | 0L/2S | DAX | 2026-02-04 |
| OUM9LYwL8eA | TOM | 1 | 0L/1S | Nasdaq | 2026-01-21 |
| 4MoNjEQ2Dd8 | TOM | 1 | 1L/0S | not stated | 2025-12-31 |
| n7ZSkjb7JXs | TOM | 1 (+gold short mention) | 0L/1S | DAX | 2026-01-14 |
| l8RZrBfzvp4 | TOM | 1 (2 tries: -1R, +4R) | 0L/1S | not stated | n/a |
| wPMiyJXL0zU | TOM | 1 | 0L/1S | not stated | 2025-11-11 |
| dh-ysRR8f-M | TOM | 2 | 2L/0S | crude oil | 2026-03-26 |
| 0jM5Y31YJak | FABIO | 3 (5+ positions) | 0L/3S | NASDAQ | n/a |
| 8CWKfoSJu3c | FABIO | 2 | 0L/1S/1 unk | NASDAQ | n/a |
| fZlNGWvd2Ko | FABIO | 2 | 1L/1S | not stated | n/a |
| jasv3L-d8ZE | FABIO | 2 | 0L/1S/1 mixed | not stated (NQ inferred) | n/a |

Fabio videos with 0 trades: 0KyIEdvVKMQ (mental models), LQvv5xgy_ik (risk management, prop/competition protocol; shows
"all the execution that I took in the cup" as a chart only), FawPrRUGNpk (liquidity heat-map teaching; one hypothetical short).
Tom videos with BTC only as context: zQTbdEweG3c, T6hDJcHrVBM, n7ZSkjb7JXs, sQ_biBKhPVU, KEe_CWHyuSg, DVZVE9rXGtU.

## 5. Videos with NO concrete trade (teaching only)
TOM (40 files): YVUcLTsCOZI qLnQan0KGmQ gWjHq5UMisY HySZZSjMxF8 zAwEX_tRUfE 43JaKHRvxHk pgdmKLJ0hhA sQ_biBKhPVU hQ8sOq67x5o usho6UVLqkE e6Gm1n2h05M 3JqMyzE8jIQ NkQeOVDTAec 1xBWnyr1qe4 Ld1dhjGdTCA C9n_d91Uitc vl01TiVTuoQ RwQBdF9TSvc VumVuGnCcFM v5EuDl9c0iI rFPCtOcfUMI -dMWA_bbm3o KEe_CWHyuSg 4P5WAxyPCis rrHj24GSR6M aursfDVYzUk oa8kxSLLkAo 7BQPMJ39WpI y67l86cSqb8 G0CiJcuXCRs YmygDgtoxO8 vk0mkNPuhDc oYu9SBQved0 9eHZMVXilgc DVZVE9rXGtU Vd83oo_geMk YopZ5ZDmMFw Fj4FDZQxw0I WQ_OAdz-PJ8 96iPFDpXEcU
OTHER (38 files; not Tom-extract, not Fabio-list): UrZ4vpHJ97g Wvq1TZh8aF0 YYYuaetck_0 Kg6sYKgtkrY cBkwYjn-6mM StaphlRH8NQ 0CrkbfuIhkc viT_VzF5Fsw 15JoLK0PbMU uk4PZV59nYw kKZCJui4S9U cw8LWQmec1E Sy-x5AQ9-Pk YkclL6xgu-s Ly62G168MkQ ODdF0Bn_KSc VOiy8mAALWA -CBvFi40sIQ AQR6zIgCx7I 2xnNPIyHGQ4 AtR_c-B0jw8 9VN9y2DVtGQ 6BAzqewtPUk jXR1afMy-3o 4VXpUjhKG2U gFJBg8Bsw68 lO-Iptd29t4 cQ-y1oULkBw ridY2Z0hSQA m3IMdc7QwN4 _Uvb2RIjZvk 3oqxklw9zuU f225iVdsrfg VxN5IxTwpbE ACb0Qtt3DSQ 1utSjHs_Mq8 uFxYcpiaOpw K8qtT2_axPo
Notes on OTHER: -CBvFi40sIQ, Wvq1TZh8aF0, cQ-y1oULkBw are Vishal Malkan / Samco (Indian equities, RSI); hQ8sOq67x5o
names Tom Hougaard; StaphlRH8NQ reads as Fabio (Nasdaq edges, BTC MVRV accumulation; unverified, no trades); AtR_c-B0jw8 is an
interview about Tom (mentions a crude-oil night-loss anecdote by the guest); f225iVdsrfg is a third trader's "day in the life"
(Cyprus) with no trades; Patrick Nill appears in _Uvb2RIjZvk (interview). None contain dated, priced trades.

## 6. Verbatim quote evidence (R<n> matches the catalog row)

R1 tS6ZEiHj8gQ L19 ~55%
> "if you entered the market at 640, you had a stop loss at 730"
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

R2 tS6ZEiHj8gQ L19 ~91%
> "Second idea, that one worked."
**Source GPS: tS6ZEiHj8gQ | END**

R3 WSCIURybK3U L19 ~28%
> "Entry 630, stop loss 730, exit 230, the currency is US dollars."
**Source GPS: WSCIURybK3U | BEGIN**

R4 kXhIAug0Gh8 L19 ~31%
> "And so I opened my position here."
**Source GPS: kXhIAug0Gh8 | BEGIN**

R5 kXhIAug0Gh8 L19 ~55%
> "And so I had a risk reward ratio of eight here."
**Source GPS: kXhIAug0Gh8 | MIDDLE**

R6 kXhIAug0Gh8 L19 ~76%
> "Specifically two ticks lower than where my stop loss had been set."
**Source GPS: kXhIAug0Gh8 | END**

R7 kXhIAug0Gh8 L19 ~85%
> "And I then placed my stop loss below the last swing low again."
**Source GPS: kXhIAug0Gh8 | END**

R8 zQTbdEweG3c L19 ~69%
> "I've taken the 24,400 price range as my first target area."
**Source GPS: zQTbdEweG3c | END**

R9 ujedEcmvBMk L13 ~29%
> "And as you can see the position is running."
**Source GPS: ujedEcmvBMk | BEGIN**

R10 ujedEcmvBMk L13 ~59%
> "And then we went to the low volume and at the low volume I took out a position again"
**Source GPS: ujedEcmvBMk | MIDDLE**

R11 T6hDJcHrVBM L13 ~59%
> "As you can see 690 was my entry level."
**Source GPS: T6hDJcHrVBM | MIDDLE**

R12 UOBgXV20yCM L7 ~36%
> "Is exactly an average risk-reward ratio of a good 2 2."
**Source GPS: UOBgXV20yCM | MIDDLE**

R13 yRvMW6lgN1o L19 ~12%
> "In this trade, I entered with a limit order and simply had a sell order here."
**Source GPS: yRvMW6lgN1o | BEGIN**

R14 k0zm5NYn0IQ L19 ~4%
> "For the first position, I'm setting a stop-loss of 20 points in the DAX."
**Source GPS: k0zm5NYn0IQ | BEGIN**

R15 k0zm5NYn0IQ L19 ~40%
> "And now I am actually going to proceed with entering another trading position."
**Source GPS: k0zm5NYn0IQ | MIDDLE**

R16 OUM9LYwL8eA L19 ~78%
> "After it go deeper than my last range, I decide for the next short trade."
**Source GPS: OUM9LYwL8eA | END**

R17 4MoNjEQ2Dd8 L19 ~4%
> "The stop loss goes below the last low here and my take-profit is set above the highs."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

R18 n7ZSkjb7JXs L19 ~26%
> "I'm running a trade there where I see a similar picture."
**Source GPS: n7ZSkjb7JXs | BEGIN**

R19 l8RZrBfzvp4 L13 ~77%
> "But as you can see here, you simply won four R and so it is all cool."
**Source GPS: l8RZrBfzvp4 | END**

R20 wPMiyJXL0zU L19 ~45%
> "So I simply had a risk of about 15 points, but a planned range of nearly 80 points."
**Source GPS: wPMiyJXL0zU | MIDDLE**

R21 dh-ysRR8f-M L19 ~42%
> "I remember I bought a lot somewhere in the 14, 15, 16 range."
**Source GPS: dh-ysRR8f-M | MIDDLE**

R22 dh-ysRR8f-M L19 ~14%
> "I had crude oil contracts long."
**Source GPS: dh-ysRR8f-M | BEGIN**

R23 WSCIURybK3U L19 ~54%
> "And here I set my stop loss above the last supposed high."
**Source GPS: WSCIURybK3U | MIDDLE**

R24 BVpYGKz9PBU L19 ~73%
> "Now here at 260 I have the opportunity to take my entry."
**Source GPS: BVpYGKz9PBU | END**

R25 3o1VVsfBmmU L19 ~56%
> "my stop loss in this case let's say is 10 ticks"
**Source GPS: 3o1VVsfBmmU | MIDDLE**

R26 0jM5Y31YJak L4 ~43%
> "This was my first position because the market told me Fabio we are going down"
**Source GPS: 0jM5Y31YJak | MIDDLE**

R27 0jM5Y31YJak L4 ~77%
> "So we already commented like we already had a commentary of five different position that were trailed"
**Source GPS: 0jM5Y31YJak | END**

R28 0jM5Y31YJak L4 ~90%
> "the buyers are punching a wall and I want to be short in this position"
**Source GPS: 0jM5Y31YJak | END**

R29 8CWKfoSJu3c L31 ~12%
> "we are going to commend in this one the short that I took on NASDAQ"
**Source GPS: 8CWKfoSJu3c | BEGIN**

R30 8CWKfoSJu3c L33 ~13%
> "after building $27,500 in profit on the first trades of the day"
**Source GPS: 8CWKfoSJu3c | BEGIN**

R31 fZlNGWvd2Ko L23 ~12%
> "The first trades that we took was a continuation short and we gave back two trades inside here."
**Source GPS: fZlNGWvd2Ko | BEGIN**

R32 fZlNGWvd2Ko L47 ~87%
> "As you can see, we loaded the first one here, then we reloaded here, then we reloaded here"
**Source GPS: fZlNGWvd2Ko | END**

R33 jasv3L-d8ZE L? ~15%
> "my trend following model took a straight stop loss"
**Source GPS: jasv3L-d8ZE | BEGIN**

R34 jasv3L-d8ZE L152 ~71%
> "But look at this 18 contract from the top with risk-to-reward 1 to 20."
**Source GPS: jasv3L-d8ZE | END**

R35 FawPrRUGNpk L1123 ~93%
> "So if I took a short from here, I would consider bringing my full take profit way lower than the low."
**Source GPS: FawPrRUGNpk | END**

R36 UrZ4vpHJ97g L7 ~58%
> "a 100 point profit distance and a 20 point loss distance which gives a riskreward ratio of five"
**Source GPS: UrZ4vpHJ97g | MIDDLE**

R37 zAwEX_tRUfE L9 ~31%
> "equilibrium was at 7485, and the market reached this target."
**Source GPS: zAwEX_tRUfE | BEGIN**

R38 pgdmKLJ0hhA L7 ~50%
> "So, I'd have a stop loss at 394 and my entry at 406."
**Source GPS: pgdmKLJ0hhA | MIDDLE**

R39 Wvq1TZh8aF0 L8 ~59%
> "I put a stop loss and what would be my target?"
**Source GPS: Wvq1TZh8aF0 | MIDDLE**

