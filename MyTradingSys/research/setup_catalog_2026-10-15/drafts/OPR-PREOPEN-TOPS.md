# DRAFT catalogue row OPR-PREOPEN-TOPS: pre-open tops, break speed, and what follows (2026-10-15)

Status: DRAFT in its own file; `SETUP_CATALOG.md` is NOT edited. Not a Tom/Fabio/Malkan setup: it is an operator hypothesis about probabilities. Every parameter is labelled OPERATOR (his words) or OURS (a variant for G5, decided on DEV, never called his). No trader quote is used, so there is nothing for `verify_extract_quotes.py` to check; the operator text is `../sources/OPERATOR_2026-10-15_preopen_tops_break_speed.md` (a relayed paraphrase, see its header). Data checks: `../evidence/preopen_tops_checks.txt`. Operator's own caveat: "a suggestion to look into, not a hard rule"; "We need to understand the PROBABILITIES of what can happen and then frame rules around them".

### OPR-PREOPEN-TOPS Pre-open tops: how fast they break decides what follows
1. **Name / trader.** Operator reading (OPERATOR). Not Tom, Fabio or Malkan. Closest catalogue neighbours, for the flow layer only: FAB-1 (CVD pressure then break on volume), FAB-2 (absorbed push vs rewarded effort), TOM-6 (speed picks up at the break), TOM-12 (outside prices fail to hold, return inside); none says "break speed" in these words, so no quote is borrowed.
2. **What you see.**
   - Levels (OPERATOR, shot 60d1b41a87bb): two tops marked before the US open, 81720.9 (about 05:00Z) and 81146.6 (about 12:30Z); both are highs of 4h bars (checks file). How tops are chosen: NOT STATED (two of at least four unbroken 4h-bar highs were marked).
   - Hypothesis H1 (OPERATOR): broken quickly, then more likely sold later in the session.
   - Hypothesis H2 (OPERATOR): built slowly, then more likely to break higher levels (leveraged shorts taken out, liquidity grab) or to tag the upper Bollinger band.
   - Hypothesis H3 (OPERATOR): break of a 4h-or-higher support or resistance gives a bounce that can be real, can fade, or can stall and range while liquidity builds (three outcomes, no odds given).
   - Chart state on 2026-10-15 at 13:46Z (not a hit of H1 or H2: neither top was broken): price fell from the 12:30 dump, broke the 4h 00:00 low 80188.0 at 13:28Z, bounced to 80743.5 by 13:45, was at 80570 (3m BB mid 80492, upper 80804) when the shot was taken; our 1m close at 13:50 was 80220.6, so that bounce faded within 5 minutes of the shot (after-the-fact, one instance).
3. **Entry, stop, target, management.** NOT STATED. The operator gives probabilities to study, not a trade. Nothing filled in; any entry or stop here would be OURS and belongs to G5.
4. **Context.** US session (the 13:30Z cash open while the US is on EDT until 2026-11-01; 14:30Z afterwards). BTC has no cash open: using it as an anchor is OURS (see the existing catalogue note, BTC visibility key). Not a hard rule (OPERATOR).
5. **BTC visibility: YES.** Tops, 4h levels, break time and speed, BB, session returns, MAE/MFE: 1m klines. Flow state: taker delta/CVD from klines (aggTrades for finer), OI from the archive `metrics` 5m (coverage on disk must be checked first: on this machine the archive ends 2026-09-26) and the 1m recorder from 2026-10-05.
6. **Evidence.** 1 instance (2026-10-15, no break of either top yet: so 0 instances of H1/H2 outcomes; H3 has one, the 13:28 break of the 4h low and its fade). No ledger trade.
7. **Gaps.** "Quickly" and "slowly": NOT STATED. Which tops count: NOT STATED. How far "later in the session" reaches: NOT STATED. "Real / fade / stall" thresholds: NOT STATED. Who is trapped ("leveraged shorts"): NOT STATED and not visible in our data (no liquidation history on disk; the old liquidation-cluster fields are null in historical snapshots).

## Parameter table (every parameter labelled)

| parameter | value or definition | label |
|---|---|---|
| tops are levels worth watching | at least the two marked ones | OPERATOR |
| which tops qualify | OURS variant: confirmed 15m swing highs (3 bars each side) formed between 00:00Z and the open, still unbroken at the open, at most 3 x ATR(14, 1h) above the open price; alternative: highs of 4h bars of the last 24 h | OURS |
| the open | 13:30Z (EDT) or 14:30Z (EST) = 09:30 New York, by calendar; control: a fixed 13:30Z all year | OURS |
| break | first 3m close above the top by at least 0.1 x ATR(14, 3m) (grid 0, 0.1, 0.25) | OURS |
| speed, definition S1 | minutes from the open to the break (quick = in the first tertile of DEV, slow = in the last tertile) | OURS |
| speed, definition S2 | ATR-normalised approach: (close at the break - lowest low in the previous 10 3m bars) / ATR(14, 3m); quick = top DEV tertile | OURS |
| speed, definition S3 | dwell: number of 3m bars with the high within 0.25 x ATR(14, 3m) below the top before the break; slow = long dwell (top DEV tertile) | OURS |
| choice among S1-S3 | the one with the largest DEV separation of outcome H1 at fixed n; the other two stay in the trial ledger; checked once on VALIDATION | OURS |
| 4h level | high or low of any closed 4h bar of the previous 48 h (and 1D/1W levels as a separate bucket) | OURS |
| "level held" | no 3m close beyond the 4h level by more than 0.1 x ATR(14, 3m) within the horizon | OURS |
| "sold later in the session" | horizon returns: close at +1 h, +3 h, +6.5 h after the break (BTC has no session close; 6.5 h = the US cash session length) below the break price | OURS |
| "tags the upper Bollinger band" | any 3m or 15m high at or above the BB(20,2) upper band within the horizon (two tests, reported separately) | OURS |
| "takes out higher levels" | the next unbroken top above is exceeded by one tick within the horizon | OURS |
| bounce is "real / fade / stall" (H3) | real: price recovers more than 0.5 x the break distance and holds above the broken level for 6 closes; fade: recovers, then closes back through the broken level within the horizon; stall: range under 0.5 x ATR(14, 15m) x 10 bars; other = none | OURS |
| flow covariates | at the break: OI change over the prior 30 min (up, flat, down), CVD slope over 15 min (up, down), sign of net delta in the break bar and the 3 bars before | OURS |

## Outcomes to measure (per instance)
1. Session return: close at +1 h, +3 h, +6.5 h vs the open price and vs the break price.
2. MAE and MFE in ATR(14, 1h) units from the break, over the same horizons, long and short measured separately (so H1 and H2 are tested as signed claims).
3. Whether the 4h level held (definition above), whether the next top was taken, whether the upper BB was tagged.
4. For each: the conditional frequency given break speed (quick / middle / slow), with a Wilson 95 % interval and n, then the same split by the flow covariates (2 x 2 only, because n is small).

## G5 event-study sketch (DEV only, fee-net; not run)
Same structure as the plan's G5 row: break instances from the DEV days, unconditional frequency as the baseline, and the same level without the speed condition as the control; fee-net R only for the second step: where a conditional outcome beats baseline, a plain rule (short at the break close for H1, long on the first pullback for H2) is costed with the METHOD.md fees (taker 5 bp + 1 bp slippage per fill) and stops from G2 (none stated: OURS variants). Holdout stays sealed; VALIDATION once, after the DEV choice. n is the risk: about one US open per day, tops broken on some of them, so with a 6-month DEV window the break count is expected in the tens, not hundreds; every table prints n and an interval and a cell with n < 10 is not read.
The task card is `MyTradingSys/system/tasks/opr-preopen-tops-g5-dev-event-study-brea.json` (state raw, then refined by `tasks.py check`).
