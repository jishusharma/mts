SOUND

## Scope and method
Audited `MyTradingSys/research/bb_range_to_range_2026-11-04/study.py` against its frozen `PRE_REG.md` and the reused helper implementations. This is a code/math audit; no return pass was run and no market-data bars were loaded.

## Findings

| Severity | Location | Finding | Evidence and verdict | Fix |
|---|---|---|---|---|
| LOW | `study.py:45-54`; `PRE_REG.md` Parameters / Bands | Bollinger window and standard deviation are causal and match the registration. | **MATCH**: each band at i uses closes `[i-19, i]`; `numpy.std()` defaults to population ddof=0. | None. |
| LOW | `study.py:57-76`; `PRE_REG.md` Parameters / Signal, Target | Event, level, target, and timestamp are based only on the signal bar and prior bar. | **MATCH**: close beyond the current lower/upper band and prior close not beyond its own prior band selects the first excursion bar; target is the opposite band at i. `t_close = open + tf_ms`. | None. |
| LOW | `study.py:113-138`; `research_kit.py:275-289`; `PRE_REG.md` Parameters / Entry | Signal and retest entry indexing match the registered definitions. | **MATCH**: signal enters at bar i close. Retest checks i+1 through i+10 inclusive, excludes bar i, fills at the band or the gapped-through open, and skips no-touch events. Helper explicitly implements those rules. | None. |
| LOW | `study.py:79-100`; `PRE_REG.md` Parameters / Stop, Time-out | Exit loop avoids reading the entry bar and implements the registered bracket ordering. | **MATCH**: checks j+1 through j+24 inclusive; when both stop and target are touched, stop is tested first. Stop gaps fill at open via `min(o, stop)` long / `max(o, stop)` short. If neither bracket hits, timeout uses close of j+24. | None. |
| LOW | `study.py:34, 141-152`; `research_kit.py:21`; `PRE_REG.md` Parameters / Cost, Statistics | Fee-net math is consistent with the 0.14% round-trip fee. | **MATCH**: `net = gross - COST`, with `COST = TAKER_RT_PCT = 0.14` percentage points; cluster mean/SE, p, and CI use net returns. | None. |
| LOW | `study.py:107-110, 183-192`; `research_kit.py:240-259`; `PRE_REG.md` Parameters / Range definition | Gate uses as-of regime at the signal close; `all` retains missing regime tags. | **MATCH**: exact regime equality filters range/bull/bear, while `all` bypasses regime tags. The helper's as-of lookup uses only daily/weekly/monthly closes at or before t. | None. |
| LOW | `study.py:103-105, 186-200`; `research_kit.py:270-272`; `PRE_REG.md` Parameters / Session | Session assignment matches the registered signal-bar-close session for all entry types. | **MATCH**: session is assigned from `e.t_close` before entries are evaluated and carried on the trade; confirmatory sessions are asia/london/ny and late remains descriptive. | None. |
| LOW | `study.py:175-181, 189-200`; `splits.py:35-42`; sibling `study.py:147-153`; `PRE_REG.md` Windows | Window filter is on signal close in `[lo, hi)` and loader is exclusive at hi. | **MATCH**: `load_1m(hi_ms)` is followed by assertion that final bar open `< hi_ms`; events require `lo <= t_close < hi`. No post-hi bars can enter resampling or exit simulation. | None. |
| LOW | `study.py:208-213`; `PRE_REG.md` Comparison arm | Range-minus-ungated comparison passes gross returns to `cluster_diff`, while the table is described as net gate effect. | **MATCH**: subtracting the same fixed 0.14 percentage-point fee from each arm leaves the difference of means and its paired day-cluster influence unchanged; `cluster_diff` computes mean difference and day-clustered SE. | None. |

## Verdict
No lookahead, fee-net, entry/exit indexing, or range/session boundary mismatch found against the frozen registration. **SOUND** for the encoded rules. This does not validate the result or claim a performance edge; no data run was performed.

## Follow-up cards
None.
