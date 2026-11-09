Verdict: T11=FAIL (DEV mean net R -0.146 +-0.042, n=1588), T12=FAIL (DEV mean net R -0.133 +-0.044, n=1477); VALIDATION not read (no trial passed the DEV screen); regime A fees, BTC+ETH spot 1h+4h, 2.5R / 48 bars.

# RESULT: eh-s3-rsi-line-confluence (RSI 40/60 bounce with other-timeframe confluence)

Rules and trial ids: `PRE_REG.md` (committed before any return). Code `line_confluence.py`, tests `test_line_confluence.py`, per-cell stats `cells.csv`, event counts `counts.csv`, run log `dev_run.txt`.

Regime mix: 352 weeks: bull 72 (20%) | bear 0 (0%) | range 223 (63%) | n/a 57 (16%)   (BTC, research_kit logic, DEV weeks 2017-10..2024-06; n/a = monthly-RSI warm-up; bear is empty as expected)

## Plain words
- The confluence bounce does not make money. Buy the 40-line bounce / sell the 60-line rejection when another timeframe sits at the same line, stop beyond the approach extreme, exit at 2.5R or 48 bars: gross R is about zero (+0.028) and costs (fee 0.176 R) take it to -0.146 R per trade. The CI upper bound (-0.064) is below the MDE (0.117), so this is a FAIL at adequate power, not an "unclear".
- The confluence did not help even against its own contrast: bounces with no other TF at the line are -0.078 R (n=3347), confluent ones -0.146 R; the gap (-0.068, SE about 0.05 if independent) points the wrong way. The study's higher hold rate at confluence does not turn into a better 2.5R trade, because the hit rate is the same (30 % vs 32 %): a bounce that "holds" a few more points of RSI does not travel 2.5 stop-distances more often.
- T12 is nearly the same trade as T11. "Against the HTF bias" is 93 % of all confluent bounces (1745 of 1880 events), because when the 1h RSI sits at 40 the 4h RSI is below 50 in 96 % of cases, and when it sits at 60 the 4h RSI is above 50 in 96 %. The bias rule therefore barely separates anything here; the "agreeing" side (only 111 events) is too thin to test. T12 = -0.133 R.
- Where it loses: sideways markets. In the research_kit "range" weeks T11 is -0.236 R (n=1069, CI [-0.330, -0.141]); in "bull" weeks +0.090 R (n=287, CI [-0.117, +0.298], not significant). Exploratory only. The bear regime is empty (0 weeks), so a bull-vs-range split is all this label can give.
- Per year (DEV, T11): positive only in 2017 (+0.23, n=44), 2021 (+0.08) and flat in 2022; strongly negative in 2019, 2020 and 2023 (-0.29, -0.31, -0.39). No year clears zero with a CI.

## T11 and T12 on DEV (2017-10-01 signals .. 2024-06-30; signals before 2020-01 carry no funding)
| Trial | n | hit | mean gross R | mean fee_r | mean funding R | mean net R | SE (ISO week) | 95 % CI | MDE (80 %) | DEV screen |
|---|---|---|---|---|---|---|---|---|---|---|
| T11 confluent bounces, 1h+4h, 2 symbols, 2 lines | 1588 | 0.302 | +0.028 | 0.176 | -0.003 | **-0.146** | 0.042 | [-0.228, -0.064] | 0.117 | no |
| T12 T11 against the HTF bias | 1477 | 0.307 | +0.044 | 0.180 | -0.003 | **-0.133** | 0.044 | [-0.219, -0.047] | 0.123 | no |

Counts (1h+4h, BTC+ETH): 1880 confluent and 4512 no-confluence bounce events before the one-trade-at-a-time rule; 1456 entries skipped for overlap, 0 invalid, 1 censored, 11 events skipped for a missing bar (`counts.csv` has events per year, TF, line and side).
Verdict rule: FAIL = DEV mean <= 0 with the CI upper bound below the MDE. T11: -0.064 < 0.117; T12: -0.047 < 0.123. Neither passed the DEV screen (CI lower bound > 0 needed), so the single VALIDATION read was not made (`validation_once.txt` does not exist; the VALIDATION and HOLDOUT bars were never loaded).

Per year, DEV (net R mean, n):
| Year | T11 | T12 |
|---|---|---|
| 2017 (Oct-Dec) | +0.227 (44) | +0.206 (42) |
| 2018 | -0.127 (211) | -0.068 (191) |
| 2019 | -0.287 (230) | -0.324 (213) |
| 2020 | -0.312 (225) | -0.302 (208) |
| 2021 | +0.079 (277) | +0.129 (260) |
| 2022 | -0.001 (245) | -0.032 (230) |
| 2023 | -0.385 (247) | -0.340 (230) |
| 2024 (to Jun) | -0.051 (109) | -0.085 (103) |

## Exploratory (cannot promote; full table in `cells.csv`)
| Cell | n | gross | fee_r | net | 95 % CI |
|---|---|---|---|---|---|
| T11 1h | 1243 | +0.062 | 0.199 | -0.134 | [-0.226, -0.042] |
| T11 4h | 345 | -0.097 | 0.096 | -0.191 | [-0.356, -0.027] |
| T11 line 40 (long) | 816 | +0.034 | 0.166 | -0.141 | [-0.248, -0.034] |
| T11 line 60 (short) | 772 | +0.021 | 0.187 | -0.152 | [-0.272, -0.032] |
| NOCONF all (contrast) | 3347 | +0.079 | 0.158 | -0.078 | [-0.135, -0.022] |
| NOCONF 1h | 2723 | +0.074 | 0.176 | -0.102 | [-0.164, -0.039] |
| NOCONF 4h | 624 | +0.101 | 0.077 | +0.024 | [-0.103, +0.151] |
| T11, 1 confluent TF | 1227 | +0.023 | 0.175 | -0.149 | [-0.242, -0.056] |
| T11, 2 confluent TFs | 316 | +0.028 | 0.178 | -0.146 | [-0.327, +0.035] |
| T11, 3 confluent TFs | 45 | +0.144 | 0.210 | -0.069 | [-0.535, +0.398] |
| T11 HTF up / down | 777 / 811 | +0.029 / +0.026 | 0.185 / 0.168 | -0.143 / -0.149 | both CI upper < 0 |
| T11 regime bull | 287 | +0.229 | 0.151 | +0.090 | [-0.117, +0.298] |
| T11 regime range | 1069 | -0.043 | 0.193 | -0.236 | [-0.330, -0.141] |

No dose-response: 1, 2, 3 confluent TFs give -0.149, -0.146, -0.069 (the 3-TF cell is n=45, MDE 0.67). The 4h no-confluence cell (+0.024, n=624) is the only non-negative timeframe cell and is not significant (CI [-0.103, +0.151]; one of several dozen exploratory cells, no correction); none of them is a candidate.

The confluence effect was found by the 2026-11-04 study on the same DEV span (2017-08..2024-06), so the DEV screen here is not independent evidence. This result is a clean negative on that span; since the DEV screen already failed, the question of independence did not matter and VALIDATION stays unread for a future use.

## Caveats
- Spot data, not futures; funding records start 2020-01 in the archive (the 2019-09..2019-12 files are not published), so the 2017-2019 trades carry cost only (485 of the 1588 T11 trades, 31 %).
- Event logic is adapted, not identical, to the study: the study's HOLD is "RSI leaves the band on the origin side within N bars", scored by price return over N bars from the next open; here the entry is the first close back out of the band within 6 bars, and the exit is a 2.5R/48-bar structural-stop trade. A "hold" in the study's sense that needs more than 6 bars is not a trade here. The result says the confluence tilt is not tradeable in this form; it does not say the hold rates were wrong.
- Stops are structural and short on 1h (mean fee_r 0.20 R on 1h): any stop distance under about 12 bps costs more than 1R in fees. No floor was applied (d-stops-follow-trade-1106). Whether a maker entry at the line (regime B) changes the sign was not tested: it needs a different entry rule and is a new trial.
- Clustering by ISO week for sets containing 4h trades (conservative); 1h-only cells cluster by day.
- 4h and 1h trades of one symbol can overlap in time (the overlap rule is per symbol x TF); BTC and ETH trade together. The week clusters absorb this in the SE.

## DECISION (OURS) list
- Cushion fixed at 2 RSI points, bounce window 6 bars, target 2.5R, 48 bars: as the brief; no tuning. The DEV-picked cushions of the study (picks_dev.json) were not used.
- Band entry restricted to the origin side the brief names (40 from above, 60 from below); the study's entries are two-sided.
- Event bars must be consecutive in time (k-1..j); 11 events with a gap skipped.
- Entry at the close of the bounce bar; stop = exact extreme of bars k..j (band entry through the bounce bar), no buffer; gaps fill at the open, same-bar tie goes to the stop; the target fills at the open if the bar gaps past it.
- One trade at a time per symbol x TF x population (confluent chain; the no-confluence contrast is its own chain; T12 is the HTF-against subset of the T11 trades).
- HTF map 1h -> 4h and 4h -> 1d (the study used 4h -> 12h); RSI exactly 50 or missing = no bias (never "against"; none occurred).
- As-of RSI of another TF is "missing" if older than 2 of its own bar lengths (data gaps).
- SE clustering: ISO week for any set with 4h trades, UTC day for 1h-only sets.
- Signals counted from 2017-10-01 (1d RSI warm-up). 12h and 1d resampled from complete closed 1h buckets only; 4h from the archive's 4h files. The existing public spot cache (F:/MTS/Dumps/backtest/spot_2017) was reused instead of re-fetching; the loader never opens months at or after the split end.
- ETH funding was fetched by calling the repo's `fetch_binance_archive.fetch_one` with its module-level `SYM` set to ETHUSDT (the CLI is hard-wired to BTCUSDT); no repo file was edited.
- Regime tag: research_kit `ma_side` and `rsi_band` with the as-of logic recomputed locally (as the eh-h2 worker did, because `regime_tag`'s as-of path returned None there).
- VALIDATION not read because neither trial passed the DEV screen; no Holm computation was needed (the `val` path is coded and tested).

## Tests
- Failing run before the code existed, last line: `ModuleNotFoundError: No module named 'line_confluence'`.
- After the code: `32 passed, 0 failed` (hand-built bars for approach, bounce, break-first, 6-bar window, edge values 38/42/58/62, wrong-side approach, gap skip, confluence +-2 and exactly-2, trade TF excluded, no lookahead on higher TFs (a bar closing 1 h after T is invisible; future values change nothing), stale as-of, HTF map and 50 threshold, against, structural stop, long/short target/stop/tie/gap/time/censored, fee and funding arithmetic, net R, resampling, split refusal incl. the loader never opening a 2025-07 file, overlap, clustered SE, Holm, verdict rules).

## Context
- Regime: research_kit Malkan band (weekly+monthly RSI 60/40) with the daily SMA side; the study is ungated. T11 by regime is exploratory: bull +0.090 (n=287), range -0.236 (n=1069), bear n=0.
- Phase: DEV 2017-10..2024-06 pooled; no cycle-phase split (eh-o2).
- Session: none (24h bars).
- Entry: at the close of the bounce bar, taker, regime A (10 bps RT + 2 bps slippage + funding where it exists).

## Next
END: both trials FAIL on DEV at adequate power (MDE 0.12 R against a mean of -0.14 R). No testnet-forward card. The one open follow-up (not filed, a new trial would be needed): the confluence tilt as a context filter on a different entry (maker limit at the line, regime B), because the 1h stop distances make fee_r 0.20 R.

## Noticed
- "Against the HTF bias" is almost the whole set (93 %) for the RSI line bounce: the HTF RSI is on the same side of 50 as the line (40 -> below, 60 -> above) by construction of the RSI. The study's "agreeing bias holds 10-14 points less" contrast is therefore a comparison of a large cell with a small one; any future "HTF bias" rule on RSI-line trades should use a different HTF measure (a trend or SMA side), not HTF RSI vs 50.
- research_kit `regime_tag`'s as-of path returned None for the weeks (same as eh-h2 noted); worked around locally; a repo fix would help every worker.
- `fetch_binance_archive.py` CLI ignores `--symbols` for the futures datasets (hard-coded `SYM = "BTCUSDT"`), so ETH funding cannot be fetched by the CLI.
