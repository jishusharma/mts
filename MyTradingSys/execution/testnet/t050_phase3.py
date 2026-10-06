"""
T050 phase 3, primitive-level (MyTradingSys/items/T050_deribit_execution_layer.md L141-146). TESTNET ONLY, default account.

buy()/sell()/cancel()/close_position() straight from deribit_orders - NOT through executor.py.
  T1a  buy 10 BTC-PERPETUAL limit at the exchange's own lower price band (~3% under mark): place, list, cancel,
       confirm zero open orders.
  T1b  sell 10 BTC-PERPETUAL market: place, confirm short 10, close_position, confirm size 0.
Writes the transcript + account-summary snapshots to MyTradingSys/research/testnet_status/T050_PHASE3_<date>.md.

Safety: refuses (BLOCKED, exit 2, no order placed) unless env is test, MTS_ACCOUNT is unset, and the default account
is flat with zero open orders - it never cancels or closes anything it did not create. On any failure it prints the raw
exception, exchange error code and an account snapshot, then stops: no retry, no remediation (exit 1).
Never prints the secret or the access token; summary snapshots are numeric-field whitelisted (no email/username/ids).

Run: python MyTradingSys/execution/testnet/t050_phase3.py
Exit: 0 PASS, 1 FAIL, 2 BLOCKED.
"""
import sys
sys.dont_write_bytecode = True

import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
import deribit_orders as do  # noqa: E402

ROOT = HERE.parents[3]
I = "BTC-PERPETUAL"
AMOUNT = 10  # BTC-PERPETUAL amount is USD notional; min_trade_amount 10
LABEL_LIMIT = "t050p3-limit"
LABEL_MKT = "t050p3-mkt"

SUMMARY_KEYS = ("currency", "equity", "balance", "available_funds", "margin_balance", "initial_margin",
                "maintenance_margin", "total_pl", "session_upl", "session_rpl", "futures_pl",
                "futures_session_upl", "futures_session_rpl", "delta_total")
ORDER_KEYS = ("order_id", "instrument_name", "direction", "order_type", "order_state", "amount", "filled_amount",
              "price", "average_price", "label", "time_in_force", "post_only", "reduce_only")
TRADE_KEYS = ("order_id", "direction", "amount", "price", "fee", "fee_currency", "liquidity")

LINES = []


def emit(msg=""):
    line = f"{datetime.now(timezone.utc).strftime('%H:%M:%S')}Z {msg}" if msg else ""
    print(line, flush=True)
    LINES.append(line)


class CheckFailed(Exception):
    pass


def check(name, cond, detail=""):
    emit(f"{'PASS' if cond else 'FAIL'} {name}" + (f" :: {detail}" if detail != "" else ""))
    if not cond:
        raise CheckFailed(f"{name} :: {detail}")


def pick(d, keys):
    return {k: d.get(k) for k in keys if isinstance(d, dict) and k in d}


def summary_snapshot(tok):
    return pick(do.get_account_summary(tok), SUMMARY_KEYS)


def open_orders_all(tok):
    return do._call("private/get_open_orders_by_currency", {"currency": "BTC"}, tok)


def position_size(tok):
    return do.get_position(tok, I).get("size", 0)


def ceil_tick(x, tick):
    return math.ceil(x / tick - 1e-9) * tick


def snapshot_after_failure(tok):
    emit("-- post-failure snapshot (read-only) --")
    for name, fn in (("position_size", lambda: position_size(tok)),
                     ("open_orders_BTC", lambda: [pick(o, ORDER_KEYS) for o in open_orders_all(tok)]),
                     ("account_summary", lambda: summary_snapshot(tok))):
        try:
            emit(f"{name}: {fn()}")
        except Exception as e:  # snapshot is best effort; never mask the original failure
            emit(f"{name}: snapshot failed {type(e).__name__}: {e}")


def write_log(verdict, before, after, started):
    day = started.strftime("%Y-%m-%d")
    path = ROOT / "MyTradingSys" / "research" / "testnet_status" / f"T050_PHASE3_{day}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    out = [f"# T050 phase 3 (primitive-level, Deribit TESTNET) {day}", "",
           f"Verdict: **{verdict}**  (started {started.strftime('%Y-%m-%dT%H:%M:%SZ')})",
           "Script: MyTradingSys/execution/testnet/t050_phase3.py - buy/sell/cancel/close_position from "
           "deribit_orders, not via executor.py. Default account, test.deribit.com.", ""]
    out += ["## Account summary (numeric whitelist)", "", "| field | before | after |", "|---|---|---|"]
    for k in SUMMARY_KEYS:
        if (before and k in before) or (after and k in after):
            out.append(f"| {k} | {(before or {}).get(k, '-')} | {(after or {}).get(k, '-')} |")
    out += ["", "## Transcript (stdout)", "", "```"] + LINES + ["```", ""]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    return path


def main():
    started = datetime.now(timezone.utc)
    before = after = None
    tok = None
    verdict = "FAIL"
    rc = 1
    try:
        do.select_environment(False)
        emit(f"env={do.active_env()} base={do._base()} account=default instrument={I} amount={AMOUNT}")
        if do.active_env() != "test" or not do._base().startswith("https://test.deribit.com/"):
            raise CheckFailed("not on testnet")
        verdict, rc = "BLOCKED", 2
        if os.environ.get("MTS_ACCOUNT"):
            raise CheckFailed("MTS_ACCOUNT is set: this script is default-account only")
        tok = do.authenticate()
        emit("authenticate OK (token not printed)")
        before = summary_snapshot(tok)
        emit(f"account_summary BEFORE: {before}")
        pre_pos, pre_orders = position_size(tok), open_orders_all(tok)
        emit(f"preflight: position_size={pre_pos} open_orders_BTC={len(pre_orders)}")
        if pre_pos != 0 or pre_orders:
            raise CheckFailed("default account not flat/clean; refusing to place anything")
        verdict, rc = "FAIL", 1

        # ---- T1a: limit far below mark: place, list, cancel
        emit("== T1a buy limit far below mark: place, list, cancel ==")
        tkr = do.get_ticker(I)
        inst = do._call("public/get_instrument", {"instrument_name": I})
        tick, mark, lo = inst["tick_size"], tkr["mark_price"], tkr["min_price"]
        price = max(ceil_tick(lo, tick), ceil_tick(mark * 0.95, tick))
        emit(f"mark={mark} min_price={lo} tick={tick} -> limit price {price} ({(mark - price) / mark * 100:.2f}% under mark)")
        check("limit price >= 2% under mark", (mark - price) / mark >= 0.02, f"price={price} mark={mark}")
        r = do.buy(tok, I, AMOUNT, "limit", price=price, label=LABEL_LIMIT)
        order = r["order"]
        emit(f"buy -> order={pick(order, ORDER_KEYS)} trades={len(r.get('trades', []))}")
        oid = order["order_id"]
        check("limit order resting, no immediate fill", order.get("order_state") == "open" and not r.get("trades")
              and order.get("filled_amount") == 0, f"state={order.get('order_state')}")
        opens = do.get_open_orders(tok, I)
        emit(f"get_open_orders -> {[pick(o, ORDER_KEYS) for o in opens]}")
        check("get_open_orders lists exactly the placed order", len(opens) == 1 and opens[0]["order_id"] == oid)
        c = do.cancel(tok, oid)
        emit(f"cancel -> {pick(c, ORDER_KEYS)}")
        check("cancel returns order_state=cancelled", c.get("order_state") == "cancelled", f"state={c.get('order_state')}")
        time.sleep(0.5)
        opens = do.get_open_orders(tok, I)
        check("zero open orders after cancel", len(opens) == 0, f"open={len(opens)}")
        check("position still 0 after T1a", position_size(tok) == 0)
        emit("T1a PASS")

        # ---- T1b: market sell then close_position
        emit("== T1b sell market 10, then close_position ==")
        pre_pos, pre_orders = position_size(tok), open_orders_all(tok)
        check("re-check flat/clean immediately before market sell", pre_pos == 0 and not pre_orders,
              f"pos={pre_pos} open={len(pre_orders)}")
        r = do.sell(tok, I, AMOUNT, "market", label=LABEL_MKT)
        emit(f"sell -> order={pick(r['order'], ORDER_KEYS)} trades={[pick(t, TRADE_KEYS) for t in r.get('trades', [])]}")
        check("market sell filled", r["order"].get("order_state") == "filled"
              and r["order"].get("filled_amount") == AMOUNT and r.get("trades"), f"state={r['order'].get('order_state')}")
        pos = do.get_position(tok, I)
        emit(f"get_position -> {pick(pos, ('instrument_name', 'direction', 'size', 'average_price', 'mark_price', 'floating_profit_loss'))}")
        check("position is short 10 after sell", pos.get("size") == -AMOUNT, f"size={pos.get('size')}")
        cp = do.close_position(tok, I)
        emit(f"close_position -> order={pick(cp.get('order', {}), ORDER_KEYS)} "
             f"trades={[pick(t, TRADE_KEYS) for t in cp.get('trades', [])]}")
        time.sleep(0.5)
        pos = position_size(tok)
        check("position size 0 after close_position", pos == 0, f"size={pos}")
        check("zero open orders at end", len(open_orders_all(tok)) == 0)
        emit("T1b PASS")
        after = summary_snapshot(tok)
        emit(f"account_summary AFTER: {after}")
        verdict, rc = "PASS", 0
    except Exception as e:
        code = getattr(e, "code", None)
        emit(f"{verdict} {type(e).__name__}: {e!r}")
        emit(f"exchange error code: {code} | raw error: {getattr(e, 'error', None)}")
        if tok:
            snapshot_after_failure(tok)
    emit(f"T050 PHASE3 {verdict}")
    path = write_log(verdict, before, after, started)
    print(f"log: {path}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
