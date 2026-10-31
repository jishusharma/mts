# Funding rerun: flat 1 bp vs real signed funding (card fix-screen-real-funding, T06-F1)

DEV only (rates and bars < 2024-07-01). Cost to a trade = side x sum(rate of settlements in (entry, exit]) x 100 % of notional
(long pays a positive rate, short receives it). The old flat 1 bp per straddling encounter stays as `FUND_OLD` (old_flat_1bp).
Loader: `bt_data.load_funding_strict(base)`: `raw_fund/fundingRate` first, then `raw/fundingRate`, raises if neither exists
(screen default base F:/MTS/Dumps/backtest; this run read Dumps/backtest/raw_fund/fundingRate in the live tree, 4929 rates, read-only).

Primary cell (d=1, h=60), mean G after funding, % per encounter (before the 0.14 % trading cost):

| arm | n | old flat 1 bp | real funding | move (pp) |
|---|---|---|---|---|
| T | 40 | -0.05678 | -0.05610 | +0.00067 |
| notF | 1399 | -0.00674 | -0.00548 | +0.00126 |
| C | 1439 | -0.00813 | -0.00688 | +0.00125 |

Verdict INCONCLUSIVE before and after: no flip. Scope: the +0.0013 pp is the largest arm move in the primary cell (d=1, h=60) only, not overall.
The T06 audit (`T06_cost_fill_realism.md`) shows a larger secondary-cell move: preopen S1 SHORT h=180, +0.0181 pp. Largest single-cell funding difference 0.129 %.
INCONCLUSIVE is forced by the sample rule (n_T = 40 < 200, PRE_REG.md), not by funding being small.
Numbers equal `scripts/T06/out/funding_rerun.json` (same formula, independent audit script). No published verdict, ledger row or
pre-registered bar was edited; the RESULT.md text still describes the flat substitute it was produced with.

Boundary rule (card funding-cost-boundary-jitter): archive calc_time sits 1-31 ms after the 8h boundary (1215 of 2736 settlements, T06 doc). `funding_cost_pct` now floors each settlement stamp to the second, so a settlement at 08:00:00.005 counts as 08:00:00 and the window stays (entry, exit]: entry exactly on the boundary is not charged, exit exactly on it is. Before, the jitter did the opposite (entry-on-boundary charged, exit-on-boundary exempt). Primary-cell move from the rule: not re-measured on this machine (the DEV funding archive is only on the desktop live tree); bar-aligned trades straddling a boundary are the only ones affected, no verdict change expected. Re-measure with `screen.py` where the archive exists.
