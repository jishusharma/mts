# G3 pack audit — 2026-10-16

## Verdict: FIX-FIRST

Four HIGH issues affect blindness or the stated selection/fence rules. Keep the pack unmarked until they are resolved and this audit is rerun. The requested synthetic test file passed: `python -m pytest MyTradingSys/research/g3_marks_2026-10-16/test_g3_pack.py -q -p no:cacheprovider --basetemp=MyTradingSys/research/layer_lab/gpt-g3-pack-audit/pytest_tmp` → **8 passed**. The first run had 7 passed and one environment setup error because pytest could not scan its default temp directory; the rerun used the writable lab folder.

The stdlib poison probe is [probe.py.txt](../gpt-g3-pack-audit/probe.py.txt). It reports all 11 unit pre-filters and all 11 corresponding chart builders unchanged after later rows are deleted/poisoned. It also reproduces the intraday timestamp-fence defect described below. No key, real market data, marking sheet, pack build, or draw was opened/run.

## (a) Causality at the right edge

Here `i` is the last closed chart/pre-filter bar; all listed ranges are inclusive unless noted. **MATCH** means the calculations end at `i` or at its exclusive close time. The poison probe checks behavior, while the table records source-level ranges.

| Component | Bars/data read relative to edge `i` | Result / evidence |
|---|---|---|
| Intraday aggregation | Each emitted TF bar uses its own `tf_min` 1m rows in `[bar_start, bar_end)`; incomplete buckets are dropped. The bucket for `i` ends at the right edge. | MATCH — `g3_pack.py:74-91`; probe 7/7 unit filters and charts unchanged. |
| `pf_tom4` | `B[i]`, VWAP[i], plus footprint rows in `[end-12h,end)` partitioned into three 4h blocks ending at `end`. | MATCH — `:170-181`; no row at/after end. |
| `pf_tom6` | Balance/volume `i-12..i-1`; current volume/close at `i`; clear-space closes from `max(0,i-240)..i-13`. | MATCH — `:184-194`. |
| `pf_tom12` | Prior UTC session profile; closes `i-4..i` (four outside, current break-in). | MATCH — `:197-208`; prior-session profile is `[prior_day_start, current_day_start)`, `:145-160`. |
| `pf_tom15` | Balance `i-12..i-1`; median ranges `i-21..i-2`; candle shapes `i-2..i`. | MATCH — `:211-225`. |
| `pf_fab1` | Balance, delta/volume aggregation `i-36..i-1`; current close and flags at `i`, previous flag at `i-1`. | MATCH — `:228-239`. |
| `pf_fab4` | Prior-session VA; session start `j0..i`; current close `i`, prior close `i-1`, then backwards outside run ending at `i-1`. | MATCH for causality — `:242-255`. Definition mismatch is in table (c). |
| `pf_fab5` | Current bar `i`; candidate touches `i-1..i-60`, at least three bars apart; held closes from oldest selected touch through `i`. | MATCH — `:257-276`. |
| `pf_krs1` | Candle/previous candle `i,i-1`; volume mean `i-30..i-1`; swing candidates through `i-4`, with comparison neighbors no later than `i-1`. | MATCH — `:379-394`. |
| `pf_krs8` / BBWP | Trigger closes `i` and `i-20..i-1`; BBWP values at `i` and `i-10..i-1`. Each BBWP rank at `k` uses current width from closes `k-19..k` and prior widths `k-252..k-1` (source closes no later than `i`). | MATCH — `:307-316`, `:397-403`. |
| `pf_mal25` | Weekly RSI at `wk`, `wk-1`, `wk-3`, and `wk-12..wk-2`; monthly RSI is last completed month whose end is `<=` the weekly edge. | MATCH — `:406-412`, `:356-359`. |
| `pf_mal1617` | 20-bar close extrema `i-19..i`; candidate pivot `b` in `i..i-3`; comparison pivot range ends at `b-5`; RSI/trigger candle no later than `i`. | MATCH for causality — `:415-429`; protocol-range mismatch in table (c). |
| 4h blocks | Three adjacent intervals `[end-12h,end-8h)`, `[end-8h,end-4h)`, `[end-4h,end)`; bar-aligned at the chart edge. | MATCH — pre-filter `:176-179`, chart `:639-645`. |
| Session VWAP | Cumulative typical-price × volume and volume within each UTC day, reset at day change; chart selects VWAP indices `i-n+1..i`. | MATCH — `:135-143`, `:630-632`. |
| Session/prior profiles | `profile(t0,t1)` uses footprint rows with timestamps `>=t0` and `<t1`; prior VA uses the previous UTC day. TOM6 uses the five days ending at edge; FAB5 uses the prior 24h; current-session close histogram ends at `B[i]`. | MATCH — `:145-160`, chart `:633-661`. |
| Weekly/monthly aggregates | Weekly candle includes its seven daily rows and is emitted only when complete; monthly RSI selects a completed month ending by the queried edge. | MATCH on complete daily input — `:319-359`. Monthly completion relies on the final observed daily row of the month being present. |
| RSI / weekly RSI / monthly RSI | Wilder RSI(14) recursively consumes closes through each plotted index only; weekly RSI consumes completed weekly closes; monthly RSI consumes completed monthly closes. | MATCH — `:293-304`, `:345-359`, chart `:691-716`. |
| Intraday chart builder | Price/volume/delta/CVD and VWAP slices are `i-n+1..i`; day profiles and annotations use those visible bars; overlays' interval ends are at the edge. | MATCH — `:611-683`. |
| Daily/weekly chart builder | Candles and timeframe RSI are `i-n+1..i`; volume averages end at each visible index; BBWP is sliced through `i`; monthly RSI queries each shown weekly end. | MATCH — `:686-719`. |

The poison probe compared each filter/chart on synthetic full, truncated, and poisoned series: **11/11 filters MATCH, 11/11 charts MATCH**. This verifies no later row influences pack calculations at an edge; it does not establish protocol parity or the loader's date fence.

## (b) Blindness

| Surface | Severity / result | Evidence |
|---|---|---|
| Published IDs, filenames and title | MED — no explicit half/tag label. `WINDOWS.csv` has 213 rows, 11 units, columns `window_id,row,timeframe,bars_shown,right_edge_utc,seed,data`; no half/tag columns and zero IDs contain “random” or “enriched”. PNG basename is the ID; title repeats it and the row/TF. | `README.md:16`; `g3_pack.py:617,696,749-754`; test `test_published_window_list_does_not_reveal_the_half` (`test_g3_pack.py:148-157`). |
| Bar count and spacing | MATCH — one fixed shown-bar count and one spacing rule per unit, shared by both samples. Aggregate distribution is 10 units × 20 windows and one unit × 13 (213 total); the 13-window case is documented in aggregate in `README.md:16`. | `g3_pack.py:38-50,433-463`; `WINDOWS.csv` aggregate counts. |
| Dates / right-edge time of day | MED — dates are omitted, but intraday charts label 6-hour UTC grid times and mark UTC day boundaries. The edge's time of day can be inferred from the last grid labels. Without reading the closed key, half-specific time-of-day association was not tested. | `g3_pack.py:617,624-629`; daily charts use relative offsets `:698-699`; text renderer preserves supplied text (`render_png.ps1:17-21`). |
| Last-bar pattern and pre-filter tag | **HIGH — visually inferable.** The README publishes each enrichment rule, and the charts show the same edge evidence used by those rules: the selection requires `tag_of(i)` to be true for enriched entries, while drawings expose the relevant price/volume/VA/RSI/VWAP/BBWP/delta features. A reader with the row catalogue and protocol can often recognize the enriched signature and infer the tag from the last bars. The source/test proves no literal half field, but that is not effective blindness. | `README.md:16-27`; selection `g3_pack.py:443-463`; chart overlays `:617-682,686-719`; protocol `READER_PROTOCOL.md:10-38`. Follow-up card below. |

No report line pairs an individual window identifier with its half or tag. The key file was not opened.

## (c) Reader protocol definitions

| Protocol term / wording (section 1 unless noted) | Code comparison | Result |
|---|---|---|
| Balance: consecutive closes; width as % of last close; timeframe-specific N/W. | `bal_run` uses closes and `(max-min)/last_close`; relevant 5m/30m callers use 36/1.0 and 12/1.5. | MATCH — `READER_PROTOCOL.md:12`, `g3_pack.py:163-167,184-186,211-214,228-231`. |
| Value area: contiguous 70% volume around POC; 10 USD bins; ties lower. | `BIN=10`; fp bins sum buy+sell; POC ties lower; neighbor ties grow lower. | MATCH — protocol `:13`; code `g3_pack.py:31,94-119,145-160`; reference `chart_lab.py:26-47`. |
| P / b / D: 20 equal bins of session closes; POC third determines label. | Session close histogram has 20 bins and count-per-close, but code does not assign P/b/D labels; the chart gives the reader the histogram to apply this definition manually. | MATCH (visual/manual only) — protocol `:14`; code `g3_pack.py:600-608,649-652`. |
| Thin top: top quarter contains at most 10% of session closes. | No boolean detector; session close histogram is available for manual assessment on applicable charts. | MATCH (visual/manual only) — protocol `:15`; code `g3_pack.py:600-608,649-652`. |
| Big trade: aggTrades print at/above prior-30-day `thr999`, displayed via `b999_*` flags. | Input flags are carried and summed into TF bars; any nonzero flag draws a tick. The percentile threshold is upstream in the data, not recomputed here. | MATCH — protocol `:16`; code `g3_pack.py:67-69,81-88,662-666`. |
| Healthy trend: three consecutive 4h-block VPOCs rise twice by ≥1 bin and close above session VWAP (mirror down). | TOM4 filter computes those three edge-ending blocks and checks `BIN` increments plus current close relative to VWAP. | MATCH — protocol `:17`; code `g3_pack.py:170-181`. |
| VWAP pullback: low at/below VWAP and close above (mirror down). | TOM4 checks `low <= vwap < close` (mirror `high >= vwap > close`). | MATCH — protocol `:18`; code `g3_pack.py:170-175`. |
| Outside P / break-in: at least four closes outside old VA, then first close inside. | TOM12 uses four previous closes and current close inside. FAB4 accepts outside runs of **2..24** closes, not minimum 4. | **MISMATCH (HIGH for enriched sampling)** — protocol `:19`; TOM12 `g3_pack.py:197-208`; FAB4 `:242-255`; README enrichment rule `:22`. |
| BBWP: 20-day 2σ width percentile within prior 252 daily bars; compression below 30, release above 50. | Width is `4*population_sd/mean`; rank compares with prior 252 widths; trigger uses recent `<=30` then current `>50`. Since ranks advance in 1/252 steps, equality at 30 is not representable. | MATCH — protocol `:23`; code `g3_pack.py:307-316,397-403`; chart `:706-710`. |
| RSI: Wilder 14 on row TF; 40/60 levels. | Wilder smoothing on closes; daily/weekly charts use their own close series and draw 40/60. | MATCH — protocol `:24,38`; code `g3_pack.py:293-304,345-353,711-716`. |
| Divergence: highest/lowest close in last 20 vs extrema 5..60 bars back; RSI confirms lower/higher. | The tag checks extrema within last 20 but only examines recent pivot candidates `b=i..i-3`; prior search is `i-60..b-5`, not the complete 5..60 bars before `b`. A valid recent 20-bar extremum older than 3 bars is missed; the reference interval also shifts with `b`. | **MISMATCH (HIGH for enriched sampling)** — protocol `:24`; code `g3_pack.py:415-429`; test only checks causality (`test_g3_pack.py:64-76`). |
| Weekly RSI and monthly RSI: RSI(14) on weekly closes; monthly is last completed calendar month, no partial month. | Weekly bars require seven daily rows; RSI uses weekly closes. Month RSI is chosen by the last month end `<=` weekly edge; monthly rows are emitted after a month boundary. | MATCH on complete daily data — protocol `:24,38`; code `g3_pack.py:319-359,406-412,691-716`. |

## DEV fences

| Check | Result / evidence |
|---|---|
| Intraday upper bound | **MISMATCH (HIGH).** `load_intraday` iterates filenames only through `INTRA_LAST` but appends every timestamp in each file without a timestamp cutoff. Synthetic file named for the final allowed date containing a next-day row makes `load_intraday` return it. `load_intraday` `g3_pack.py:59-71`; constants `:35`; probe output `intraday=MISMATCH`. Fix should reject timestamps after the final allowed instant (and ideally verify file/day consistency). |
| Daily upper bound | MATCH. `load_daily` computes exclusive end = 2024-07-01 and retains only timestamps `< end`; synthetic July 1 row is discarded. `g3_pack.py:283-290`; constants `:36`; probe output `daily=MATCH`. |
| README versus date constants | MATCH for selected edges: footprint input dates 2024-12-02..2025-03-31 and eligible edges from 2024-12-08; daily/weekly edges 2021-03-01..2024-06-30. Code constants are `INTRA_FIRST/EDGE0/LAST` and `DAILY_FIRST/EDGE0/LAST` at `g3_pack.py:35-36`. The daily loader also reads 2020 warm-up history (`DAILY_FIRST`) as README explains for the 60-week view (`README.md:4,29`); marks remain within the stated edge range. |
| Fence test coverage | The requested test passed but only tests the next-date file and a later timestamp in a June file; it does not place a post-fence timestamp inside the final allowed intraday filename. `test_g3_pack.py:135-146`; the added poison probe covers that case and fails the intraday fence. |
| Real data | No real series was loaded or queried. The poison probe and requested tests use synthetic bars; no VALIDATION/HOLDOUT data was inspected. |

## HIGH follow-up cards created (five cards for four findings; the last two cover the blindness issue)

- `g3-intraday-loader-must-enforce-timestam` — enforce timestamp fence inside the final intraday file.
- `g3-align-mal-divergence-pre-filter-pivot` — make the divergence candidate detector match the protocol's full pivot windows.
- `g3-align-fab4-break-in-prefilter-minimum` — enforce the protocol's four-close minimum for the FAB4 break-in filter.
- `g3-assess-and-remove-visible-chart-side-` — assess/remove chart side channels that let a reader infer enriched selection/tag.
- `g3-remove-visible-chart-cues-that-disclo` — remove visible chart cues that disclose enriched selection/tag.

`python scripts/dev/tasks.py done gpt-g3-pack-audit --result "FIX-FIRST 2026-10-16_gpt-g3-pack-audit.md"`
