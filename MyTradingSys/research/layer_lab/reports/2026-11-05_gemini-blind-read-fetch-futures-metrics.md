# Blind read: MyTradingSys/backtest/fetch_futures_metrics.py (docstring vs code)

Method: code read first (resolve_root, http_get, fetch_day, list_gaps, run), expected behaviour derived, then diffed against the module docstring (lines 2-22). No network, no keys. Reader: Claude Builder (card was Gemini-labelled; independent of the author's summary).

## Derived behaviour (code only)
- Re-run: fetch_day returns "skip" if the target CSV exists (l.64-65), before any network call.
- 404 day: http_get returns None on HTTP 404 (l.48-49); fetch_day returns "404" (l.68-69), nothing written. Not remembered, so every re-run retries it.
- Short day (<288 rows): fetch_day does not look at row counts; the file is extracted normally. Only list_gaps counts rows (l.99-102) and flags rows < 288 as short.
- Missing CHECKSUM: returns "nochecksum", nothing written (l.70-72). Mismatch raises RuntimeError (l.73-74), nothing written.
- Transient errors: 3 tries with 2**i sleep; the last failure re-raises (l.41-56).

## Claim table
| Claim (docstring) | Code line | Result |
|---|---|---|
| Public archive only, no keys | BASE data.binance.vision l.25; header only has User-Agent l.43 | MATCH |
| Root order: --root, else MTS_METRICS_ROOT, else MTS_DATA_ROOT + "/metrics" | l.32-37; SystemExit l.38 if none | MATCH |
| Root never hard-coded | no path literal in module | MATCH |
| Layout <root>/<SYM>/<SYM>-metrics-YYYY-MM-DD.csv | l.59, 63, 79 (extractall into root/SYM) | MATCH (relies on the zip member name equalling csv_name; not checked in code, so skip would not trigger if the member was named differently) |
| SHA256-verified | l.73 hashlib.sha256 vs .CHECKSUM first token | MATCH |
| zip dropped | zip held in memory (io.BytesIO l.76), never written | MATCH |
| Re-run skips present files (idempotent) | l.64-65 | MATCH |
| Gaps listed per month | l.89-92 key strftime %Y-%m; format_gaps l.118-128 | MATCH |
| Missing days (archive 404) | list_gaps lists any absent CSV as missing l.95-97 (also absent for nochecksum/errors, not only 404) | MATCH (wider than stated) |
| Short days (< 288 five-minute rows) | ROWS_PER_DAY = 288 l.27, test l.101; rows = lines - 1 header l.100 | MATCH |
| 288 rows per day = 24h / 5m | 24*60/5 = 288 | MATCH |

## Notes
- Short days are only reported, never refetched: skip means a short file stays short forever unless deleted.
- A downloaded short day counts as "ok" in run() output.

VERDICT: MATCH
