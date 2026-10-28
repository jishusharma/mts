# MTS Critical-Gap Audit, Revalidation & End-to-End Roadmap (2026-10-19)

- **Producer:** Antigravity Builder Session (`surface=GEM`, `host=JIS-NUC`), branch `jis-nuc/gemini-mts-gap-audit`
- **Review Status:** `REVIEWED:2026-10-19 T0-ONLY` (Strict `Producer != Reviewer`: Producer is Antigravity; shipped to `origin/fast-track` for independent Claude review).
- **Scope:** Critical-only gaps across Live Trading & Execution Safety, Backtest / Lab Statistical Integrity, CI/CD & Gate Architecture, and Multi-Agent Workflow & Process Economics.

---

## Executive Summary: Top 8 Critical Gaps Ranked by Value & Risk

| Rank | ID | Domain | Severity | Title | Core Value / Payoff |
|---|---|---|---|---|---|
| **1** | **GAP-1** | Backtest / Live Capital | **CRITICAL** | **Zero Validated Fee-Net OOS Edges vs. 27 Grandfathered Live Calibration Sources Expiring 2026-10-23** | **Risk / Capital Protection:** Prevents deploying real capital on unvalidated edges (`promoted_setups.json` has `0` entries; all 22 `layer_map.json` layers have `0` OOS PASS; Q76/B187 PIT study is ~1,220 days short of power gate). |
| **2** | **GAP-2** | Live Path / Data Integrity | **CRITICAL** | **`StateCodeEmitter.java` Unbackfilled Session CVD (-367.4 BTC error) & VWAP (26.8% missing volume) on Restart/Reconnect + `vwap_anchor_utc` Future-Timestamp Bug** | **Defect Removal:** Fixes corrupted live 5-signal state vote (`state_code.json` letters `A..`) after any JVM restart or WebSocket drop (`StateCodeEmitter.java:177-189, 454-479`). |
| **3** | **GAP-3** | Live Path / Mainnet Gate | **HIGH** | **Mainnet PnL & Daily Loss Monitor Gaps: Unverified `settlement`/`funding` on Real Capture (L6/B149) + Subaccount Aggregate Blindness on Mainnet (`daily_loss_monitor.py:510`)** | **Safety / Defect Removal:** Ensures `daily_loss_monitor.py` cannot under-count daily loss or mis-book 08:00 UTC settlement/funding before mainnet cutover. |
| **4** | **GAP-4** | CI/CD & Ship Gate | **HIGH** | **Fast Ship Gate (`--fast`) Skips `3dl` (`ci_deps_lint.py`), Drops Deferred Tests Silently, and Starves Per-Clone Gate Slots (`sv7-host-gate-budget`)** | **Performance & Reliability:** Eliminates 2–3 hour ship queues on 100% CPU hosts and prevents non-test helper imports from breaking `fast-track` CI (`run_all_tests.py:667,716-718`, `sync.py:183-187`). |
| **5** | **GAP-5** | Workflow & Process Economics | **HIGH** | **10 Zombie Open Task Cards (Already Delivered on `origin/fast-track`) + 6 Unshipped Completed `gemini-q/*` Branches** | **Economization:** Immediately saves **10 full builder/Codex/Gemini runs** (~5M–12M tokens and ~3–5 hours of compute) by reconciling cards whose code/tests already landed on `origin/fast-track`. |
| **6** | **GAP-6** | Workflow & Git Economics | **HIGH** | **59.8% Plumbing Commit Overhead (1,229 of 2,056 Commits in 72h are Claim/Release/Merge) + 12 Orphan Claims + 57 Unshipped Worktrees** | **Economization & Simplification:** Cuts git/CI churn by >50% and eliminates `refs/remotes/origin/fast-track` lock contention across 106 worktrees. |
| **7** | **GAP-7** | Multi-Machine Ops / Lab | **HIGH** | **Codex Layer Lab Stalled for 29.2 Hours (`15 ready` Cards, `6%` 5h Window Used) + Scheduled-Task Retirement Deadlock (`C2`/`C3`/`C7`)** | **Throughput Optimization:** Unlocks idle prepaid GPT/Codex capacity (94% of 5-hour window sitting unused) and 11 stalled `DSA-NB` audit rows (65h+ old). |
| **8** | **GAP-8** | Live Host Stability (JIS-NB) | **HIGH** | **Tracked Live-Host Generated Files Polluting `.mts_live` + Stale `.new` Files (174h old) + 60 KB Boot-Context Bloat** | **Process & Host Hygiene:** Removes deploy blockers on `JIS-NB` (`STATUS.md`, `BUILD_REPORT.md` dirtying `.mts_live`) and trims ~15,000 tokens per session boot. |

---

## Detailed Audit Findings, Proofs, Revalidations & Minimal Fixes

### GAP-1 [CRITICAL] — Zero Validated Fee-Net OOS Edges vs. 27 Grandfathered Live Sources Expiring 2026-10-23 (`B171`, `B187`, `T085`, `T086`)

- **Category:** Defect / Capital Protection / Statistical Integrity
- **Proof 1 (`MyTradingSys/execution/promoted_setups.json:1-4`):**
  ```json
  {
   "version": 1,
   "entries": []
  }
  ```
- **Proof 2 (`MyTradingSys/execution/auto_trader_config.json:1-99`):**
  All 27 live sources in `pre_pipeline_sources` (`tom`, `layer:fabio:*`, `layer:cryptocred:*`, `layer:rsi:*`, `layer:session*`, `layer:turn_of_candle:`, `layer:wlow_bounce:`, etc.) trade ONLY under a temporary grandfather clause expiring in 4 days:
  > `"reason": "grandfathered pre-pipeline testnet calibration, operator decision pending", "review_by": "2026-10-23"`
- **Proof 3 (`MyTradingSys/system/layer_map.json` & `MyTradingSys/research/TRIAL_LEDGER.csv`):**
  Inspection of all 22 entries in `layer_map.json` and all 29 rows in `TRIAL_LEDGER.csv` (`Splits: Counter({'DEV': 29})`) confirms **zero layers have a validated fee-net out-of-sample (`VALIDATION` or `HOLDOUT`) PASS**:
  - `tom_core`: `"STOP: do not backtest or tune the current BTC encoding ... being redefined as Tom v2"`
  - `fabio_cvd_absorption` / `fabio_escalation` / `fabio_volume_fvg`: `"L1 no edge / insufficient n"`
  - `funding_cvd_fade`, `session_momentum`, `turn_of_candle`, `rsi_divergence`, `session_levels`, `bb_lvn_triggers`: `"FAIL, closed"` or `"no edge"`
  - Furthermore, per `BUGS.md` row `T085`: *"97 % of testnet trades end on the time exit: find why targets/stops are almost never reached"*, and `ANNOUNCEMENTS.md` (`A-20261018-2`): the PIT price-level study (`Q76`/`B187`) has only `1,207` feasible days vs `2,427` needed (~1,220 days short of the statistical power gate).
- **Why It Matters:** Without a fee-net OOS edge and with 97% of testnet trades closing on the arbitrary time exit (`max_hold_minutes: 120` / `max_hold_bars: 8`), live execution is testing plumbing rather than edge. Additionally, if `review_by: 2026-10-23` enforces expiry or is reviewed without a replacement promotion, testnet calibration stops or continues on falsified layers (`turn_of_candle`, `rsi_divergence`).
- **Concrete Fix & Simplification:**
  1. Prune already-falsified layers (`turn_of_candle`, `rsi_divergence`, `session_levels`) from `auto_trader_config.json` `pre_pipeline_sources` on 2026-10-23 so testnet subaccounts (`jishu_1..21`) only sample active candidates (Tom v2, Fabio v2, LC3/LC4 Levels Confluence, CryptoCred 4h/1d).
  2. Enforce `lab-trust-tag` (`UNCHECKED` -> `MACHINE-OK` -> `VERIFIED-C1/C2`) so no `VALIDATION` read (`lc-validation`, `tom-btc-validation`) runs on an unverified DEV base.
  3. Close `T086` (`D06-gate`) by codifying the quantitative Go-Live Bar in `promoted_setups.json` schema validation.

---

### GAP-2 [CRITICAL] — `StateCodeEmitter.java` Silent Session CVD/VWAP Corruption on Restart or WebSocket Drop + `vwap_anchor_utc` Bug (`state-code-accumulator-backfill`)

- **Category:** Live-Path Defect Removal / Fail-Closed Safety
- **Proof 1 (`src/main/java/datafeed/StateCodeEmitter.java:177-189, 470-474`):**
  ```java
  private void applySessionAccumulator(Tick t) {
      long dayStart = utcDayStart(t.T);
      if (sessionDayStartMs != dayStart) {
          sessionDayStartMs = dayStart;
          sessionCvd = 0.0;
          sessionCumPV = 0.0;
          sessionCumVol = 0.0;
      }
      double signed = t.buyerMaker ? -t.qty : t.qty;
      sessionCvd += signed;
      sessionCumPV += t.price * t.qty;
      sessionCumVol += t.qty;
  }
  ```
  And in `restoreStateFromDisk()` (`lines 470-474`):
  ```java
  if (root.has("session_day_start_ms")) sessionDayStartMs = root.get("session_day_start_ms").asLong();
  if (root.has("session_cvd"))           sessionCvd         = root.get("session_cvd").asDouble();
  if (root.has("session_cum_pv"))        sessionCumPV       = root.get("session_cum_pv").asDouble();
  if (root.has("session_cum_vol"))       sessionCumVol      = root.get("session_cum_vol").asDouble();
  ```
- **Proof 2 (`MyTradingSys/research/audits/state_cvd_vwap_audit_2026-10-18.md:23-25`):**
  - **M1 (2026-10-15 12:41Z):** `state_code.json` emitted `session_cvd = -6549.7 BTC` vs archive klines `-6182.3 BTC` (**error: `-367.4 BTC`**).
  - **M2 (2026-10-12 13:08Z):** `state_code.json` emitted `cum_pv/cum_vol = 83,498.0` on `53,825 BTC` vs klines VWAP `83,577.0` on `73,527 BTC` (**error: `19,702 BTC` = `26.8%` of daily volume missing, shifting VWAP by `$79`**).
  - **M3 (`MarketDataSnapshot.java:832-836, 861`):** Writes `session.vwap_anchor_utc` as `2026-10-15T13:30:00Z` (NY 09:30 open) even at `12:43Z` (in the future!), whereas the actual VWAP is anchored at `00:00:00Z` (`dailyBars`).
- **Why It Matters:** `StateCodeEmitter` fails **OPEN** on tick gaps: after a JVM restart or WebSocket reconnect (`scheduleReconnect`, line 160), it resumes summing ticks on top of stale disk state without backfilling the missing window, and emits a valid-looking `state_code.json` state letter (`A..`).
- **Concrete Minimal Fix:**
  - Execute ready card [`state-code-accumulator-backfill.json`](file:///F:/MTS/mts-jis-nuc-gemini-mts-gap-audit/MyTradingSys/system/tasks/state-code-accumulator-backfill.json): on startup and WebSocket reconnect, backfill `sessionCvd`, `sessionCumPV`, and `sessionCumVol` from UTC `00:00Z` (or last persisted tick timestamp) via 1m klines/aggTrades; if the backfill HTTP call fails, mark `state_code.json` state `INVALID` (fail closed).
  - Fix `MarketDataSnapshot.java:861` so `vwap_anchor_utc` reports the true `00:00Z` UTC day start (`session_start_utc`).

---

### GAP-3 [HIGH] — Mainnet PnL & Daily Loss Monitor Gaps: L6/B149 Settlement Verification & Mainnet Subaccount Blindness

- **Category:** Live-Path Safety / Mainnet Cutover Gate
- **Proof 1 (`MyTradingSys/research/STATUS.md:73`):**
  > `L6: ... Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet`
  *(Note: Revalidation of [`mainnet_pnl.py`](file:///F:/MTS/mts-jis-nuc-gemini-mts-gap-audit/MyTradingSys/execution/mainnet_pnl.py#L8-L38) shows `ALLOWED_TX_TYPES = frozenset({"trade", "settlement"})` was updated after `txlog_capture_2026-10-10_jishu_11.json`, but `make_status.py` / `STATUS.md:73` still lists L6/B149 as an open finding blocking mainnet!)*
- **Proof 2 (`MyTradingSys/execution/daily_loss_monitor.py:505-513`):**
  ```python
  named = {}   # testnet: named subaccounts in the aggregate (mainnet: always empty)
  while True:
      try:
          if _client_env(do) != "mainnet":
              named = refresh_named_accounts(do, named, named_account_labels())
          result = run_once(do, token, currency=args.currency, instrument=args.instrument,
                            cap_usd=args.cap_usd, pnl_source=args.pnl_source, accounts=named)
  ```
- **Why It Matters:**
  1. `STATUS.md:73` is out of sync with `mainnet_pnl.py:8-13` (which already includes `"settlement"`), leaving ambiguity over whether a funding-bearing perpetual position across 08:00 UTC has been verified end-to-end.
  2. In `daily_loss_monitor.py:510`, `if _client_env(do) != "mainnet":` skips subaccount aggregation on mainnet, assuming mainnet will never use named accounts. If `auto_trader_config.json` `"accounts"` is ever populated on mainnet, `daily_loss_monitor` will silently ignore subaccount losses (failing open on subaccounts) rather than refusing or aggregating them.
- **Concrete Minimal Fix:**
  1. In `daily_loss_monitor.py`, if `_client_env(do) == "mainnet"` and `auto_trader_config.json` has any existing `mainnet_<label>.secret.json` or configured subaccounts, either aggregate them or fail closed at startup (`RuntimeError("named accounts present on mainnet")`).
  2. Reconcile `STATUS.md:73` / `make_status.py` with the B149 `mainnet_pnl.py` settlement verification.

---

### GAP-4 [HIGH] — Ship-Gate Fast Path (`--fast`) Skips `3dl` (`ci_deps_lint`), Drops Deferred Receipt, and Starves Host Gate Slots (`REPORT_2026-10-19.md`)

- **Category:** CI/CD Reliability & Developer Velocity Optimization
- **Proof 1 — Revalidation of MTS_Doctor Flag #1 (`scripts/dev/run_all_tests.py:667, 715-721`):**
  ```python
  FAST_COSTLY_ALWAYS = ("3w", "3tl", "3dl")
  ...
  for f in files:
      needed.update(gate_select._name_matches(f, steps_list))
      if gate_impact.is_test_file(f):
          needed.add("3dl")
  ```
  Revalidated on current `HEAD` (`2130dfbe`): `3dl` (`ci_deps_lint.py`, which takes ~1.5s–3s and checks 395 test files transitively) is **still skipped** whenever a non-test `.py` helper or `.github/workflows/ci.yml` is edited! If a builder adds a third-party import to a helper module imported by a test, `--fast` skips `3dl`, pushes to `origin/fast-track`, and turns CI red, blocking all subsequent ships.
- **Proof 2 — Per-Clone Gate Slot Starvation (`scripts/dev/sync.py:183-187` & `REPORT_2026-10-19.md:17-19`):**
  ```python
  def _dir(self):
      common = Path(git(self.repo, "rev-parse", "--git-common-dir").stdout.strip())
      d = (common if common.is_absolute() else Path(self.repo) / common) / self.name
  ```
  Because `gate_slot` locks `<git-common-dir>/gate-slots`, separate clones (`F:/MTS/mts-codex-lab` vs `C:/Users/.../BinanceDataFeed`) do not share a machine-wide lock directory, and `--precheck` runs outside the slot (`run_all_tests.py:1028-1029`). On 2026-10-18/19, this caused 100% CPU saturation and 20+ minute slot starvation (`sv7-host-gate-budget`).
- **Proof 3 — Quarantine Path Filter Gap (`scripts/dev/gate_impact.py:204-205`):**
  `NO_QUARANTINE` only blocks `MyTradingSys/execution/` and `MyTradingSys/runtime/` prefixes; live-path tests located under `MyTradingSys/tests/` or `scripts/dev/` are not blocked from quarantine, and `quarantine_problems()` has no maximum expiry horizon (`max_days`).
- **Concrete Minimal Fix:**
  1. **Immediate (`fast-gate-run-3dl-on-any-py-change`):** In `scripts/dev/run_all_tests.py:717`, change `if gate_impact.is_test_file(f):` to `if f.endswith(".py") or f == ".github/workflows/ci.yml": needed.add("3dl")`.
  2. **Host-wide slot (`sv7-host-gate-budget`):** Move `gate_slot._dir()` to a single machine-wide path (e.g., `Path(tempfile.gettempdir()) / "mts-gate-slots"` or `F:/MTS/.gate-slots`) and include `--precheck` inside the slot budget.
  3. **Persist deferred tests:** Record `fast_info["deferred"]` into the gate receipt JSON so audits can see which tests were deferred to CI.

---

### GAP-5 [HIGH] — 10 "Zombie" Open Task Cards Whose Deliverables Are Already on `origin/fast-track` + 6 Unshipped Completed `gemini-q/*` Branches

- **Category:** Workflow & Process Economization (Direct Token & Compute Savings)
- **Proof (Revalidated via Git Forensics on `origin/fast-track` HEAD `2130dfbe`):**
  A full cross-check of all 135 open task cards (`MyTradingSys/system/tasks/*.json`), `MyTradingSys/research/layer_lab/reports/*.md`, and `git cherry -v origin/fast-track gemini-q/<id>` proves that **10 currently open (`ready` / `refined`) cards have ALREADY been built, tested, and committed to `origin/fast-track`**, due to two process bugs:
  - **Cause A (Cherry-Pick Without Closing Card):** When a Claude reviewer cherry-picked the code commit from `gemini-q/<id>` onto `origin/fast-track`, they skipped the second commit on `gemini-q/<id>` (`tasks.py done <id>`), leaving the card `ready` or `refined` on trunk!
  - **Cause B (Merge / Bulk-Revert Regression `6005be0d` / `7cc09701`):** Card [`outcome-labeler-timeout.json`](file:///F:/MTS/mts-jis-nuc-gemini-mts-gap-audit/MyTradingSys/system/tasks/outcome-labeler-timeout.json) (weight `CRITICAL`) was completed and marked `done` in commit `e185a5f1` (`2026-10-18 02:29:19 +0530`), with code shipped in `36081c4c` and `73e0ae45` (`MyTradingSys/runtime/outcome_labeler.py` already has `load_snapshots(done)` skipping labeled files!). Subsequent branch merge `6005be0d` and revert `7cc09701` overwrote `"state": "done"` back to `"state": "ready"` and erased `"result"`.
  - **Cause C (`tasks.py` Partial Update):** Card [`review-ground-layer-youtube-strategy-and.json`](file:///F:/MTS/mts-jis-nuc-gemini-mts-gap-audit/MyTradingSys/system/tasks/review-ground-layer-youtube-strategy-and.json) has its full completion text populated in `"result": "2026-10-19: Dropped 4 saturated/429-blocked YT cards..."` (commit `41c8a303`), but `"state"` was left as `"ready"`.

  **Complete Table of 10 Zombie Open Cards on `origin/fast-track`:**
  | Card ID | Current State | Weight / Lane | Proof of Delivery Already on `origin/fast-track` | Why Still Open |
  |---|---|---|---|---|
  | `outcome-labeler-timeout` | `ready` | `CRITICAL` / `JIS-NB` | Code in `36081c4c` & `73e0ae45` (`outcome_labeler.py:22-28`); marked `done` in `e185a5f1` | Overwritten to `ready` by merge `6005be0d` / `7cc09701` |
  | `gross-screen-refuse-a-changed-data-manif` | `ready` | `IMPORTANT` / `CODEX` | Code + 12 passing tests in `f068fd95` (`screen.py`, `test_screen.py`, report) | Reviewer cherry-picked `fa6af95c`, skipped `eb47d272` (`record task done`) |
  | `one-timeframe-map-for-the-whole-toolchai` | `ready` | `ROUTINE` / `CODEX` | Code + 45 passing tests in `884a3b3a` & `4c95b4ed` (`test_tf_map.py`, report) | Reviewer cherry-picked `e5c35606`, skipped `fd10df91` (`tasks.py done`) |
  | `positioning-c1-longwindow-count-power` | `ready` | `ROUTINE` / `SONNET` | Code + report in `655d1074` (`COUNT_POWER.md`, `count_power.py`, `test_count_power.py`) | Reviewer cherry-picked `5b474af2`, skipped `3b3f9a70` (`marked done`) |
  | `tom-v2-btc-min-stop-width` | `ready` | `IMPORTANT` / `CODEX` | Code + tests in `05b19696` (`tom_bt.py`, `tom_noise_units.py`, `test_tom_min_stop_width.py`) | Reviewer cherry-picked `08b38d70`, skipped `455ca07c` (`mark card done`) |
  | `score-context-reads-automatically-carrie` | `refined` | `IMPORTANT` / `SONNET` | Code + 5 tests in `bc97ca74` (`market_guide.py`, `shot.py`, `test_shot.py`) | Cherry-picked from `gemini-q` (`a7876c54`) without closing card |
  | `rv05-h3-outcome-evidence` | `refined` | `IMPORTANT` / `SONNET` | Shipped in `6048a073` (`RV05 H3: record 1150 gap as NOT_IN_DATA for F13-x in Fabio ledger`) | Cherry-picked from `gemini-q` (`44bfb08d`) without closing card |
  | `time-adjusted-volume-context-line-for-th` | `refined` | `IMPORTANT` / `SONNET` | Shipped in `2264a331` (`market_guide: add time-adjusted volume context line`) | Cherry-picked from `gemini-q` (`89939ddd`) without closing card |
  | `tom-probe-prereg` | `refined` | `IMPORTANT` / `SONNET` | Shipped in `e83be62e` (`tom-probe-prereg: pre-register surviving M/F arms and create tom-probe-runner card`) | Cherry-picked from `gemini-q` (`ac1b7d6f`) without closing card |
  | `review-ground-layer-youtube-strategy-and` | `ready` | `IMPORTANT` / `SONNET` | Shipped in `41c8a303`; card's own `"result"` field is already populated! | `"state"` left as `"ready"` in `41c8a303` |

  **Plus 6 Completed `gemini-q/*` Branches Waiting in `F:/MTS/gq` for Claude Review & Ship:**
  | `gemini-q/<id>` Branch | Card State | Unshipped Commits on Branch (`git log origin/fast-track..gemini-q/<id>`) |
  |---|---|---|
  | `gemini-q/live-loop-timeouts-b191` | `refined` (`CRUCIAL`) | `9f53f044 research: audit live-loop timeouts, wrapper priority and snapshot.cp post-B191` |
  | `gemini-q/live-orderflow-state-line-1m-5m-15m-pric` | `refined` (`IMPORTANT`) | `5afb3079 market guide: add order-flow state lines (1m/5m/15m) and 00:00Z VWAP` |
  | `gemini-q/malkan-universe-data-power` | `ready` (`IMPORTANT`) | `cd0ae2fd Malkan: Indian-equity D/W/M data sources, universe size, and power` |
  | `gemini-q/positioning-c1-prereg-no-source` | `raw` (`IMPORTANT`) | `01e3dcb8 positioning-c1-prereg-no-source: pre-registration for positioning C1 NO-SOURCE re-test` |
  | `gemini-q/tom-ledger-add-the-losing-first-attempts` | `ready` (`IMPORTANT`) | `241d87c6` + `494f95cd` (`add losing first attempts S1 and S6 to Tom ledger`) |
  | `gemini-q/trim-builder-cwd-and-prelaunch-worktree` & `gemini-q/trim-claudemd-re-read-guard` | `ready` (`ROUTINE`) | `9a0489e3` + `2e96d337` (startup token savers) |

- **Payoff:** Closing the 10 already-shipped zombie cards (`tasks.py done`) and reviewing/shipping the 6 completed `gemini-q/*` branches prevents `codex_run.py` and Claude builders from re-executing 16 completed tasks (**saving ~8M–15M tokens and ~4–6 hours of wall time**).
- **Concrete Prevention Fix:** Add a check in `tasks.py lint` (or `tasks.py sweep`) that flags any `ready`/`refined` card where (a) `"result"` is non-empty, or (b) `MyTradingSys/research/layer_lab/reports/*_<id>.md` already exists on disk!

---

### GAP-6 [HIGH] — 59.8% Plumbing Commit Overhead (1,229 of 2,056 Commits in 72h) + 12 Orphan Claims + 57 Unshipped Worktrees

- **Category:** Workflow & Process Optimization / Git & CI Economization
- **Proof 1 — 72-Hour Commit Breakdown on `origin/fast-track`:**
  Command:
  ```powershell
  python -c "import subprocess,collections;s=subprocess.run(['git','log','origin/fast-track','--since=72.hours','--pretty=%s'],capture_output=True,text=True,encoding='utf-8').stdout.splitlines();c=collections.Counter(('claim' if l.startswith('claim ') else 'release' if l.startswith('release ') else 'merge' if l.startswith('Merge') else 'sync' if l.startswith('sync') else 'other') for l in s);print(len(s),dict(c))"
  ```
  Exact output:
  ```text
  2056 {'claim': 285, 'other': 823, 'release': 264, 'merge': 681, 'sync': 3}
  ```
  - Out of **2,056 commits** in 72 hours (~685 commits/day), **549 (`26.7%`)** are standalone `claim`/`release` commits and **681 (`33.1%`)** are `Merge` commits triggered by constant trunk tip movement — **1,230 commits (`59.8%`) are pure coordination plumbing**, while only `823` (`40.0%`) carry actual work.
  - `STATUS.md:15` confirms: `commits 24h: 408 = research 23% | claim/release 44% | other 33% OVER 30% CAP`.
- **Proof 2 — 16 of 24 Active Claims on `origin/fast-track` Are Orphaned (`card_state == done/dropped` or zombie-shipped):**
  Cross-checking `MyTradingSys/system/claims/*.md` against `MyTradingSys/system/tasks/*.json` proves that **12 active claim files belong to cards already in `state: "done"` or `"dropped"`** (`backfill-t087-session-level-split-and-ve`, `bb-top-reversal-candle-backtest`, `cryptocred-prereg-4h-1d`, `encode-v1-only-kill-scope-for-weekly-low`, `eu-low-us-sweep-follow-ups-long-after-sw`, `funding-carry-with-real-spot-basis-margi`, `identify-the-coinglass-net-delta-panel-u`, `krown-foundations-ep08-follow-through`, `kurisko-quad-rotation-module`, `malkan-captions-fetch-noauth`, `malkan-home-fit-audit`, `positioning-flowhorse-ledger-feasibility`, `positioning-home-fit-audit`, `rv02-fix-dax-full-dev-authorization`), plus **3 claims belong to the cherry-picked zombie cards** (`gross-screen-refuse-a-changed-data-manif`, `one-timeframe-map-for-the-whole-toolchai`, `tom-v2-btc-min-stop-width`).
- **Proof 3 — Worktree Sprawl (`sync.py where`):**
  `106` git worktrees exist on `JIS-NUC`; **57 worktrees** hold unshipped commits or modified/untracked files.
- **Why It Matters:** Every `push_claim_commit()` (`sync.py:829-858`) advances `origin/fast-track`, forcing every concurrent `sync.py ship` to lose push races (`SHIP_PUSH_TRIES = 5`), create merge commits (`681` in 72h), and contend on `refs/remotes/origin/fast-track.lock`.
- **Concrete Simplification & Fix:**
  1. **Auto-release claims in `tasks.py done` / `sync.py ship`:** When `sync.py ship` commits a card transition to `"state": "done"` or `"dropped"`, automatically `git rm -f MyTradingSys/system/claims/<card-id>*.md` in the same commit even if the caller forgot `--release <slug>`.
  2. **Sweep orphan claims in `tasks.py sweep` / `sync.py tidy`:** Automatically remove any claim file in `MyTradingSys/system/claims/<slug>.md` whose matching card `MyTradingSys/system/tasks/<slug>.json` is already `done` or `dropped` in a single batched commit.

---

### GAP-7 [HIGH] — Codex Layer Lab Stalled for 29.2 Hours (`15 ready` Cards, `6%` 5h Window Used) + Scheduled-Task Retirement Deadlock (`ROUTING.md` C2/C3/C7)

- **Category:** Process & Throughput Optimization / Allowance Economization
- **Proof (`python scripts/dev/codex_run.py status` on `JIS-NUC` at `2026-10-19 04:05Z`):**
  ```text
  Layer lab (Codex) at 2026-10-19 04:05Z: on
    Codex allowance (plus): 5-hour window 6% used (resets 10-19 08:32Z); week 27% used (resets 10-24 20:41Z)
    Lab spend guard: window 0/50 pts, 0/10 runs (astra 0/1); week 0/60 pts; resets 08:32Z
    Last check by the scheduler: 2026-10-17T18:54Z RAN gap-g2-dax-ask-candles BLOCKED ...
    Queue: 15 ready
    NEEDS A LOOK:
      - STALLED: 15 card(s) ready, lane up, no allowance hold, but nothing ran for 29.2 h: read last_tick.txt and last_lane.txt on the lab host
  ```
- **Why It Matters:**
  - `SCHEDULING_POLICY.md` retired all Windows scheduled tasks (including the 30-min Codex lab tick and `MTS-DailyHygiene` which ran `desk.py assign`), replacing them with *"the super-session coordinator runs `codex_run.py tick` / `desk.py assign` on wake"*.
  - However, when no coordinator wakes to call `codex_run.py next`, **94% of the 5-hour Codex window and 73% of the weekly allowance sit idle for 29.2 hours** while 15 ready `CODEX` cards wait (`ANNOUNCEMENTS.md` `A-20261018-3`), and 11 `DSA-NB` audit rows sit untaken for 65+ hours (`ROUTING.md` C7).
  - Furthermore, 3 of the 15 `ready` cards in the Codex queue (`gross-screen-refuse-a-changed-data-manif`, `tom-v2-btc-min-stop-width`, `one-timeframe-map-for-the-whole-toolchai`) are the zombie cards identified in **GAP-5** — if `codex_run.py next` runs before GAP-5 is cleaned up, Codex will waste 3 runs re-doing already-shipped work!
- **Concrete Fix:**
  1. First close the 10 zombie cards (GAP-5) so they drop out of the `15 ready` queue.
  2. Have the NUC coordinator immediately invoke `python scripts/dev/codex_run.py next` (or a foreground loop in the NUC coordinator terminal) in the `A-20261018-3` priority order (`lab-trust-tag`, `lab-review-gate-harden2`, `dsa-audit-08-split-trials`, `lc-ladder-dev`, `simulator-validation-planted-edge`).

---

### GAP-8 [HIGH] — Live-Host Generated File Collisions (`move-live-host-generated-files-status-md`), Stale `.new` Files (174h), and Boot Context Bloat (60 KB)

- **Category:** Host Hygiene & Token Economization
- **Proof 1 — Live Tree Dirtying (`MyTradingSys/system/tasks/move-live-host-generated-files-status-md.json` & `sync.py where`):**
  `sync.py where` shows `UNSHIPPED BinanceDataFeed [fast-track] unshipped-commits=1 modified=6 untracked=1`. Tracked files rewritten by live-host scripts (`MyTradingSys/research/STATUS.md`, `MyTradingSys/runtime/BUILD_REPORT.md`, etc.) dirty the live checkout (`.mts_live`) and cause merge conflicts (`TAKE_ORIGIN` workaround in `sync.py:42-43`).
- **Proof 2 — Stale `.new` Files (`STATUS.md:25-27`):**
  - `MyTradingSys/backtest/layers/fabio/htf_context_live.py.new` (`173.9h` old)
  - `MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new` (`173.9h` old)
- **Proof 3 — Boot Context & Documentation Sprawl:**
  ```text
  system md: 210 files, 1,034,744 bytes (~258k tokens)
  boot read set (CLAUDE.md + STATUS.md + ANNOUNCEMENTS.md + ROUTING.md + PARALLEL.md + GEMINI_START.md): 59,991 bytes (~15,000 tokens per session start)
  scripts/dev/*.py: 169 scripts, 1,853,668 bytes (76 test files; 11 scripts flagged WARN NO-READER by wiring_scan.py)
  ```
- **Concrete Fix:**
  1. Ship `gemini-q/trim-claudemd-re-read-guard` and `gemini-q/trim-builder-cwd-and-prelaunch-worktree` (already built in `F:/MTS/gq`) to cut per-session startup token burn (`B172` / `B183`).
  2. Execute `move-live-host-generated-files-status-md` on `JIS-NB` to untrack live-generated status files or move them to gitignored `runtime_data/`.
  3. Archive or promote the two 174-hour-old `fabio/*htf_context_live*.py.new` files and the 11 `WARN NO-READER` scripts in `scripts/dev/`.

---

## What Was Checked and Verified SOUND (No Action Needed)

To prevent duplicate audits, the following critical components were inspected line-by-line and verified **SOUND**:
1. **Server-Side Stop Invariant (`MyTradingSys/execution/executor.py` & `position_manager.py`):**
   - `executor.py` places a `reduce_only` `stop_market` on the very first entry fill and resizes it on subsequent ladder fills (R1).
   - `fail_closed()` and `flatten_halt()` sweep `cancel_by_label` across all compiled entry, stop, and target labels (`<plan_id>:<label>`, capped at 64 chars via `PLAN_ID_RE`), preventing orphan orders after `OrderStateUnknown` (S6).
   - `position_manager.py` enforces `MAX_UNPROTECTED_SECONDS = 4s`, refreshes `pm_heartbeat` every 60s for `orphan_watchdog.py`, and retries transient read/auth errors (`READ_RETRY_DELAYS = (2,4,8,16,32)`) before exiting with `RC_LOST_CONTACT = 3` so `auto_trader.py` never frees an active slot on a network blip.
2. **Reconciler (`MyTradingSys/execution/reconciler.py`):**
   - Nets all order fills (`entries`, `stop`, `targets`, `emergency_close`), verifies live stop coverage `covered >= abs(actual_position)`, detects unknown plan orders by prefix `<plan_id>:`, and halts without auto-correcting.
3. **Daily Loss Guard & Blind Recovery (`MyTradingSys/execution/daily_loss_guard.py` & `daily_loss_monitor.py`):**
   - Missing `pnl_usd` keys or non-numeric `change`/`cashflow` values raise `ValueError` (fail closed, L7).
   - Corrupted `daily_loss_monitor_state.json` raises `StateUnreadable` and writes `HALT_DAILY_LOSS` instead of re-baselining from current equity (FIX3 H4).
   - Testnet `BlindRecovery` (`BLIND_CLEAN_SECONDS = 1800`, `BLIND_MAX_CLEARS_PER_DAY = 2`, `BLIND_FLAP_SECONDS = 3600`) only clears halts tagged `"kind": "blind", "owner": "daily_loss_monitor"`, never overwrites or clears a `"loss"` halt, and is completely disabled on `"mainnet"`.
4. **Gate Test Discovery & CI Dependencies (`Step 3gd` & `Step 3dl`):**
   - `MyTradingSys/tests/test_gate_discovery_b150.py` (`Step 3gd`) passes (`exit=0`): all 400 active test files on disk are accounted for by `run_all_tests.py` / `run_extra_tests.py`.
   - `scripts/dev/ci_deps_lint.py` (`Step 3dl`) currently passes (`exit=0`) across all 395 gated test files.
   - `scripts/dev/tasks.py lint` currently passes (`exit=0`) across all 421 task cards.

---

## Prioritized End-to-End Roadmap & Next Steps (For Claude Review & Dispatch)

### Phase 0 — Immediate Zero-Risk Economization (< 30 mins, Saves ~16 Task Runs)
1. **Close the 10 Zombie Open Cards & Release 15 Orphan Claims:**
   - Run `tasks.py done` on the 10 cards whose commits are already on `origin/fast-track` (`outcome-labeler-timeout`, `gross-screen-refuse-a-changed-data-manif`, `one-timeframe-map-for-the-whole-toolchai`, `positioning-c1-longwindow-count-power`, `tom-v2-btc-min-stop-width`, `score-context-reads-automatically-carrie`, `rv05-h3-outcome-evidence`, `time-adjusted-volume-context-line-for-th`, `tom-probe-prereg`, `review-ground-layer-youtube-strategy-and`).
   - Delete the 15 orphaned claim files in `MyTradingSys/system/claims/*.md` whose cards are `done`/`dropped`.
2. **Review & Ship the 6 Completed `gemini-q/*` Branches (`F:/MTS/gq`):**
   - Claude reviewer session inspects and ships `gemini-q/live-loop-timeouts-b191`, `gemini-q/live-orderflow-state-line-1m-5m-15m-pric`, `gemini-q/malkan-universe-data-power`, `gemini-q/positioning-c1-prereg-no-source`, `gemini-q/tom-ledger-add-the-losing-first-attempts`, `gemini-q/trim-builder-cwd-and-prelaunch-worktree`, and `gemini-q/trim-claudemd-re-read-guard` (making sure to include the card-closure commit!).

### Phase 1 — CI/CD & Dev-Pipeline Hardening (Day 1)
1. **Fix Fast-Gate `3dl` Skip (`fast-gate-run-3dl-on-any-py-change`):**
   - 2-line change in `scripts/dev/run_all_tests.py:717` so `3dl` runs whenever any `.py` file or `ci.yml` changes (+ unit test in `scripts/dev/test_gate_impact.py`).
2. **Fix Host-Wide Gate Slot Starvation (`sv7-host-gate-budget`):**
   - Move `sync.gate_slot` lock directory to a single host-wide directory and count `--precheck` inside the slot budget.
3. **Prevent Future Zombie Cards & Orphan Claims in `tasks.py` & `sync.py`:**
   - Add a `tasks.py lint` rule that fails if an open card has a non-empty `result` or an existing `layer_lab/reports/*_<id>.md` report.
   - Make `sync.py ship` auto-remove `MyTradingSys/system/claims/<id>*.md` whenever a shipped commit sets `MyTradingSys/system/tasks/<id>.json` to `"done"` or `"dropped"`.

### Phase 2 — Live-Path & Host Safety Fixes (Days 1–2)
1. **Backfill `StateCodeEmitter.java` Session CVD & VWAP (`state-code-accumulator-backfill`):**
   - Backfill UTC-day `sessionCvd`, `sessionCumPV`, `sessionCumVol` on startup and WebSocket reconnect; fail closed (`INVALID`) on backfill error. Fix `MarketDataSnapshot.java:861` `vwap_anchor_utc` label.
2. **Untrack Live-Host Generated Files on `JIS-NB` (`move-live-host-generated-files-status-md`) & Unregister Legacy Scheduled Tasks (`host-legacy-tasks-unregister`):**
   - Keep `.mts_live` clean without `GENERATED_RE` / `TAKE_ORIGIN` hacks.
3. **Mainnet Daily Loss Monitor Guard (`daily_loss_monitor.py:510`):**
   - Fail closed on mainnet if named subaccounts exist in `auto_trader_config.json`, and update `make_status.py` / `STATUS.md:73` to reflect B149 settlement verification.

### Phase 3 — Statistical Edge & Pre-2026-10-23 Calibration Gate (Days 2–4)
1. **Unstick the Codex Layer Lab on `JIS-NUC` (`A-20261018-3`):**
   - Run `codex_run.py next` across `lab-trust-tag`, `lab-review-gate-harden2`, `dsa-audit-08-split-trials`, `lc-ladder-dev`, and `simulator-validation-planted-edge`.
2. **Pre-2026-10-23 `pre_pipeline_sources` Review (`auto_trader_config.json`):**
   - Before `2026-10-23`, prune falsified layers (`turn_of_candle`, `rsi_divergence`, `session_levels`) from testnet calibration and require `VERIFIED-C2` trust tags before running one-shot `VALIDATION` reads (`lc-validation`, `tom-btc-validation`).
