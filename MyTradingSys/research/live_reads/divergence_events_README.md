# divergence_events.csv - provenance and rules

DESCRIPTIVE ONLY. Forward evidence for `tom-corr-divergence-backtest`. No parameter, threshold or
verdict may be picked from this file; it records what a live read saw, not a tested rule.

## Columns
- `utc` - event timestamp, UTC, ISO 8601 with Z.
- `btc_since_open`, `es_since_open`, `nq_since_open` - percent move since the 13:30Z US cash open,
  as read live. Source: the live read of that day (`2026-10-26_cross_market_tools/`).
- `vix` - VIX level if the read recorded one; empty when it did not.
- `r5m_1h_es`, `r5m_1h_nq` - rolling 1h correlation of 5m returns vs BTC at the event. Empty when the
  read did not record it.
- `footprint_delta_note` - free text: what the footprint/delta read showed, or why it is absent.
- `out_30m`, `out_60m`, `out_120m` - the same since-open numbers plus `gap` (ES since-open minus BTC
  since-open) at +30/+60/+120 minutes, each with the exact timestamp the row was taken from.

## Event 1 (2026-10-26 14:36Z) - what is exact and what is not
- The 14:36Z since-open numbers come from the card text, which quotes the day's live read.
- `vix`, `r5m_1h_es`, `r5m_1h_nq` are empty: `watch_rows.csv` (893 rows, 14:58:31Z..06:41Z next day)
  starts 22 minutes after the event and never records VIX or NQ correlation. Left empty, not guessed.
- The three outcomes are read from `watch_rows.csv` at 15:06:05Z, 15:36:40Z and 16:36:59Z.
  `watch.py` uses the corrected since-open baseline (13:25 bar close for ES/NQ, 13:30 1m open for BTC),
  not the `live.py` baseline bug named in that folder's README.

## Append only
Use `python MyTradingSys/research/live_reads/divergence_event.py append --utc ... ...`. It refuses a
duplicate `utc` and refuses a row whose outcome columns are not all filled, so a row is never half-written.
