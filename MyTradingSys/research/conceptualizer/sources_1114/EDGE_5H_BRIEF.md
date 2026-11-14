# EDGE 5H push: common rules for every edge-study worker (Supervisor C, 2026-11-13 ~15:25Z)

Operator order 15:20Z: use the full 5-hour window (until 20:00Z) to find an edge. Every worker reads this file first.

## Why these studies
The layer map holds 46 studies; nearly all are BTC-only intraday (5m-1h) rules, and 4-10 bp fees killed them.
Wave 1 goes where fees matter less and where the repo has not looked: cross-coin, 4h/1d, positioning/crowding.
Check `git ls-tree origin/fast-track MyTradingSys/research/` for an existing folder on your topic first; extend it, never duplicate.

## Method (non-negotiable, CLAUDE.md gates apply)
1. `python scripts/dev/sync.py start <slug>`; work only in the printed worktree.
2. PRE_REG.md committed BEFORE any outcome is computed: hypothesis, exact rule, params (each SOURCED or OURS),
   `## Context` section, `Regime mix:` line, splits DEV 2020-01-01..2024-06-30 / VALIDATION 2024-07-01..2025-06-30 /
   RECENT 2025-07-01..now, primary metric, pass rule. Pass = VALIDATION fee-net mean > 0 with block-bootstrap 95% CI
   lower bound > 0, n >= 30, beats a same-period placebo, BH 10% over all cells you test.
3. Data: Bybit v5 public API (`api.bybit.com/v5/market/...`; kline, funding/history, open-interest, account-ratio).
   Binance/OKX do not answer from this machine; never write the string of the Binance futures host in code or docs
   (a CI guard flags it). Cache raw data under `runtime_data/<slug>/` (ignored). Never commit data files > 1 MB.
4. Fees: import from `MyTradingSys/backtest/fees.py` (e.g. `fees.BINANCE_TAKER * 2`), never a bare numeric fee constant
   (gate test_no_own_costs). If you add any cost constant, add its row to
   `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/costs.csv`.
5. Forward-outcome lines (`x[i + h]`) trip the look-ahead lint: name helpers `fwd_*` or add reviewed rows to
   `scripts/dev/lookahead_allowlist.tsv` (file<TAB>fwd-index<TAB>exact source line<TAB>reason).
6. Every `subprocess` call needs `creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)`.
7. Tests: one `test_*.py` for the rule's core function; register it in `scripts/dev/extra_tests.tsv`.
8. Report: REPORT.md with a verdict line (PASS / FAIL / UNDERPOWERED), n per split, fee-net mean + CI, placebo, and
   a row added to `MyTradingSys/system/layer_map.json` (then `python scripts/dev/make_layer_map.py`).
9. Ship: `python scripts/dev/sync.py ship --release <slug>` with `Result:` / `Next:` lines; read the log fully; on a
   gate failure read `runtime_data/gate_fail_logs/` in your worktree, fix, re-ship. Never rebase/reset/force-push.
10. Hard limits: testnet only, never read .secrets/.env/keys, repo is PUBLIC, no .mts_live, no deploys, no process
    kills, no Chrome, no schedulers.

## Return (final message, <= 12 lines)
Verdict line, VALIDATION n / fee-net mean / CI / placebo, the commit sha on trunk (`git cherry origin/fast-track HEAD`
empty), and one line: the best next test if anything was close. End with `Noticed:` for gaps.
