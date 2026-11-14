# Extract: Fabio Valentini, "4 Trading Champions Trade the Same Session (Live Trading)" (`DD73wDVvObI`)

- **Video ID:** `DD73wDVvObI`
- **Speaker:** Fabio Valentini (Fabervaale) only. The video has four traders (Fabio, Emir Gams, Patrick Niel, Freddy Sarento) plus an unlabeled host/narrator; the other champions are out of scope. Andrea Cimi: no statement can be attributed to him (the caption has no speaker labels; he appears only as the person Fabio addresses), so nothing is extracted for him. Passages where the speaker is ambiguous were left out.
- **Market in the video:** CME Nasdaq (NQ) futures, one Monday session in the New York open, with SPX option levels (call wall); no crypto. Session clock and option levels do not transfer to Binance.
- **Source:** `raw_transcripts_canonical/DD73wDVvObI_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote. Every number he reports is a speaker claim, no data shown, unless stated otherwise. One live session is an anecdote, not evidence; the R figures below are that day only.

## Rules

### D1. Pre-session map: previous aggression and absorption zone lined up with value area low (SOURCED)

Rule: the day's key area is where the previous session showed maximum aggression on the profile and strong absorption at the bottom, and it lines up with the value area low. Plan: retrace at the open into that area, accumulate, then expand toward the option call wall; check option flow in the first minutes, then use order flow for the actual entry. Levels were 7,750 to 7,760 on SPX (ES-equivalent). Entry trigger, stop and target distances: NOT stated. For BTC the call-wall target has no Binance equivalent (OURS: use the prior session high or HVN instead).

> "that is the point of maximum previous aggression on the profile and the absorption that we have at the bottom and this level is lining up with a value area low." [0:01:54]
**Source GPS: DD73wDVvObI | BEGIN**

> "my market plan is that we could retrace during the opening to then accumulate and then expand to the call wall that we saw." [0:02:08]
**Source GPS: DD73wDVvObI | BEGIN**

### D2. Entry timing tool: Nasdaq effort plus delta profile on the footprint candle (SOURCED)

Rule: level and bias come from the map (D1); the actual entry is timed with his Nasdaq-effort area (proprietary, see `extract_VHhvg96W6lc.md` V14) plus the delta profile on the footprint candle. Threshold values: NOT stated. Computable on BTC: partly (delta per price level per bar yes; Nasdaq effort no).

> "For the timing I use the NASDAQ effort plus the delta profile on the footprint candle." [0:02:30]
**Source GPS: DD73wDVvObI | BEGIN**

### D3. Risk to zero, then trail behind the next aggression area (SOURCED)

Rule: once the trade is in profit move the stop to break even ("covered the risk to zero"), keep a second aggression area protecting the position, and trail instead of taking the first target because the open is violent. He calls this one a conservative 1 to 2 trade. How much profit triggers the break-even move: NOT stated.

> "I already covered the risk to zero. I have another NASDAQ effort area protecting my position and I will trail this one because during the opening it can be very violent the market." [0:08:09]
**Source GPS: DD73wDVvObI | BEGIN**

### D4. Failed breakout: manage by the aggression, accept break-even (SOURCED)

Rule: when the breakout fails and the market stays in a range, manage the trade by following the aggression of price and accept being stopped at zero rather than holding. He puts that trade at about 0.3 R (caption "0 3R", sign unclear; speaker claim, one session).

> "You can see that here they failed the breakout of the position. And I will manage see this reaction here. I will manage following always the aggression of the price and I got taken out at 0" [0:13:39]
**Source GPS: DD73wDVvObI | MIDDLE**

### D5. Rotational session: small size; go directional only on the break out of balance (SOURCED)

Rule: in a rotational (balance) phase he makes and gives back small amounts and pays for the losses with small positions; the model's money is made by getting directional when price leaves the balance. Sizes: NOT stated. In the live session he marked the opening value area high from a fixed profile and bet directional when pressure built at the top, calling the explosive case about 2.5 R (speaker claim, one session).

> "So, in this uh rotational phase, I managed to make money to give it back to make money give it back. So, paying for my losses with the small position and ultimately the model is built on getting directional when you go out of the balance." [0:18:23]
**Source GPS: DD73wDVvObI | MIDDLE**

> "I mark the value area high here that we had of the opening because I get the fixed profile and as soon as I saw all this pressure building on the upside I belt on the bet on the directional side" [0:18:36]
**Source GPS: DD73wDVvObI | MIDDLE**

### D6. Momentum squeeze: buyers sit at the top of the candle, sellers not rewarded; stop below the last aggression (SOURCED)

Rule: after the aggression bar, look for a momentum squeeze when buyers stay sustained at the top of the candle and sellers get no result there; the stop goes below the low / last aggression. If the candle is rejected the setup fails because the aggression was not sustained, and the stop at the last aggression takes it out. Entry is limit-style ("let's see if we manage to get fill"). Target: extract as much as possible, NOT a fixed multiple. Computable on BTC: yes (close position within bar range, delta at the high, swing low).

> "I will cover below the low and I will try to get the momentum squeeze of the top." [0:19:27]
**Source GPS: DD73wDVvObI | MIDDLE**

> "the buyers are sustained here because they are located at the top of the candle and the sellers are not rewarded here." [0:19:37]
**Source GPS: DD73wDVvObI | MIDDLE**

> "if this one is so rejected anyway the setup fail because the aggression is not sustained. So I cover below the last aggression and I try to get a directional squeeze" [0:20:18]
**Source GPS: DD73wDVvObI | MIDDLE**

### D7. Move the stop to a level once price rejects it and auctions higher (SOURCED)

Rule: when price taps a level and rejects it then auctions higher again, move the stop up to that level (cover the risk to the level) provided the candle closes with the aggression. A trailing rule by structure, not by ticks.

> "If they reject the 62 and auction higher again I want to cover my risk to the 62." [0:20:46]
**Source GPS: DD73wDVvObI | MIDDLE**

### D8. Exit at the call wall; option flow decides rotation vs directional (SOURCED)

Rule: he takes the position out at the call wall rather than re-entering long, because the option flow showed the call wall being lowered, meaning a compressed rotational day expected; without option flow he would have kept trading long and likely given back the day's profit. Day result 1.75 R (speaker claim, one session). Needs option-chain data (not in Binance files); Deribit options would be a separate data source.

> "Today without option flow, I will not be able to take my position out at the cold wall and not try again another long because I will think okay we can squeeze higher." [0:20:53]
**Source GPS: DD73wDVvObI | MIDDLE**

### D9. Stop the session when the day is good; consistency over size (SOURCED)

Rule: after building profit on a compressed session he cut the session short rather than trade the last part, and says the goal on a prop account is steady profit, not a huge one-day gain, because that breaks the consistency rule. Loss limit and daily target: NOT stated.

> "So I decided to cut the session short, build some profit today and tomorrow it's another day and another fight." [0:21:28]
**Source GPS: DD73wDVvObI | MIDDLE**

> "the goal specifically in prop is not making a huge amount of money one day otherwise you will break also the consistency rules is building profit." [0:33:34]
**Source GPS: DD73wDVvObI | END**
