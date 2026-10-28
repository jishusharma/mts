# G3 pack audit rerun ? 2026-10-16

## Verdict: MATCH ? three code HIGH findings closed; no new causality or DEV fence break

Draw rebuild: **NO**. The visual blindness findings and their follow-up cards remain open in the prior audit (`2026-10-16_gpt-g3-pack-audit.md`, section ?Blindness?). This rerun did not open the answer key or `KEY.csv`, read VALIDATION/HOLDOUT, or rebuild drawings.

## What was checked

- `MyTradingSys/research/g3_marks_2026-10-16/g3_pack.py`: `load_intraday` lines 59?74; `pf_fab4` lines 245?258; `pf_mal1617` lines 418?434.
- `MyTradingSys/research/g3_marks_2026-10-16/test_g3_pack.py`: 11 test functions, including new regression cases for the FAB4 minimum, divergence pivot window, and timestamp fence.
- `MyTradingSys/research/layer_rebuild_2026-10-15/READER_PROTOCOL.md`: section 1, outside P / break-in (line 19) and RSI divergence (line 24).
- Poison probe command: `python -c "exec(open('MyTradingSys/research/layer_lab/gpt-g3-pack-audit/probe.py.txt', encoding='utf-8').read())"` ? synthetic data only.
- Test command: `python -m pytest MyTradingSys/research/g3_marks_2026-10-16/test_g3_pack.py -q -p no:cacheprovider --basetemp=MyTradingSys/research/layer_lab/reports/pytest_g3_rerun_tmp` ? **11 passed**.

## Findings

| Severity | Check | Verdict | Evidence |
|---|---|---|---|
| HIGH (closed) | FAB4 outside run minimum | **MATCH** | Protocol requires at least four consecutive closes outside prior VA before the first close back inside (`READER_PROTOCOL.md:19`). `pf_fab4` counts the consecutive run ending at `i-1` and returns a tag only for `run >= 4` (`g3_pack.py:253?257`). Regression test checks 2 and 3 return none; 4 and 6 return down (`test_g3_pack.py:161?171`). |
| HIGH (closed) | MAL-16/17 divergence window | **MATCH** | Protocol compares the highest/lowest close in the last 20 bars with the corresponding extremum 5..60 bars before that pivot (`READER_PROTOCOL.md:24`). The function selects `bh`/`bl` from `i-19..i`, then searches `range(pivot-60, pivot-4)`, i.e. inclusive pivot-60 through pivot-5 (`g3_pack.py:422?432`). Regression covers a pivot 10 bars before `i`, both directions, and excludes a reference 61 bars back (`test_g3_pack.py:174?189`). |
| HIGH (closed) | Intraday timestamp fence | **MATCH** | Loader computes exclusive end as 2025-04-01 UTC and discards each row with `t >= end_ms` even inside the last allowed file (`g3_pack.py:61?69`). Synthetic poison probe: `loader fences: intraday=MATCH daily=MATCH`; unit test also checks the next-day row in the 2025-03-31 file is dropped (`test_g3_pack.py:192?199`). |
| ? | Causality probe | **MATCH** | Output: all 11 units report prefilter=MATCH and chart=MATCH; totals `prefilters 11/11`, `charts 11/11`. Probe asserts all 22 comparisons. |
| ? | Regression suite | **MATCH** | Command above: `11 passed in 2.67s`. |
| ? | Blindness / draw decision | **NOT CLEARED** | Existing visual side-channel findings and follow-up cards remain open per prior audit?s Blindness section. By task rule, rebuild is unsafe until those cards close; no answer key or key CSV was read. |

No new causality or fence defect was observed in the synthetic rerun. No real market series was loaded; no VALIDATION or HOLDOUT data was read.

## Follow-up cards

No new cards created. Existing blindness cards remain responsible for the disclosure findings.
