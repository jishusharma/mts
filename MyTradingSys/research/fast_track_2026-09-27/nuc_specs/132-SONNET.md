# 132-SONNET: wire mainnet_pnl into daily_loss_monitor (audit item #3, blocks raising size, not the 50 USD smoke)

## Why Sonnet, not Qwen
daily_loss_monitor.py is 337 lines (about 5k tokens on its own) and its output must be the whole file; the change is about 15 lines
in `compute_total_pnl_usd`. The arithmetic itself is spec 129 (Qwen). This brief is only the wiring plus the docstring update.

## Prerequisite
129 `mainnet_pnl.py` promoted and gated (`realized_btc`, `unrealized_btc`, `daily_pnl_btc`).

## Edit (daily_loss_monitor.py only)
1. `import mainnet_pnl  # noqa: E402` beside the other sibling imports.
2. In `compute_total_pnl_usd`, the `pnl_source == "transaction_log"` branch: after fetching `entries` (unchanged call, same `start_ms`
   = UTC day start, `end_ms` = now) and the ticker, also fetch `summary = client.get_account_summary(token, currency=currency)` and return
   `round(mainnet_pnl.daily_pnl_btc(entries, summary) * ticker["mark_price"], 2)`. Any ValueError propagates: run_once's caller
   already turns consecutive failures into HALT_DAILY_LOSS (fail closed) - do not catch it here.
3. Leave `transaction_log_pnl_btc`, `_is_money_movement` and the `equity` branch in place (the equity path is the unchanged testnet
   default; existing tests import the two helpers). Mark `transaction_log_pnl_btc` DEPRECATED in its docstring (change-only sum, misses
   `cashflow` when profit_as_cashflow is true, audit HIGH #3).
4. Docstring "L6 PART 2" paragraph: replace the `sum(change)` description with: realized = sum(change + cashflow if
   profit_as_cashflow) over allow-listed type "trade" entries; plus session unrealized (`futures_session_upl`, fallback `session_upl`);
   times mark price. Cite the Deribit field semantics quoted in spec 129. Record the residual limits honestly:
   `settlement` entries are excluded (double count with cashflow); session UPL is "since last 08:00 UTC settlement", not since 00:00 UTC,
   so a position carried across the 08:00 settlement has its pre-settlement P/L booked into that settlement entry and not counted;
   funding (`interest_pl`) is not added. Fine for intraday flat-to-flat trading; revisit before holding overnight.

## Tests
`MyTradingSys/execution/test_daily_pnl_wiring.py.new` (written; 2 failures on the pre-change code): mainnet -71.2 USD case with a
deposit/swap/correction/transfer mix, UTC-day query window, missing UPL fails closed, testnet equity path untouched and does not read
the tx log. Hand check: realized = (-0.00001 - 0.0005) + (-0.000002) = -0.000512 BTC; UPL -0.0002; total -0.000712 BTC x 100000 = -71.2.
Existing `test_daily_loss_monitor.py` and `test_premainnet1_offline.py` must stay green (their fake clients may need
`get_account_summary` to return a `futures_session_upl` in the transaction_log branch; add it to the fakes, do not weaken the code).

## Gates
`python scripts/dev/run_all_tests.py --quick`. Tick audit item #3 in MAINNET_READINESS_CHECKLIST.md. One operator check before raising
size (not the agent): run `daily_loss_monitor.py --mainnet --once` right after the smoke trade and compare the printed USD P/L against
the Deribit UI's session P/L + fees for that trade.
