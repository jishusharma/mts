# PROMOTION PIPELINE: how a new setup reaches testnet

Code: `MyTradingSys/backtest/layers/promotion/` (`promote.py` gates, `registry.py` reader). Registry: `MyTradingSys/execution/promoted_setups.json`
(ships EMPTY: no tested config has a fee-net out-of-sample edge yet). Nothing here runs a backtest or reads VALIDATION / holdout data;
it only checks the records a research session wrote down. Testnet only (Deribit test); real money is a separate operator decision (GO_LIVE_BAR.md).

## Stages
1. Research -> 2. pre-registered screen (PRE_REG.md committed BEFORE the screen result; verdict file PASS) -> 3. backtest gate
(report with the BT-TUNED label, fee-net OOS) -> 4. testnet candidate = `shadow` -> 5. testnet trading = `testnet`.

## Gates (`promote.py check <manifest>`; any missing or unreadable field = REJECT with the reason; JSON via `--json`)
- PRE_REG exists at the manifest's git sha and its commit date is earlier than the first commit of the screen verdict file.
- Screen verdict file says PASS (JSON `{"verdict": "PASS"}` or a line `VERDICT: PASS`).
- Backtest report exists and carries the BT-TUNED label.
- Fee-net OOS net R > 0 AND 95 % CI low > 0 (GO_LIVE_BAR line 1), net R inside its CI, n_trades >= 30 (OURS: sanity floor).
- Trial ledger (CSV, column `study`): entry exists and its row count equals the manifest's variant count.
- VALIDATION and holdout each have exactly one read record.
- setup_id is not on `trade_blocklist` or `trade_blocklist_parked` (prefix match both ways); unreadable config = REJECT.
Manifest format: docstring at the top of `promote.py`.

## Who may run what
- Research / layer-lab sessions: write the manifest and run `check`. Nobody hand-inserts a registry entry.
- A builder session: `promote.py register <manifest> --mode shadow`, then commits on fast-track. CI re-checks every entry
  (`test_promote.ShippedRegistry`), so a bad entry makes the gate red and the deploy gate refuses it (MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md; deploys are manual or coordinator-run, DEPLOY_RUNBOOK.md).
- `--mode testnet`: needs PASS, an existing shadow entry, AND a sized testnet flag (`size_overrides` prefix covering the setup in
  auto_trader_config.json). DEFAULT (DECISION, OURS): without that flag the setup stays shadow, because a testnet entry with no size
  would be an unsized order path. Setting the size flag is a live-path config change and follows the CLAUDE.md live-path rules.

## Shadow rule (wired in the live path)
- `live_runner_cli.poll_once` passes every alert through `apply_promotion_gate`: an alert whose source (`layer:<layer>:<sub>:<tf>`)
  starts with a `shadow` entry loses `side` (kept as `shadow_side`) and gets `collection_only: true`; it is still logged and
  collected. `auto_trader.layer_signal` also rejects `collection_only` alerts, because a layer_rules entry could map a side-less alert.
- DEFAULT-DENY (fable H1, enforced in `auto_trader.promotion_reject`, for layer signals and Tom as source `tom`): a source with no
  registry entry trades only if it starts with a prefix in `pre_pipeline_sources` in `auto_trader_config.json`
  (`{prefix: {reason, review_by}}`, the operator's explicit grandfather list for the pre-pipeline testnet calibration); otherwise it is
  rejected `unregistered (promotion pipeline)`. Mode `testnet` trades, mode `shadow` never trades (it beats a grandfathered prefix).
  A fresh layer wired only through `layer_rules`/`size_overrides`/`accounts` therefore cannot reach `place()`.
- Unreadable/malformed registry, malformed or None `pre_pipeline_sources`, or an unreadable auto_trader config = FAIL CLOSED in
  auto_trader too: every layer signal and Tom is rejected. `review_by` is informational (not enforced: expiry would silently halt trading).
- Missing, unreadable or malformed registry = FAIL CLOSED: every alert becomes collection-only (nothing trades until fixed). The file is
  re-read on every poll, so a restart, demotion or edit takes effect on the next poll.

## Demote
`promote.py demote <setup_id> --to shadow` (testnet back to collection-only) or `--to off` (entry removed AND the setup_id written to
`trade_blocklist` in auto_trader_config.json, the list auto_trader enforces, with a reason: off is blocked, never a return to trading;
refused if the config cannot be written; works for a grandfathered source with no entry too). `verify` flags any sized
`size_overrides` prefix with no registry, `pre_pipeline_sources` or `trade_blocklist` entry. `check` also rejects when the PRE_REG blob at
`pre_reg.git_sha` differs from HEAD ("edited after registration"). Commit on fast-track; the next manual or coordinator-run deploy ships it (AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md).
A failed `verify` (`promote.py verify`) means fix or demote the entry first.
