# BTC options data collection (Deribit, public market data only)

Part of the independent options module (`MyTradingSys/options/OPTIONS_PLAN.md`). Data collection only: no orders,
no keys, no `private/*` calls, nothing imported from `execution/` or `layers/alerts/`, nothing in the live tree is
touched. Stdlib only (the repo uses `urllib`; `requests` is not a repo dependency).

Safety is enforced in code, not by convention (`deribit_opt_common.DeribitPublic`): only `public/<method>` is
accepted (anything else raises before a request is made), only `www.deribit.com` and `history.deribit.com` over
https are accepted, no auth header is ever sent, rate is hard-capped at 5 req/s (default 4, shared across threads),
10028 / 10040 / HTTP 429 / 5xx / network errors are retried with exponential backoff (1, 2, 4 ... capped at 60 s,
`Retry-After` honoured), any other API error is raised at once.

## Files

| File | Role |
|---|---|
| `collector/deribit_opt_common.py` | client, rate limiter, gzip append / repair, atomic writers |
| `collector/deribit_opt_snapshot.py` | one-shot (or `--every N` loop) full-chain snapshot |
| `collector/deribit_opt_backfill.py` | resumable historical backfill + `--report` |
| `tests/test_opt_*.py`, `tests/opt_testutil.py`, `tests/fixtures/` | offline tests (fake HTTP, recorded response shapes) |
| `data/` (gitignored) | `chain/YYYY-MM-DD.jsonl.gz`, `hist/...` |

## Run commands

```
python MyTradingSys/options/collector/deribit_opt_snapshot.py                 # one snapshot (~70-150 s)
python MyTradingSys/options/collector/deribit_opt_snapshot.py --every 900     # loop on a fixed 15-min grid, Ctrl+C stops
python MyTradingSys/options/collector/deribit_opt_backfill.py --max-seconds 1500   # everything, resumable
python MyTradingSys/options/collector/deribit_opt_backfill.py --only dvol,perp,funding,delivery,instruments
python MyTradingSys/options/collector/deribit_opt_backfill.py --only trades --trades-from 2024-01-01 --max-seconds 3600
python MyTradingSys/options/collector/deribit_opt_backfill.py --report         # facts parsed from the files
python -m pytest MyTradingSys/options/tests -q                                  # or: python -m unittest discover -s MyTradingSys/options/tests -p "test_opt_*.py"
```

Scheduling (not created here): run the snapshot command every 900 s, either as the `--every 900` loop in a
background shell, or one-shot from a Windows scheduled task repeating every 15 min (the grid loop skips missed
slots instead of bursting). Run the backfill (`--max-seconds 600` is plenty once caught up) at least every few
days: the expired-instrument list is only served for the last expiry day (see quirks), and `get_instruments`
history cannot be recovered later except through the trade shards.
Single writer assumption: do not run two snapshot loops or two backfills against the same `data/` at once.

## Data schemas

### `data/chain/YYYY-MM-DD.jsonl.gz` (UTC day of `ts_ms`), one line per snapshot, each line its own gzip member
```
{"v":1,"ts_ms":int,"iso":str,"index":float (btc_usd index),"dvol":float|null (latest DVOL close),"dvol_ts":int|null,
 "params":{"atm_strikes":8,"max_dte":90},"n_rows":int,"n_ticker":int,"n_ticker_fail":int,"elapsed_s":float,
 "rows":[{...}]}
```
Row fields from `get_book_summary_by_currency` (all ~960 live options): `instrument_name, bid_price, ask_price,
mark_price, mark_iv, open_interest, volume, volume_usd, last, high, low, price_change, underlying_price,
underlying_index, interest_rate`. Prices are in BTC (inverse options), `mark_iv` is in percent. Dropped as
redundant: `creation_timestamp` (= snapshot time), `estimated_delivery_price` (= index), `base_currency`,
`quote_currency`, `mid_price`.
Extra fields on the ticker subset only (per expiry <= 90 d out, ATM +- 8 strikes, calls and puts; absent elsewhere):
`delta, gamma, vega, theta, rho, bid_iv, ask_iv, best_bid_amount, best_ask_amount, t_ts` (ticker time),
`t_mark_price, t_mark_iv, t_underlying_price, t_index_price` (values at ticker time, so greeks can be re-derived
consistently; the ticker call is seconds to a minute after the summary call). Rows outside the subset have
`mark_iv` + `underlying_price` and can be greeked offline. A failed ticker is counted in `n_ticker_fail` and the row
simply lacks the ticker fields; if the index or the book summary fails nothing is written (fail closed).
Read with `gzip.open(path, "rt")` (multi-member is transparent) or `deribit_opt_common.read_gz_lines` (also tolerates
a truncated final member). Appends write one complete member with one `write()` + fsync, and a damaged tail left by a
crash is cut back (kept in `<file>.badtail`) before the next append.

### `data/hist/` (CSV, header row, LF newlines, sorted by `ts_ms`, values as returned by the API)
| File | Columns | Source |
|---|---|---|
| `dvol_1h.csv`, `dvol_1d.csv` | `ts_ms,open,high,low,close` (DVOL index points, annualised vol %) | `get_volatility_index_data` |
| `perp_1h.csv`, `perp_1d.csv` | `ts_ms,open,high,low,close,volume,cost` for BTC-PERPETUAL (USD price) | `get_tradingview_chart_data` |
| `funding.csv` | `ts_ms,interest_8h,interest_1h,index_price,prev_index_price` hourly | `get_funding_rate_history` |
| `delivery_prices.csv` | `ts_ms,date,delivery_price` (btc_usd index at the 08:00 UTC delivery; `ts_ms` = 00:00 UTC of `date`) | `get_delivery_prices` |
| `instruments_expired.jsonl.gz` | full `get_instruments` objects + `_first_seen_ms`, merged across runs | `get_instruments expired=true` |
| `trades/YYYY-MM-DD.jsonl.gz` | one JSON trade per line (below) for that complete UTC day | `get_last_trades_by_currency_and_time` |
| `trades/_manifest.jsonl` | one line per finished day: `date,n_trades,calls,first_ts,last_ts,file,bytes,fetched_ms` | |
| `instruments_from_trades.csv` | `instrument_name,expiry_code,strike,type,first_trade_ms,last_trade_ms,n_trades` | derived from the shards |
| `_cursors.json`, `_depth_report.json` | resume state; what each host serves | |

Trade fields (as returned, minus `starbase_match_id` / `starbase_timestamp`): `timestamp, trade_id, trade_seq,
instrument_name, direction, price (BTC), amount, iv (percent), index_price (USD), mark_price (BTC), tick_direction`
and, when present, `contracts, liquidation, block_trade_id, combo_id, combo_trade_id`.
Daily timestamps differ by series: DVOL daily candles are stamped 00:00 UTC, perp daily candles 08:00 UTC.
The newest candle of each series is the in-progress one; the next run overwrites it with the final values.

## Resume design
Series: stored rows are one contiguous block `[earliest, latest]`. A rerun (1) walks back from now until a page
overlaps the stored latest (usually 1 call, also refreshes the partial candle), then (2) continues below the stored
earliest until the API says nothing older exists (`complete_back` in `_cursors.json`). Pages are flushed every 10
pages and in `finally`, so a crash or the time cap loses at most 10 pages.
Trades: one immutable shard per complete UTC day, newest day first, `--workers` days in parallel (the global rate
limit still applies). A day is published (`os.replace` of a tmp file) and recorded in the manifest only when fully
fetched; the cap, a crash or a failed day leave no partial shard, and the next run refetches exactly the missing
days. Pagination inside a day: `sorting=asc`, next page starts AT the last timestamp (inclusive) and trades already
written for that millisecond are skipped by `trade_id`, so same-millisecond trades split across pages are neither
lost nor doubled. If a whole page is already-written trades of one millisecond the loop steps past it
(`same_ms_advances` in the manifest; only lossy if more than `count` trades share one millisecond).

## DEPTH_PLACEHOLDER

## API quirks found (verified by probes on 2026-10-08/09)
1. **`www.deribit.com` serves only a rolling ~24 h of trades.** `get_last_trades_by_currency_and_time` with 1-hour
   windows returns trades for windows up to 23 h old and nothing at 24 h or older; `start_timestamp=0, sorting=asc`
   returns a trade ~24 h old as the earliest. `include_old` (true / True / 1) is accepted and changes nothing;
   `get_last_trades_by_instrument_and_time`, `get_last_trades_by_instrument` and `get_last_trades_by_currency` with
   `start_id` behave the same. Trades of instruments that expired today are not served at all. This is why a probe
   of 2025-01-01..02 on `www` comes back empty.
2. **`history.deribit.com` is the depth source**: same `/api/v2/public/...` API, no auth, serves BTC option trades from
   2016-11-29. It is a different host from `www.deribit.com`; the collector uses it for trades only (and allows only
   these two hosts). The live host cannot supply history, so skipping `history.deribit.com` means skipping the
   trade backfill (`--only` without `trades`); every other series comes from `www.deribit.com`.
3. **`count` goes up to 10000** on the history host (20000 -> `-32602 value is too high`), not 1000: ~2.5 MB / ~3.7 s per
   10000-trade page. The server honours `Accept-Encoding: gzip` (~5x smaller), the client asks for it.
4. **`get_instruments(expired=true)` has no pagination and no depth**: it returns only the most recent expiry day
   (60 instruments on 2026-10-08), `include_old` does nothing. Accumulate it over time (`instruments_expired.jsonl.gz`)
   and use `instruments_from_trades.csv` for the historical list.
5. **`get_volatility_index_data`**: with `start_timestamp=0` the response is the newest <= 1000 points at or before
   `end_timestamp` plus `continuation` (the end_timestamp for the next older page); `continuation` is absent on the
   last page. Resolutions seen: `60` (minute), `3600`, `1D`.
6. **`get_tradingview_chart_data`** returns at most 5001 bars per call and, when the window holds more, the NEWEST
   ones, so walk backwards by windows of 5000 bars. `status: no_data` with empty arrays outside the series.
7. **`get_funding_rate_history`** returns at most 744 hourly rows per call (use windows <= 30 days); empty list
   before the first record. `get_funding_chart_data` only covers recent history.
8. **`get_delivery_prices`**: `count` is silently capped at 100 per page; offset pagination, newest first,
   `records_total` gives the end.
9. **`get_book_summary_by_currency`** is one cheap call for the whole chain (~960 rows, ~430 KB) with `mark_iv` but
   without greeks or bid/ask IV; those need `ticker` (1 call per instrument), hence the ATM subset.
10. Some calls are slow (empty funding windows took ~5 s); the client timeout is 90 s.
