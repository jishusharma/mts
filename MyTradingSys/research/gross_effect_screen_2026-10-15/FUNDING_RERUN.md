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

Verdict INCONCLUSIVE before and after: no flip. Largest arm move +0.0013 pp; largest single-cell funding difference 0.129 %.
Numbers equal `scripts/T06/out/funding_rerun.json` (same formula, independent audit script). No published verdict, ledger row or
pre-registered bar was edited; the RESULT.md text still describes the flat substitute it was produced with.
