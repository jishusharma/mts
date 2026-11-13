UNVERIFIABLE

Blind review of `MyTradingSys/research/live_aid_review_2026-11-13` and `MyTradingSys/research/live_aid_liq_meaning_2026-11-13`.
Verdict: **UNVERIFIABLE** for `live_aid_review_2026-11-13` (no backtest/replay data or scripts in the folder to recount the cited hit rates); **SOUND** for `live_aid_liq_meaning_2026-11-13` (reports `NOT MEASURED` because `runtime_data/live_aid/xliq_events.jsonl` is absent, and all code parameters match `RESULT.md`).

## 1. Claim Recount Table

| Claim | Claimed Value | Recounted Value | Status | Source |
|---|---|---|---|---|
| `live_aid_liq_meaning_2026-11-13`: Verdict | `NOT MEASURED. No usable liquidation history exists. No number is given.` | `runtime_data/live_aid/xliq_events.jsonl` does not exist on disk | MATCH | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:5` |
| `liq_meaning.py`: Bucket edges (USD) | `250k / 1M / 5M USD` | `("250k-1M", 250_000, 1_000_000), ("1M-5M", 1_000_000, 5_000_000), ("5M+", 5_000_000, 1e12)` | MATCH | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:21` |
| `liq_meaning.py`: Dedup window | `15 min dedup` | `DEDUP_MS = 15 * 60_000` | MATCH | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:23` |
| `liq_meaning.py`: Horizons | `5 / 15 / 60 min` | `HORIZ = (5, 15, 60)` | MATCH | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:24` |
| `liq_meaning.py`: Minimum span | `24 h minimum span` | `MIN_SPAN_H = 24` | MATCH | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:20` |
| `liq_meaning.py`: Anecdote threshold | `n < 30 flagged as anecdote` | `low = [r for r in rows if r["n"] < 30]` | MATCH | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:132` |
| `liq_meaning.py`: Burst windows | `1m / 2m` | `WINS = {"1m": 60_000, "2m": 120_000}` | MATCH | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:18`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:22` |
| `live_aid_review_2026-11-13`: Setup & Idea replay hit rates | `setup 51% n 1342, idea 47% n 763` | No replay script or data in folder | UNVERIFIABLE | `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:79` |
| `live_aid_review_2026-11-13`: Gauge / stacking hit rates | `52%` (single reading), `51% vs 49%` (stacking) | No scoring script or data in folder | UNVERIFIABLE | `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:27-29` |
| `live_aid_review_2026-11-13`: MTS layers PASS count | `0 of 40 fee-net rows carry a surviving PASS` | No MTS layer data in folder | UNVERIFIABLE | `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:80` |
| `live_aid_review_2026-11-13`: 11-10 replay prices | `73,525` sweep, `74,844` squeeze | No replay data in folder | UNVERIFIABLE | `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:82` |

## 2. Look-Ahead Hunt

- `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:64`: `end = (b + 1) * win_ms` sets the decision/entry timestamp to the end of the aligned 1m/2m bin.
- `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:82-83`: `t_ref = end // 60_000 * 60_000 - 60_000` and `ref = px.get(t_ref)` select the close (`MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:49`) of the last 1m bar inside the bin, which closes at `end`.
- `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:87`: `f = px.get(t_ref + h * 60_000)` evaluates future closes strictly after `t_ref` (`h in (5, 15, 60)`).
- **Finding**: No look-ahead in `liq_meaning.py`. `live_aid_review_2026-11-13` contains no backtest/feature computation code.

## 3. Fee & Slippage Hunt

- `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:89`: `(f / ref - 1) * 100` computes raw percentage price return with **no fee or slippage model** (0 bps, no side-dependent fee, no round-trip deduction).
- Because `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:5` reports `NOT MEASURED` and no trading PnL is claimed, no fee error is currently realized; however, if `med15` (`MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:99`) is later used as a tradable edge metric, round-trip fees and slippage must be subtracted.
