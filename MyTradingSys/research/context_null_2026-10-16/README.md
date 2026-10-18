# Context-null harness (2026-10-16)

Why: the Fable gross-effect screen's location-only control arm FAILED hard (n=1,439, mean -0.008 %, t_cost -6.0,
`research/fable_audit_2026-10-16/FABLE_RUNS_AUDIT.md`). Being at a level / in a context is itself a cost-losing place, so a
trigger must beat bars in the **same context**, not zero. This harness is that comparison. Independent of the point-in-time
level builders (`research/pit_levels_2026-10-16/`): level distance is an optional precomputed input column.

Files: `context_null.py` (library), `test_context_null.py` (10 tests on synthetic tapes, `python test_context_null.py`).
No market data is read here: the caller passes arrays. DEV only: any bar opening at/after 2024-07-01 raises `ValueError`.

## What it computes

Per event bar `t` (decision at the close of bar `t`; entry `close[t+d]`, exit `close[t+d+h]`, return in %):
`K` controls (default 20, OURS) from the same array with the same context key, every key from bars `<= t` only:

| key | definition |
|---|---|
| hour | UTC hour of the bar's open time |
| vol | tercile of trailing realised vol (6 h window, OURS); cut points from the trailing 30 d window ending at the bar |
| trend | `tom_bt.trend_tag` of the trailing 30 d return (imported from `backtest/tom_bt.py`, not copied) |
| level | optional caller column, one int per bar, point in time, `<0` = unknown (event unmatched) |

Controls never lie inside or within `cooldown` bars of any event's `[t, t+d+h]` window and are `> cooldown` bars apart.
Events with `< kmin` controls (default `K//2`, OURS) or with no context (first 30 days, unknown level) are dropped and counted.

Output (percent): `n events`, `n matched`, `n unmatched` (split into no_fwd / no_context / too_few_controls);
**trigger effect** = mean over matched events of (event fwd - mean of its controls' fwd), day-clustered SE
(`screen.cluster_mean_se`), t; **context-only effect** = matched-control mean minus the unconditional mean of eligible
(outside-event-window) bars, day-clustered (`screen.diff_cluster`); identity
`event_mean - uncond_mean = context_effect + trigger_effect`. A control-reuse line warns when the pool is thin
(`control_reuse > 5`): shared controls make the SE too small, so use fewer events or a looser key.

## Use

```python
import sys; sys.path.insert(0, "MyTradingSys/research/context_null_2026-10-16")
import context_null as CN
cfg = CN.Config(bar_min=1, cooldown=60, seed=0)           # cooldown = the signal's own; K=20
res = CN.run(close, event_bar_indices, h=60, d=1, cfg=cfg, level=level_bucket_or_None)
print(CN.format_report(res))
```

`close[i]` is the close of the bar opening at `cfg.ts0_ms + i * bar_min * 60000`. Events must already obey the signal's own
cooldown. Ablation: `Config(match=("hour","vol"))` drops keys.

## Naming it as a PRE_REG control arm

In the PRE_REG, section "control arm", write:

> Control arm: context-null (`MyTradingSys/research/context_null_2026-10-16/context_null.py`, commit <sha>), keys hour + vol
> tercile + trend tag (+ level bucket <name of the PIT column, built by ...>), K=20, kmin=10, cooldown=<signal cooldown>,
> h=<h>, d=<d>, seed=0. PASS_CONTROL requires trigger effect > 0 with t >= <threshold fixed in this PRE_REG> AND the trigger
> effect minus 0.14 % (taker) / 0.09 % (maker-in) round trip > 0 on DEV. The context-only line is reported, never a gate.

Fix `K`, `seed`, the keys and the thresholds in the PRE_REG before the one run. Do not run it on a real signal set outside
that run: reading the outcomes burns the PRE_REG.

## Limits

- SE is day-clustered on the event side only; controls reused across days correlate (see the reuse line).
- Trend tag needs 30 d of history, so the first 30 days of a tape are never events or controls.
- Parameters marked OURS in `context_null.py` (K, kmin, 6 h vol window, 30 d cut window, reuse warning 5) are judgement, not tuned.
- Test fixtures are iid Gaussian tapes: they prove the mechanics (planted context rejected, planted trigger recovered, no
  look-ahead), not that real BTC context keys are sufficient.
