# Order-flow extract: LIVE TRADING: DAX Short Using My Correlation Trick! (`e83njGZFrPw`)

- **Video ID:** `e83njGZFrPw`
- **Analyst:** Tom Vorwald (@TomVorwald), published 2026-10-23; analyst statements are context, never signals
- **Source:** `raw_transcripts_canonical/e83njGZFrPw_raw.txt` (browser transcript panel, 82 cues, 1802 words; on disk, no network; position = third of transcript)
- **Scope:** order-flow idea only (acceptance of lower prices, thin liquidity, logical stop). The DAX/S&P comparison, DAX heavy-weight stocks, cash sessions, market open and correlation trick are index-futures content, not carried to BTC (OPERATOR_DECISIONS 2026-11-12); BTC is read on its own terms
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## What is useful for us

### R1. Thin liquidity before the move (SOURCED)

Rule: Demand drying up in a range precedes the break.

> "it was very clearly visible that liquidity was drying up."
**Source GPS: e83njGZFrPw | BEGIN**

### R2. Range resolves either way (SOURCED)

Rule: A range alone gives no direction; direction needs the volume evidence.

> "And whenever a range appears, the move can of course go either downwards or it can go upwards."
**Source GPS: e83njGZFrPw | BEGIN**

### R3. Volume spike on the first move (SOURCED)

Rule: The first move out is accompanied by a volume spike; this shows real participation.

> "I don't just have the first move down, which by the way was also accompanied by a volume spike."
**Source GPS: e83njGZFrPw | MIDDLE**

### R4. Acceptance of the new prices (SOURCED)

Rule: After the spike, price staying and bouncing inside the new zone means the market accepts it.

> "the market then said, I accept these lower prices."
**Source GPS: e83njGZFrPw | MIDDLE**

### R5. Stop at a logical reference (SOURCED)

Rule: The stop sits at the swing that proves the idea wrong (here the second acceptance), not a fixed distance.

> "a stop-loss needs a logical point of reference."
**Source GPS: e83njGZFrPw | MIDDLE**

### R6. Target: trade through the accepted area (SOURCED)

Rule: After acceptance at a level, price is expected to trade through that area once more before moving on.

> "whenever a market has found acceptance at a certain level again, it is statistically much more likely to trade through that area of acceptance once more before moving on."
**Source GPS: e83njGZFrPw | MIDDLE**

### R7. Open at prior value low, aggressive move away (SOURCED)

Rule: Opening at the previous period's value low and moving down hard supports the short.

> "We had the opening up here at the previous day's profile value low and immediately made an aggressive move down."
**Source GPS: e83njGZFrPw | MIDDLE**

### R8. Partial exit, let the rest run (SOURCED)

Rule: Exit management choice: take part off, let part keep running.

> "make partial sales and let part of the position keep running"
**Source GPS: e83njGZFrPw | END**

## What we do not do

| Item | Why |
|---|---|
| Compare DAX to S&P ("the S&P future moved sideways during the same period where the DAX was already marching upwards") | index cross-market pair; BTC analogue already judged NOT-ADD in `tom_correlation_trick_2026-10-26` (R78) |
| Look through the heavy-weight stocks (Siemens, SAP, Allianz, Airbus, Telecom) | index composition; no BTC equivalent |
| Cash-session and market-open timing | index-futures clock (decision 2026-11-12) |
| Short because price is at an all-time high | we take no direction from price level alone; his view is context |
| His chart levels and trade as a signal | analyst statement is context |

## What we should do

- Test the accepted-breakdown retest and the logical-stop exit as frozen rules only after the family-2 order-flow level cards finish; no sweeps. (OURS)
- Keep the stop idea (swing that proves the idea wrong) as an exit variant on whichever entry passes. (OURS)

## What we learn

- One discretionary swing trade shown with hindsight (one trade, no n); its transferable logic: volume spike out, acceptance in the new zone, entry on the retest, stop beyond the second acceptance, target the old range edge. (OURS)
- No parameter is stated: no spike size, no number of closes for acceptance, no stop distance. All are OURS below.

## Testable ideas (frozen rules; every number OURS, none from Tom)

| # | Frozen rule | Tested before? |
|---|---|---|
| 1 | Accepted breakdown retest: BTC 1h; range = prior 24 bars (high minus low under 2.5% of price); event bar closes below range low with volume at least 2x the median of the prior 24 bars; acceptance = next 2 1h closes also below range low; short at the next open when a 1h high touches the range low from below within 24 bars; stop 0.2% above the highest 1h high since the breakdown; target the lowest low since the breakdown, exit 48 bars; taker fee both sides; mirror for longs | No. T04 first-touch sweep-reclaim and R25 fractal fades are fades at levels, not retests after accepted breaks; `btc_of_level_auction_1112` B1 is absorption at a level |
| 2 | Logical-stop exit: on any entry that has a frozen entry rule, compare stop at the last swing against a fixed 1x ATR14 stop, same entries, same exits; report net R of both | Partly. Stops tested were ATR or signal-bar extreme (T01, T05, R12, R19); swing-reference vs ATR was never the question |
| 3 | Half off at the target, trail the rest under the prior 1h low (long) or above prior 1h high (short) | Yes. `census_5m_15m_session_ladder_2026-11-09` (R15) tested node/BE/half/trail exits; no edge, 10 of 10 negative. Do not repeat |
