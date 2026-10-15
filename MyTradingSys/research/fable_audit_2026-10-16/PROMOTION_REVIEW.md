# Adversarial review of tonight's testnet changes (2026-10-15T18:00Z .. 2026-10-15T19:30Z on origin/fast-track)

Reviewer: Claude Fable 5.1 session `fable-testnet-adversarial-review` (JIS-NB, jishusharma), zero operator input. Production code untouched.
Scope (claim/release commits name the lanes): promotion-pipeline bff7c423; orderflow-stall bde4a491; live-reliability b0cb201e, 2913fefa,
51bee990, 67bd1110, 225ea98f, 36476c72; super-watchdog 1e50bbf8 (claimed, NOT on origin/fast-track at review time: reviewed from the branch).

## Verdict: SAFE WITH FIXES

Nothing shipped tonight opens a new order path, and the shadow mode is collection-only end to end. Three HIGH findings are gaps in what the new
pipeline claims to protect, not regressions: the gate is opt-in (every layer trading today bypasses it), `demote --to off` re-enables
trading, and the deploy fallback can still carry a CI-red commit that is green on the local `--quick` gate. Each HIGH has a task card
(lane SONNET, prio 0, pinned): `fable-h1-promotion-default-deny`, `fable-h2-demote-off-blocklist`, `fable-h3-deploy-fallback-ci-check`.

## Answers to the six questions

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Anything placing testnet orders without the pre-registered gate? | **YES.** Every source without a registry entry trades as before; Tom never touches the gate. | `registry.py:66-75` (unregistered pass unchanged), `auto_trader.py:734-738` (tom_signal, no gate), config `size_overrides`/`accounts` list ~20 live prefixes, `promoted_setups.json` is empty |
| 2 | Shadow mode truly places no orders? | **Yes.** `poll_once` strips `side` and sets `collection_only`; `layer_signal` rejects it before `plan_args`; `cycle()` logs `signal_rejected` and never calls `place()`. Unreadable registry = every alert collection-only. Only one producer writes `runtime/alerts/*.jsonl` (the runner); consensus/observation/bigtrade only read. | `live_runner_cli.py:334-337`, `registry.py:53-75`, `auto_trader.py:381-383, 743-747, 767` |
| 3 | Fail-closed on stale/missing data, API errors, restart, non-trade balance moves? | **Yes, with one LOW.** 10041 skip fires only when `not entries` (nothing placed), journals `entry_skipped_settlement`, returns `no_fill` which `place()` maps to no manager; any other code or a later-ladder 10041 still HALTs. Recorder stall exits 3, loop-supervisor matches the module name and relaunches. Settlement P/L is counted since B149. | `executor.py:435-442`, `auto_trader.py:508-509`, `loop-supervisor.ps1:39,85` |
| 4 | Can a red commit reach the live tree via MTS-AutoDeploy? | **In one corner, yes (pre-existing, more likely tonight).** `pick_branch` falls back to origin/fast-track when green/fast-track is >90 min stale, gated only by local `run_all_tests --quick` (no Maven, no backtest, one OS). With `sync.py ship` now a SMOKE gate, fast-track being red for 90 min is more likely, which is exactly when the fallback engages. | `auto_deploy.py:35-37, 120-129, 163-176`; `gate_select.py:1-11` |
| 5 | Is mainnet unreachable? | **Yes from the automated path.** `select_environment(True)` needs the `--mainnet` flag, the mainnet secret file and an interactive typed confirmation (EOF = refused); auto_trader passes only `--max-entry-seconds`; `deribit_read`/`deribit_client` hard-code test.deribit.com. | `deribit_orders.py:79-88, 190-212`, `executor.py:596-601`, `auto_trader.py:264, 505` |
| 6 | Do the new tests fail on the pre-change code? | **Yes, all five sets** (run in a throwaway detached worktree, table below). | this session |

### Q6: new tests against pre-change code (throwaway worktree, removed afterwards)

| Test set | Pre-change target | Result |
|---|---|---|
| promotion/test_registry_gate.py | bff7c423^ auto_trader + live_runner_cli | 4 failed / 10 passed (PollOnceWiring x2, AutoTraderRejectsCollectionOnly) |
| promotion/test_promote.py | bff7c423^ tree | 1 failed / 37 passed (ShippedRegistry: no registry file) |
| execution/testnet/offline/test_settlement_skip_offline.py | b0cb201e^ executor.py | collection error (SETTLEMENT_IN_PROGRESS absent) = fails |
| scripts/dev/test_auto_deploy.py | 2913fefa^ auto_deploy.py | 2 failed / 43 passed (generated-file restore) |
| fabio/test_orderflow_live.py | bde4a491^ orderflow_live.py | 8 failed / 11 passed (StallLoopTests) |
| tests/test_super_watchdog.py | 1e50bbf8^ relay.py | 7 failed / 0 passed |

CI collects the promotion tests: `run_all_tests.find_layer_modules` rglobs `backtest/layers/**/test_*.py` into step 5b, so `ShippedRegistry`
re-checks every registry entry on both OSes as the commit claims.

## Findings, ranked

### H1 HIGH: the promotion gate is opt-in; every layer that trades today, and Tom, bypass it
- Where: `MyTradingSys/backtest/layers/promotion/registry.py:66-75` (`apply_promotion_gate`: unregistered sources "pass unchanged");
  `MyTradingSys/execution/auto_trader.py:367-383` (gate check only on `collection_only`), `:734-738` (Tom path has no gate at all);
  `MyTradingSys/execution/auto_trader_config.json` `size_overrides` + `accounts` (~20 trading prefixes, none in the registry).
- Failure scenario: a builder adds `layer_rules`, `size_overrides` and an `accounts` entry for a new layer and ships; the next alert
  trades on testnet with no PRE_REG, no screen, no fee-net OOS. Meanwhile GO_LIVE_BAR.md line 1 says only trades "from configs that passed
  the walk-forward backtest" count, and the pipeline doc itself says no tested config has that edge yet, so none of today's testnet
  trades can ever count toward the bar. The pipeline protects nothing that exists.
- Also (defence in depth): the gate lives in ONE producer (`live_runner_cli.poll_once`). auto_trader never reads the registry, so any
  future writer of `runtime/alerts/*.jsonl` (none today) or a hand-written alert line bypasses shadow.
- Fix (card `fable-h1-promotion-default-deny`): default-deny. In `auto_trader.layer_signal`, look the source up in the registry itself:
  no entry and not on an explicit `pre_pipeline_sources` list in auto_trader_config.json (with a `review_by` date) = reject
  `unregistered (promotion pipeline)`; unreadable registry = reject all; `tom_signal` goes through the same lookup under source `tom`.
  The grandfather list is the operator's decision to keep today's calibration trades running; it is written down, not implicit.

### H2 HIGH: `promote.py demote --to off` is weaker than shadow: it returns the setup to trading
- Where: `MyTradingSys/backtest/layers/promotion/promote.py:274-290`; doc `PROMOTION_PIPELINE.md` "Demote" admits "the layer returns to
  today's behaviour" but nothing enforces the "use it only for a layer that traded before the pipeline" caveat.
- Failure scenario: a session sees a testnet setup losing, runs `demote <id> --to off` to "switch it off". The entry is gone, `layer_rules`
  and `size_overrides` still match, and the next alert trades at the configured size. Shadow would have stopped it; off does not.
- Fix (card `fable-h2-demote-off-blocklist`): `--to off` writes the setup_id into `trade_blocklist_parked` with the reason (or is refused
  unless it is already blocklisted); `verify()` adds a problem for any `size_overrides` prefix that has neither a registry entry nor a
  blocklist entry. With H1 in place, "off" naturally becomes collection-only and this card shrinks to the verify() check.

### H3 HIGH (Q4): the stale-green deploy fallback can carry a CI-red commit, and the smoke gate makes that state likelier
- Where: `scripts/dev/auto_deploy.py:35-37` (`FALLBACK_BRANCH`, `GREEN_STALE_S = 90 min`), `:163-176` (`pick_branch`), `:120-129`
  (local gate = `run_all_tests.py --quick`: skips Maven and backtest, runs on Windows only); `scripts/dev/gate_select.py` (ship = smoke).
- Failure scenario: a ship touches non-live code, the smoke gate passes, CI goes red on ubuntu (or in Maven). Nobody fixes it for 90 min
  (overnight, dispatcher idle on THROTTLE per 51bee990). green/fast-track is now "stale", fast-track is ahead, `pick_branch` returns
  fast-track, the local `--quick` gate is green on Windows, the red commit is merged into the live tree. `ci_red_card.py` files a card but
  does not stop the deploy. Pre-existing design (operator 2026-10-10 fallback), but 67bd1110 removed the full local gate at ship time, so
  the window is wider tonight than it was yesterday.
- Fix (card `fable-h3-deploy-fallback-ci-check`): in `pick_branch`, consult `ci_red_card.fetch_runs`/`first_failing` (already written):
  fallback to fast-track only when the newest completed CI run on fast-track is green (CI slow/down = runs in progress or `gh` unavailable);
  a red newest run = stay on green/fast-track and log `FALLBACK_REFUSED_CI_RED`. Test: red run list + stale green -> BRANCH, not FALLBACK.

### M4 MEDIUM: PRE_REG content is not pinned to the registered sha
- Where: `promote.py:118-124` checks `git cat-file -e sha:path` and compares dates, never that the PRE_REG at HEAD equals the blob at `git_sha`.
- Failure scenario: PRE_REG is edited after the screen result (thresholds loosened, outcome redefined); the committed sha still "holds the
  file", the date check still passes, the gate says PASS against a pre-registration that no longer exists.
- Fix: REJECT unless `git rev-parse sha:path` equals `git rev-parse HEAD:path` (or `git log sha..HEAD -- path` is empty).

### M5 MEDIUM: fee-net OOS numbers are self-declared in the manifest
- Where: `promote.py:150-165` reads `oos.net_r/ci_low/ci_high/n_trades` from the manifest; the BT-TUNED report is only checked for the label.
- Failure scenario: a typo or optimistic transcription (`ci_low: 0.1` where the report says -0.1) passes; the gate is "fail closed" on
  shape, not on truth.
- Fix: require a machine-readable line in the BT-TUNED report (`OOS_FEE_NET net_r=.. ci_low=.. ci_high=.. n=..`) and REJECT on mismatch.

### L6 LOW: deploy restore of `research/htf_context/*.json(l)` reverts a live input to its committed state
- Where: `auto_deploy.py:45-47` (`GENERATED_RE` includes htf_context), `:218-232` (`git checkout -- <file>` before the merge).
- Scenario: fabio's HTF context, rewritten live by `htf_context_live.py`, is reset to the repo copy at deploy; the layer reads stale context
  until the writer's next cycle. Backed up under `deploy_backup/<stamp>/regenerated/`, so no loss, one stale read window.
- Fix: restore the backed-up copy after the ff-merge for files that are live inputs, or drop htf_context from the tracked set (already carded).

### L7 LOW: `has_testnet_flag` and `auto_trader.size_override` validate differently
- Where: `promote.py:229-240` accepts any `size_usd` int > 0; `auto_trader.py:347-365` needs a multiple of 10 up to 10000 plus `max_loss_usd > 0`.
- Scenario: a testnet entry registers with `size_usd: 25`; every alert is then rejected `bad size_overrides` (fails closed, no order), but the
  registry says "testnet" while nothing trades. Fix: `has_testnet_flag` calls `auto_trader.size_override` (one validator).

### I8 INFO: super-watchdog (1e50bbf8) reviewed from the branch, not yet on origin/fast-track
Only a stop whose reason starts with `super-session` and whose heartbeat is missing/malformed/older than 60 min is lifted; operator stops
and unreadable flag files are never touched; it moves no live process. 7 tests fail on the old relay.py. No finding.

### Checked and clean
- 10041 skip: `not entries` guard means no entry, no stop, no position; later-ladder 10041 and every other code still `fail_closed` + HALT.
- Orderflow recorder: corrupt `_state.json` keeps the old behaviour with a WARN; exit 3 is a plain process exit for loop-supervisor.
- `registry.REPO = parents[4]` resolves to the repo root from `backtest/layers/promotion/`; the registry is re-read every poll.
- `ci_red_card.py` builds card text from run metadata only, never copies log lines.
- Mainnet: no code path reaches `select_environment(True)` without an interactive terminal and the secret file.

## DECISIONS (OURS)
- Verdict SAFE WITH FIXES rather than BLOCKER: no new order path, shadow is airtight, mainnet gated; the HIGHs are coverage gaps.
- H3 rated HIGH not MEDIUM because Q4 is answered "yes" and tonight's smoke gate widened the window.
- Pre-change test runs done in a detached throwaway worktree under the session scratchpad, removed afterwards; live tree untouched.
