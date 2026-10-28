# B148 - Daily-loss monitor re-authenticates as the MAIN account when a named subaccount token expires; it also silently drops accounts on a config read error; orphan sweep can miss orphans and never reports a halt

Status: IN-FIX. Severity: HIGH. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

Daily-loss monitor re-authenticates as the MAIN account when a named subaccount token expires; it also silently drops accounts on a config read error; orphan sweep can miss orphans and never reports a halt.

## Evidence

- execution/daily_loss_monitor.py:362-377 refresh_named_accounts authenticates each label with MTS_ACCOUNT set, then RESTORES the env. execution/deribit_orders.py:273-281 _call re-authenticates on codes 13009/13010/13011 via authenticate(), which reads MTS_ACCOUNT at call time (:168). After restore it is unset, so the re-auth logs in as MAIN. Worker repro with fakes: get_account_summary returned account_of_token 'tok_MAIN', auth calls ['jishu_7','MAIN']. I re-read both code paths and confirm the mechanism; the real Deribit token lifetime is unverified.
- Effect: a subaccount's PnL is replaced by main's (main counted twice, the loser invisible); on a breach kill_all flattens main again and leaves the subaccount open. Nothing raises, so the failure path never runs.
- daily_loss_monitor.py:357 named_account_labels returns [] on any config read/parse error and is re-read every loop (:405), while auto_trader loads its config once (auto_trader.py:745) and keeps trading those accounts. orphan_watchdog_cli.py:40 falls back to ['fabio'], so no jishu_N account is swept.
- Orphan watchdog: orphan_watchdog_cli.py:99 always calls run_once(..., None, ...), so the log only gets orphan_seen/ok; mts.ps1:198-205 reports only ok and orphan_halt, so a confirmed orphan halt prints nothing. live_accounts decides liveness by pid only; pm_heartbeat.pid_alive treats 'unknown' as alive (:148-180), so a hard-killed position_manager plus Windows pid reuse hides an orphan. The sweep runs once a day (launch-orphan-sweep.vbs, 09:10, 7 x 120 s).
- auto_trader.py:440-445: when a named account's secret file is missing account_for returns None = main slot, so a layer trade goes to the main account at the override size (up to 1000 USD on jishu_14); the only signal is one _account_missing log line.

## Fix shape

Failing-first tests, then fixes: (1) make re-auth account-explicit (pass the label into authenticate / keep the label on the client) so a token for jishu_N can only be refreshed as jishu_N, and fail closed (raise, counted by the failure path) if it cannot; (2) config read error must keep the last good account list, not return []; (3) a missing named-account secret must REJECT the layer trade, not fall to main; (4) log orphan_halt from the CLI path and make mts status show it; (5) liveness uses heartbeat age. Safety diff: Opus review. Live path: stage, supervisor deploys.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-09 consolidate session: parts 1-3 done in git (deribit_orders token->account map, named_account_labels last-good/raise, auto_trader rejects routed trade with missing secret; tests test_b148_reauth_account, test_dlm_aggregate, test_fabio_slot). NOT DEPLOYED: needs auto_trader + daily_loss_monitor restart. Parts 4-5 (orphan_halt log, heartbeat-age liveness) open.

2026-10-09 supervisor session (jisnb/stage1-2026-10-09): parts 1-4 are DEPLOYED. The live tree already held origin's auto_trader, daily_loss_monitor and deribit_orders (written 08:42) and auto_trader (pid 18860, 08:44) and daily_loss_monitor (pid 14848, 08:42) started after that, so parts 1-3 run. orphan_watchdog_cli (part 4) is picked up by the next 09:10 sweep. Part 5 (liveness by heartbeat age instead of pid only) stays OPEN: it needs an agreed heartbeat-age limit (no source for a number; ask on the Control Room page) and a test for pid reuse; pm_heartbeat.pid_alive deliberately fails open today.

# END
2026-10-09 CI/CD session: part 5 DONE in code (operator D10 = 10 minutes). pm_heartbeat.beat() + beat_utc; position_manager refreshes it every 60 s; live_accounts()/orphan_watchdog_cli --hb-max-age (default 600) treat an older beat as dead even if the pid was reused. Legacy heartbeats without beat_utc stay pid-only, so managers already running are never condemned by age. Tests: test_pm_heartbeat.py (9 new), test_orphan_watchdog_cli.py (2), test_pm_heartbeat_wiring.py (3), fail-first on the old code. Deploy: files are Python, picked up by the next watchdog sweep / newly started managers; B148 can close once a new manager's beat_utc is seen refreshing.

2026-10-10: Step 0 fallout cleared (9b27da3): 4 failures + 14 errors in test_mainnet_flag_offline appeared only when MTS_ACCOUNT was set in the host environment (the safety code is correct: it refuses named accounts on mainnet). The test now clears MTS_ACCOUNT in setUp and pins the refusal in test_named_account_never_selects_a_mainnet_secret; the quick gate is green with and without MTS_ACCOUNT=sharma. Remaining: live evidence. pm_heartbeats on origin/backup/JIS-NB at 2026-10-09T20:13Z (S-mkt-1009-1845, S-mkt-1009-1901) have no beat_utc yet, i.e. no manager started after the deploy; close when one does and its beat_utc refreshes every 60 s.
