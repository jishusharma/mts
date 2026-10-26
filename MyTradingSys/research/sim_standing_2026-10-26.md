# Simulator stand-up brief, 2026-10-26

Operator asked: where is the MTS Simulator today, what was done and why, what is the
roadmap, and does it match the current state of the art. Verified on disk at trunk
`origin/fast-track` CI green `ec00608e` (STATUS.md 2026-10-26 04:31). Plain words; no
internal names without a gloss.

## 1. Where the simulator stands today

What is shipped on trunk (CI green at `ec00608e`, verified by `git log` and the files
above, not memory):

- **Desk v1** `ab5f42d1e` — one local page: settings, Run, verdict, 3 numbers, 6 example
  trade charts, trial ledger, DEV-only date lock. The Levels study is plugged in.
- **Levels review fixes** `46c596a40` → `3c262f8b3` — after the Fable review found
  517 of 772 "trades" never actually filled; now counts filled trades only (255),
  sample-spread verdict, UTC-dated charts.
- **Plug-in seam + Questions panel** `5f2c69939` — a new layer is one file in
  `studies/`; no edit to `desk.py` or the page.
- **RSI and WaveTrend studies** `2b80ef52b` — two more bar-based layers on the desk
  (`studies/rsi.py`, `studies/wavetrend.py`); see `PLUGIN.md` for the contract.
- **LC3 ladder simulator** `da096725e` / `0b2ab1b61` — the 240-variant DEV run of
  pre-registered arms shipped on 2026-10-21; the desk's frozen rule
  E1 S2 K5 X0_2R reproduces this exact result (INPUTS.md §3, verified by
  `test_reference.py` `0fc67ac06`).
- **sim-v2 batch 1 + overnight a–e** (2026-10-25) — see `HANDOVER_SIMV2.md`: levels
  filled-trades bug, result schema, `export_results.py`, catalogue (151 rows),
  static builder, reference tests, CONDITIONS panel, run-time display, scrubbable
  equity curve, `results/desk-<study>-<hash>.json` per Run.
- **sim-v2 Fable items** — numbers strip `bba212e80`; slippage box `1282d9c21` (shipped,
  **reverted** `cceaedf7b` on CI red for T06 cost inventory, **re-landed**
  `11b8f95c4` with the 3 costs.csv rows); drawdown shading `b99094841`; clickable
  trade list `2f2954f6e`; Monte Carlo reshuffle band + luck line `afd937964`.
- **One-command launcher** `80d63bacd` — `python desk.py` starts on a free port,
  opens the browser, prints the URL; study chips + DEV banner; saved-runs table with
  side-by-side of two runs (`runs_view.py`). Pre-revert smoke run `271ef8fc6` was
  **reverted** `e0a985ca2` because its result file broke `test_artifact`'s
  catalogue, making CI red.
- **Breakdown table + fold** `67426492d` — year / side / 4h-UTC-hour cells under
  each run, "too few trades" under 30; example charts and trial ledger folded
  behind toggles; every saved desk run always gets a catalogue row.
- **Krown study** `60f53e24c` / `1f6571e6c` / `2730ef09b` — S5/S8/S4, exploratory
  DEV-only, fee-net, ledger row; the planted-leak test was added without a
  forward-index pattern the lint would flag.
- **MTS Home wiring** `119aea4ec` — compact home page, dedupe, Sim Desk and
  CBP Analyst Desk now linked from the home page.
- **Planted-edge validation** (2026-10-20) — `MyTradingSys/backtest/
  test_sim_planted_edge.py`: 34 tests pass, no simulator defect found; the
  per-trade fee-net formula matches FORMULAS.md §18.5 exactly.

What is still open (not on trunk or not delivered):

- **ETH data not fetched.** `studies/_bars.py:39` already ships the symbol box
  (`BTCUSDT`/`ETHUSDT`), but `F:/MTS/data/tom_raw/klines` has no `ETHUSDT-1m-*.csv`
  files, so RSI/WaveTrend/Krown on ETH is wired but data-gated. R2 from
  `ROADMAP.md` (data breadth) is half-shipped: the code is there, the data fetch is
  not.
- **The lane-3 merge is stuck.** `research/sim_ideas_2026-10-26.md` asked
  Argon-medium, Astra-low and Fable for their top-3 sim-desk ideas each; the
  answers should land in `research/sim_ideas_raw/{argon,astra,fable}.md`.
  **All three raw files are missing on trunk** — Argon is queued on DSA-NUC,
  Astra on CODEX (card `sim-ideas-astra-low`, state=ready), Fable's session
  `local_33336c24` was not found. The ranked merge cannot happen until the
  files land.
- **Fable "what-was-tested" page contract** — card `5ea6032bf` closed 2026-10-26,
  but the **deliverable file `FABLE_TESTED_PAGE_CONTRACT.md` is missing from
  trunk** (`git cat-file -e` fails; `design_cards_2026-10-26/` has
  `FABLE_CONFLUENCE_MAP.md`, `FABLE_LAYER_REVIEW_RUBRIC.md`, `argon_*.md`, but
  not the tested-page contract). Re-filed as redo desk task `6ce0c39e6`.
  So `sim-dashboard-v1` (card `sim-dashboard-v1.json`, state=ready) still
  blocks on the file landing.
- **Argon lane answers** — `argon_sim_layer_coverage.md`
  (`0f9e76065`, shipped 2026-10-26): 13 layer families; 3 dedicated studies
  (rsi, krown, wavetrend), 2 partial via `studies/levels.py` (tom, fabio),
  8 NOT_IN_DATA. `argon_trials_by_layer.md`
  (`de4e0a2ca`, shipped 2026-10-26): 281 trial rows in TRIALS.md total —
  280 DEV, 1 VALIDATION, 0 HOLDOUT, 1 UNKNOWN; 28 mapped across 8 families,
  253 UNMAPPED. `argon_formulas_vs_bars.md` (FORMULAS.md vs
  sim_desk stats/fill drift audit, card `3bb24f9f6`) and
  `FABLE_CONFLUENCE_MAP.md`, `FABLE_LAYER_REVIEW_RUBRIC.md`,
  `FABLE_FEE_STOP_RULE.md` are also in `design_cards_2026-10-26/`.
- **`layer-review-after-simulator`** — PARKED 2026-10-26. The 13 layer
  sheets exist (`cb903f9d` LAYER_SHEETS.md); the integration map and
  confluence rule wait for the 26 lf-*-gemini-facts and lf-*-gpt-rederive
  fact sheets; operator's rule 2026-10-25: no layer dropped before it is
  seen in the simulator.
- **Handover "Next (small first)" items still open**
  (`HANDOVER_SIMV2.md`):
  - confirm the slippage default and the deflated-Sharpe luck form once
    `research/gemini_burn_2026-10-25/` files land (they are not on trunk);
  - Fable cards: breakdown table by family/condition with n; declutter
    page (Questions panel off, `mockup/` deleted, SIM_DESIGN_RESEARCH.md
    §2-5 cut); entry/exit reason columns in the trade list (run results
    do not carry them yet);
  - click-test `page.html` in a real browser (only node-sychecked so far);
  - layer-B condition uses default settings of the other study; typed
    settings are not wired.

## 2. What was done and why (file:commit, on disk)

| Change | Commit / file | Why |
|---|---|---|
| Desk v1 (levels study) | `ab5f42d1e`; `INPUTS.md` §1 | Operator asked for a one-screen, one-click simulator after the lc-ladder run; "very light, very precisely taken, so not cluttering." |
| Levels filled-only fix | `46c596a40` → `3c262f8b3` | Fable found 517 of 772 "trades" were never-filled ideas; the verdict was being computed on a model the zeros broke. Count fills only; 255 is the real n. |
| Plug-in seam | `5f2c69939`; `PLUGIN.md` | A new layer should be one file, not a rewrite of `desk.py` and the page. |
| RSI + WaveTrend | `2b80ef52b`; `studies/rsi.py`, `studies/wavetrend.py` | Both are bar-based (no Java pipeline) so they fit the plugin shape; the trader's daily 4h/1h charts are the trader's, the next-bar entry is OURS. |
| LC3 ladder + reference test | `da096725e`; `0fc67ac06` | A pre-registered frozen rule (E1 S2 K5 X0_2R) is the one known number the desk must reproduce; pin it with a test so refactors cannot silently break it. |
| CONDITIONS panel | `de7acbac6` | Operator's OVERRIDE item 2: side/UTC-hour/EMA/ATR/weekday filters on any layer, post-filter so a changed condition costs under a second. |
| Run-time display | `0337601f0` | Operator OVERRIDE item 3 (speed): a cached run should feel instant; show it. |
| Equity curve + A vs B | `533eab730` | Operator OVERRIDE item 4 (charts): a scrubbable R-and-$1,000 curve, side-by-side with another run. |
| Per-Run result file | `3ecd38c21` | Operator OVERRIDE item 6 (wired): every Run writes `results/desk-<study>-<hash>.json` so the catalogue and artifact page grow without code. |
| Standard numbers strip | `bba212e80` | Fable review item 2: win rate, PF, max DD and fee share were already in `stats`; expose them. |
| Slippage box | `1282d9c21` → `cceaedf7b` → `11b8f95c4` | Fable review item 3: the one real accuracy gap — stops were filling at the exact stop price. Add a 0.02 % OURS slippage on market/stop legs. Shipped, then CI red on the T06 cost inventory (3 missing costs.csv rows), reverted, re-landed with the rows. |
| Monte Carlo + luck line | `afd937964` | Fable review items 5 & 7: a 1,000-shuffle band on the equity curve and the "luck line" — the best of N no-edge rules reaches `sd * sqrt(2 ln N) / sqrt(n)` R. |
| One-command launcher | `80d63bacd`; `desk.py:4-7` | Operator: "one command, it opens." `python desk.py` picks a free port, opens the browser, prints the URL. |
| Breakdown table + fold | `67426492d` | Operator's "click-to-see-what-was-tested" ask: a year/side/4h-UTC-hour cell table under each run, with the 6 example charts and the trial ledger behind toggles. |
| Krown study | `60f53e24c`, `1f6571e6c`, `2730ef09b` | Krown TA-101 (S5 MA cross, S8 squeeze break, S4 coil break) is being re-derived as an exploratory layer; plug it in on DEV only, fee-net, with the "exploratory" label honest and the trade-construction test in place. The planted-leak test was written to avoid the forward-index pattern the lookahead lint would flag. |
| MTS Home wiring | `119aea4ec` | Sim Desk and CBP Analyst Desk are now reachable from the MTS Home compact page. |
| Planted-edge validation | `test_sim_planted_edge.py` | Prove the per-trade fee-net formula is correct by hand: 20/20 trades match a hand-built list; the planted-edge case recovers mean net R = 1.38 exactly; the fee-including null recovers the fee as negative R. No simulator defect found. |
| Argon coverage matrix | `0f9e76065`; `design_cards_2026-10-26/argon_sim_layer_coverage.md` | So the operator knows, per layer family, what the simulator can and cannot show, before the layer review. 13 families: 3 dedicated, 2 partial, 8 NOT_IN_DATA. |
| Argon ledger count | `de4e0a2ca`; `design_cards_2026-10-26/argon_trials_by_layer.md` | 281 TRIALS.md rows, 280 DEV, 1 VALIDATION, 0 HOLDOUT — the baseline number a future multiple-testing correction starts from. |
| Fable layer-review rubric | `dd3f311c1`; `design_cards_2026-10-26/FABLE_LAYER_REVIEW_RUBRIC.md` | 12-row per-layer evidence rubric so the layer-review cards have a common structure. |
| Fable tested-page contract | `5ea6032bf` (**file missing on trunk**); redo `6ce0c39e6` | The data-contract file for the "click-to-see-what-was-tested" page: per-record fields, which are NEW vs which already exist in the catalogue. Card closed but the `.md` did not land; re-filed as a desk task. |

## 3. The roadmap, as designed

From `ROADMAP.md` (2026-10-21, pre-sim-v2) + `HANDOVER_SIMV2.md`
(2026-10-25 "Next small first") + `sim_ideas_2026-10-26.md` (2026-10-26
lane-merge) + the 13 design cards in `ec00608e` (2026-10-26):

- **R2 (data breadth)** — ETH 1m for the DEV months; the symbol box is
  shipped in `_bars.py:39` but the data fetch is not. Until the data lands,
  RSI/WaveTrend/Krown on ETH are wired but data-gated. Goal: 2× to 3× the
  trades per idea without touching the sealed windows.
- **R3 (second layer decision)** — CryptoCred wrapper (`cc_bt_adapter.py`
  already converts signals to trades) or the Tom v2 wrapper once v2 rules
  are written. Default: nothing new plugged until the operator picks; the
  13-family coverage matrix (`0f9e76065`) is the decision input.
- **R4 (validation run)** — once, for any idea that PASSES on DEV with
  the wider data; Fabio order-flow only after a DEV-like order-flow window
  exists (the order-flow bars start 2024-12-02, after the DEV window ends).
- **R5 (dashboard polish)** — the "click-to-see-what-was-tested" one-screen
  page (card `sim-dashboard-v1`, prerequisite the Fable tested-page
  contract `5ea6032bf`), only after R2 shows the desk gets used.
- **2026-10-26 lane merge** — when Argon, Astra and Fable each land their
  `sim_ideas_raw/*.md` files, the ranked merge goes into
  `sim_ideas_2026-10-26.md`. Each lane was asked for the ONE thing to add
  or improve, cost S/M/L, which layer family it helps. Nothing is
  demoted or dropped by any idea.
- **Layer-review-after-simulator pipeline** — the 13 cards in `ec00608e`
  form a facts → audit → coverage → contract → integration map:
  Argon-medium produces the coverage matrix and ledger count; Astra-low
  produces the sealed-window guard challenge, trials-multiplicity bar,
  formulas-vs-bars drift, and levels fee-drag recompute; Fable produces
  the confluence integration map, the evidence rubric, the tested-page
  contract, and the fee-vs-stop rule note. The 26 fact sheets
  (`lf-*-gemini-facts` and `lf-*-gpt-rederive`, one per layer family) are
  the precondition for the parked `layer-review-after-simulator` card.
- **Handover open items** (`HANDOVER_SIMV2.md` §"Next"): confirm the
  slippage default and the luck-line form once the Gemini burn files land;
  breakdown table by family/condition with n; declutter page (Questions
  panel off, `mockup/` deleted, SIM_DESIGN_RESEARCH.md §2-5 cut);
  entry/exit reason columns in the trade list (the run result does not
  carry them yet); click-test `page.html` in a real browser; layer-B
  condition typed settings.

## 4. Does the roadmap match the 2026 state of the art?

Two 2026 sources verified by fetch this session (labeled
`NOT_IN_DATA` — they are not in the repo):

1. [arXiv 2512.12924 — Walk-Forward Validation Framework
   (Dec 2025, 34 OOS folds, 2015-2024, 100 US equities)](https://arxiv.org/html/2512.12924v1)
   `NOT_IN_DATA`
2. [Backtrex Walk-Forward Optimization for Backtesting — The Complete
   2026 Guide](https://backtrex.com/en/blog/walk-forward-optimization-backtesting-guide)
   `NOT_IN_DATA`

| Practice (2026 SOTA) | Desk has today | Roadmap covers it? | Gap |
|---|---|---|---|
| Fixed DEV/VALIDATION/HOLDOUT split, sealed windows, read-once VALIDATION | **HAS** (better than most retail tools) | Roadmap keeps it; R4 is the one validation read | No gap; the desk is ahead here. |
| Multiple re-optimization cycles (walk-forward rolling/anchored) | **NOT_IN_DATA** — explicitly *not* planned | `ROADMAP.md` says "do not build walk-forward; 27 months is too short to roll" | With the 27-month DEV window, a rolling walk-forward would give at most 2–3 independent cycles; the arXiv source wants ≥5, the backtrex source wants 8–15. The desk's answer — a sealed VALIDATION read-once — is the right substitute given the data constraint; this is not a gap to close, it is a documented trade-off. Label it OURS (roadmap decision) not NOT_IN_DATA. |
| Monte Carlo trade reshuffle (5–95 % band on the equity curve) | **HAS** (`afd937964`, 1,000 fixed-seed shuffles) | In the shipped sim-v2 | No gap. |
| Trial-counted verdict / "try #N" on the verdict bar | **HAS** (TRIALS.md row per new setting; footer counter) | In the shipped v1 | No gap. This is the desk's differentiator. |
| Deflated / trial-adjusted Sharpe (Bailey & López de Prado 2014) | **PARTLY** — the "luck line" `sd * sqrt(2 ln N) / sqrt(n)` is the *scalar level* luck reaches as the best of N no-edge rules; it is the same formula family as the DSR but is **not** the full DSR z-test (no Sharpe-ratio normalization, no significance threshold) | Roadmap item: "confirm the deflated-Sharpe luck form once the Gemini files land" | The desk shows the luck level, not the DSR p-value. The arXiv 2025 source explicitly does NOT apply a multiple-testing correction ("to report transparent limitations"); the desk is *ahead* of that paper in practice. The gap is small: the desk's verdict already uses the 95 % day-bootstrap range, which is the honest cousin of a permutation p-value. Recommend: keep the scalar luck line, add a one-line note that it is the DSR's numerator not the denominator, and do not build a full DSR test unless the Gemini files say the operator wants one. |
| Slippage modeling (≥ 5 bps on BTC is the 2026 retail default) | **HAS** but **0.02 % = 2 bps, on the optimistic side** | Shipped `1282d9c21`/`11b8f95c4`; confirmed default still open | The 2026 backtrex source defaults to 5 bps on BTC. The desk's 2 bps is at the low end — defensible if the fills are maker on entry and the stop is the only taker leg, but the operator should see a "slippage default: 2 bps (ours, below the 5 bps retail 2026 default)" label on the page. |
| Regime-aware / rolling re-fit | **NOT_IN_DATA** | Not in roadmap; explicitly out of scope (see walk-forward row) | Same trade-off as walk-forward: the 27-month window is too short to regime-roll; the desk's answer is to use the sealed VALIDATION window for the one read. This is documented, not a gap. |
| Per-trade fee-net formula independent of the live engine | **HAS** — `test_sim_planted_edge.py`: 34 tests, 20/20 hand-built match, no defect | In the planted-edge validation shipped 2026-10-20 | No gap; the desk's fee model is independently verified. |
| "Click-to-see-what-was-tested" page (operator's ask) | **PARTLY** — `sim-dashboard-v1` card is ready; the prerequisite (Fable tested-page contract `5ea6032bf`) is missing from trunk and re-filed as `6ce0c39e6` | In the roadmap (R5) | One file away: when the redo desk task ships `FABLE_TESTED_PAGE_CONTRACT.md` to trunk, `sim-dashboard-v1` can start. The card is data-gated, not design-gated. |
| Plain-words verdict (PASSED / FAILED / NOT ENOUGH DATA with a 95 % range) | **HAS** — better than most retail tooling (backtrex: "judge by the concatenated OOS curve, not IS") | In the shipped v1 | No gap; this is ahead of retail practice. |

**Conclusion.** The roadmap is correctly designed for the data constraint
(27 months, one asset, sealed split). Where the desk is *ahead* of the
2026 SOTA: the trial ledger with "try #N," the plain-words verdict with a
range, the independent planted-edge formula check, and the sealed
VALIDATION/HOLDOUT read-once discipline. Where it is *behind* the 2026
SOTA, by a small amount: the slippage default is 2 bps vs the 5 bps
retail default, and the "luck line" is the DSR numerator not the full
z-test. Neither requires a roadmap change; both are a one-line label on
the page and a confirmation when the Gemini files land. The
walk-forward / rolling re-fit gap is a data constraint, not a design
gap, and the roadmap documents it correctly.

Sources (web, NOT_IN_DATA):
- arXiv 2512.12924 (Dec 2025): walk-forward validation framework, 34
  OOS folds, strict information-set discipline, reports a 0.55 %
  annualized OOS with p = 0.34.
- Backtrex (2026 guide): IS:OOS 3:1 default (12 mo : 4 mo → 11 cycles over
  5 yr), rolling for regime-sensitive short-term strategies, anchored for
  long-horizon; WFE = annualized OOS / annualized IS; 0.50 minimum
  confidence threshold.
