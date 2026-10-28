"""B149: read-only capture of the transaction log + account summary around an 08:00 UTC settlement, so mainnet_pnl.py's
settlement handling can be verified against real Deribit data instead of docs.

Testnet only, no order calls, nothing written outside --out. Run once on the host that holds the testnet secrets,
after a day in which a position was open across 08:00 UTC (daily_loss_monitor logs show it):
  python MyTradingSys/execution/capture_txlog_settlement.py --hours 36 --out MyTradingSys/research/txlog_capture_<date>.json
The file keeps per entry: type, ts (UTC), change, cashflow, profit_as_cashflow, session_profit_loss, instrument. No keys, no ids.
`summarize` counts per type and lists the settlement entries so the double-count question can be answered from the numbers.
"""
import json
import sys
import time
from datetime import datetime, timezone

sys.dont_write_bytecode = True

KEEP = ("type", "change", "cashflow", "profit_as_cashflow", "session_profit_loss", "instrument_name", "currency")


def slim(entry):
    ts = entry.get("timestamp")
    out = {k: entry.get(k) for k in KEEP if k in entry}
    if isinstance(ts, (int, float)) and not isinstance(ts, bool):
        out["ts_utc"] = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def summarize(entries):
    by_type = {}
    for e in entries:
        by_type[e.get("type")] = by_type.get(e.get("type"), 0) + 1
    return {"count": len(entries), "by_type": by_type, "settlements": [e for e in entries if e.get("type") == "settlement"]}


def capture(client, token, summary_fn, hours, now_ms=None, currency="BTC"):
    now_ms = int(time.time() * 1000) if now_ms is None else now_ms
    entries = client.get_transaction_log(token, currency, now_ms - int(hours * 3600 * 1000), now_ms)
    slim_entries = [slim(e) for e in entries]
    return {"captured_utc": datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "hours": hours, "currency": currency, "entries": slim_entries, "summary": summarize(slim_entries),
            "account_summary": summary_fn()}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hours", type=float, default=36.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--currency", default="BTC")
    args = ap.parse_args(argv)
    import deribit_orders as do
    if do.active_env() != "test":
        print("REFUSED: testnet only")
        return 1
    token = do.authenticate()
    res = capture(do, token, lambda: {k: v for k, v in do.get_account_summary(token, args.currency).items()
                                      if k in ("equity", "balance", "futures_session_upl", "session_upl", "futures_session_rpl",
                                               "session_rpl", "currency")},
                  args.hours, currency=args.currency)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res["summary"]["by_type"]), "->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
