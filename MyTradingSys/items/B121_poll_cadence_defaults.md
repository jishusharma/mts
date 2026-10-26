# B121 - Bar-aligned polling and 5 s auto_trader poll not landed; live_runner_cli 60 s and auto_trader 20 s defaults unchanged

Status: OPEN. Severity: LOW. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (c) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

Bar-aligned polling and 5 s auto_trader poll not landed; live_runner_cli 60 s and auto_trader 20 s defaults unchanged.

## Findings

- M29-08 | audit source MyTradingSys/research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-29.md:66,101 | C1 verdict NOT | Predates 10-01, open. live_runner_cli.py:366 poll default still 60 s; sleep at :406 not bar-aligned.
- M29-10 | audit source MyTradingSys/research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-29.md:68,101 | C1 verdict NOT | Predates 10-01, open. auto_trader.py:648 --poll-seconds default still 20.
- M30-14 | audit source MyTradingSys/research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-30.md:28,29 | C1 verdict NOT | Predates 10-01, open. Bar-aligned polling and 5 s auto_trader poll not landed; defaults unchanged.

## Evidence

- MyTradingSys/backtest/layers/alerts/live_runner_cli.py:366 poll default 60 s; sleep at :406 not bar-aligned.
- MyTradingSys/execution/auto_trader.py:648 --poll-seconds default 20.
- M30-14 repeats both proposals from MAINTAINER_REPORT_2026-09-30.md:28-29.

## Fix shape

Latency proposals, not strategy parameters. Follow-up decides whether to land them. LIVE PATH: both files run under the live testnet system, so stage .new and let the supervisor restart.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

