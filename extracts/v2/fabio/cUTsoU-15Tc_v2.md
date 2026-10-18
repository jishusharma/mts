# V2 extract cUTsoU-15Tc (Fabio; "The Simplest Orderflow Trading Model": IVB, opening range breakout plus order flow)

Method: EXTRACTION_METHOD_V2.md, compact form. Read in full, start to end, 2026-10-18 (25 minutes: 12 min lecture, 13 min replay of the Deep Charts backtest tool).
Label rule: SOURCED = verbatim quote from `raw_transcripts_canonical/cUTsoU-15Tc_raw.txt` (caption file, no header). OURS = our reading or number, not Fabio's.

## Header
```
video_id: cUTsoU-15Tc
trader: Fabio (first person: "my favorite", "how I work with the deep charts team"; staged as fabervaale_cUTsoU-15Tc_raw.txt)
identity check: not a duplicate of any canonical file (nearest overlap 0.07 %)
instrument_stated: NY cash session of an index future (instrument not named); IVB = initial balance / opening range
trades: 0 live trades; the second half replays sessions in the Deep Charts backtester (no prices, no fills stated)
caution: the "protection level", "TP2" and "extended average" come from the Deep Charts algorithm (not published); the 65 to 70 % is his statement about that tool, not something we can verify.
```

## Rows (all SOURCED unless marked)
### R1 Frame: the first break of the opening range decides the day
> "the first one that break is telling you what is telling you who won the battle of the most important time of the day."
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:54, raw line)

> "The New York session is the session that hold the maximum amount of volume for the day."
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:32, raw line)

Range = first 15, 30 or 60 minutes "It depends how you want to use it" (scalp versus intraday bias).

### R2 IVB model 1 (profile only): location, invalidation, risk-to-reward (FAB-6)
Fixed profile dragged from the top (point A) to the bottom (point B) of the first 15 to 30 minutes. After a breakout and retrace, the reload block is between the value area and the POC.
> "the most sensitive level after you have this is the level contained between the value area and the PC. This is our real block of orders."
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:118, raw line)

> "So you have a value area low that if it gets broken, so the market accept it, it's an invalidation point."
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:136, raw line)

> "If we close a candle here, okay, the setup is invalidated."
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:141, raw line)

Reading (OURS): long case; the invalidation is a candle CLOSE beyond the value area low (VAL), not a touch. A stop distance in ticks or points is NOT STATED. Target is the "first protection point" (algo level); he states the resulting reward as "1 to 2 / 1 to 2.5" (caption "1 to2 one to 2.5").

### R3 IVB model 2 (order flow after the breakout): trigger and stop
> "Maybe we have a lot of aggressive sellers here with zero result. This means that there is a big absorption on this level on the PC."
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:170, raw line)

> "you can take a momentum trade with a really tight stop-loss to go to the protection level."
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:179, raw line)

> "when you have aggression of the buyers for example here okay they are protecting the area you can consider a buy with a stop loss below that goes to the protection level."
**Source GPS: cUTsoU-15Tc | END** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:481, raw line)

Two triggers named: (a) absorption of sellers on the POC, (b) seller exhaustion plus buyer momentum. Stop = below the protected area. Distance NOT STATED.

### R4 Targets, win rate and R multiples he mentions
> "So you know that with 65 to 70% probability, you go here"
**Source GPS: cUTsoU-15Tc | BEGIN** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:199, raw line)

> "So it's better to take 1 2 3 1 to 2.5 with a really consistent way of executing it."
**Source GPS: cUTsoU-15Tc | END** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:561, raw line)

> "if you wants to keep a runner when taking it out, the most sensitive area for the day is the protection level."
**Source GPS: cUTsoU-15Tc | MIDDLE** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:329, raw line)

The 65 to 70 % is the tool's claim for the protection-level target; OURS: untested, treat as a hypothesis to be measured on our own data. Reaching the full extreme is stated to lower the win rate ("the win rate goes low").

### R5 Direction and the inside-range alternative
> "So if they will break on the downside, we will consider short. If they break on the upside, we will consider long."
**Source GPS: cUTsoU-15Tc | END** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:505, raw line)

> "you have the opportunity to fade the top and the bottom using a mean reverting"
**Source GPS: cUTsoU-15Tc | MIDDLE** (raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:224, raw line)

## Verdict for the catalogue
- FAB-6 (IVB) was "entry, stop, target NOT STATED". Now sourced: location (VA to POC block), invalidation (candle close beyond VAL), two order-flow triggers, stop "below the protected area", reward 1:2 to 1:2.5 (model 1) and "1 2 3 ... 1 to 2.5" (replay). Still NOT STATED: stop in ticks, order type, the protection-level formula (Deep Charts algo).
- BTC visibility stays PARTIAL (the NY-open range is computable; the algo protection level is not).
