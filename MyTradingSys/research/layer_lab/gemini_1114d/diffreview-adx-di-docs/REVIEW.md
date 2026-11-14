# Diff Review: `MyTradingSys/research/adx_di_2026-11` (last 24 h of `origin/fast-track`)

Task: `diffreview-adx-di-docs-gemini4-1114`
Reviewed against: `git log --since='24 hours ago' origin/fast-track --name-status -- MyTradingSys/research/adx_di_2026-11` (11 commits on 2026-11-13).
Method: Read-only diff and cross-file audit; ran `pytest MyTradingSys/research/adx_di_2026-11/` (7 passed), `scripts/dev/verify_extract_quotes.py` on all 8 `.md` files (all `PASS: 0 problem(s)`), and `pytest` on `test_measure_1113.py` + `test_flow_read.py` + `T06/` cost tests. All numbers below are SOURCED from the listed `file:line` or commit messages (0 OURS parameter choices).

## Commit-by-Commit Summary

| # | SHA | Files in `adx_di_2026-11` | Matches `Result:` line? | Verdict |
|---|---|---|---|---|
| 1 | `2f10c870366d7f75e5b1a9be2012f7482deef3d0` | `A MASTERS_1113.md` | Yes (`rules, common ground and disagreements tables with URLs`) | 1 LOW |
| 2 | `66b4a85e35be82c0466a0b09a547224040bc8051` | `A CRYPTO_USE_1113.md` | Yes (`no fee-net OOS backtest; CCU ADX unconfirmed`) | 1 MED, 1 LOW |
| 3 | `3b01320f3e73345c6737b7e9eb83968b813eb1e4` | Merge `origin/fast-track` into `JIS-NB/adx-masters-1113-2` | n/a (merge commit) | NO FINDINGS |
| 4 | `630c918e77af6d24088fd078d7469001dd88fc91` | `A INVENTORY_1113.md` | Yes (`10 studies listed, none fee-net, 5m/5d/1w and all entry rules untested`) | NO FINDINGS |
| 5 | `2bffd911c55c0d74f20fcbb7c9e58b48b16155ad` | Merge `origin/fast-track` into `JIS-NB/adx-inventory-1113-2` | n/a (merge commit) | NO FINDINGS |
| 6 | `329ee21c843a452e8fe6045c9182643c315588db` | `A HOW_TO_USE_ADX_1113.md` | Yes (`trend gauge; no fee-net edge for DI cross... only 1d ADX-through-25 helps (thin, n=34)`) | 2 LOW |
| 7 | `e41c9ab72cd922cd2a09d8efb4d2738966c0c0de` | `A MEASURE_1113.md`, `measure_1113.py`, `test_measure_1113.py` | Yes (`L_adx25` n=34, `S_adx25` n=33; later reverted for `fapi.binance.com` string) | 1 MED, 3 LOW |
| 8 | `73c47df5bfd483943a79022357b0d2bcdb45cb60` | `M measure_1113.py` | Yes (`lint 0 new FAIL, output logic unchanged`) | NO FINDINGS |
| 9 | `025912e4af8b88481fe130bf26d86051b98ba31b` | `M measure_1113.py` (+ `costs.csv`) | Yes (`_fees.BINANCE_MAKER * 2` = `0.0004`, same fee value) | NO FINDINGS |
| 10 | `65586b240fe1e8000211aa64da47f9abbce59eb6` | `D MEASURE_1113.md`, `measure_1113.py`, `test_measure_1113.py` | Yes (`trunk goes back to the last-green bytes for these files`) | 1 LOW |
| 11 | `45ad3a6a42f9894bbefdcfebfbb7d9cbd8cb848c` | `A MEASURE_1113.md`, `measure_1113.py`, `test_measure_1113.py` | Yes (`test_flow_read + test_measure_1113 + cost tests` pass) | 1 MED, 3 LOW (inherited from `e41c9ab72`) |

## Findings

| SHA | File:Line | Severity | Evidence Quote & Note |
|---|---|---|---|
| `2f10c870366d7f75e5b1a9be2012f7482deef3d0` | `MyTradingSys/research/adx_di_2026-11/MASTERS_1113.md:55` | LOW | `\| Re-entry \| Book reportedly covers second pullback; an MQL5 article says second entry needs ADX to fall under 30 and come back \| secondary \| https://www.mql5.com/en/articles/24280 \|` — Label column uses `secondary` without the `SOURCED` prefix used elsewhere in the table. |
| `66b4a85e35be82c0466a0b09a547224040bc8051` | `MyTradingSys/research/adx_di_2026-11/CRYPTO_USE_1113.md:71` vs `MyTradingSys/research/adx_di_2026-11/CRYPTO_USE_1113.md:93` | MED | Internal contradiction on the Cryptonomist 2023 rule: line 71 states `exit on 200-bar low / 5% stop / 5 days`, whereas line 93 states `Buy BTC/MATIC/BNB when 15m ADX < 45 (200-bar-high based), 5% stop, 5-day cap`. |
| `66b4a85e35be82c0466a0b09a547224040bc8051` | `MyTradingSys/research/adx_di_2026-11/CRYPTO_USE_1113.md:13` | LOW | `file MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md and grep of ccu_DXntdN3jfTg_extract.md` — `ccu_DXntdN3jfTg_extract.md` is in `MyTradingSys/research/cbp/`, not `yt_feed_2026-10-31/`. |
| `3b01320f3e73345c6737b7e9eb83968b813eb1e4` | `MyTradingSys/research/adx_di_2026-11/CRYPTO_USE_1113.md:1` | NO FINDINGS | Clean merge of `origin/fast-track` into `JIS-NB/adx-masters-1113-2`. |
| `630c918e77af6d24088fd078d7469001dd88fc91` | `MyTradingSys/research/adx_di_2026-11/INVENTORY_1113.md:1` | NO FINDINGS | All referenced repo paths exist on disk; parameters and thresholds are labeled `SOURCED`, `OURS`, or `UNKNOWN`. |
| `2bffd911c55c0d74f20fcbb7c9e58b48b16155ad` | `MyTradingSys/research/adx_di_2026-11/INVENTORY_1113.md:1` | NO FINDINGS | Clean merge of `origin/fast-track` into `JIS-NB/adx-inventory-1113-2`. |
| `329ee21c843a452e8fe6045c9182643c315588db` | `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md:64` | LOW | `MEA: after a peak over 40, ADX is still above 25 twelve bars later in 92-100%` — omits that `1w` in `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:186` has `ADX<25 after: 12% UNDERPOWERED` (88% above 25, n=8). |
| `329ee21c843a452e8fe6045c9182643c315588db` | `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md:3` | LOW | `MEA = MEASURE_1113.md (branch JIS-NB/adx-measure-1113, not yet on trunk)` — stale branch note now that `MEASURE_1113.md` is on trunk. |
| `e41c9ab72cd922cd2a09d8efb4d2738966c0c0de` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:5` | MED | `Levels 20 / 25 / 40 = Wilder and Schaap rule-of-thumb levels (SOURCED: research/cbp/ccu_DXntdN3jfTg_extract.md, research/tv_favorites_2026-11/USAGE_adx.md)` — `ccu_DXntdN3jfTg_extract.md` has no ADX content (`MyTradingSys/research/adx_di_2026-11/CRYPTO_USE_1113.md:13`, `MyTradingSys/research/adx_di_2026-11/INVENTORY_1113.md:26`), and `MyTradingSys/research/adx_di_2026-11/MASTERS_1113.md:16` notes 20/25/40 are convention, not Wilder's. |
| `e41c9ab72cd922cd2a09d8efb4d2738966c0c0de` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:194` | LOW | `ADX is still above 25 twelve bars later in 92-100% of cases` — excludes `1w` in `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:186` (`ADX<25 after: 12% UNDERPOWERED`, i.e. 88% above 25). |
| `e41c9ab72cd922cd2a09d8efb4d2738966c0c0de` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py:280` | LOW | `L += ["", "## SUMMARY_PLACEHOLDER", ""]` — script emits a placeholder, so `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:188-195` was hand-authored rather than generated directly. |
| `e41c9ab72cd922cd2a09d8efb4d2738966c0c0de` | `MyTradingSys/research/adx_di_2026-11/test_measure_1113.py:1-55` | LOW | Unit tests cover `compute`, `events`, and `fwd`, but do not test `fade_table`, `peak_row`/`fwd_peak_outcomes`, or `build_series`/`cell`. |
| `73c47df5bfd483943a79022357b0d2bcdb45cb60` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py:172-198` | NO FINDINGS | Pure refactor extracting `fwd_abs_move` and `fwd_peak_outcomes`; logic unchanged. |
| `025912e4af8b88481fe130bf26d86051b98ba31b` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py:31` | NO FINDINGS | `FEE = _fees.BINANCE_MAKER * 2` equals `0.0004` (`0.0002 * 2`), matching prior constant. |
| `65586b240fe1e8000211aa64da47f9abbce59eb6` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py:244` | LOW | Commit body states `measure_1113.py calls fapi.binance.com without binance_doh.`, whereas `measure_1113.py` only had `fapi.binance.com` in a source-note string (clarified in `45ad3a6a4`). |
| `45ad3a6a42f9894bbefdcfebfbb7d9cbd8cb848c` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:5` | MED | Re-lands `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:5` (`ccu_DXntdN3jfTg_extract.md` false ADX citation) and `MyTradingSys/research/adx_di_2026-11/measure_1113.py:4`, `:237-238`. |
| `45ad3a6a42f9894bbefdcfebfbb7d9cbd8cb848c` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:194` | LOW | Re-lands `92-100%` summary omission of `1w` (`88%` above 25 at `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:186`), `MyTradingSys/research/adx_di_2026-11/measure_1113.py:280` `SUMMARY_PLACEHOLDER`, and `MyTradingSys/research/adx_di_2026-11/test_measure_1113.py:1-55` coverage scope. |
