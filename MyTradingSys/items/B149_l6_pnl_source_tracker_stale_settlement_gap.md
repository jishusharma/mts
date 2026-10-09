# B149 - L6 part 2 (daily-loss PnL source) is implemented but the tracker still says OPEN/DEFERRED, and the built source excludes settlement/funding and loses unrealised loss across the 08:00 settlement

Status: BLOCKED. Severity: MED. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

L6 part 2 (daily-loss PnL source) is implemented but the tracker still says OPEN/DEFERRED, and the built source excludes settlement/funding and loses unrealised loss across the 08:00 settlement.

## Evidence

- Commits 1542151 and 924d7a0 switched the PnL source to the transaction log plus session UPL (mainnet_pnl.py). research/fast_track_2026-09-27/OPEN_FINDINGS.md:31 still says OPEN / DEFERRED.
- mainnet_pnl.py allows only 'trade' entries, so settlement and funding are excluded, while the FIX4_DESIGN decision said to include them. The log window starts 00:00 UTC but futures_session_upl resets at the 08:00 UTC settlement, so an unrealised loss on a position held across 08:00 moves into an excluded settlement entry and drops out of the day total. Layer holds up to 8 bars (8 h at 1h) make this reachable. The --pnl-source help text (daily_loss_monitor.py:388) says 'equity on testnet', contradicting default_pnl_source (:235-242). Real Deribit semantics unverified (worker could not check live data).

## Fix shape

Verify against a captured testnet response across an 08:00 settlement; include settlement/funding as decided or record why not; fix the help text; update OPEN_FINDINGS L6. Must be closed before any mainnet use.

## Related

- MyTradingSys/research/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-10: (a) --pnl-source help now says transaction_log on testnet and mainnet whenever the client can read the log (test_daily_loss_monitor.TestHelpText fails on the old text); (b) OPEN_FINDINGS L6 states part 2 IMPLEMENTED with the settlement question open; (c) execution/capture_txlog_settlement.py (+ test, gated) captures type/change/cashflow/session_profit_loss for 36 h around a settlement. NOT verified: whether a settlement entry double counts the trade cashflow, or drops pre-08:00 unrealised loss. No code change to mainnet_pnl.py without that data. Desk task 20261009-205713-b149-capture-the-transaction-log-across- (JIS-NB).

# END
