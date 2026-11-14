# PRE_REG: prior-NY-session POC as the target after value re-entry, confirmed on NEW coins

Written 2026-11-13 ~19:00Z before any outcome of THIS study was computed. Slug edge5-ny-value-poc-target-1113.
Parent: MyTradingSys/research/ny_session_value_return_2026-11-13/ (edge4). Parent code is copied unchanged as `parent_study.py` (session window, `prior_ny_session_profile`
call, setup detection, costs, cluster bootstrap); this study only adds the POC target, the two stops and the new-coin run.

## Hypothesis
Parent finding (BTC/ETH/SOL, descriptive, noted AFTER seeing the numbers): from the entry (open outside the prior NY-session value area, re-entry, two 30-minute closes inside),
price touches the prior-session POC about 69% of the time (Tom: "about 70%"), while the opposite value edge is reached only about 40%.
H: that 69% reproduces on coins the parent never used, and the trade "enter at the second inside 30m close, target = prior-session POC" has positive fee-net mean R.
The count on seen coins was descriptive on the same data, so it cannot count as evidence; the new coins are the test.

## Data
Binance SPOT 1m klines, public archive data.binance.vision monthly zips, 2020-01 to 2026-10 (coin listings that start later start later; coverage printed in RESULT.md).
TEST set (new coins): BNBUSDT XRPUSDT DOGEUSDT ADAUSDT AVAXUSDT LINKUSDT LTCUSDT DOTUSDT TRXUSDT BCHUSDT. SEEN set (labelled "seen data", reported separately): BTCUSDT ETHUSDT SOLUSDT.
BTCUSDT is also used for the `Regime mix:` label only. Closed 1m bars only, signals at the close of the last 1m bar of a 30m block, fills at that close.

## Exact rule (identical to the parent except the target and the stops)
- Session = NY cash 09:30-16:00 America/New_York weekdays (13:30-20:00 UTC summer, 14:30-21:00 UTC winter, `auction_context._us_dst`); prior session = previous weekday (Monday: Friday);
  sessions with < 90% of expected 1m bars skipped; US holidays not modelled. Profile = `prior_ny_session_profile` (70% value area, HLC3, bin 5 bp of mean close).
- Day opens outside: first 1m open > VAH (SHORT) or < VAL (LONG), strict.
- Setup: first pair of consecutive 30m closes (blocks aligned to session start) both inside [VAL, VAH], first block of the pair >= block 1 (first 30 minutes skipped; no variant without the skip). Entry = close of the second block.
- Target = prior-session POC (profile `poc`). Skip the setup when the POC is less than 3 x round-trip cost = 36 bp from entry in the trade direction (POC on the wrong side of entry counts as skipped); the number skipped is reported.
- Stop A "extreme": running session extreme so far (high for short, low for long, session open to entry) beyond by a 1 bp buffer (as parent).
- Stop B "edge": the value-area edge price re-entered through (VAH for a short, VAL for a long) beyond by 0.1% (10 bp).
- Time exit: last 1m close of the session. Stop-first on a 1m bar touching both stop and target. Skip when the stop distance < 10 bp of entry (parent guard).
- Net R = (signed move/entry - round-trip cost) / (stop distance / entry); round-trip cost = 2 x (fees.BINANCE_TAKER + fees.BINANCE_TAKER/5) = 12 bp. Gross R = same without cost.
- Balanced day: parent rule (prior session inside the session before it, OR today's first-30-min range < median of the prior 20 sessions). "All days" = no filter.

## Cells (EXACTLY 8, fixed)
stop {A extreme, B edge} x side {long, short} x day type {all days, balanced}. Pooled over the 10 new coins. Per-coin and per-year numbers are descriptive, not cells.
The same 8 cells are re-run on BTC/ETH/SOL as "seen data" and are NOT part of the verdict.

## Report order
1. Plain counts per cell (new coins): n setups, skipped for < 36 bp, reach-POC % (touch before session end, stop ignored) and reach-stop %, median reward-to-risk at entry, gross vs net mean R, per-year mean net R, share of total R from the best 10 days.
2. Trade table: cell | n | days | reach-POC % | median RR | mean R gross | mean R net | trade CI | day CI | placebo p | 2024+ | verdict.
3. Seen-data table (same layout).

## Pass rule (per cell, new coins, ALL required)
1. mean net R > 0. 2. 95% bootstrap CI lower bound > 0 on the per-trade view (resample trades, 5000 draws) AND on the day-cluster view (resample session dates across coins, 5000 draws).
3. n >= 100 and >= 60 distinct session dates. 4. Beats a random-time-entry placebo inside the same session (entry at a random 1m close from the earliest possible entry minute (bar 89) to session end
that is inside the value area and passes the 36 bp POC-distance rule, same side, same POC target, same stop type computed at that moment, same costs); 2000 draws; real mean above the 95th percentile and placebo p (share of draws >= real) < 0.05/8.
5. Bonferroni over 8 cells: one-sided day-cluster bootstrap p (share of bootstrap means <= 0) < 0.05/8 = 0.00625. 6. The 2024-01-01-onward slice has mean net R > 0 (same sign as the full sample).
Verdict PASS only if all six hold; otherwise FAIL (or UNDERPOWERED when n/days fails with a positive mean).
Splits for descriptive reporting only: DEV to 2023-12-31, 2024+ from 2024-01-01 (VALIDATION/RECENT merged as in the parent).

## Parameter labels
| param | value | label |
|---|---|---|
| value area 70%, prior NY cash session | | SOURCED (VumVuGnCcFM; Of_wlv3xaZo, see Context) |
| skip first 30 min | yes | SOURCED (Of_wlv3xaZo) |
| target = POC of the prior session | | SOURCED in kind (VumVuGnCcFM "return to the Vpo ... about 70%"); exact use as a trade target OURS |
| two 30m closes inside as the hold | 2 x 30m | OURS |
| stop A session extreme + 1 bp | | OURS |
| stop B value edge + 10 bp | | OURS |
| min target distance 36 bp = 3 x round trip | | OURS (task order) |
| min stop 10 bp, bin 5 bp | | OURS (parent) |
| balanced-day rule | | OURS (concept SOURCED VumVuGnCcFM / VxN5IxTwpbE) |
| costs 5 bp taker + 1 bp slip per side | | OURS (repo fees.py) |
| new coins list, 8 cells, Bonferroni | | OURS |

## Context
Regime: balanced vs all days is a cell dimension; RESULT.md also gives the BTC bull/bear/range mix (close vs 200-day SMA, 5% band) as `Regime mix:`.
Phase: balance (Tom: the return to the POC holds when the market stays balanced; "when a market becomes strongly trending, please stop trying to get back").
Session: prior NY cash session profile, traded in today's NY cash session, 13:30-20:00 UTC (14:30-21:00 winter), first 30 min skipped.
Entry: second consecutive 30m close back inside the prior value area after an open outside; target prior-session POC; stop extreme or value edge; time exit at session end.
Quotes (SOURCED, Tom, gap report sonnet_conditions.md): VumVuGnCcFM "markets always tend to return to the Vpo to regain balance. And that happens about 70% a little over 70% of the time. But heaven help us if that's not the case.";
Of_wlv3xaZo "stop trading in the first 30 minutes of the New York session"; Of_wlv3xaZo "if you only trade during cash hours, please only refer to the cash session."; aursfDVYzUk "we also like to call the point of control a magnet as long as the market environment is stable."
