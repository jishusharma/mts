# V2 extract Pz8f0wWW12M (Fabio; "The Only Orderflow Guide You'll Ever Need": effort/result, absorption vs exhaustion, LVN, profile framing)

Method: EXTRACTION_METHOD_V2.md, compact form. Read in full (the lecture parts in order, the Nasdaq profile walk-through from skimmed text for the stop and target words), 2026-10-18.
Label rule: SOURCED = verbatim from `raw_transcripts_canonical/Pz8f0wWW12M_raw.txt` (43,083 characters, caption file). OURS = our reading.

## Header
```
video_id: Pz8f0wWW12M
trader: Fabio (first person: "that I used to trade live in front of millions of people"; staged as fabervaale_Pz8f0wWW12M_raw.txt)
identity check: not a duplicate of any canonical file (nearest overlap 0.05 %)
instrument_stated: ES-like book example (6,840.5 / 6,841.5), NASDAQ for the profile walk-through (20 November onwards, two months)
trades: 0 fully described. Teaching lecture; the profile walk-through names long and short setups without prices.
```

## Rows (all SOURCED)
### R1 Where he trades
> "I only trade in the New York session for US indices because it's where the majority of the volume get traded"
**Source GPS: Pz8f0wWW12M | END** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:655, raw line)

### R2 U2 discriminator: absorption (continuation) versus exhaustion (reversal)
Continuation: aggressive orders are absorbed inside the candle and the candle closes in the trend direction.
> "we have a market that is in a consolidation phase here, and we can spot that all these aggressive market participants here got absorbed and the candle closed green. This is a potential continuation of the move"
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:322, raw line)

Reversal: volume falls into the extreme and a contrarian imbalance prints.
> "from the concept of vertical volume you can find an exhaustion where you can see that the market is pushing really strong, printing another green candle, but the volume is getting lower and lower. This is a dry up in volume, and usually what you see this in a pattern order flow is that you have a sudden reversal in price."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:417, raw line)

> "So you have the price going up up up up up not being followed by the volume, so you have this divergence and the price snap back to the value"
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:409, raw line)

Reading (OURS): the split is "volume against the move AND a contrarian imbalance at the extreme = reversal; aggression absorbed with the candle closing with the trend = continuation". No numeric thresholds are given (no volume ratio, no imbalance size).

### R3 LVN rebalance pivot (the former OURS-only V3 model A, now has a Fabio quote)
> "Usually, the market like to rebalance the low volume node before continuing in the direction of the trend."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:518, raw line)

> "When you have a low volume node and the market goes in price discovery, you can clearly see a lot of days the price coming back to rebalance in this low volume node and using this as a pivot before resuming the direction of the auction."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:533, raw line)

> "This one it's where you can use confluence and order flow pattern to join the market direction."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:541, raw line)

He teaches the idea and says to join with confluence and order flow; entry price rule, stop and target are NOT STATED for it.

### R4 Profile framing: P shape, hook, bias
> "We have the value building on the upside. This is what we call the P shape. It's where the buyers are really aggressive and you close the cash session on the upside, so you can expect a directional move also on the day after."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:602, raw line)

> "when we go back to the value area low and down, we do what we call the hook. So, they do a failed auction, they try to break, they get rejected."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:592, raw line)

> "if you want to join the trend early in its development, you need to understand that the when the the price accept and the volume accept below the value area low or the value area high, the market participants are telling you that we are in a situation of out of balance."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:487, raw line)

### R5 Management words (the only stop and target words in the video)
> "And when you break this level, you can decide to put your stop loss to break even."
**Source GPS: Pz8f0wWW12M | END** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:919, raw line)

> "you can decide to go from 1 to 2 to 1 to 5 and put your stop loss to break even."
**Source GPS: Pz8f0wWW12M | END** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:923, raw line)

Initial stop level and size: NOT STATED.

## Verdict for the catalogue
- V3 model A "LVN pullback trend" gets a SOURCED rationale (R3) but no entry, stop or target; it stays an OURS rule, now with a quote behind the idea.
- U2 is resolved qualitatively (R2); a number for "dry up in volume" is OURS and must be tuned on DEV.
