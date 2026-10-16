# Layer readiness for testnet trading - census 2026-10-16

Scope: every layer family in `system/LAYERS.md` except tom, fabio, guidance. Read-only census of origin/fast-track at `3b6ad9af`
(2026-10-16). No code, config, process or secret was touched. Testnet only; trading here is a calibration/data source, NOT a claim of edge
(every in-scope backtest verdict is FAIL, NO EDGE, INCONCLUSIVE or unrun - see column "Best verdict").

Result: 9 layers TRADES / 4 need wiring / 8 need builds.

## How the live path decides (verified in code)

- Detectors live in the registry `live_runner_cli.build_default_registry` (`MyTradingSys/backtest/layers/alerts/live_runner_cli.py:333-413`),
  adapters in `alerts/live_layers.py` (side per event). Registry key = `layer:<layer>:<sub>:<tf>`.
- `poll_once` runs `apply_promotion_gate` (`live_runner_cli.py:434-435`): a `shadow` registry entry strips the side -> collection-only.
- `auto_trader.layer_signal` (`execution/auto_trader.py:399-448`) rejects: no side, `collection_only`, then `promotion_reject`
  (default-deny, commit `8254ece6`): a source trades only with a `promoted_setups.json` entry (it ships EMPTY, `entries: []`) or a
  prefix in `pre_pipeline_sources` (prefix match, `promotion/registry.py:80-91`). Then size from the longest `size_overrides` prefix, else the
  `layers` default (100 USD / 10 max loss).
- `trade_blocklist` is `[]`; `trade_blocklist_parked` (session_momentum, funding_cvd_fade, turn_of_candle, fabio escalation,
  rsi 15m) is a parking lot and blocks nothing (`auto_trader_config.json`, `_calibration`). So "parked" layers do trade.
- Empirical check (live mirror `auto_trades.jsonl` tail of 500 rows, mirror stamp 2026-10-16T09:11Z): trade_attempt/trade_closed seen
  for rsi 5m/15m/1h, session_momentum 15m, funding_cvd_fade 1h, cryptocred sr_flip 15m + fib_pullback 15m, turn_of_candle 1m (73 attempts).
  Not in that tail (rare events; config says they may trade): malkan_bull/bear, failed_msb, sr_flip/fib 1h. Many `skipped_halt` rows
  (e.g. turn_of_candle 97) show the testnet HALT was active for part of that window.

## 2026-10-16 live-path fixes: which apply to the in-scope layers

| Fix | Commit | Applies to |
|---|---|---|
| Promotion gate default-deny | `8254ece6` (+ `644ca8b6` demote/verify) | every layer signal via `auto_trader.promotion_reject`; all 9 TRADES layers pass only through `pre_pipeline_sources` |
| Deribit 10041 settlement_in_progress = skip plan, no HALT | `b0cb201e` (`execution/executor.py`) | all layers (shared executor) |
| Orderflow writer stall guard | `539a7c85` (`backtest/layers/fabio/orderflow_live.py`) | only layers reading order-flow bars (Fabio v3, excluded). In-scope layers run on plain klines (`tbv` column); none depends on it |
| Live-loop one-owner guard | `ce7e74ad`, `5c3b440e` (`scripts/dev/live_owner.py`, mts.ps1, loop-supervisor) | whole live loop, all layers |
| Deploy allowlist | NOT FOUND on origin/fast-track. Q75 auto_deploy hardening is claimed by JIS-NB (claim `q75-auto-deploy-hardening`). Landed and related: `3c7dcf86` (stale-green fallback needs green CI), `9942c7b9` (gate timeout), `dc807bf8` | not touched here. DECISION (OURS): treat as not landed, no dependency on it; wiring ships through ordinary ship -> CI -> AutoDeploy |

## Census table

State: TRADES = detector live, side mapped, passes the gate through a grandfather prefix. COLLECTION-ONLY = detector live but emits no side.
NOT-WIRED = no detector in the live registry. "Parked" = on the non-blocking parked list.

| # | Layer (family) | Live detector (file:line) | State | Account / size (USD, max loss) | Best verdict | Open cards (state) |
|---|---|---|---|---|---|---|
| 1 | rsi_events 5m/15m/1h (rsi) | `live_layers.py:146` rsi_level_layer, registry `live_runner_cli.py:345-363`; side only on `failure`, plus `layer_rules` rsi:support/rejection/cross | TRADES (15m parked, not blocked) | jishu_2/3/4; 50/2, 100/3, 250/5 | L1-D3 mixed: 1h support PBO 0.030, rest PBO 0.39-0.91 (`BACKTEST_L1_REPORT.md`) | malkan-home-fit-audit (refined) |
| 2 | malkan_bull 1h (rsi) | `live_layers.py:111`, registry `live_runner_cli.py:387` | TRADES via `layer:rsi:malkan_` | jishu_7; 500/10 | no dedicated backtest row; Kurisko spec only | malkan-captions-fetch-noauth (ready), malkan-hindi-rows-gpt-read (ready), malkan-home-fit-audit (refined) |
| 3 | malkan_bear 1h (rsi) | `live_layers.py:117`, `live_runner_cli.py:388` | TRADES via `layer:rsi:malkan_` | jishu_8; 500/10 | same as 2 | same as 2 |
| 4 | cryptocred sr_flip 15m/1h | `live_layers.py:139`, `live_runner_cli.py:389,396` | TRADES | jishu_16/17; 200/4, 600/12 | FAIL after trade-through rerun; stop buffer unsourced (B143); his TF (1d/4h) untested | cryptocred-home-fit-audit (refined) |
| 5 | cryptocred fib_pullback 15m/1h | `live_layers.py:140`, `live_runner_cli.py:390,397` | TRADES | jishu_18/19; 350/7, 800/16 | same as 4 | same as 4 |
| 6 | cryptocred failed_msb 15m/1h | `live_layers.py:141`, `live_runner_cli.py:391,398` | TRADES via `layer:cryptocred:`; no own size_override, so layers default 100/10 | jishu_20 | same as 4 | same as 4 |
| 7 | funding_cvd_fade 1h (positioning) | `live_layers.py:88`, `live_runner_cli.py:386` | TRADES (parked, not blocked) | jishu_10; 750/15 | T055-C1 FAIL, OOS net -0.0453 %, closed | positioning-home-fit-audit (refined) |
| 8 | session_momentum 15m (session_timing) | `live_layers.py:68`, `live_runner_cli.py:385` | TRADES (parked, not blocked) | jishu_9; 150/3 | T055-C2 FAIL, closed | eu-low-us-sweep-follow-ups (raw) |
| 9 | turn_of_candle 1m (session_timing) | `live_layers.py:169`, `live_runner_cli.py:392` | TRADES (parked, not blocked); `sampling: True` | jishu_1; 20/2 | T055-C3 NO EDGE (gross about 0; 12 bp cost) | none |
| 10 | wlow_bounce bbrsi60 1h (volume_candles_ma) | `live_runner_cli.py:259-330` make_wlow_bounce_layer, registry `:406`; emits `shadow_side` + `collection_only` | COLLECTION-ONLY | none (would fall to jishu_21) | wlow_bounce_bbrsi60_2026-10-16 INCONCLUSIVE, n=8 DEV, gross -0.293 % | none |
| 11 | rsi_divergence (rsi) | none; pure fn `rsi/rsi_divergence.py:32` | NOT-WIRED (needs wiring) | - | RSI-DIV-MTF FAIL: 31 of 32 net negative, no TF edge | none |
| 12 | session_levels (session_timing) | none; pure fn `session_levels/session_levels.py:82` failed_break_events | NOT-WIRED (needs wiring) | - | T087 no edge, net -0.036 %, t -1.72; EUR-low/US-sweep FAIL | eu-low-us-sweep-follow-ups (raw) |
| 13 | bigtrade_fires (volume_candles_ma) | none; `backtest/bigtrade/fires_kline.py:106` kline_registry (bar-function shape unverified) | NO-SOURCE (build blocked; spec BIGTRADE_SPEC.md 2026-10-16) | - | FIRES-B1 parity PASS; BIGTRADE-EXIT first row negative both splits; HOLDOUT unread | none |
| 14 | bb_top_reversal 15m (volume_candles_ma) | none | NOT-WIRED (needs build) | - | unrun | bb-top-reversal-candle-backtest (raw) |
| 15 | candle_close (volume_candles_ma, lab) | none; lab `research/layer_lab/candle_close_2026-10-14/study.py` | NOT-WIRED (needs build) | - | 0 of 126 arms pass the exploratory screen | candle-close-phase-encounter-design (blocked), candle-close-test-import-guard (blocked) |
| 16 | levels confluence lc-* (no family row in LAYERS.md) | none; `research/levels_confluence_2026-10-14/levels.py`, `event_table.py` | NOT-WIRED (needs build) | - | LC1 levels_hold KEEP for 8 level families (prior_day_high/low/poc, naked_poc, 4h fractals, round_1000, prior_week_high); LC-SIZING-QUICK negative; Qriptal imbalance filter FAIL; context composite INCONCLUSIVE | lc-ladder-dev (raw), lc-validation (raw), context-composite-v2-dev-read (ready) |
| 17 | oi_delta / whale (positioning) | none | NOT-WIRED (needs build) | - | OI-DELTA descriptive only; OI divergence / event studies show no edge | positioning-home-fit-audit (refined) |
| 18 | volume + candle_patterns | none | NOT-WIRED (needs build) | - | VOLUME no validated edge, HOLDOUT sealed; CANDLE-P1 1d engulfing FAIL; 0/108 cells | time-adjusted-volume-context-line (raw) |
| 19 | ma_daily | none | NOT-WIRED (needs build) | - | NO-SOURCE (chatbot handoff numbers); provenance rule bars it | none |
| 20 | callers / Qriptal | none | NOT-WIRED (needs build) | - | scorecard n = 0 on DEV (`qriptal_2026-10-10/SCORECARD.md`); his 67.1 % wins claim unverified | none open |
| 21 | krown | none | NOT-WIRED (needs build) | - | not built, not backtested; spec v0.2 | krown-layer-v0-detectors (blocked), krown-recall-check (blocked), krown-dev-event-study (blocked), krown-ta101-extract-remaining-10 (ready), krown-catalogue-gpt-audit (ready) |

Totals: rows 1-9 TRADES (9). Wiring (detector exists, adapter or side missing): rows 10-13 (4). Builds: rows 14-21 (8).

## Findings that change the plan

1. Nine layers already trade; nothing is needed to "enable" them. Their exposure is the `pre_pipeline_sources` grandfather list
   (every entry `review_by 2026-10-23`, not enforced, expiry does not halt trading). DECISION (OURS): leave all entries as they are; pruning is the operator's.
2. Account scarcity: only `jishu_22` is spare. A new layer with no account prefix falls to the catch-all `layer:` -> `jishu_21`, so all
   new layers share one position slot (one position per account; `skipped_busy`). DECISION (OURS): new layers share `jishu_21`
   (collisions cost fills, not safety). More sub-accounts need secrets and are out of scope.
3. A new layer wired only through `layer_rules` / `size_overrides` / `accounts` cannot trade: it needs a `pre_pipeline_sources` entry (or a
   registry entry via `promote.py`, which no in-scope layer can pass, since none has a PASS verdict). So every wave ends with a grandfather
   entry. DECISION (OURS): the final wiring worker adds each new prefix with reason "grandfathered testnet calibration, operator decision
   pending" and `review_by 2026-10-23`, the existing pattern, flagged for the operator to prune.
4. Provenance rule: a detector parameter without a transcript quote + file:line is NO-SOURCE. Adapters for rows 11-13 must reuse the
   parameters of the backtest that produced the verdict and label the bracket SAMPLING (as layers already do); ma_daily (row 19) is
   blocked by this rule.

## Per-layer step list (testnet as calibration)

**Rows 1-9 (TRADES): no steps.** Optional hygiene, no operator decision: add a `size_overrides` entry for `layer:cryptocred:failed_msb:`
(today the 100/10 default, 5-10x the sr_flip entries); folded into the final wiring worker.

**Row 10 wlow_bounce** (wiring, 2 steps, operator decision on step 2):
1. Code (final wiring worker, owns `live_runner_cli.py`): in `make_wlow_bounce_layer` (`:259-330`) emit `side: "long"` and drop `collection_only`
   behind a flag; keep the forward log row. Test: stays side-less with the flag off.
2. Config: `pre_pipeline_sources["layer:wlow_bounce:"]`, `size_overrides["layer:wlow_bounce:"]` (OURS 20/2), no account line (shares jishu_21).
   Operator decision: INCONCLUSIVE n=8, so the grandfather entry is the operator's. DECISION (OURS): keep COLLECTION-ONLY unless the
   coordinator accepts the entry; the step 1 code is safe either way.

**Row 11 rsi_divergence** (wiring, 3 steps, code only): (1) new `alerts/live_rsi_divergence.py` adapter fn(bars) calling
`rsi_divergence(close, rsi, ts, min_bars, max_bars, kind)` (`rsi/rsi_divergence.py:32`), bullish -> long, bearish -> short, params from
`rsi/run_divergence_mtf.py`; (2) its own `test_live_rsi_divergence.py`, failing on pre-change code; (3) registry line + grandfather via the final wiring
worker. TF: 1h first (4h/6h had n 6-54).

**Row 12 session_levels** (wiring, 3 steps, code only): (1) new `alerts/live_session_levels.py` wrapping `failed_break_events(bars, side)`
(`session_levels/session_levels.py:82`), prior-day-high fade short and low fade long; (2) test; (3) registry + grandfather.

**Row 13 bigtrade_fires** (wiring, 4 steps, code only): (1) confirm the bar-function shape of `fires_kline.kline_registry` (`fires_kline.py:106`);
(2) new `alerts/live_bigtrade.py` adapter; (3) test; (4) registry + grandfather. If (1) shows it is not a pure fn(bars), reclassify as build.

**Row 14 bb_top_reversal** (build, 4 steps): card `bb-top-reversal-candle-backtest` is raw (operator rule 2026-10-14). (1) pure detector
`alerts/live_bb_top_reversal.py` (15m top-reversal candle at the upper BB(20,2), short); (2) test with expected values from FORMULAS.md;
(3) adapter in the same file; (4) registry + grandfather. The backtest card stays separate.

**Row 15 candle_close** (build, 4 steps): reuse the lab study's close sequences (`candle_close_2026-10-14/study.py`) as a causal fn(bars) on 1m in
`alerts/live_candle_close.py`; test; registry + grandfather. DECISION (OURS): 0 of 126 arms passed, so trade only the lab's top arm per side,
labelled SAMPLING. The blocked cards (import guard, encounter design) are research-side and not prerequisites.

**Row 16 lc-* levels confluence** (build, 6 steps; Q79 touch-bar fix landed `e6a3b0be`): (1) pure point-in-time level builder from `levels.py` for the 8
KEEP families; (2) touch-hold event detector; (3) side from hold direction; (4) test against the `levels_hold.md` counts; (5) adapter;
(6) registry + grandfather. Do not wait for lc-ladder-dev / lc-validation (research-side). Read-only on `research/pit_levels_2026-10-16/`
(JIS-NB territory).

**Rows 17-21** (oi_delta / whale, volume + candle_patterns, ma_daily, Qriptal, krown): deferred. oi_delta needs an OI feed in the live runner;
volume and candle_patterns have no directional event definition; ma_daily is NO-SOURCE; Qriptal has n = 0 scored calls and needs a manual call feed plus an
operator ruling; krown is spec-only with its cards blocked and a pending ruling on "no resting stop". DECISION (OURS): reported, not forced.

## Rank by fewest steps to testnet

1. Rows 1-9: 0 steps (already trading).
2. wlow_bounce: 2 steps (1 operator decision).
3. rsi_divergence, session_levels: 3 steps each.
4. bigtrade_fires, bb_top_reversal, candle_close: 4 steps each.
5. lc-* levels: 6 steps.
6. Deferred: oi_delta / whale, volume + candle_patterns, ma_daily, Qriptal, krown.

## Waves (at most 2 layers per worker; disjoint files; config last)

Every worker brief repeats the CLAUDE.md live-path rules: no in-place edit of a file the running system imports, no stop/restart of
live processes, no HALT-file or open-trade changes, tests for restart/reset state, non-trade balance moves and API errors, fail closed.
Each adapter lives in its OWN new module + test file, so wave 1-2 workers touch none of `live_layers.py`, `live_runner_cli.py` or
`auto_trader_config.json`. Those, plus `wiring_registry.json`, are owned by the single final wiring worker.

| Wave | Worker | Layers | Files (create only) |
|---|---|---|---|
| 1 | W1a | rsi_divergence, session_levels | `alerts/live_rsi_divergence.py`, `alerts/live_session_levels.py`, two `test_live_*.py` |
| 1 | W1b | bb_top_reversal, candle_close | `alerts/live_bb_top_reversal.py`, `alerts/live_candle_close.py`, two tests |
| 2 | W2a | lc-* levels | `alerts/live_levels_confluence.py` + test |
| 2 | W2b | bigtrade_fires | `alerts/live_bigtrade.py` + test |
| 3 (final) | W3 wiring | all of the above + wlow_bounce side + failed_msb size | `alerts/live_runner_cli.py` (registry entries, wlow side), `execution/auto_trader_config.json` (size_overrides, pre_pipeline_sources; accounts unchanged, share jishu_21), `system/wiring_registry.json`, `scripts/dev/alert_rate_check.py` TF/family maps |

Waves 1 and 2 can run in parallel (disjoint files); W3 starts after they have shipped. W3 greps every TF/family map (CLAUDE.md rule for adding a
layer family), runs `run_all_tests.py`, ships, and CI + AutoDeploy carry it. Only the supervisor restarts the live runner, after the commit is gated and deployed.
