"""Outcome ledger: one JSONL row per CLOSED auto-trade, joining signal source, account, alert key, plan, entry fill,
exit fill(s), exit reason, gross/fees/funding/net P/L (USD) and hold time.

Operator order 2026-09-29: gates must not be loosened before outcomes are measurable per source.

Data: auto_trades.jsonl (source/key/side/account), the plan file (max_hold_minutes), the plan journal when it exists
(exit reason), and exchange fills through the existing read method get_user_trades_by_instrument_and_time
(testnet, per account; the account is selected with MTS_ACCOUNT exactly like the trader does). Read-only.

BTC-PERPETUAL is inverse (amount = USD contracts, P/L and fees settle in BTC). With entry VWAP E, exit VWAP X and
matched quantity q (USD): long gross USD = q * (X/E - 1), short gross USD = q * (1 - X/E)  (BTC pnl q*(1/E - 1/X)
valued at X). Fees are converted per fill at that fill's price. Funding = sum of transaction-log interest_pl for the
instrument in the fetch window x exit price; None when unavailable.

Usage (repo root):
  python -m MyTradingSys.execution.trade_ledger --backfill     # rows for closed plans found in auto_trades.jsonl
  python -m MyTradingSys.execution.trade_ledger --summary      # per-source n / win rate / mean net / sum net
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER_PATH = HERE / "trade_ledger.jsonl"
AUTO_LOG = HERE / "auto_trades.jsonl"
PLANS_DIR = HERE / "plans"
SECRETS_DIR = HERE / ".secrets"
INSTRUMENT = "BTC-PERPETUAL"


def _iso(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def _vwap(fills):
    q = sum(f["amount"] for f in fills)
    return (sum(f["amount"] * f["price"] for f in fills) / q) if q else None


def _fee_usd(t, share=1.0):
    fee = float(t.get("fee") or 0) * share
    if str(t.get("fee_currency") or "BTC").upper() == "BTC":
        return fee * float(t["price"])
    return fee


def classify_exit(events, exits, plan_max_hold_min, hold_min):
    """(reason, source). Journal first, then fill labels, then hold time vs the plan's time exit, else manual."""
    types = [e.get("event_type") for e in events or []]
    if "time_exit" in types:
        return "time_exit", "journal"
    for e in events or []:
        if e.get("event_type") == "mismatch_halt":
            why = str((e.get("data") or {}).get("reason", ""))
            return ("manual" if why.startswith("position flat but no stop") else "flatten_halt"), "journal"
    for e in events or []:
        if e.get("event_type") == "reconciliation":
            d = e.get("data") or {}
            if d.get("stop_state") == "triggered_by_fills":
                # position_manager folds the plan's reduce-side fill total (the STOP's own fill) into target_filled
                # on this fallback path, so target_filled is not evidence of a target: decide from the fill label.
                lab = str((exits[-1] if exits else {}).get("label") or "")
                return ("target" if ":target" in lab else "stop"), "journal"
            if d.get("target_filled"):
                return "target", "journal"
            if d.get("stop_state") not in (None, "time_exit"):
                return "stop", "journal"
    last = exits[-1] if exits else {}
    lab = str(last.get("label") or "")
    if ":target" in lab:
        return "target", "labels"
    if ":stop" in lab:
        return "stop", "labels"
    if plan_max_hold_min and hold_min is not None and hold_min >= plan_max_hold_min * 0.98:
        return "time_exit", "hold_time"
    return "manual", "labels"


def build_row(attempt, trades, events=None, plan=None, account=None, manager_rc=None, funding_btc=None, force=False):
    """Pure. attempt = the auto_trades trade_attempt row; trades = exchange fills (dicts with timestamp ms, price,
    amount, direction, label, fee, fee_currency). Returns a ledger row, or None if not (yet) a closed round trip."""
    plan_id = attempt["plan_id"]
    entries = sorted((t for t in trades if str(t.get("label") or "").startswith(f"{plan_id}:entry")),
                     key=lambda t: t["timestamp"])
    if not entries:
        return None
    entry_dir = str(entries[0]["direction"]).lower()
    side = "long" if entry_dir == "buy" else "short"
    entry_total = sum(t["amount"] for t in entries)
    t_entry = entries[0]["timestamp"]
    cand = sorted((t for t in trades if str(t["direction"]).lower() != entry_dir and t["timestamp"] >= t_entry),
                  key=lambda t: t["timestamp"])
    exits, left = [], entry_total
    for t in cand:
        if left <= 0:
            break
        take = min(t["amount"], left)
        exits.append({**t, "amount": take, "_full": t["amount"]})
        left -= take
    if not exits or (left > 0 and not force):
        return None
    qty = entry_total - left
    e_px, x_px = _vwap(entries), _vwap(exits)
    gross = qty * (x_px / e_px - 1) * (1 if side == "long" else -1)
    fees = sum(_fee_usd(t) for t in entries) + sum(_fee_usd(e, e["amount"] / e["_full"] if e["_full"] else 1)
                                                   for e in exits)
    hold = (exits[-1]["timestamp"] - t_entry) / 60000.0
    mh = (plan or {}).get("max_hold_minutes")
    reason, rsrc = classify_exit(events, exits, float(mh) if mh else None, hold)
    funding = None if funding_btc is None else funding_btc * x_px
    net = gross - fees + (funding or 0.0)
    return {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": attempt.get("source"), "account": account or attempt.get("account"),
        "alert_key": attempt.get("key"), "alert_ts": attempt.get("ts"),
        "plan_id": plan_id, "side": side,
        "entry": {"price": round(e_px, 2), "amount": entry_total, "ts": _iso(t_entry)},
        "exits": [{"price": t["price"], "amount": t["amount"], "ts": _iso(t["timestamp"]),
                   "label": t.get("label")} for t in exits],
        "exit_reason": reason, "exit_reason_src": rsrc,
        "gross_pnl_usd": round(gross, 4), "fees_usd": round(fees, 4),
        "funding_usd": None if funding is None else round(funding, 4),
        "net_pnl_usd": round(net, 4), "hold_minutes": round(hold, 2), "manager_rc": manager_rc,
        "partial": left > 0,
    }


# ---------------------------------------------------------------- exchange + file access

def fetch_exchange(plan_id, account, t_from_s, t_to_s=None, instrument=INSTRUMENT):
    """(trades, funding_btc) from the testnet account via existing read methods. Raises on auth/read failure."""
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import deribit_orders as do
    prev = os.environ.get("MTS_ACCOUNT")
    if account:
        os.environ["MTS_ACCOUNT"] = account
    else:
        os.environ.pop("MTS_ACCOUNT", None)
    try:
        token = do.authenticate()
        t1 = int(((t_to_s or time.time()) + 120) * 1000)
        t0 = int(t_from_s * 1000)
        trades = do.get_user_trades_by_instrument_and_time(token, instrument, t0, t1)
        funding = None
        try:
            tlog = do.get_transaction_log(token, "BTC", t0, t1)
            funding = sum(float(e.get("interest_pl") or 0) for e in tlog if e.get("instrument_name") == instrument)
        except Exception:  # noqa: BLE001 - funding is optional
            funding = None
        return trades, funding
    finally:
        if prev is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = prev


def _journal_events(plan_id):
    try:
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        import journal
        return journal.read_events(plan_id)
    except Exception:  # noqa: BLE001
        return []


def _plan(plan_id):
    try:
        return json.loads((PLANS_DIR / f"{plan_id}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def existing_plan_ids(path=None):
    """Plan ids with a RESOLVED row. Rows carrying "unresolved" do not count: a later run may supersede them."""
    return {r.get("plan_id") for r in _read_jsonl(path or LEDGER_PATH) if not r.get("unresolved")}


def unresolved_row(attempt, account, reason, manager_rc=None):
    """A ledger row for a plan whose outcome could not be computed (never drop a trade silently)."""
    return {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": attempt.get("source"), "account": account or attempt.get("account"),
            "alert_key": attempt.get("key"), "alert_ts": attempt.get("ts"), "plan_id": attempt["plan_id"],
            "side": attempt.get("side"), "exit_reason": None, "net_pnl_usd": None, "manager_rc": manager_rc,
            "unresolved": reason}


def append_row(row, path=None):
    with open(path or LEDGER_PATH, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row) + "\n")


def attempt_for(plan_id, auto_log=None):
    for r in reversed(_read_jsonl(auto_log or AUTO_LOG)):
        if r.get("event") == "trade_attempt" and r.get("plan_id") == plan_id and r.get("outcome") == "entered":
            return dict(r)
    return None


def record_closed(plan_id, source=None, account=None, manager_rc=None, fetcher=None, ledger_path=None,
                  auto_log=None, events=None, plan=None, force=True, write_unresolved=True):
    """Write the ledger row for a closed plan (idempotent per plan_id). Always writes a row: when the outcome cannot
    be computed (fetch failure, no fills, position not flat) the row carries "unresolved": reason.
    Returns the row, or None if the plan already has a resolved row. write_unresolved=False (backfill probing)
    raises fetch errors and returns None instead."""
    ledger_path = ledger_path or LEDGER_PATH
    if plan_id in existing_plan_ids(ledger_path):
        return None
    attempt = attempt_for(plan_id, auto_log) or {"plan_id": plan_id}
    if source and not attempt.get("source"):
        attempt["source"] = source
    account = account or attempt.get("account")
    t_from = time.time()
    if attempt.get("ts"):
        try:
            t_from = datetime.strptime(attempt["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass
    try:
        trades, funding = (fetcher or fetch_exchange)(plan_id, account, t_from - 7200)
    except Exception as e:  # noqa: BLE001
        if not write_unresolved:
            raise
        row = unresolved_row(attempt, account, "exchange read failed: " + repr(e)[:160], manager_rc)
        append_row(row, ledger_path)
        return row
    row = build_row(attempt, trades, _journal_events(plan_id) if events is None else events,
                    _plan(plan_id) if plan is None else plan, account, manager_rc, funding, force=force)
    if row is None:
        if not write_unresolved:
            return None
        row = unresolved_row(attempt, account, "no closed round trip found in exchange fills (position may still be "
                             "open or entry fill missing)", manager_rc)
    append_row(row, ledger_path)
    return row


def account_candidates(attempt_account=None):
    """Account labels to probe for a plan whose account was not logged. Filenames only, never contents."""
    if attempt_account:
        return [attempt_account]
    labels = [None]
    try:
        cfg = json.loads((HERE / "auto_trader_config.json").read_text(encoding="utf-8"))
        labels += list((cfg.get("accounts") or {}).values())
    except (OSError, ValueError):
        pass
    if SECRETS_DIR.exists():
        for p in sorted(SECRETS_DIR.glob("testnet_*.secret.json")):
            labels.append(p.name[len("testnet_"):-len(".secret.json")])
    seen, out = set(), []
    for lab in labels:
        if lab not in seen:
            seen.add(lab)
            out.append(lab)
    return out


def backfill(fetcher=None, ledger_path=None, auto_log=None, candidates=None):
    """Rows for every entered plan in auto_trades.jsonl that is a closed round trip on some account.
    Returns (rows_added, unresolved_plan_ids)."""
    auto_log = auto_log or AUTO_LOG
    ledger_path = ledger_path or LEDGER_PATH
    log_rows = _read_jsonl(auto_log)
    done = existing_plan_ids(ledger_path)
    added, unresolved, seen = [], [], set()
    for a in log_rows:
        pid = a.get("plan_id")
        if a.get("event") != "trade_attempt" or a.get("outcome") != "entered" or pid in done or pid in seen:
            continue
        seen.add(pid)
        closed = next((c for c in log_rows if c.get("event") == "trade_closed" and c.get("plan_id") == pid), {})
        acct_hint = a.get("account") or closed.get("account")
        got = None
        for acct in (candidates or account_candidates)(acct_hint):
            try:
                row = record_closed(pid, a.get("source"), acct, closed.get("manager_rc"), fetcher, ledger_path,
                                    auto_log, force=False, write_unresolved=False)
            except Exception:  # noqa: BLE001 - wrong account / auth failure: try the next
                continue
            if row:
                got = row
                break
        if got:
            added.append(got)
        else:
            unresolved.append(pid)
            if pid not in {r.get("plan_id") for r in _read_jsonl(ledger_path)}:
                append_row(unresolved_row(a, acct_hint, "backfill: no closed round trip on any probed account",
                                          closed.get("manager_rc")), ledger_path)
    return added, unresolved


def summarize(rows):
    """{source: {n, wins, win_rate, mean_net, sum_net}}; a win is net P/L > 0."""
    out = {}
    for r in rows:
        if r.get("unresolved"):
            continue
        s = out.setdefault(r.get("source") or "?", {"n": 0, "wins": 0, "sum_net": 0.0})
        s["n"] += 1
        s["sum_net"] += r.get("net_pnl_usd") or 0.0
        s["wins"] += 1 if (r.get("net_pnl_usd") or 0.0) > 0 else 0
    for s in out.values():
        s["win_rate"] = s["wins"] / s["n"]
        s["mean_net"] = round(s["sum_net"] / s["n"], 4)
        s["sum_net"] = round(s["sum_net"], 4)
    return out


def print_summary(path=None):
    rows = _read_jsonl(path or LEDGER_PATH)
    if not rows:
        print("ledger empty")
        return
    print(f"{'source':<38} {'n':>3} {'win%':>6} {'mean net':>10} {'sum net':>10}")
    for src, s in sorted(summarize(rows).items()):
        print(f"{src:<38} {s['n']:>3} {s['win_rate'] * 100:>5.0f}% {s['mean_net']:>10.4f} {s['sum_net']:>10.4f}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args(argv)
    if a.backfill:
        added, unresolved = backfill()
        print(f"backfill: {len(added)} row(s) added, {len(unresolved)} unresolved {unresolved}")
    print_summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
