# PRE_REG (brief): positioning build then forced flush, BTC/ETH and 20 coins, 2026-11-15, frozen before any return or fee-net number

Status: BRIEF, ready to freeze. Only counts and next-24h descriptive stats (DEV, no fee, no trade) were computed; they are below. SOURCED = named file; OURS = our choice. Research, not advice. Testnet only. Card: `edge-brief-funding-oi-gemini3-1114` (its Gemini lab folder does not exist; this brief is the deliverable).

## Context

Question: when new positions pile in while price falls (OI up, funding positive: the crowd leans long into a decline), does the later forced unwind (OI collapses on a big red day) mark a washout that rebounds over about 3 days, net of 12 bp, beyond what a plain price flush gives?
Operator observation 2026-11-15 (OURS to test): three red days, OI rising, funding positive, no flush yet. Live state is not checkable here (live mirror refused, OI cache ends 2026-11-04); the brief covers the pattern, not today.
Phase: BTC falling or choppy (the crowded-long washout phase); the per-coin gate is the close below its 20-day mean (OURS).
Entry: open of day d+1 after the flush day d (full rule below).
Regime: phase where a crowded-long washout can happen = a falling or choppy market. Gate (OURS): the signal day close below its own 20-day mean; BTC cycle state BULL/BASE/BEAR is printed as a descriptive row, not a gate.
Session: none (daily bars, 24/7). OI and funding stamps at 00:00 UTC are used only after they print.
Regime mix: BTC daily close vs 200d SMA, 2021-01-01..2026-11: bull 49 % / bear 38 % / range 13 % (SOURCED: `research/capitulation_breadth_2026-11-13/RESULT.md`). Build-then-flush events by year (20 coins, `counts_buildflush.json`): 2021 8, 2022 77, 2023 40, 2024 40, 2025 40, 2026 27, so DEV leans bear (2022) and VAL spans the 2024 bull, 2025 and the 2026 bear.

## Repeat check: what already failed (do not re-run these)

| Prior study | Rule | Result | Why this brief differs |
|---|---|---|---|
| `t12_funding_extreme_reversal_2026-11-14` | funding extreme plus reversal bar, 68 coins, 1d | KILL, VAL n 125 and 611, price-only net -0.079 / -0.036 R | no funding level as trigger; funding only splits the OI-up group |
| `edge_crowding_reversal_1113` | funding extreme, account ratio, OI surge with flat price, 10 coins | 0 of 24 cells pass; OI surge flat price n 23-75, UNDERPOWERED | here price must fall and the trigger is the OI unwind, not the surge |
| `rsi_oi_unwind_newcoins_2026-11-13` | RSI extreme plus OI 24h <= -3 % (1h), 40 new coins | A FAIL: n 270, +0.025 R, -0.139 R without best 5 days | no RSI; requires a prior multi-day OI build; daily bars |
| `oi_pivot_2026-10-26`, `oi_side_2026-10-30` | OI x price at 30 min to 4 h, BTC | no lean beyond about 4 points, below fee | different clock (days) and an event sequence, not a state |
| `layer_lab/funding_extreme_event_table`, `btc_orderflow_map_1112` A3 | funding extreme fade, BTC | A3 n 819, -7.5 bp net, no edge | not a funding fade |
| `capitulation_breadth_2026-11-13` | price breadth washout, 60 coins | FAIL 0 of 12 | breadth uses prices only; here the washout is measured in OI |

Not in data: liquidation history (`btc_orderflow_map_1112/DATA_INVENTORY.md`: NOT_IN_DATA). The OI drop on a red day is the proxy for forced closes (OURS).

## Descriptive gate 1 (OURS): next-24h low after 3 red days, OI up vs OI down

Definitions (OURS): red day = UTC close < open; event = the day the red streak reaches exactly 3 (no overlap); OI3 = OI at that close vs OI at the close 3 days earlier; up >= +2 %, down <= -2 %, else flat; funding3 = mean funding over the 3 days; outcome = next UTC day low (fwd_low) and close (fwd_close) vs the event close. DEV = events before 2024-01-01 only. VAL events are counted, outcomes not computed. Scripts: `count_red3_oi.py`, `count_pool20.py`, outputs `out_*.txt`, `counts*.json`.

| Set | Group (DEV) | n | weeks | fwd_low median | share fwd_low <= -3 % | fwd_close mean |
|---|---|---|---|---|---|---|
| BTC | 3 red, OI up | 13 | - | -0.56 % | 31 % | -0.70 % |
| BTC | 3 red, OI down | 18 | - | -1.79 % | 33 % | -1.41 % |
| ETH | 3 red, OI up | 8 | - | -2.40 % | 38 % | -0.70 % |
| ETH | 3 red, OI down | 24 | - | -1.51 % | 25 % | +0.98 % |
| 20 coins | 3 red, any OI | 881 | 112 | -2.13 % | 38 % | -0.06 % |
| 20 coins | 3 red, OI up | 293 | 86 | -2.37 % | 43 % | -0.07 % |
| 20 coins | 3 red, OI up, funding > 0 | 171 | 76 | -2.38 % | 44 % | +0.08 % |
| 20 coins | 3 red, OI flat | 179 | 74 | -1.95 % | 35 % | +0.04 % |
| 20 coins | 3 red, OI down | 409 | 88 | -2.11 % | 36 % | -0.10 % |

VAL event counts (outcomes unread): BTC 66 (OI up 12), ETH 58 (OI up 20); 20 coins OI up 431, flat 391, down 628, OI up with funding > 0: 261, over 145 weeks.

Reading (descriptive, no fee, not a verdict):
- BTC and ETH alone are far too thin: 13 and 8 OI-up events in DEV. The operator's pattern cannot be judged on two coins; the 20-coin pool is the minimum.
- The 20-coin low mean differs by +0.06 pp between OI up and OI down (naive SE 0.33 pp, ignores same-day correlation across coins): the depth of the next-24h low is the same.
- OI up shows a slightly higher chance of a -3 % low (43 % vs 36 %, about 1.9 naive z, weaker once same-day coins are clustered).
- fwd_close mean is about zero in every group: no washout-and-bounce and no continuation on the 24h close. Shorting "OI up, funding positive" at the next open has no support (mean -0.07 % to +0.08 %), so that cell is NOT proposed.

## Hypothesis

H: a market that builds positions into a falling price (OI up over days while the close falls) and then prints a heavy red day with an OI collapse has flushed its weakest holders; the next 1 to 3 days rebound more than after a price-only red day of the same size.
Mechanism (OURS, not SOURCED): an OI collapse on a red day = forced or panic closing of the build-up; once those sellers are exhausted, fewer forced sellers remain than on a red day with no OI unwind. Control 1 separates this from plain mean reversion after a -3 % day.

## Rule (one cell, long only)

| Item | Value | Label |
|---|---|---|
| Universe | the 20 coins with an OI file in `F:/MTS/data_cache/binance/combo-edge-miner-1114/oi` (ADA ATOM AVAX BCH BNB BTC DOGE DOT ETC ETH LINK LTC NEO SOL TRX UNI VET XLM XRP ZEC), daily bars from `spot_1d`; delisted kept | SOURCED cache, choice OURS |
| Build window | days d-4..d-1: OI(d-1) / OI(d-4) - 1 >= +3 % and close(d-1) < close(d-4) | OURS |
| Flush day d | OI(d) / OI(d-1) - 1 <= -3 % and close(d) / close(d-1) - 1 <= -3 % | OURS |
| Regime gate | close(d) below its 20-day mean | OURS |
| Entry | open of day d+1 | OURS |
| Stop | below the low of day d | OURS |
| Exit | close of day d+3, or the stop, whichever first; stop first on an ambiguous bar | OURS |
| Cooldown | 5 days per coin | OURS |
| Cost | 12 bp round trip charged on entry and divided by stop distance (shared cost model) | SOURCED `rsi_oi_unwind_newcoins_2026-11-13/RESULT.md` |
| Split | DEV < 2024-01-01; VAL >= 2024-01-01 opened once | OURS (the split on the card) |
| Control 1 (must be beaten) | same price condition (3-day price fall, flush day <= -3 %) with the OI conditions removed | OURS |
| Control 2 | same coin, same side, shifted placebo +/- 8 weeks | SOURCED method `t12_funding_extreme_reversal_2026-11-14/PRE_REG.md` |

Parameter labels: every threshold above is OURS; none is the trader's. They are single guesses, not tuned: one build (+3 %), one flush (-3 % OI, -3 % price), one hold (3 days). No grid. Note: the event counts below were produced before the regime gate (20-day mean) and are therefore an upper bound on the gated n; the gate count is the first line of stage 1.

## Power estimate (counts from `count_buildflush.py`, no returns)

| Item | DEV | VAL |
|---|---|---|
| Events after 5-day cooldown (245 before cooldown, both splits) | 125 | 107 |
| Distinct signal days | 70 | 64 |
| Weeks with an event | 49 | 46 |

Cluster unit = the week (same-day coins are one market move). Scale (OURS assumption, replaced by the DEV figure at freeze): the 20-coin sd of the next-24h low is 4.0 %; a 3-day return sd of about 6 to 7 %. Minimum detectable mean at 80 % power, one-sided 5 %, is about 2.5 x sd / sqrt(weeks) = 2.2 to 2.4 % per trade with 46 VAL weeks, or 1.4 to 1.6 % if the 107 trades were independent (they are not). The 12 bp fee is small against this; the noise is the gate, so only a large rebound can pass. Expected verdict range: UNDERPOWERED unless the effect is above about 2 % per trade. The n floor (n >= 30 and weeks >= 20) is met by count: 107 and 46.

## Kill criterion

KILL if any of: (a) VAL price-only net mean R <= 0 with n >= 30 and weeks >= 20; (b) the rule does not beat Control 1 (same price condition without OI) by a positive mean R difference in VAL; (c) placebo p97.5 not beaten with n >= 100; (d) ex-best-5-weeks mean <= 0; (e) DEV mean R <= 0 (VAL is then not opened). One honest FAIL ends it; no re-tuning of thresholds; a second cell needs a new PRE_REG.

## Stage plan

1. Compute DEV only: gated event count, price-only net R, Control 1, placebo; record in `holdout_reads.csv` before any VAL read (append conflicts: keep both rows).
2. Open VAL once only if DEV mean R > 0 and Control 1 is beaten.
3. Funding split (funding3 > 0 vs <= 0) is a descriptive row in the result, not a gate.

## Look-ahead notes

OI and funding at the close of day d are the last 5m row of day d in the cache (stamp 00:00 UTC of d+1); the entry is the open of d+1, after that stamp. The `fwd_*` columns in the count scripts use the next bar by design (descriptive outcomes) and need allowlist rows if the lint flags them.
