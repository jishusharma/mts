# Extract: deepcharts, "The Only Orderflow Footprint Chart Guide You'll Ever Need [Tutorial]" (`KObUowoFiK0`)

- **Video ID:** `KObUowoFiK0`
- **Speaker:** Andrea Cimi on the deepcharts channel (platform tutorial; published 2025-12-18)
- **Market in the video:** CME futures (ES, Nasdaq, gold) on 1-minute and 5-minute footprint bars; session clock is the 9:30 US cash open; no crypto. Concepts transfer, session clocks and contract sizes do not.
- **Source:** `raw_transcripts_canonical/KObUowoFiK0_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Note:** most of the video is platform set-up (fonts, colours, offsets, alerts) and sales: skipped. Bar-level delta, delta percent and CVD: same as `extract_Ni6quY00dcw.md` C1/C2 (not repeated). Imbalance 2x/4x, POC, stacked imbalances, unfinished auction are also in `extract_h4emw9_2LU8.md`; this video adds the numbers below.

## Rules

### K1. Footprint cell definitions: volume, delta, tick grouping (SOURCED)

Rule: per price level, volume = traded at bid plus traded at ask; delta = ask traded minus bid traded (worked example 22 at ask, 18 at bid, delta 4; the spoken sentence names the subtraction the other way round, the example fixes the sign: positive delta = more aggressive buying). When a level holds too few contracts, group ticks manually by 4 or 5 (his figure for ES/Nasdaq/gold set-ups; for BTC the bin size is OURS, untested).

> "volume is nothing more than the sum of the bid traded and the ask traded" [0:06:58]
**Source GPS: KObUowoFiK0 | BEGIN**

> "it's going to take for one tick, 22 - 18 = 4. Well, that's our delta." [0:07:15]
**Source GPS: KObUowoFiK0 | BEGIN**

> "if you see too few contracts or you have to zoom in too much, always put it on manual, and maybe manually group it with a factor of 4/5" [0:16:50]
**Source GPS: KObUowoFiK0 | MIDDLE**

### K2. Diagonal imbalance 200 percent and 400 percent (SOURCED)

Rule: compare the ask volume at a level with the bid volume one tick below (diagonal): at least 2x = imbalance, at least 4x = strong imbalance (his colour ranges: third range 200%, fourth range 400%). Same numbers as `h4emw9_2LU8` F2.

> "I always like to keep the third range at 200% and the fourth range at 400%" [0:09:34]
**Source GPS: KObUowoFiK0 | BEGIN**

> "every one of these kind of dark colors is a 200% imbalance, which mean this number is at least twice as big as this number" [0:10:31]
**Source GPS: KObUowoFiK0 | MIDDLE**

> "if you compare this number over here which is 12 with this number slightly below which is 38, so kind of diagonally" [0:09:42]
**Source GPS: KObUowoFiK0 | MIDDLE**

### K3. Imbalance cluster = zone to trade when revisited (SOURCED)

Rule: several consecutive levels with sell imbalance (example: seven) form an imbalance cluster; mark the zone and expect a reaction when price returns, because the same sellers are likely to be present again. Minimum count NOT stated (7 is only the example). Entry, stop, target NOT stated.

> "There's a lot of imbalance, 1 2 3 4 5 6 7. This is a clear imbalance cluster, as we call it." [0:17:23]
**Source GPS: KObUowoFiK0 | MIDDLE**

> "this could be an area where price can later response because the same sellers that created this imbalance in price are likely to be present once more if price goes into the same prices" [0:17:32]
**Source GPS: KObUowoFiK0 | MIDDLE**

### K4. Exhaustion ratio of the last two ticks, minimum 10 (SOURCED)

Rule: at the top (bottom) of a bar, ratio = volume at the second-to-last tick divided by volume at the last tick; ratio of at least 10 marks exhaustion of that side (example 27). Bigger ratios tend to sit at tops of big moves, but "by itself, it's not a magical indicator". Direction use: ratio at the high = buying exhausted (bearish); stop/target NOT stated. Computable from aggTrades with tick bins.

> "I like to put it with a minimum ratio of 10. And when you see this happening, this simply means a phase of exhaustion." [0:19:10]
**Source GPS: KObUowoFiK0 | MIDDLE**

> "if you compare the last two ticks, what's the ratio between them? If the ratio is more than 10, it's likely that there was some form of exhaustion in selling activity" [0:19:31]
**Source GPS: KObUowoFiK0 | MIDDLE**

> "Of course, by itself, it's not a magical indicator, but it's a very clear example of exhaustion that you can start seeing very often." [0:20:28]
**Source GPS: KObUowoFiK0 | END**

### K5. Big single-level volume that is absorbed, then bar close decides (SOURCED)

Rule: a very large volume at one price level (example 1,000 contracts at one level on a 5-minute bar) hit by aggressors but blocked by a passive reloading seller is effort without result; if the bar then closes below that level, price likely continues down. Mirror: huge selling absorbed by a big buyer, then reject with imbalance at the bottom, means upward pressure. Size threshold OURS (BTC volume scale differs; never stated as a number except the 1,000 example). Stop and target NOT stated.

> "this 1,000 contracts all in one price level, that tried to buy, but there was a passive seller who was constantly reloading contracts, and basically blocking all of this buy pressure." [0:12:09]
**Source GPS: KObUowoFiK0 | MIDDLE**

> "And as soon as the candle closes below this huge trade, I know there's a good chance that price will continue dropping lower." [0:12:25]
**Source GPS: KObUowoFiK0 | MIDDLE**

### K6. Volume cluster at a single level as catalyst (SOURCED)

Rule: highlight any price level whose traded volume exceeds a chosen threshold; big volume at one level is a catalyst for big price moves. Threshold is user-set, NOT stated (OURS: percentile of recent bars). Direction, stop, target NOT stated.

> "Whenever there's a big volume being traded at a single level, those are catalysts for big price movements." [0:21:20]
**Source GPS: KObUowoFiK0 | END**

### K7. Stop run absorbed, then high-volume initiative candle (SOURCED)

Rule: a spike of selling below a prior low with high volume (not a fast low-volume drift) that market makers absorb, followed at once by a high-volume initiative candle up with a lot of green inside, means buyers are in control; he reads this as a long confirmation with a long bias. Volume or delta thresholds NOT stated (initiative 10 percent delta is in `Ni6quY00dcw` C2). Stop and target NOT stated.

> "So, here I can understand this was a clear sell aggression, more of like a stop run." [0:26:52]
**Source GPS: KObUowoFiK0 | END**

> "But right after that, we had a very strong high volume, high initiative candle up with a lot of green inside." [0:26:41]
**Source GPS: KObUowoFiK0 | END**

### K8. Failed break of the value area edge (SOURCED)

Rule: build the volume profile for the session; the value area edges are support and resistance. If price breaks outside the value area but is dropping back inside right away, the buyers are not strong enough; if price then drives back inside and creates more value inside, it confirms a sell from the top of the area to the bottom. Zoom into the footprint at the edge for confirmation. Value area percentage NOT stated. Stop NOT stated; target = other edge of the value area (implied by "from here to here", OURS reading).

> "this auction broke outside of the main value area. But right as we did it, we're dropping back inside. So, these buyers are not powerful enough to keep driving the auction higher" [0:25:17]
**Source GPS: KObUowoFiK0 | END**

> "if for example, they will drive price back inside and create more value inside, this could be a confirmation that I can sell from here to here." [0:25:34]
**Source GPS: KObUowoFiK0 | END**

### K9. Opening range breakout with a big-trade stop (SOURCED)

Rule: opening range = first 15-minute candle from the 9:30 US cash open (three 5-minute bars). Qualify an upside breakout with footprint: a big buyer that beats the opposing seller and many imbalances at the top of the candle. Buy when the test (retest) comes. Stop: under the big trade, called "a very small stop loss". Target: 1R to 3R / 1R to 4R, stated as 1 to 3, 1 to 4. Session clock is US index; BTC has no cash open (OURS: untested).

> "I can take my first 15-minute candle. So, this is the 9:30 candle. So, this is the opening candle." [0:28:02]
**Source GPS: KObUowoFiK0 | END**

> "I can buy when the test comes, protect myself under this big trade, so with a very small stop loss, and even with a 1 to 3, 1 to 4 target, this is a very high confidence type of trade." [0:28:50]
**Source GPS: KObUowoFiK0 | END**

### K10. Timeframe pairing (SOURCED parameter)

Rule: 5-minute chart pairs with volume profiles, dynamic VWAPs, composite profiles and volume by time; short-term order flow (1-minute footprint with CVD and per-bar delta stats) is where he says order flow gives its best edge. Choice of 1m versus 5m for BTC: OURS.

> "With the 5-minute chart, I typically pair volume profiles, dynamic VWAPs, composite profiles, plus volume by time." [0:23:34]
**Source GPS: KObUowoFiK0 | END**

> "And with short-term order flow, which is where order flow tends to give its best edge in general, I like to have footprint charts with a clear understanding of delta." [0:23:42]
**Source GPS: KObUowoFiK0 | END**
