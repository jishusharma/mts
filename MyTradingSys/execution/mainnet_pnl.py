"""Pure arithmetic, BTC units, no I/O; quotes the Deribit field semantics below (docs.deribit.com, fetched 2026-09-29):
  - transaction log `change`: "Change in cash balance for this entry. ... otherwise cashflow - commission."
  - `cashflow`: "Signed cash-related amount for this entry, in the log currency."
  - `profit_as_cashflow`: "Present on trades. true on future trades when realized session PnL is carried in cashflow and has not yet been settled."
  - account summary `futures_session_upl`: "Session unrealized profit and loss for open futures and perpetual positions." `session_upl` is the all-instrument version.
So a futures trade's realized P/L is invisible in `change` (only the fee is there) until the daily 08:00 UTC settlement; it is in `cashflow` while profit_as_cashflow is true.

ALLOWED_TX_TYPES = frozenset({"trade", "settlement"}). Allow-list, not deny-list: every other type (deposit, withdrawal, transfer, swap, correction, reward, insurance and anything new) is ignored. `settlement` is INCLUDED (B149, captured testnet log research/loose_code/txlog_capture_2026-10-10_jishu_11.json): at the 08:00 UTC settlement Deribit books the pre-08:00 session P/L of a held position as a settlement entry (change == cashflow, e.g. -1.59e-06), and the later closing trade carries only the rest (cashflow -4e-08); the two sum to the position's whole P/L, so there is no double count. A settlement entry contributes `change` only (its cashflow equals change and is never added again)."""
import sys
sys.dont_write_bytecode = True


ALLOWED_TX_TYPES = frozenset({"trade", "settlement"})


def realized_btc(entries) -> float:
    """Sum over entries. An entry counts only if str(entry.get("type") or "").lower() is in ALLOWED_TX_TYPES;
    other entries are skipped and NOT validated (they may lack fields). A counted entry contributes `change`,
    plus `cashflow` when entry.get("profit_as_cashflow") is True (identity check `is True`; type "trade" only: a
    settlement entry contributes `change` alone). `change` must be
    an int or float and not a bool, else raise ValueError(f"transaction_log entry {i} (type=...) has no numeric 'change'")
    with i the index in the list. When profit_as_cashflow is True, `cashflow` must also be a non-bool int/float,
    else ValueError. Empty list returns 0.0. Return a float."""
    total = 0.0
    for i, entry in enumerate(entries):
        typ = str(entry.get("type") or "").lower()
        if typ not in ALLOWED_TX_TYPES:
            continue
        change = entry.get("change")
        if not isinstance(change, (int, float)) or isinstance(change, bool):
            raise ValueError(f"transaction_log entry {i} (type={typ}) has no numeric 'change'")
        total += change
        if typ == "trade" and entry.get("profit_as_cashflow") is True:
            cashflow = entry.get("cashflow")
            if not isinstance(cashflow, (int, float)) or isinstance(cashflow, bool):
                raise ValueError(f"transaction_log entry {i} (type={typ}) has no numeric 'cashflow'")
            total += cashflow
    return total


def unrealized_btc(summary) -> float:
    """Use summary["futures_session_upl"] if that key is present, else summary["session_upl"] if present,
    else raise ValueError("account summary has no futures_session_upl or session_upl"). The chosen value must be
    a non-bool int/float, else ValueError. (A present-but-invalid futures_session_upl raises; it does NOT fall back.)
    Return float(value)."""
    if "futures_session_upl" in summary:
        upl = summary["futures_session_upl"]
        if not isinstance(upl, (int, float)) or isinstance(upl, bool):
            raise ValueError("account summary has no futures_session_upl or session_upl")
        return float(upl)
    elif "session_upl" in summary:
        upl = summary["session_upl"]
        if not isinstance(upl, (int, float)) or isinstance(upl, bool):
            raise ValueError("account summary has no futures_session_upl or session_upl")
        return float(upl)
    else:
        raise ValueError("account summary has no futures_session_upl or session_upl")


def daily_pnl_btc(entries, summary) -> float:
    """Return realized_btc(entries) + unrealized_btc(summary). Both parts are always evaluated,
    so an unreadable summary raises even when the log is fine."""
    return realized_btc(entries) + unrealized_btc(summary)
