# EVENTS: BTC order-flow map A2/A3 on DEV (card btc-of-map-events-1112)

Status: NOT_RUN on the machine that built this card (DESKTOP-F7IU69N has no F: drive; `F:/MTS/data/tom_raw/klines` and `F:/MTS/Dumps/backtest/raw/fundingRate` are absent). No number below was computed or invented.
Code and tests are done and pass on synthetic data (`events.py`, `test_events.py`, 9 tests, fail-first confirmed). Where the inputs are on disk, run:

    python MyTradingSys/research/btc_orderflow_map_1112/events.py --split dev

It overwrites this file with the A2/A3 table (event, horizon, n, mean net %, sd, t, share positive, placebo 1-99 % band, session mix, Regime mix; INSUFFICIENT_N where n < 180), then `python scripts/dev/verdicts.py backfill`.

| Event | Horizon | n | mean net % | sd | t | share positive | placebo 1-99 % | session mix | Regime mix |
|---|---|---|---|---|---|---|---|---|---|
| A2 absorption | 15m | NOT_RUN | | | | | | | |
| A2 absorption | 60m | NOT_RUN | | | | | | | |
| A3 funding extreme | 15m | NOT_RUN | | | | | | | |
| A3 funding extreme | 60m | NOT_RUN | | | | | | | |

A1 remains NOT_RUN (aggTrades not on disk). VALIDATION, GAP, RESERVE and HOLDOUT were not opened; the loader refuses any split but dev.
DECISION (OURS): no verdicts.py row is added, because a row needs a measured n and mean and none exists.
