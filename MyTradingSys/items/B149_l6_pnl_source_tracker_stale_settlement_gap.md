# B149 - L6 part 2 (daily-loss PnL source) is implemented but the tracker still says OPEN/DEFERRED, and the built source excludes settlement/funding and loses unrealised loss across the 08:00 settlement

Status: CLOSED 2026-10-10 (code in repo; JVM-free but live auto_trader/daily_loss_monitor Python processes load it at next restart, desk/supervisor task). Severity: MED. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

L6 part 2 (daily-loss PnL source) is implemented but the tracker still says OPEN/DEFERRED, and the built source excludes settlement/funding and loses unrealised loss across the 08:00 settlement.

## Evidence

- Commits 1542151 and 924d7a0 switched the PnL source to the transaction log plus session UPL (mainnet_pnl.py). research/fast_track_2026-09-27/OPEN_FINDINGS.md:31 still says OPEN / DEFERRED.
- mainnet_pnl.py allows only 'trade' entries, so settlement and funding are excluded, while the FIX4_DESIGN decision said to include them. The log window starts 00:00 UTC but futures_session_upl resets at the 08:00 UTC settlement, so an unrealised loss on a position held across 08:00 moves into an excluded settlement entry and drops out of the day total. Layer holds up to 8 bars (8 h at 1h) make this reachable. The --pnl-source help text (daily_loss_monitor.py:388) says 'equity on testnet', contradicting default_pnl_source (:235-242). Real Deribit semantics unverified (worker could not check live data).

## Fix shape

Verify against a captured testnet response across an 08:00 settlement; include settlement/funding as decided or record why not; fix the help text; update OPEN_FINDINGS L6. Must be closed before any mainnet use.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-10: (a) --pnl-source help now says transaction_log on testnet and mainnet whenever the client can read the log (test_daily_loss_monitor.TestHelpText fails on the old text); (b) OPEN_FINDINGS L6 states part 2 IMPLEMENTED with the settlement question open; (c) execution/capture_txlog_settlement.py (+ test, gated) captures type/change/cashflow/session_profit_loss for 36 h around a settlement. NOT verified: whether a settlement entry double counts the trade cashflow, or drops pre-08:00 unrealised loss. No code change to mainnet_pnl.py without that data. Desk task 20261009-205713-b149-capture-the-transaction-log-across- (JIS-NB).

Capture 2026-10-10 12:20Z (relay B, JIS-NB, read-only testnet, MTS_ACCOUNT=jishu_11 and jishu_13, --hours 36): research/loose_code/txlog_capture_2026-10-10_jishu_11.json, _jishu_13.json. (1) NO DOUBLE COUNT: S-mkt-1009-0731 (jishu_11, short 100 USD 82500 -> 82611.5, held 07:31-09:31Z 10-09) produced a settlement entry at 08:00:00Z cashflow -1.59e-06 BTC and a closing trade cashflow -4e-08; sum -1.63e-06 = the position's whole PnL 100*(1/82611.5-1/82500) = -1.636e-06. The settlement carries the pre-08:00 part, the close only the rest. (2) So mainnet_pnl.py's trade-only filter drops 1.59/1.63 = 97.5% of that day's loss: settlement entries must be INCLUDED. (3) Saturday 2026-10-10: S-mkt-1010-0715 (jishu_11) and L-mkt-1010-0745 (jishu_13) were open across 08:00 but the log has no settlement entry; their close cashflows (-3.05e-06, +6.28e-06) equal their full PnL (-3.053e-06, +6.277e-06), so including settlements cannot double count on such days either. (4) Entries carry no session_profit_loss field on testnet. (5) No funding-type entry appeared although the ledger shows funding_usd -0.0017 for L-mkt-1010-0745 (funding sits inside settlement/trade cashflow on perpetuals). Next: mainnet_pnl.py accepts type settlement (live-path change: test + gate).

2026-10-10 ~13:20Z (relay, dispatcher-run): mainnet_pnl.py ALLOWED_TX_TYPES now {trade, settlement}; settlement contributes change only. test_mainnet_pnl: 2 new tests fail on the old code (checked), 17 pass; daily_loss_monitor + wiring tests pass. Restart needed for the live monitor to pick it up (supervisor).

# END
