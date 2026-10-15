# CATALOG DELTA: Fabio V2 re-extract vs ledger, rulebook, SETUP_CATALOG s4 (2026-10-15)

Inputs: the 8 files in this folder (`<id>_v2.md`, method EXTRACTION_METHOD_V2.md, one independent Sonnet worker per video, each PASS on the quote checker), compared with FABIO_TRADE_LEDGER.md (F1-F14), FABIO_RULEBOOK.md (FR-n), SETUP_CATALOG.md s4 (FAB-1..FAB-8). Nothing outside this folder was edited; a later merge pass applies this. No fees, no backtests, no code.
Every quote below is verbatim from `raw_transcripts_canonical/<id>_raw.txt` and machine-checked. Computed numbers are marked "(mine)".

## 0. Summary (result line)
- Videos extracted: 8 of 8 (0KyIEdvVKMQ, 0jM5Y31YJak, 8CWKfoSJu3c, FawPrRUGNpk, LQvv5xgy_ik, StaphlRH8NQ, fZlNGWvd2Ko, jasv3L-d8ZE).
- V2 trades: 8CWK 1, 0jM5 3, fZ 2, jasv3L 2, the other four 0 (lectures; FawPr has 5 illustrations/hypotheticals, StaphlRH8NQ 5 model illustrations). 8 trade blocks in all.
- New setups: 1 variant (FAB-7b, retest entry after a reload breakout, s1) and 4 non-intraday edges from StaphlRH8NQ that are not execution setups (s1). No new intraday setup with a stop.
- New trades vs ledger and catalogue: 2, both without prices (jasv3L teaser long, fZ failed continuation short; s2). The other 6 blocks are F1, F2/R26-R28, F3a-c, F5 already held.
- Setups that gained a stated initial stop: 3, none with a tick or point distance (s3): FAB-7 (location in words, illustrations only), FAB-2 (money, 3,500), FAB-3 (money, $600 on added lots; $980 risk). FAB-1 still has only "The first stop loss was here"; FAB-4, 5, 6, 8 gain none.
- Contradictions found: 6 (s4).

## 1. New setups

### N1 FAB-7b: enter on the retest ("the test") of a broken resting-liquidity level (FawPrRUGNpk, illustration 3, rows 28-31)
Not in FAB-7 as an entry: FAB-7 holds the reload breakout (FR-43) only as a paraphrase. In V2 it is a separate entry type: after an aggressive breakout with a fresh reload he waits for the price result to be positive, then enters on the test of the level, stop below the reload wall, target the next liquidity level, R:R 1:2 to 1:3. Hypothetical teaching example, no trade taken.
> "I can enter on the test"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "protect myself below the wall reload"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "go to the next liquidity level, maybe for a 1:2 1:3 risk to reward"
**Source GPS: FawPrRUGNpk | MIDDLE**

### N2 Four edges in StaphlRH8NQ (rows 7-26): not intraday execution setups
They are "two long-term models on the stock market" plus option and crypto-cycle edges. None has an entry, stop or target in his words (every block says "no stop stated"). They are listed so the merge pass can mark them out of scope for BTC intraday.
- N2a earnings drift (PEAD), hold "up to 60 days", spread 4%:
> "stock with high standardized unanticipated earning continue to drift upward for up to 60 days, while negative surprise stocks drift downwards"
**Source GPS: StaphlRH8NQ | BEGIN**

- N2b politician tracking (copy disclosed trades, disclosure delay 45 days):
> "to avoid cherry-picking the politician, we test Nancy Pelosi, Brian Higgins, and Mark Green portfolio"
**Source GPS: StaphlRH8NQ | END**

- N2c option premium harvesting:
> "option premium harvesting is the systematic selling of out-of-the-money option to capture the volatility risk premium"
**Source GPS: StaphlRH8NQ | END**

- N2d MVRV-scored allocation (the only crypto-flavoured one; sizing, no entry):
> "value, the MVRV zeta score to identify macro market cycles and adjust allocation size dynamically"
**Source GPS: StaphlRH8NQ | END**

### N3 FAB-6 gets a verbatim source (not a new setup)
FAB-6 / FR-81 were paraphrase ("not verified here"). StaphlRH8NQ now supplies the opening-range definition and the 13.5% test with R:R one-to-one. Entry timing and stop are still not stated.
> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "with the risk to reward okay of one of one measuring the same amount"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "measuring the session after the breakout that close above this breakout, it's already blindly without order flow, without option flow, without logic of the strategy confirmation 13.5%"
**Source GPS: StaphlRH8NQ | MIDDLE**

Note: the catalogue spells the setup "IVB" (from LQvv5xgy_ik). The StaphlRH8NQ captions give "initial balance" in the definition and "IVB"/"battle of the first 30 minutes" in garbled places; both are the first-30-minute range. LQvv5xgy_ik still has only this one line (no entry, stop or target):
> "the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

### N4 Management and stance items with no catalogue row (LQvv5xgy_ik, 0KyIEdvVKMQ)
- Two account styles: a high-win-rate low-variance scalp for prop evaluations, and an aggressive trend-following scalp for the competition. No entry or stop rule is given for either.
> "on this one, I go aggressively trend following scalping."
**Source GPS: LQvv5xgy_ik | END**

- Day-stop rule in the 0KyIEdvVKMQ lecture (a drawdown stop, different from the profit floor in fZlNGWvd2Ko; see s4 C6):
> "If I reach 1% of draw down, I stop for the day."
**Source GPS: 0KyIEdvVKMQ | END**

## 2. New trades (vs ledger F1-F14 and catalogue evidence)
Mapping of all 8 V2 trade blocks: 8CWK trade 1 = F1 (NQ short 10 contracts); 0jM5 trades 1-3 = F2 (approximate in the ledger) and ANG R26-R28; fZ trade 2 = F3a-c; jasv3L trade 2 = F5. The ledger's F4, F6-F14 come from videos with no raw transcript here, so V2 cannot touch them.

### T-new-1 jasv3L-d8ZE trade 1, long, teaser mention (row 5)
Not in the ledger (F5 is the short) and not in the catalogue. No price, stop, size or outcome; the teaser's profit figures are the session's open profit, not this trade's.
> "And we are going long again."
**Source GPS: jasv3L-d8ZE | BEGIN**

### T-new-2 fZlNGWvd2Ko trade 1, failed "continuation short" (rows 4-5)
In the catalogue only as unassigned (ANG R31); not an F row in the ledger. V2 gives it a block: loss, "we gave back two trades", session gave back about $5,000 (the worker's reading). No price, stop, size.
> "The first trades that we took was a continuation short"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "We tried this continuation and we failed"
**Source GPS: fZlNGWvd2Ko | BEGIN**

### Not new but sharpened
- 0jM5Y31YJak trade 3 (low-of-day short, "another model that I use") is catalogue FAB-2 evidence (ANG R28) and now has its own block with the add and the stop-to-zero rows:
> "this is a confirmation that the buyers are punching a wall"
**Source GPS: 0jM5Y31YJak | END**

- The 0jM5Y31YJak first position closes at "almost 1 to three even more 1:5", after the stop had gone to break even:
> "almost 1 to three even more 1:5 risk-to-reward ratio"
**Source GPS: 0jM5Y31YJak | MIDDLE**

## 3. Stated initial stops (catalogue baseline: 0 of 8 setups)
No stop is given as a price or as a tick or point distance anywhere in the 8 videos. What exists:

| setup | what he states | kind |
|---|---|---|
| FAB-2 (8CWK, F1) | stop size in money, 3,500 | money, no level |
| FAB-3 (jasv3L, F5) | $600 on the two added contracts, unit unclear | money, no level |
| FAB-3 (fZ, F3c) | risk $980 after lowering risk | money (risk), not the initial stop |
| FAB-7 (FawPr) | below the reload level / below the next liquidity area / below the wall reload / "cover below the low" | location in words, illustrations only |
| FAB-1 (0jM5) | "The first stop loss was here." | chart pointer only; no gain |
| FAB-4, 5, 6, 8 | nothing (no raw source in this set) | no gain |

> "we started with a small stop-loss for 3,500"
**Source GPS: 8CWKfoSJu3c | END**

> "Set up here the stop loss $600 and profit target."
**Source GPS: jasv3L-d8ZE | BEGIN**

> "My risk goes really low and now I'm risking $980"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "you can enter at the breakout protected below the reload level"
**Source GPS: FawPrRUGNpk | BEGIN**

> "put your stop loss below the next liquidity area"
**Source GPS: FawPrRUGNpk | BEGIN**

> "I enter here and I cover below the low"
**Source GPS: FawPrRUGNpk | BEGIN**

> "The first stop loss was here."
**Source GPS: 0jM5Y31YJak | MIDDLE**

Caveat for the merge pass: catalogue s2.2 says "the initial stop is never described in words". That stays true for a price level on any executed trade. It is not true for FAB-7 (location in words) or for the money size on F1 and F5. The FawPr stops are teaching illustrations, not trades.
Also: "cover" is used for both a stop and an exit in these captions (fZ rows, 8CWK "cover myself", FawPr "I cover below the low"); the workers flagged it and did not resolve it.

## 4. Contradictions
- C1 F1 initial risk, 3,150 vs 3,500 (8CWK against itself; ledger agrees with 3,150). At the start of the clip:
> "we are risking a small amount of profit, only 3,150 to make an additional 23,000 of profit on the short position here"
**Source GPS: 8CWKfoSJu3c | BEGIN**

At the end of the clip:
> "we started with a small stop-loss for 3,500"
**Source GPS: 8CWKfoSJu3c | END**

Ledger F1: stop 25668.50, 15.75pt, "$3150". The two spoken numbers cannot both be the first stop; the ledger value matches the first one. Not resolved.

- C2 F1 "Final target is 27,600" is a money figure in the transcript, not a price. Ledger: TP 25514.75, 138pt, $27,600; arithmetic (mine) 138 x $20 x 10 contracts = $27,600, so the ledger agrees. Catalogue FAB-2 lists it as "a far fixed target on the label" without saying it is dollars.
> "Final target is 27,600 for 1 to 19 risk-to-reward"
**Source GPS: 8CWKfoSJu3c | MIDDLE**

- C3 F5 (jasv3L) day result: ledger "Daily P/L ... +2331.50 (+11909$ on the trade)" agrees with "closing 2,330", but the same passage says he made 10,000 for the day, and the opening drawdown is "negative 9,000" against the ledger's -9,577.50.
> "a day that was in negative 9,000 is going to be closing 2,330"
**Source GPS: jasv3L-d8ZE | END**

> "we still made 10,000 for the day"
**Source GPS: jasv3L-d8ZE | END**

> "we locked in $12,000 and we are out of the position"
**Source GPS: jasv3L-d8ZE | END**

- C4 Break-even timing (already in catalogue s5; V2 adds an order problem on 0jM5Y31YJak). He says the first position went to break even at once, yet it is later closed at about 1:3 to 1:5; whether the close was a target, the break-even stop, or manual is not stated (0jM5 row 19, ambiguity flag).
> "the first position went to break even immediately"
**Source GPS: 0jM5Y31YJak | MIDDLE**

- C5 FR-13 "Minimum 1:3 reward-to-risk on initial trades" (rulebook, source 0jM5Y31YJak R4). The V2 read of 0jM5Y31YJak finds only the realised "almost 1 to three even more 1:5" (above) and no "minimum". The rulebook line reads as a stated floor; the transcript gives an outcome. LQvv5xgy_ik states the opposite geometry for prop accounts:
> "moderate risk reward, one to one, even one to 0.75, maximum one to 1.5"
**Source GPS: LQvv5xgy_ik | BEGIN**

- C6 Day-stop rules differ by context: a loss-side stop in 0KyIEdvVKMQ (1% drawdown, see N4) against a profit-side floor in fZlNGWvd2Ko ("break even" on the day).
> "if we go back to break even, we stop the session"
**Source GPS: fZlNGWvd2Ko | BEGIN**

## 5. Worker flags the merge pass should keep (from each file's section 3.6)
- All 8 raw files are auto-captioned; 6 have no `# ---` header (title `unknown`). Fabio is named only by the task for 0KyIEdvVKMQ, FawPrRUGNpk, LQvv5xgy_ik, StaphlRH8NQ, jasv3L-d8ZE.
- fZ trade 2 side is inferred ("he never says long"); the catalogue and ledger already say long.
- FawPr caption garbles: "view up" (VWAP), "CBD" (CVD), "cover" (stop), "Nasdaq effort area".
- 0jM5 positions 2 and 3: add or new trade is not stated; "five different position that were trailed" does not match the three he names.
- 8CWK: no PARTIAL rows and no ADD rows; he rejects adding a contract (already 10). The V1 catalogue wording "add high in the curve, not low" stays as quoted there.
