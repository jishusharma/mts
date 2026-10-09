# B148 - Daily-loss monitor re-authenticates as the MAIN account when a named subaccount token expires; it also silently drops accounts on a config read error; orphan sweep can miss orphans and never reports a halt

Status: OPEN. Severity: HIGH. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

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

- MyTradingSys/research/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

# END
