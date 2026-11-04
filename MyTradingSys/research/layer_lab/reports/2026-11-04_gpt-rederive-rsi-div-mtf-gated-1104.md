# GPT independent re-derivation: RSI divergence MTF gated, strict vs bear proxy

**Verdict: FAIL — the causal timing and fee deduction are sound in code, but the long-window strict-vs-proxy result is not independently reproducible from this machine’s permitted source set, and the proxy definition is narrower than its label suggests.**

## Scope and evidence

Read `study.py` and `study_long.py`, plus their dependencies `research_kit.py`, `rsi_divergence.py`, `rsi_core.py`, `tf_resample.py`, `registry.json`, and `malkan_mtf.py`. Evidence references below are repository file:line. No post-2024-07-01 DEV bars were read. The permitted perp 1h/15m NPZ and BTC 1m DEV archives exist, but the scripts’ configured roots are different. No study was rerun and no return metrics were derived from bars.

## Findings

| Severity | File:line | Result | Evidence / implication | Proposed fix |
|---|---|---|---|---|
| LOW | `study.py:156-163`; `tf_resample.py:90-117`; `research_kit.py:209-212,240-255` | MATCH | `rsi_series` drops the final weekly/monthly bucket and timestamps each retained RSI at the next bucket open. `state_asof` is latest timestamp `<= t`; `regime_tag` applies it to both HTFs. The day cache evaluates at 00:00 UTC, which is conservative (may lag the event close intraday) and cannot use a still-open HTF candle. `resample` emits closed buckets only. | None for look-ahead; document the midnight sampling as conservative daily alignment. |
| LOW | `study.py:77-87`; `rsi_divergence.py:48-57,78-97` | MATCH | Strict close pivots require both neighboring closes. Swing B is confirmed using the following bar; event index is `b+1`, and `t_close = ts[i] + TF_MS[tf]`. Therefore entry/gate occurs after the confirmation bar closes, one full bar after B. | None. |
| LOW | `study.py:25-27,90-121`; `research_kit.py:12-14,21` | MATCH | Gross return is signed close-to-close percentage for signal entry, or level/open fill for retest; `cell_stats` subtracts one 0.14 percentage-point round-trip charge from each trade. `TAKER_RT_PCT=0.14` is documented as 5+5 bp fees and 2+2 bp slippage. This is a fixed notional percentage approximation; no funding or compounding is included. | Keep the stated cost model attached to any result. |
| HIGH | `study_long.py:20-30,33-47,105-118` | MISMATCH | P40 changes a primary regime tag to bear only when primary `side == "below"` and weekly RSI `<=40`; all other states retain primary bull/range/none. It therefore does not implement an independent “weekly RSI <=40 alone” bear gate as the docstring/comment claims, because monthly RSI and primary regime tagging still affect the starting label. Holm `m=48` counts the primary 32 plus proxy 16 as intended, but the proxy arm’s meaning is not the advertised rule. | Define proxy state directly from the intended weekly condition plus an explicitly stated price-side rule, and report its mutually exclusive regime mapping. |
| HIGH | `study.py:36,147-154`; `study_long.py:25,56-62,79-89` | NOT_IN_DATA | The short loader reads only `F:/MTS/Dumps/backtest/raw_1m_*`; the long loader defaults to `F:/MTS/Dumps/backtest/spot_2017`. Neither is an allowed DEV source here. This machine’s permitted 1m DEV zips and perp 15m/1h caches are present, but the long study specifically needs spot 2017 onward, which is not supplied in the allowed data inventory. The stated strict-vs-proxy long metrics cannot be rederived without reading prohibited/absent spot data. | Rerun from an authorized spot archive on a machine where it is an approved DEV source, or explicitly scope a new study to the available perp DEV series. |
| MED | `study.py:156-163`; `tf_resample.py:131-155` | MISMATCH | The docstring says final HTF close is unknown and drops it, which prevents trailing partial-bar look-ahead. However, `resample` calls a bucket “closed” based on the last timestamp reaching its scheduled end; it records `gap_count` but retains buckets with missing constituent minutes. An HTF RSI can therefore be computed from a partial bucket if internal/final minute bars are missing. | Require expected constituent coverage before using a weekly/monthly bar for RSI, or mark this limitation in results. |

## Metrics and verdict boundary

The checked code’s fee arithmetic is internally consistent with the cited 0.14% round-trip convention. The current result artifacts are descriptive outputs, not an independent re-derivation: `dev_survivors.json` and `dev_survivors_long.json` contain empty arrays, and `BLOCKED.md` / `BLOCKED_LONG.md` say power is inadequate and the result ceiling is INCONCLUSIVE (short 15m aligned bullish W12: 96 event days; long primary bull 15m: 282; P40 bear 15m: 236; long primary bear: 0 weeks). Those artifact counts are not promoted here as independently verified because the configured inputs are unavailable under this run’s source restrictions.

Weekly/monthly no-look-ahead and the one-bar pivot confirmation delay: **PASS** by code inspection. Fee deduction: **PASS** by independent formula inspection. Strict-vs-proxy long metrics: **NOT independently verified**. Overall task verdict: **FAIL** pending correction/clarification of P40 and a permitted source-backed rerun.

## Follow-up cards

None created.
