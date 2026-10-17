# WaveTrend source / parity contract (card wavetrend-priority-source-parity, 2026-10-17)

Scope: pins WHICH oscillator the study measures. It is a source-parity claim only; it says nothing about observation utility or profit.
Labels: SOURCED = quoted from the saved source (file:line); OURS = our choice, bounded below; PINE-UNVERIFIED = what the Pine runtime did, not readable from the source.

## 1. Source pin (saved source, no blocker)
| File (this folder, `source_snapshot/`) | Origin | Read |
|---|---|---|
| `WT_Crosses_lonestar108_jFQn4jYZ.pine.txt` (sha256 25d5f18a459225fb...) | `https://www.tradingview.com/v/jFQn4jYZ/` page JSON `script.content` (script id 2295), page title "WaveTrend with Crosses [LazyBear]", user lonestar108, created 2016-02-20, `access:1`, `script_terms:""`, Pine `study()` | 2026-10-17, raw page JSON, not a summary |
| `LB_WaveTrend_marketcalls_gist.pine.txt` (sha256 839bba8a402ec5d7...) | gist.githubusercontent.com/marketcalls/f9c795c7d5ba0f988761/raw (plain WaveTrend, no cross markers) | 2026-10-17 |

- **Version answer.** The Crosses script is not a different oscillator. Line diff of the two files: only the title, plot styles and three added lines (cross markers `cross(wt1, wt2) ? wt2 : na` and `barcolor(...)`, Crosses:32-34). The math (Crosses:14-21) is identical to the gist. Both carry the header `@author LazyBear`. So "the layer" = LazyBear's oscillator; the marker fires on ANY-direction `cross()`, sits at wt2; direction is `wt2 - wt1 > 0` = down-cross (red/aqua), else up-cross (lime/yellow), Crosses:33-34.
- **Attribution / terms.** Header (both files, lines 1-4): "@author LazyBear ... If you use this code in its original/modified form, do drop me a note." No licence text, `script_terms` empty, open-source access. The Crosses copy is a republication by lonestar108 crediting LazyBear. Position: we re-implement the published formula (three EMAs and an SMA) from scratch, copy no Pine text into the module, cite both sources and credit LazyBear in the module docstring. The "drop me a note" courtesy cannot be actioned by us and is not a licence condition; logged as a known open courtesy, not a blocker.
- The 2014 original page (`2KE8wTuF`) carries no parameters (CLAUDE_VERIFY section A); the numbers below come from the code files.
- Fix E5 (CLAUDE_VERIFY): `0.015` and `d = EMA(|ap-esa|, n1)` are now pinned at Crosses:16-17 and gist:16-17.

## 2. Formula (SOURCED, Crosses:14-21 = gist:14-21)
`ap=(h+l+c)/3; esa=EMA(ap,10); d=EMA(|ap-esa|,10); ci=(ap-esa)/(0.015*d); wt1=EMA(ci,21); wt2=SMA(wt1,4)`; bands 60/53 and -60/-53 (:9-12), centre 0 (:23). The module's FORMULAS.md entry must copy these lines and cite file:line (done by card wavetrend-observation-module).

## 3. Conventions the source does not state (reference: `wt_parity_ref.py`, checks: `test_wt_parity_ref.py`)
| Topic | Source says | Contract (label) | Evidence |
|---|---|---|---|
| EMA seed | nothing (runtime) | Seed with the first source value; **output is used only after WARMUP = 200 bars from series start or from any gap (OURS)**. The ER-07 note "Pine: first source value" stays PINE-UNVERIFIED and is not needed | 1,500 synthetic bars: first-value seed vs SMA seed differ by < 1e-3 WT points (OURS threshold) after bar 144 (measured) (printed by the test); 200 leaves margin, so the seed choice cannot affect any event after warm-up |
| d = 0 (flat window) | nothing | `ci = NaN` when d <= 1e-9*abs(ap) (OURS tolerance: float EMA of a flat price leaves ~1e-14, not exact 0), propagates to wt1, wt2: **no event** (OURS, fail closed). Never 0, never inf | test 1 |
| wt2 warm-up | SMA(4), :21 | wt2 NaN until 4 valid wt1; no cross unless wt1 and wt2 are defined at t and t-1 | ref `sma` |
| Cross equality | `cross()`, strictness in the runtime (PINE-UNVERIFIED) | **"le" (OURS): an event fires at the first bar strictly on the opposite side of the last strict side.** A tie bar is skipped; tie then move away counts once; above-tie-above is NOT a cross. "strict" (both t-1 and t strictly opposite) would drop crosses through a tie bar; they differ only on exact float ties. (Review fix: the earlier "prev<=" wording fired on touch-and-bounce.) The atlas reports the tie-event count as a data-quality line | test 3 |
| Missing bar / NaN | nothing | bar is NaN, EMA state dropped, no bridging; module also suppresses output for WARMUP bars after a gap (OURS) | test 5 |
| Look-ahead | n/a | value and event at bar t use bars <= t only (cross uses t and t-1) | test 4 plants a future spike |
| Open bar | TradingView can show a cross on the forming bar | **Closed bars only.** `available_at = bar_open_time + timeframe`; earliest executable price = next bar open. A fixture row without both timestamps is invalid | TradingView repainting doc (METHOD_AND_MTS.md) |
| HTF value | n/a | for a bar at time t, HTF WT = value of the last HTF bar whose close time <= t (OURS) | |

**Golden-fixture rule for the module card.** Expected numbers come from a spreadsheet implementation of the FORMULAS.md entry run on one real dated BTCUSDT 1h sequence of >= 300 bars (compare to 1e-9 (OURS tolerance) after bar 200 (WARMUP); the 300-bar minimum is OURS), plus ideally a TradingView export of WT_CROSS_LB for the same bars. With no chart export the report must say "spreadsheet parity, not Pine-runtime parity". `wt_parity_ref.py` is NOT a golden source (same author as the module; a Python self-comparison does not count).

## 4. Module path (one chosen)
`MyTradingSys/backtest/layers/wavetrend/` (T061 plan). `layers/momentum/wavetrend.py` (T065) is dropped. Observation-only: emits wt1, wt2, zone tag, cross events with `available_at`; no side, no routing, no Tom/Fabio gate.

## 5. Policy reconciliation (default taken, logged)
Control-room text "no new layers while Tom/Fabio are redefined" is superseded by the operator's 2026-10-17 priority request, in bounded form: source + count-only + one DEV study, no live path, no Tom/Fabio dependency (CLAUDE.md layers rule, 2026-10-13). T061's 70/30 split and 0.10% round-trip are obsolete; use the repo split (DEV <= 2024-06-30, VALIDATION 2024-07-01..2025-06-30, HOLDOUT from 2025-07-01) and actual venue costs at the event-study stage.

## 6. Three separate claims
1. Source parity: this document plus the module card. 2. Observation utility: ATLAS_STUDY_SPEC.md. 3. Strategy efficacy: not claimed; no net BTC edge is known.
