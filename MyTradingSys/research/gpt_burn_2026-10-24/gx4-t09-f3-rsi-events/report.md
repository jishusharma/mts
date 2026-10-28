# GPT audit: T09 RSI event coverage

Task: `gx4-t09-f3-rsi-events`. Scope is Finding S1 in `research/dsa_backtest_audit_2026-10-16/T09_live_parity.md`.

## Finding

**HIGH (S1):** `backtest/layers/alerts/live_layers.py:146-167` emits the RSI `cross`, `failure`, `support`, and `rejection` outcomes from RSI(14) at level 40 / tolerance 0.5. The event generator itself is generic; that is not evidence that a trading rule was tested. D3 only tested the specific level/side/timeframe cells stated below. Only `support@40` on 1h at tolerance 0.5 matches the live layer's settings and a D3 study cell. `support@40` on 15m was studied at the selected tolerance 1.0, so it does not validate the live 0.5 configuration. D3's 60 rejection is not the live level-40 rejection. 5m had no D3 run.

### Event IDs and fire counts

The audit JSON has an `events` object per layer/timeframe; counts below are read from that object, which counts all emitted live events, including ones subsequently rejected as unmapped. Parenthetical coverage gives the exact D3 result where one exists.

| Live event ID | 5m fires | 15m fires | 1h fires | Matching live-rule backtest/study coverage |
|---|---:|---:|---:|---|
| `rsi:cross` (at level 40) | 527 | 180 | 29 | **No.** D3 does not test cross events at any level. `FORMULAS.md:121-130` defines cross semantics only; a formula/specification is not a performance study. |
| `rsi:failure` (at level 40) | 85 | 22 | 5 | **No.** D3 studies support@40 and rejection@60, not failure. |
| `rsi:support` (at level 40) | 78 | 24 | 3 | **No exact live-configuration test** for 5m (no D3 cell) or 15m (D3 selected tolerance 1.0, `BACKTEST_L1_REPORT.md:18`; live tolerance is 0.5). **Yes, exact parameter cell for 1h**: D3 level-40 support, tolerance 0.5, `BACKTEST_L1_REPORT.md:20` (3 live fires in this parity window). |
| `rsi:rejection` (at level 40) | 36 | 11 | 3 | **No.** D3 tested rejection at level 60 (`BACKTEST_L1_REPORT.md:19,21`), not live level 40. |

### Reproduction / source evidence

Run from repository root (PowerShell):

```powershell
$j = Get-Content MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/out/parity_result.json -Raw | ConvertFrom-Json
foreach ($tf in '5m','15m','1h') {
  $k = "rsi|rsi_events|$tf"
  [pscustomobject]@{ tf=$tf; events=$j.per_key.$k.events; live_only=$j.per_key.$k.backtest.live_only_by_event }
}
```

This parses the whole JSON document, rather than relying on a text search or truncated output. It reports 5m event counts at `parity_result.json:906-910`, 15m at `:716-720`, and 1h at `:822-826`. The study's exact selected cells and parameters are at `backtest/layers/BACKTEST_L1_REPORT.md:18-21`; it states its tolerance grid and levels at `:8-10`, and that 5m is absent from the result table. Live level/tolerance and event emission are at `backtest/layers/alerts/live_layers.py:142-167`. The generic state-machine event definitions are documented at `backtest/layers/FORMULAS.md:121-130` and `backtest/layers/rsi/TEST_PLAN.md:95-119`.

The parity JSON additionally attributes the 5m/15m/1h backtest live-only events at `:974-977`, `:800-803`, and `:885-888`; these are not substitutes for all fires because unmapped cross events are separately tallied. The task's fire-count request is answered from each timeframe's complete `events` count above.

## Proposed fail-closed gate and fail-first test

`patch.diff` is an unapplied proposal. It rejects RSI signals before side mapping, sizing, promotion, or order entry unless the layer/timeframe/event/level/tolerance tuple is explicitly in a tested-cell allowlist. The allowlist has only `1h / support / 40 / 0.5`: D3's other tested cells do not match the live rule. Missing, malformed, or unrecognized metadata rejects by default. The proposed unit test asserts that a cross alert with a tradable side is rejected, and that the one studied tuple passes the coverage gate; the cross test fails against the current code because it currently has no coverage gate.

Severity remains **HIGH**: the untested event families were emitted at scale in the 30-day replay (including 736 crosses and 112 failures across the three timeframes), and an event being specified by the generic detector does not establish tested trading performance.

Result: RSI live events are itemized with full-parsed parity fire counts; only 1h support@40/tol0.5 matches D3, and a fail-closed gate with fail-first test is proposed in patch.diff.