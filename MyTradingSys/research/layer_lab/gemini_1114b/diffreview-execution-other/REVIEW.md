0 BUG, 2 RISK (21 commits in 24h under MyTradingSys/execution; 12 us_open_trader-only excluded, 9 touching cotrade.py/test_cotrade_close.py reviewed)

| sha | file:line | finding | severity | one-line fix |
|---|---|---|---|---|
| `c122e6f44` | `MyTradingSys/execution/cotrade.py:715,748-753` | `close_trade` uses `_last_real_place(recs)` without checking that `last` belongs to `_nm(account)` or that no `closed` / `killed` record follows `last`; if `last` was on another slot (now flat) or already closed and the target slot holds a non-co-trade position of matching `side` and `amount_usd`, `close_trade` closes it. (Also STYLE: `_unknown_state` at `MyTradingSys/execution/cotrade.py:130-133` omits `close` from the recovery hint when `st` is `closed_cancel_failed`.) | RISK | Filter `last` to `_nm(account)` and verify no `closed` or `killed` record follows `last` in `recs`. |
| `ac667117b` | `MyTradingSys/execution/cotrade.py:1-1223` | Revert of `e4b85e12` (`us_open_trader` + `cotrade.py` + `test_cotrade_close.py`); re-landed in `c122e6f44`. | CLEAN | — |
| `63cab7174` | `MyTradingSys/execution/us_open_trader/runner.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `2b03571aa` | `MyTradingSys/execution/cotrade.py:748-821` | Adds F2 (keep stop while open / `_close_unreadable` / `_close_fail_open`) and F4 (refuse mismatched size) to `close_trade`; F4's missing `last.get("account")` check is tracked on `c122e6f44`. | CLEAN | — |
| `29eb9c9fc` | `MyTradingSys/execution/us_open_trader/RUNBOOK.md` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `3910c40e2` | `MyTradingSys/execution/us_open_trader/recorder.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `499773a21` | `MyTradingSys/execution/us_open_trader/levels.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `8fc6438c0` | `MyTradingSys/execution/us_open_trader/RUNBOOK.md` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `0548eb338` | `MyTradingSys/execution/us_open_trader/runner.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `f7cd418ef` | `MyTradingSys/execution/cotrade.py:211-270` | `m3` (`cotrade.py` + `test_cotrade_close.py` merge/commit); `ensure_stop` early-return issue tracked on `0e0409c71`. | CLEAN | — |
| `adebba8dc` | `MyTradingSys/execution/us_open_trader/engine.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `afe3084dd` | `MyTradingSys/execution/us_open_trader/recorder.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `0e0409c71` | `MyTradingSys/execution/cotrade.py:245-249` | In `ensure_stop` (re-landed in `c122e6f44`), when `tighter` selects a tighter live stop, `if have: return ...` returns immediately without cancelling `wrong` (any remaining looser `stop_market` orders in `mine`). | RISK | Cancel `wrong` orders even when `have` is non-empty, after confirming `have[0]` is live. |
| `2e44a7de4` | `MyTradingSys/execution/us_open_trader/engine.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `179e8bdac` | `MyTradingSys/execution/us_open_trader/plan.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `d89eb9ca2` | `MyTradingSys/execution/cotrade.py:1-1223` | Revert of `cotrade` `close_trade` (CI RED: ungated `test_cotrade_close.py`). | CLEAN | — |
| `5aa300ffb` | `MyTradingSys/execution/cotrade.py:1-1223` | Revert of `627330d8e` (`cotrade` `close_trade`). | CLEAN | — |
| `d9ae70045` | `MyTradingSys/execution/cotrade.py:1-1223` | Merge of `origin/fast-track` into `worktree-wf_42796272-ca4-2` carrying `627330d8e`. | CLEAN | — |
| `729b5e390` | `MyTradingSys/execution/us_open_trader/engine.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `a865baefa` | `MyTradingSys/execution/us_open_trader/levels.py` | Excluded (`us_open_trader` only, already reviewed). | CLEAN | — |
| `627330d8e` | `MyTradingSys/execution/cotrade.py:1-1223` | Initial `close_trade` + CLI `close` (later reverted in `5aa300ffb`, superseded by `0e0409c71`/`2b03571aa`/`c122e6f44`). | CLEAN | — |
