# Pre-implementation expectation record — gpt-formulas-rederive-14-16

Recorded before reading any of the three implementation modules, layer tests, or event-table reports. Derived only from FORMULAS.md sections 14–16 (lines 356–396).

## Synthetic fixture (zero-based bar indices)
- All fixture settings below are OURS, chosen to exercise the SOURCED rules in FORMULAS.md; no empirical-data parameters are claimed. Exactly 4,320 one-minute bars, UTC from 2020-01-01 00:00 inclusive through 2020-01-03 23:59 inclusive; `t[i] = epoch_ms + i*60,000`.
- Close baseline is `100 + i*0.001`. Each day has `open[day_start]=100`; close at `day_start+29` is set to 101 so the first 30-minute return is +1%. All other opens may equal prior close; turn return inputs will be set to 0 except specified probe bars (not used to determine event times).
- For funding divergence, at each eligible funding boundary `i = 480, 960, ..., 3840`, set `close[i] = max(close[i-2],close[i-1]) + 0.5`; set `cvd[i] = min(cvd[i-2],cvd[i-1]) - 1`, where ordinary CVD baseline is `i`. This creates a strict bearish divergence only on that boundary bar; no other bars are modified for divergence.
- Funding records at indices/times `0, 480, 960, ..., 3840` (every 8 h), rates `[0,.001,.002,.003,.004,.005,.006,.007,.008]`. Override grid parameters to `lookback=3`, `n=2`, `hi=2/3`, `lo=1/3`; ranking includes current observation per formula. At each eligible boundary the current rate is the window maximum, so pct=1 and the bearish divergence qualifies short. Index 0 cannot diverge because i<n.
- Session parameters: `session_start_min=0`, `first_min=30`, `session_len=1440`, `entry_min=30`, `min_abs=0`. Formula's bar-close timestamp condition maps each daily entry to the bar opening at minute 29.
- Turn parameters: `lead_minutes=1`, side fixed `short`. Formula maps `mq=14`; three days contain 96 such bars/day.

## Predicted events, sealed before implementation inspection
- Funding fade (combined divergence + funding): 8 events, indices `[480, 960, 1440, 1920, 2400, 2880, 3360, 3840]`.
- Session momentum: 3 events, indices `[29, 1469, 2909]`.
- Turn-of-candle: 288 events, indices `[14 + 15*k for k in 0..287]` (first 14, last 4304).

This is a spec-derived prediction, not yet a claim that the implementation produces these events. Reproduction uses the fixture definition above; no empirical market data is involved.

## Re-derivation corrections (after source comparison)
The pre-implementation record above captured the full intended synthetic shape and index formulas, but its hand-count contained two errors. Formula lines 362–363 only define a percentile at `k >= lookback - 1`: with lookback 3, funding record 0 (bar 0) has no percentile, record 1 (bar 480) is still insufficient, and the first defined extreme is record 2 at bar 960. Thus the corrected expected funding list is `[960, 1440, 1920, 2400, 2880, 3360, 3840]` (7), not the initially written 8-event list. The turn set expression `14 + 15*k, k=0..287` was right; its initially stated last index `4304` was wrong. The exact last is `14 + 15*287 = 4319` (288 events). The reproducibility script uses the corrected derivation and prints compact set notation for turn events.

## Comparison
| Module | Spec-derived expected | Actual | Result |
|---|---|---|---|
| Funding fade | 7: `[960, 1440, 1920, 2400, 2880, 3360, 3840]` | 7: `[960, 1440, 1920, 2400, 2880, 3360, 3840]` | Match |
| Session momentum | 3: `[29, 1469, 2909]` | 3: `[29, 1469, 2909]` | Match |
| Turn-of-candle | 288: `14 + 15*k`, `k=0..287` (first 14, last 4319) | 288: same exact set | Match |

Reproduce from repository root with:
`python MyTradingSys/research/layer_lab/reports/2026-10-28_gpt-formulas-rederive-14-16.py.txt`
The script prints expected and actual counts/index sets and per-module equality. It uses no market data and does not import layer tests or event-table reports.

## Findings
| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | This report, pre-implementation expectation section | Initial manual count included funding bar 480 before the 3-record lookback was available, and misstated the final turn index as 4304. | FORMULAS.md:362–363 requires `k >= lookback-1`; 4,320 bars yield turn indices `14+15*k` for k 0..287, ending at 4319. Corrected expected sets above match the independent runner output. | Keep the correction and corrected expectations above; no production change. |
| None | `funding_cvd_fade.py:22–26, 81–99`; `session_momentum.py:58–113`; `turn_of_candle.py:67–73` | No module mismatch found on the synthetic fixture. | Corrected counts and all exact bar indices match their corresponding formulas. | None. |

Checked: FORMULAS.md sections 14–16 (356–396), the three scoped modules, and the cited local whale positioning evidence file (`research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md`). No tests or event-table reports were read. No source/spec or production code changed.

Verdict: SOUND — all three modules reproduce the corrected, formula-derived synthetic event counts and indices; one LOW reporting arithmetic correction is preserved above.

