# FLOW pre-registration (written before any result was computed). All parameters OURS, none sourced.

Inventory (checked 2026-11-11)
- Funding: Dumps/backtest/raw/fundingRate/BTCUSDT-fundingRate-2020-01..2026-09.csv (8h, Binance archive starts 2020-01, not 2019-09). On disk, no fetch needed.
- OI: F:/MTS/data/binance_metrics/BTCUSDT-metrics-2022-01-01..2025-12-31.csv (5m sum_open_interest). Event (c) is limited to 2022-2025.
- Liquidations: no history on disk (only screenshots). Event (b) uses the volume/drop proxy only.
- 1h klines: fetched from data.binance.vision (public) USD-M BTCUSDT 1h 2020-01..2026-10 into F:/MTS/edge_views_data/k1h.

Common rules
- Trade = entry at the OPEN of a 1h bar, exit at the CLOSE of the last held bar (hold H bars). Net = side*(exit/entry-1) - 0.10 % (10 bp round trip taker). Primary number = price + fees only.
  Secondary (reported, not the verdict): also subtract funding paid / add funding received for settlements inside the hold.
- One position at a time per rule (signals while in a position are skipped; long and short of one rule share the slot).
- Split by entry time inside each rule's own eligible span: first 60 % = DEV, then 30 days dropped, remainder = VALIDATION.
- Placebo: per rule, side and split, the same number of entries drawn uniformly from the eligible hours of that split, same side, same hold,
  200 draws (seed 11); overlap ignored in the placebo. Percentile = share of placebo mean-net values below the real mean (95+ = beats chance).
- Verdict rule frozen: PASS needs mean net > 0 in DEV and VALIDATION, |t| >= 2 in VALIDATION, placebo percentile >= 95 in both, n >= 30 each. Otherwise FAIL (or INCONCLUSIVE if n < 30).

Events
(a) FUNDING EXTREME. At each funding settlement timestamp t (00/08/16 UTC), compare the rate with the trailing 365 days of earlier settlements (window [t-365d, t)).
    rate >= its 95th percentile -> SHORT; rate <= 5th percentile -> LONG. Entry at the first 1h bar open at or after t. H = 72 bars (3 days). Eligible from 2021-01-01.
(b) CASCADE PROXY. 1h bar with close/open-1 <= -3 % and volume > 3x the median volume of the previous 720 bars (30 days, current bar excluded) -> LONG at the next bar open, H = 24.
    Mirror: close/open-1 >= +3 % with the same volume test -> SHORT at the next bar open, H = 24. Eligible from 2020-02-01.
(c) OI FLUSH. At a bar close: OI(now)/OI(4h earlier)-1 <= -5 % and close/close(4 bars earlier)-1 < 0 -> LONG at the next bar open, H = 24. (Long only.) Eligible 2022-01..2025-12 (OI data span).
No parameter is changed after seeing results.
