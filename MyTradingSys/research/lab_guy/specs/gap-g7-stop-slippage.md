# Lab_Guy spec detail for card gap-g7-stop-slippage (2026-10-18, labguy-pass-b)

Full text of the items the card shortens (card item limit 400 chars). The card is the contract; this file is the detail.

## steps item 1

Do steps 2-3 first. Do NOT fetch aggTrades (step 4) until the NUC spec review is in this note as a REVIEW-SPEC: ACCEPT|FIX|REWORK line (C2); apply a FIX before fetching

## steps item 2

Tests first (red), expected numbers hand-computed in the test file, not from slippage.py: first_trade_beyond(trades, level, side) gap through the level returns price - level, exact hit returns 0, no trade beyond returns None, both crossing directions; price_after(trades, t_cross, delta_ms, level, direction) on a synthetic series (known 5 USD gap gives 5.0 at delta 0); tercile assignment incl. ties at the boundaries

## steps item 3

From 1m klines (F:/MTS/data/tom_raw via bt_data.load_klines, end_ms=2024-07-01, assert in code that no bar at or after 2024-07-01 is read) compute daily range % for DEV days 2022-01-01..2024-06-30; sort; take 4 evenly spaced days per tercile (12 days, OURS) into days.csv. Extension rule fixed now: if a bucket has fewer than 500 events after its days are processed, add the next 4 evenly spaced unused days of that tercile, up to 8 per tercile (24 days); the rule looks at event counts only, never at slippage values; each extension is a TRIALS.md row

## steps item 4

Fetch aggTrades for one day at a time with fetch_binance_archive.py --datasets aggTrades into a scratch dir outside the repo (about 0.1-0.3 GB zipped/day); verify and record the zip sha256 in days.csv (Binance publishes .CHECKSUM), write that day's events file, then delete that day's raw zip at once (no raw is committed, repo is public)

## steps item 5

Per day, for every round-100 USD level crossed up or down (OURS proxy for stop levels): slip_bp = adverse (price - level) in crossing direction / level * 1e4 at three latencies, delta 0 ms (the first trade at or beyond the level: the trade-through proxy, bounded by the 0.1 USD tick so it mostly re-confirms 0.0) and delta 250 ms and 1000 ms (OURS: price of the last trade at or before t_cross + delta, because a stop-market fills after trigger-to-order latency); signed, keep reversals; R at stop widths 0.20/0.40/0.80 %

## steps item 6

Write research/gap_g7_stop_slippage_2026-10-18/SLIPPAGE.md + events summary: n events and n days, median, p90 per bucket x delta; events inside a day are clustered, so a day-level bootstrap range of each median (OURS: 1000 resamples, seed recorded); name it a Binance USD-M BTCUSDT trade-through/latency proxy (no own-size impact, not Deribit, REPORT G8); propose a default (OURS: delta 250 ms median per bucket, delta 0 is the optimistic bound), trust tag UNCHECKED; tom_bt.py and maker_model.py are not edited (the adoption is its own C2 card); one row per run in layer_lab/TRIALS.md

## done_when

SLIPPAGE.md with, for each of 3 buckets and each delta (0, 250, 1000 ms): n events, n days, median and p90 in bp and in R at the 0.40 % stop, day-bootstrap range, n >= 500 events per bucket or marked THIN after the 8-days-per-tercile cap; days.csv (day, tercile, range %, zip sha256); TRIALS.md rows; test passes; scratch dir holds no aggTrades zip; no day on or after 2024-07-01; the proposed default labelled OURS. Verify: content commit sha, git cherry origin/fast-track <sha> empty, git ls-tree shows the files.
