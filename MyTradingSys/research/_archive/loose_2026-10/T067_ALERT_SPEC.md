# T067 - Alert spec: sweep + OI-drop pattern, absorption at a marked zone

Session: MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch (Cloud, static). Item: items/T067_alert_improvements.md (scope a, b; c "buy detection" is parked, see section 1.5).
Deliverable is spec + tests only. `scripts/live/alerts.ps1` and everything under `layers/alerts/` / `execution/` are untouched; staging, promotion and any restart belong to the supervisor
(claim `layers/alerts/` in SUPERVISOR_LOG first; builders never stop or restart runners, never touch HALT files).

# Part 1 - Spec

## 1.1 Gating (read first)

| Alert | Evidence status | Rule |
|---|---|---|
| A. `sweep_oi_drop` | **Gated on T063 arm A1.** Wave 3 could not run the OI clause (no OI on the ref, Binance blocked); arm A0 (sweep + price/CVD only, n=71, 4.6 days) showed no separation from its control (research/_archive/loose_2026-10/T063_STOP_RUN_OI_FLUSH.md section 2). | Build and test now, ship **disabled** (registry flag off). Enable only after A1 passes its PRE_REG decision rule on 30 d of 5m OI (last 10 d holdout). If A1 fails the layer is removed, not retuned. |
| B. `zone_absorption` | Definition from the T064 extract (Tom: reversal signal AT the pre-marked point, volume exhaustion; Fabio: aggression met by a wall / delta effort with ~zero price result). All magnitudes NO-SOURCE. | May ship as an **alert-only [SCREENER]** layer once G12 (high/low touch) is available; thresholds are config, tagged [OPERATOR-HYPOTHESIS/UNSOURCED], never a Tom filter. |

Both alerts are read-only flags: **no `side` field** on any event (auto_trader trades any alert carrying `side`, see live_layers.py header; both patterns are unvalidated). They carry `flush_dir` / `bias` instead.

## 1.2 Inputs and prerequisites

| Input | Needed by | Status / owner |
|---|---|---|
| `oi` field on each closed bar (5m sumOpenInterest joined on bar open time) | A | Feeder change on Desktop after B136 and the D2 recorder land (`runtime/oi_live`). Layer reads `bar["oi"]`; missing or non-numeric -> no event (fail closed). B136 flat-0.0 signature -> no event, no error. |
| Zones list `[{"id","lo","hi"}]` from a provider callable evaluated per call | B | Provider is `make_zone_absorption_layer(get_zones)`, same factory pattern as `make_funding_layer`. Zones come from the engine's marked levels (weekly/daily/4h VAH/VAL/POC, swing levels) and later T066 operator levels. Provider exception -> `[]`. |
| Touch by bar high/low, not sampled last price | B | G12. The layer works on closed klines `{t,o,h,l,c,v,tbv}` so it satisfies this by construction; delta = `2*tbv - v` (same as turn_of_candle_layer). |
| Feed liveness | both | G2 watchdog is separate; a feed hole yields non-contiguous bars and A fails closed on a gap in its lookback. |

## 1.3 Alert A: `sweep_oi_drop_layer(bars)` (5m bars carrying `oi`)

Definition is the T063 PRE_REG verbatim (research/_archive/loose_2026-10/T063_STOP_RUN_OI_FLUSH.md section 1), so the alert is exactly what A1 tests. Defaults N=12, W=6, M=2.0, cooldown 6 bars [OPERATOR-HYPOTHESIS/UNSOURCED; T064 found no sourced stop-run or retrace number].

1. Up-sweep at bar s: `high_s > max(high_{s-12..s-1})`. Down-sweep mirrors with lows. Requires 12 contiguous 5m bars before s (timestamp check).
2. Flush bar t in [s+1, s+6] (closed bar, no look-ahead): up-sweep needs `close<open` and `delta<0`; down-sweep needs `close>open` and `delta>0`; and `|close-open| >= 2.0 * median(|close-open| over t-12..t-1)` with that median > 0.
3. OI clause: `dOI_t = oi_t - oi_{t-1} < 0` and `|dOI_t| >= 2.0 * median(|dOI| over t-12..t-1)` with that median > 0 (so a flat or all-zero series can never fire).
4. One event per sweep (first qualifying t) and a cooldown of 6 bars per side.
5. Event: `{"t": <flush bar OPEN time ms>, "event": "sweep_oi_drop_<up|down>_<t>", "flush_dir": "down"|"up", "sweep_t": <sweep bar open ms>, "d_oi": <float>}`; the event name is unique per `(t, signal)`, matching the alert_emitter dedup key. `<up|down>` names the swept side.
6. Registry entry: layer `alerts_pattern`, sub `sweep_oi_drop`, tf `5m`, params_id `sweep_oi_drop_t063pre_2026-10-05`, **default disabled**.

## 1.4 Alert B: `make_zone_absorption_layer(get_zones)` (any TF; evaluates only the latest closed bar)

Tested on the last element of `bars` only: zones are time-varying, so re-scanning history with today's zones would emit stale alerts.

1. Baseline: median `|close-open|` (mb) and median `|delta|` (md) over the 12 bars before the latest; both must be > 0 and the 12 bars contiguous, else `[]`.
2. Effort: `|delta| >= 2.0 * md`. Result: `|close-open| <= 0.5 * mb` (effort met by a wall; Fabio "delta effort with ~zero price result", T064-Fabio-13; Tom "volume exhaustion", T064-Tom-04). 2.0 and 0.5 are UNSOURCED config.
3. Buyers absorbed at a zone: `delta>0`, bar OPENS below `lo` (approach from outside), `high >= lo`, `close <= hi` (not accepted above). Event `absorbed="buyers"`, `bias="down"`. Sellers mirror (`delta<0`, open above `hi`, `low <= hi`, `close >= lo`) -> `absorbed="sellers"`, `bias="up"`.
4. Zones with missing keys, non-numeric or `lo > hi` are ignored; no zones or provider error -> `[]`.
5. Event: `{"t","event":"zone_absorption_<zone_id>_<t>","zone_id","absorbed","bias","delta","zone_lo","zone_hi"}`; two zones touched by one bar give two events with distinct names.
6. Zone TF vs trigger TF: this layer is the **trigger-TF reader**. Per T064, zones are carried from the larger frame; the registry may run it on 1m/5m/15m against the same zone list. The ratio is NO-SOURCE and left to configuration (T064 section 4).
7. Registry entry: layer `alerts_pattern`, sub `zone_absorption`, one entry per configured trigger TF, params_id `zone_absorption_t064_2026-10-05`.

## 1.5 Parked

- **Buy detection** (T067 scope c): the operator still has to confirm the meaning (large aggressive buying vs bot detection). Working reading (b99/b999 buy tiers with OI up = new longs, OI down = short covering) needs OI too. Not specified here.
- Operator levels (T066) enter B as additional zones later; no code change to B.

## 1.6 Live-path checklist for the implementer (supervisor claims `layers/alerts/`)

- New module `MyTradingSys/backtest/layers/alerts/alert_patterns.py`; adapters registered in `live_runner_cli.py` next to the `turn_of_candle` entry (line ~297) behind a config flag; no change to `execution/`.
- Grep every TF/family map when adding the `alerts_pattern` family (CLAUDE.md): `scripts/dev/alert_rate_check.py` (TF_MIN, family classifier), `execution/auto_trader.py` (TF_SECONDS, account routing), `scripts/dev/test_testnet_status.py`, `backtest/layers/alerts/test_live_toc_tfs.py`, `test_live_runner_wiring.py`.
- Restart/reset: layers are pure (stdlib only, no state); a restart replays closed bars and `new_alerts` dedups on `(t, event)` (test `TestRestartAndDedup`).
- Non-trade balance moves: not applicable (no orders, no balances read). API errors: OI absent / provider raising -> fail closed (tests `test_missing_oi_fails_closed`, `test_zone_provider_error_fails_closed`).
- Acceptance: the 29 tests below pass; mutation spot checks (section 3) fail as expected; `python scripts/dev/run_all_tests.py` green; one live dry-run row per layer before enabling.

# Part 2 - Tests (failing-first)

File: `MyTradingSys/research/t067/test_alert_patterns.py.spec` (copy to `backtest/layers/alerts/test_alert_patterns.py` when the module is staged; the `.spec` suffix keeps it out of discovery now).

## 2.1 Failing-first evidence (run on Cloud 2026-10-05, repo root)

- **Red, module absent:** `python -m unittest MyTradingSys.backtest.layers.alerts.test_alert_patterns` -> `ImportError` / `FAILED (errors=1)` (no `alert_patterns` module on the ref).
- **Green against a throwaway reference implementation** (written only to prove the fixtures are satisfiable, NOT committed): 29 tests OK. Expected values in the fixtures were derived by hand from section 1 (comments in each fixture), not from that implementation.
- **Mutation spot checks** (each applied alone to the reference, tests must go red): M 2.0->1.0 (2 failures); a `side` key added (1); removing the result-size test condition (1); removing the OI-key fail-closed `except` (1); removing the "opens below zone" approach condition (1, after adding `test_open_inside_zone_not_an_approach`); removing BOTH the per-sweep dedup and the cooldown (1; either alone is redundant for this fixture).

## 2.2 Coverage map

| Spec clause | Tests |
|---|---|
| 1.3 steps 1-3, 5 | `test_up_sweep_oi_drop_flush_emits_one_event`, `test_down_sweep_mirror`, `test_oi_rise_on_flush_bar_no_event`, `test_oi_drop_below_adjacent_magnitude_no_event`, `test_no_sweep_no_event`, `test_cvd_not_in_step_no_event` |
| 1.3 step 4 | `test_second_flush_same_sweep_deduped` |
| fail closed / B136 / gaps | `test_missing_oi_fails_closed`, `test_flat_oi_b136_signature_no_event_no_error`, `test_gap_in_lookback_fails_closed`, `test_too_few_bars_no_event` |
| no look-ahead | `test_prefix_stable_no_lookahead` |
| 1.4 steps 1-5 | `test_buyers_absorbed_at_resistance`, `test_sellers_absorbed_at_support`, `test_touch_uses_high_low_not_close`, `test_no_touch_no_event`, `test_effort_too_small_no_event`, `test_price_result_large_means_not_absorption`, `test_accepted_above_zone_no_event`, `test_open_inside_zone_not_an_approach`, `test_effort_against_zone_side_no_event`, `test_two_zones_two_distinct_events`, `test_fail_closed_inputs`, `test_zone_provider_error_fails_closed`, `test_only_latest_closed_bar_is_evaluated` |
| alert-only (no `side`) | `test_no_side_key_alert_only` (both classes) |
| restart / purity | `TestRestartAndDedup` (2 tests) |

## 2.3 Test file (verbatim copy)

```python
"""T067 failing-first tests for MyTradingSys/backtest/layers/alerts/alert_patterns.py (module does not exist yet).
Hand-computed fixtures; every expected number is derived in the comments from the spec in research/_archive/loose_2026-10/T067_ALERT_SPEC.md,
not from the implementation. Install by copying to backtest/layers/alerts/test_alert_patterns.py when the module is staged."""
import unittest

from MyTradingSys.backtest.layers.alerts.alert_emitter import new_alerts
from MyTradingSys.backtest.layers.alerts.alert_patterns import (
    sweep_oi_drop_layer, make_zone_absorption_layer,
)

STEP = 300000  # 5m


def bar(i, o, h, l, c, v=100.0, tbv=50.0, oi=None):
    b = {"t": i * STEP, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv}  # delta = 2*tbv - v
    if oi is not None:
        b["oi"] = oi
    return b


def base_bars(n=12, oi0=1000.0):
    """12 flat bars: body 0.2, h 101, l 99, delta 0, OI +2 per bar. median|body| = 0.2, median|dOI| = 2."""
    return [bar(i, 100.0, 101.0, 99.0, 100.2, oi=oi0 + 2 * i) for i in range(n)]


def up_sweep_then_flush(doi_flush=-10.0, flush_delta_tbv=60.0, flush_v=200.0, sweep_h=103.0):
    bars = base_bars()
    # bar 12: high 103 > max(high 0..11)=101 -> up-sweep; small body, OI +2 (1000+24)
    bars.append(bar(12, 100.2, sweep_h, 100.0, 100.5, oi=1000.0 + 24))
    # bar 13: flush. body = 99.5-101 = -1.5, |body| >= 2*0.2 = 0.4. delta = 2*60-200 = -80 < 0.
    # dOI = oi13 - oi12 = doi_flush (-10); |-10| >= 2*median|dOI|(=2) = 4.
    bars.append(bar(13, 101.0, 101.5, 99.4, 99.5, v=flush_v, tbv=flush_delta_tbv, oi=1024.0 + doi_flush))
    return bars


def down_sweep_then_flush(doi_flush=-10.0):
    bars = base_bars()
    bars.append(bar(12, 99.8, 100.0, 97.0, 99.5, oi=1000.0 + 24))     # low 97 < min(low 0..11)=99 -> down-sweep
    bars.append(bar(13, 99.0, 100.6, 98.9, 100.5, v=200.0, tbv=140.0, oi=1024.0 + doi_flush))  # body +1.5, delta +80
    return bars


class TestSweepOiDrop(unittest.TestCase):
    def test_up_sweep_oi_drop_flush_emits_one_event(self):
        ev = sweep_oi_drop_layer(up_sweep_then_flush())
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual(e["t"], 13 * STEP)                    # bar OPEN time of the flush bar
        self.assertEqual(e["event"], "sweep_oi_drop_up_%d" % (13 * STEP))
        self.assertEqual(e["flush_dir"], "down")
        self.assertEqual(e["sweep_t"], 12 * STEP)

    def test_down_sweep_mirror(self):
        ev = sweep_oi_drop_layer(down_sweep_then_flush())
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["event"], "sweep_oi_drop_down_%d" % (13 * STEP))
        self.assertEqual(ev[0]["flush_dir"], "up")

    def test_no_side_key_alert_only(self):
        # auto_trader trades any alert carrying "side"; this pattern is unvalidated (T063 A1) and must never carry one
        for e in sweep_oi_drop_layer(up_sweep_then_flush()) + sweep_oi_drop_layer(down_sweep_then_flush()):
            self.assertNotIn("side", e)

    def test_oi_rise_on_flush_bar_no_event(self):
        self.assertEqual(sweep_oi_drop_layer(up_sweep_then_flush(doi_flush=+2.0)), [])

    def test_oi_drop_below_adjacent_magnitude_no_event(self):
        # |dOI| = 3 < 2 * 2 = 4
        self.assertEqual(sweep_oi_drop_layer(up_sweep_then_flush(doi_flush=-3.0)), [])

    def test_no_sweep_no_event(self):
        bars = up_sweep_then_flush(sweep_h=100.9)   # 100.9 <= 101: not a sweep
        self.assertEqual(sweep_oi_drop_layer(bars), [])

    def test_cvd_not_in_step_no_event(self):
        # flush bar falls but delta = 2*140-200 = +80: price and CVD disagree
        self.assertEqual(sweep_oi_drop_layer(up_sweep_then_flush(flush_delta_tbv=140.0)), [])

    def test_missing_oi_fails_closed(self):
        bars = up_sweep_then_flush()
        del bars[13]["oi"]
        self.assertEqual(sweep_oi_drop_layer(bars), [])
        bars2 = up_sweep_then_flush()
        for b in bars2:
            b.pop("oi")
        self.assertEqual(sweep_oi_drop_layer(bars2), [])

    def test_flat_oi_b136_signature_no_event_no_error(self):
        bars = up_sweep_then_flush()
        for b in bars:
            b["oi"] = 0.0           # B136: OI reported flat 0.0 on every snapshot
        self.assertEqual(sweep_oi_drop_layer(bars), [])

    def test_second_flush_same_sweep_deduped(self):
        bars = up_sweep_then_flush()
        # bar 14: another qualifying flush inside the same sweep window; dOI = -10, median |dOI| over 2..13 is still 2
        bars.append(bar(14, 99.5, 99.8, 97.9, 98.0, v=200.0, tbv=60.0, oi=bars[13]["oi"] - 10.0))
        ev = sweep_oi_drop_layer(bars)
        self.assertEqual([e["t"] for e in ev], [13 * STEP])

    def test_prefix_stable_no_lookahead(self):
        bars = up_sweep_then_flush()
        short = sweep_oi_drop_layer(bars)
        longer = bars + [bar(14 + k, 99.5, 100.0, 99.0, 99.6, oi=bars[13]["oi"] + 2 * (k + 1)) for k in range(10)]
        self.assertEqual(sweep_oi_drop_layer(longer), short)

    def test_gap_in_lookback_fails_closed(self):
        bars = up_sweep_then_flush()
        del bars[5]                     # a missing 5m bar inside the 12-bar lookback
        self.assertEqual(sweep_oi_drop_layer(bars), [])

    def test_too_few_bars_no_event(self):
        self.assertEqual(sweep_oi_drop_layer(up_sweep_then_flush()[:13]), [])
        self.assertEqual(sweep_oi_drop_layer([]), [])


def zone_bars(last):
    """12 baseline bars: body 0.4, delta = 2*52-100 = +4 (|delta| median 4), h 101. Then `last` as bar 12."""
    bars = [bar(i, 100.0, 101.0, 99.5, 100.4, v=100.0, tbv=52.0) for i in range(12)]
    bars.append(last)
    return bars


RES = {"id": "weekly_vah", "lo": 105.0, "hi": 106.0}
SUP = {"id": "daily_val", "lo": 94.0, "hi": 95.0}


class TestZoneAbsorption(unittest.TestCase):
    def layer(self, zones=None):
        return make_zone_absorption_layer(lambda: [RES] if zones is None else zones)

    def test_buyers_absorbed_at_resistance(self):
        # effort: delta = 2*210-300 = +120 >= 2*4 = 8. result: body |105.0-104.9| = 0.1 <= 0.5*0.4 = 0.2.
        # touch: high 105.6 >= lo 105. close 105.0 <= hi 106 (not accepted above the zone).
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=210.0)
        ev = self.layer()(zone_bars(last))
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual(e["t"], 12 * STEP)
        self.assertEqual(e["event"], "zone_absorption_weekly_vah_%d" % (12 * STEP))
        self.assertEqual(e["absorbed"], "buyers")
        self.assertEqual(e["bias"], "down")
        self.assertEqual(e["zone_id"], "weekly_vah")

    def test_sellers_absorbed_at_support(self):
        # delta = 2*90-300 = -120; body |95.0-95.1| = 0.1; low 94.4 <= hi 95; close 95.0 >= lo 94
        last = bar(12, 95.1, 95.2, 94.4, 95.0, v=300.0, tbv=90.0)
        ev = self.layer([SUP])(zone_bars(last))
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["absorbed"], "sellers")
        self.assertEqual(ev[0]["bias"], "up")

    def test_touch_uses_high_low_not_close(self):
        # G12: wick pierces the zone, close back below it. close 103.1 is nowhere near 105; high 105.5 >= 105
        last = bar(12, 103.0, 105.5, 102.9, 103.1, v=300.0, tbv=210.0)
        self.assertEqual(len(self.layer()(zone_bars(last))), 1)

    def test_no_touch_no_event(self):
        last = bar(12, 103.0, 104.9, 102.9, 103.1, v=300.0, tbv=210.0)   # high 104.9 < 105
        self.assertEqual(self.layer()(zone_bars(last)), [])

    def test_effort_too_small_no_event(self):
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=100.0, tbv=53.0)    # delta = 6 < 8
        self.assertEqual(self.layer()(zone_bars(last)), [])

    def test_price_result_large_means_not_absorption(self):
        last = bar(12, 104.5, 105.6, 104.4, 105.0, v=300.0, tbv=210.0)   # body 0.5 > 0.2
        self.assertEqual(self.layer()(zone_bars(last)), [])

    def test_accepted_above_zone_no_event(self):
        last = bar(12, 106.1, 106.4, 106.0, 106.2, v=300.0, tbv=210.0)   # close 106.2 > hi 106: price accepted above
        self.assertEqual(self.layer()(zone_bars(last)), [])

    def test_open_inside_zone_not_an_approach(self):
        # buyer effort and tiny body, but the bar OPENS inside the zone (105.5 >= lo 105): price did not approach it from below
        last = bar(12, 105.5, 105.6, 105.4, 105.5, v=300.0, tbv=210.0)
        self.assertEqual(self.layer()(zone_bars(last)), [])

    def test_effort_against_zone_side_no_event(self):
        # seller delta (-120) while touching a resistance zone is not absorption of buyers
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=90.0)
        self.assertEqual(self.layer()(zone_bars(last)), [])

    def test_two_zones_two_distinct_events(self):
        z2 = {"id": "daily_vah", "lo": 105.5, "hi": 106.5}
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=210.0)
        ev = self.layer([RES, z2])(zone_bars(last))
        self.assertEqual(sorted(e["zone_id"] for e in ev), ["daily_vah", "weekly_vah"])
        self.assertEqual(len({e["event"] for e in ev}), 2)

    def test_no_side_key_alert_only(self):
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=210.0)
        for e in self.layer()(zone_bars(last)):
            self.assertNotIn("side", e)

    def test_fail_closed_inputs(self):
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=210.0)
        self.assertEqual(self.layer([])(zone_bars(last)), [])                   # no zones
        self.assertEqual(self.layer()(zone_bars(last)[-5:]), [])                # < 12 prior bars
        flat = [bar(i, 100.0, 100.0, 100.0, 100.0, tbv=50.0) for i in range(12)] + [last]
        self.assertEqual(self.layer()(flat), [])                                # median body 0 / median |delta| 0: no baseline
        bad = [{"id": "x", "lo": 106.0, "hi": 105.0}]
        self.assertEqual(self.layer(bad)(zone_bars(last)), [])                  # inverted zone ignored, no raise

    def test_zone_provider_error_fails_closed(self):
        def boom():
            raise RuntimeError("zones unavailable")
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=210.0)
        self.assertEqual(make_zone_absorption_layer(boom)(zone_bars(last)), [])

    def test_only_latest_closed_bar_is_evaluated(self):
        # zones are time-varying (provider is called per evaluation): history must not be re-scanned with today's zones
        last = bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=210.0)
        bars = zone_bars(last)
        self.assertEqual(len(self.layer()(bars)), 1)
        later = bars + [bar(13, 105.0, 105.1, 104.9, 105.0, v=100.0, tbv=50.0)]
        self.assertEqual(self.layer()(later), [])      # bar 12 is no longer the latest bar


class TestRestartAndDedup(unittest.TestCase):
    """Live-path rule (CLAUDE.md): restart/reset state. Layers are pure, so a restart replays the same bars."""

    def test_restart_replay_is_idempotent_and_emits_nothing_new(self):
        bars = up_sweep_then_flush()
        first = sweep_oi_drop_layer(bars)
        again = sweep_oi_drop_layer([dict(b) for b in bars])      # fresh process, same closed bars
        self.assertEqual(first, again)
        self.assertEqual(new_alerts(first, again), [])           # alert_emitter dedup key (t, event) -> no re-alert

        zl = make_zone_absorption_layer(lambda: [RES])
        zb = zone_bars(bar(12, 104.9, 105.6, 104.8, 105.0, v=300.0, tbv=210.0))
        z1, z2 = zl(zb), zl([dict(b) for b in zb])
        self.assertEqual(z1, z2)
        self.assertEqual(new_alerts(z1, z2), [])

    def test_input_bars_not_mutated(self):
        bars = up_sweep_then_flush()
        snap = [dict(b) for b in bars]
        sweep_oi_drop_layer(bars)
        self.assertEqual(bars, snap)


if __name__ == "__main__":
    unittest.main()
```
