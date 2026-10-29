# PRE_REG: TOM-CTX-DIV (Tom correlation divergence filter) - FROZEN 2026-10-29, before any outcome was computed

Spec source: EXTRACT.md section 4 (OURS, unchanged). Every number below is OURS (Tom states none). FROZEN.

## Data audit (AUDIT.txt, daily bars, public data)
| Instrument | First | Last | Bar | Source |
|---|---|---|---|---|
| DAX (^GDAXI) | 2017-07-14 | 2026-10-23 | 1d | Yahoo chart API |
| ES=F, NQ=F, DX-Y.NYB, ^N225 | 2017-07-14 | 2026-10-26 | 1d | Yahoo chart API |
| BTCUSDT | 2017-08-17 | 2026-10-29 | 1d | data-api.binance.vision |
Intraday `dax_raw`/`nq_raw` exist only from 2024-10 and are NOT used (too short for n). Grid is DAILY as-of, not hourly: deviation from EXTRACT s4 "hourly bars", taken at the card's default (daily as-of) because hourly ES/Nikkei history is not free beyond ~2 years. DECISION (OURS).

## Grid and as-of rule (nothing after the traded market's close is used)
- H1 traded = DAX cash close (Xetra 16:30 UTC). Nikkei: same-date close (06:00 UTC, stale by design). ES/NQ/DXY: last close on or before date-1. BTC: daily bar of date-1 (closes 00:00 UTC of date).
- H2 traded = BTC daily bar (closes 00:00 UTC next day). ES/NQ/DXY: same-date close (earlier than the BTC close).
- Weekends/holidays: last available close carried forward (zero return). DXY enters sign-flipped.

## Rules
- Divergence day D: |L-day move| of the traded market > nearest-rank 80th percentile (primary cut) of the trailing 250 values (excluding D) AND sign opposite to the sign of the median basket L-day return.
- Primary: L=2, cut 0.8, H1 basket B1 = {ES, Nikkei, BTC}; H2 basket B1 = {ES, DXY flipped}.
- Trigger (convergence start): first day t in D+1..D+5 where median basket 1-day return has the sign of the traded market's move AND the traded close has not made a new extreme since D. Entry at close t, fade direction (short if up, long mirror), exit at close t+3 (hold 3 trading days). No stop.
- Secondary (reported, not selected): divergence-day entry (entry at D close). Control (a): same top-quintile move WITHOUT the cross-market condition, trigger = traded 1-day return against the move and no new extreme. Control (b): shuffled-basket placebo: basket series circularly shifted by random 60..N-60 days (same shift for all members), 100 draws, seed 11.
- Non-overlap: a D at or before the previous exit is skipped. Clusters = entry month; cluster-robust SE and month-bootstrap (2000 draws, seed 7) 95% lower bound of the mean.
- Fee+slippage round trip (OURS): H1 FDAX/FDXM 0.0004 (4 bp); H2 BTC perp 0.0010 (10 bp).
- Splits by grid index: DEV older 70%, VALIDATION next 15%, HOLDOUT last 15%. H1 DEV 2017-07-14..2024-01-11, VAL 2024-01-12..2025-06-04, HOLD 2025-06-05..2026-10-23. H2 DEV ..2024-01-24, VAL 2024-01-25..2025-06-11, HOLD 2025-06-12..2026-10-29. VALIDATION once, HOLDOUT once and only if VALIDATION passes (run_div.py enforces via split_reads.json).
- Pass bar: primary fee-net expectancy > 0 on VALIDATION with bootstrap lower bound > 0 and above control (a) mean and above placebo p95; then holdout. HOLDOUT or VALIDATION n<30 is INCONCLUSIVE, never pass. Otherwise TOM-DIV is not added.

## Expected events (count-only, no returns computed: `run_div.py --count-only`)
Primary H1: DEV 35 / VAL 8 / HOLD 11. Primary H2: DEV 52 / VAL 16 / HOLD 7. VALIDATION and HOLDOUT are below n=30 by construction: the best possible verdict on them is INCONCLUSIVE (low power stated in advance); DEV is the only split with n near the MDE.

## Gates pasted
`verdicts.py check 'tom correlation divergence'`: no prior row matches. Safe to pre-register.
`prereg_gate.py --n 35 --sd 0.021 --cost 0.0004 --m auto --new-cells 40`: m 105, z_holm 3.494, MDE 0.015 R per event: PASS (H1).
`prereg_gate.py --n 52 --sd 0.06 --cost 0.0010 --m auto --new-cells 40`: m 105, MDE 0.036: PASS (H2). sd values are OURS two-point (daily sd x sqrt 3).

## Trial-ledger variants (40 cells + 2 modes each, all go in layer_lab/TRIALS.md)
H1: baskets B1 {ES,Nikkei,BTC}, B2 {ES,Nikkei}, B3 {ES,BTC} x L {1,2,3,5} x cut {0.8,0.7} = 24. H2: B1 {ES,DXYflip}, B2 {NQ,DXYflip} x L {1,2,3,5} x cut {0.8,0.7} = 16. None is selected on VALIDATION; the primary is fixed above.
