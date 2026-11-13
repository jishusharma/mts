"""plan.py - build the US-open plan (JSON + markdown) from gathered levels. TESTNET module, no exchange call here.

build_plan(gathered, day, leverage=50) -> plan dict (DESIGN.md section 1); raises PlanRefused when the stop sits too
close to liquidation. render_md(plan, gathered) -> markdown. CLI:
    python MyTradingSys/execution/us_open_trader/plan.py --day YYYY-MM-DD --out-dir <dir> [--now <UTC iso>] [--leverage 50]
"""
import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # MyTradingSys/execution (risk_guard)
import levels as lv  # noqa: E402
import risk_guard  # noqa: E402

ARM_UTC = "13:35"          # OURS: 5 min after PPI-style 13:30Z data, 55 min before the 14:30Z cash open
FLAT_UTC = "16:30"         # OURS: 2 h after the cash open
MAX_ENTRIES = 3            # OURS (cotrade "one at a time")
AMOUNT_USD = 5000          # OURS (cap; actual = min(this, risk_guard.MAX_ACCOUNT_NOTIONAL_USD / 2))
LEVERAGE = 50              # OURS
BE_AT_R = 1.0              # SOURCED (research/habib_concept_book_2026-11/HABIB_CONCEPT_BOOK.md:38, C11 break-even after TP1)
FEE_PER_SIDE = 0.0005      # OURS (taker fee assumption)
BREAKOUT_ATR = 0.2         # OURS: breakout trigger = session high/low +- 0.2 * ATR15
STOP_ATR = 1.0             # OURS: stop distance = 1 * ATR15
STOP_MIN_PCT = 0.0008      # SOURCED (research/imbalance_qriptal_2026-10-16/discord/README.md:15, Habib range 0.08 %)
STOP_MAX_PCT = 0.0143      # SOURCED (same file, Habib range 1.43 %)
TARGET_R = 2.0             # OURS: target = 2 * stop_dist unless the next level is nearer
LEVEL_BUFFER = 20          # OURS: exit / fade 20 USD in front of a level
MIN_TARGET_R = 1.0         # OURS: skip an order whose target is under 1R
MAX_STOP_LEVERAGE = 0.5    # OURS: stop_dist/price*leverage must stay below 0.5 (stop far inside liquidation)
ROUND = 10                 # OURS: trigger and stop rounded to 10 USD
CONFLUENCE_ATR = 0.5       # OURS: another level within 0.5 * ATR15 of the order's level counts as confluence


class PlanRefused(ValueError):
    """The plan must not be traded (stop too close to liquidation)."""


def _r10(x):
    return int(round(x / ROUND)) * ROUND


def _amount():
    return min(AMOUNT_USD, risk_guard.MAX_ACCOUNT_NOTIONAL_USD / 2)  # read at call time: one place to tune


def _by_name(levels, name):
    return next((l for l in levels if l["name"] == name), None)


def _confluence(levels, ref, first, atr15):
    out = [first]
    for l in levels:
        tag = "%s:%s" % ("analyst" if l["source"] == "analyst" else "live_aid", l["name"])
        if tag != first and abs(l["price"] - ref) <= CONFLUENCE_ATR * atr15:
            out.append(tag)
    return out


def _fmt(x):
    return format(int(round(x)), ",")


def build_plan(gathered, day, leverage=LEVERAGE):
    price, atr15, levels = gathered["price"], gathered["atr15"], gathered["levels"]
    day = day.isoformat() if hasattr(day, "isoformat") else str(day)
    lo_stop = math.ceil(price * STOP_MIN_PCT / ROUND) * ROUND   # floor, kept on the 10 grid, never below the 0.08 %
    hi_stop = math.floor(price * STOP_MAX_PCT / ROUND) * ROUND  # cap, kept on the 10 grid, never above the 1.43 %
    stop = min(max(_r10(STOP_ATR * atr15), lo_stop), hi_stop)
    if stop / price * leverage >= MAX_STOP_LEVERAGE:
        raise PlanRefused("stop %d is %.1f %% of price; x%d leverage = %.2f >= %.2f, too close to liquidation"
                          % (stop, stop / price * 100, leverage, stop / price * leverage, MAX_STOP_LEVERAGE))
    skipped, orders = [], []
    sides = (("A", "buy", "EU_HIGH", 1, "Europe high"), ("B", "sell", "EU_LOW", -1, "Europe low"))
    for oid, side, name, sgn, text in sides:
        ref = _by_name(levels, name)
        if not ref:
            skipped.append({"id": oid, "reason": "no %s level" % name})
            continue
        trig = _r10(ref["price"] + sgn * BREAKOUT_ATR * atr15)
        beyond = [l["price"] for l in levels if (l["price"] - trig) * sgn > 0]
        raw = TARGET_R * stop
        if beyond:
            nxt = min(beyond, key=lambda p: abs(p - trig))
            raw = min(raw, abs(nxt - trig) - LEVEL_BUFFER)
        target = int(raw)
        if target < MIN_TARGET_R * stop:
            skipped.append({"id": oid, "reason": "target %d under %.0fR (%d): next level too close" % (target, MIN_TARGET_R, stop)})
            continue
        orders.append({"id": oid, "side": side, "kind": "breakout", "trigger": trig, "stop_dist": stop, "target_dist": target,
                       "level": ref["label"], "confluence": _confluence(levels, ref["price"], "live_aid:" + name, atr15), "arm_after": None})
    for oid, parent, side in (("C", "A", "sell"), ("D", "B", "buy")):
        par = next((o for o in orders if o["id"] == parent), None)
        if not par:
            continue  # a fade needs its breakout: it arms only after that breakout is done
        sgn = 1 if par["side"] == "buy" else -1
        edge = par["trigger"] + sgn * par["target_dist"]
        cl = [l for l in levels if l["source"] == "analyst" and (l["price"] - edge) * sgn > 0]
        if not cl:
            skipped.append({"id": oid, "reason": "no analyst cluster beyond the %s target %d" % (parent, edge)})
            continue
        c = min(cl, key=lambda l: abs(l["price"] - edge))
        orders.append({"id": oid, "side": side, "kind": "fade", "trigger": int(round(c["price"] - sgn * LEVEL_BUFFER)), "stop_dist": stop,
                       "target_dist": int(TARGET_R * stop), "level": c["label"],
                       "confluence": _confluence(levels, c["price"], "analyst:" + c["name"], atr15), "arm_after": parent})
    notes = []
    if gathered.get("analyst_note"):
        notes.append(gathered["analyst_note"])
    return {"day": day, "frozen_utc": gathered.get("frozen_utc", ""), "ref_feed": "binance_spot_BTCUSDT", "instrument": "BTC-PERPETUAL",
            "arm_utc": ARM_UTC, "flat_utc": FLAT_UTC, "max_entries": MAX_ENTRIES, "amount_usd": _amount(), "leverage": leverage,
            "be_at_r": BE_AT_R, "fee_per_side": FEE_PER_SIDE, "orders": sorted(orders, key=lambda o: o["id"]),
            "skipped": skipped, "notes": notes}


def render_md(plan, gathered):
    amt, lev = plan["amount_usd"], plan["leverage"]
    price, atr15, atr1h = gathered["price"], gathered["atr15"], gathered["atr1h"]
    o = ["# US open plan, %s (us_open_trader, TESTNET)" % plan["day"], "",
         "Frozen %s, before the 14:30Z cash open. BTC %s (Binance spot, public data). Mode: dry run (paper) unless the "
         "operator says otherwise. Not a forecast and not a measured edge: testnet-forward calibration." % (plan["frozen_utc"], _fmt(price)), ""]
    if gathered.get("analyst_note"):
        o += ["NOTE: " + gathered["analyst_note"], ""]
    o += ["## Levels", "", "| side | price | what | source |", "|---|---|---|---|"]
    for l in gathered["levels"]:
        side = "above" if l["price"] > price else "below"
        src = {"analyst": "SOURCED analyst_levels.py", "session": "Live Aid daily_playbook.py (OURS windows)",
               "key": "Live Aid key_levels (OURS)"}[l["source"]]
        o.append("| %s | %s | %s | %s |" % (side, _fmt(l["price"]), l["label"], src))
    o += ["", "Volatility: ATR(14) 15m = %s, 1h = %s (Wilder, closed bars)." % (_fmt(atr15), _fmt(atr1h)), "",
          "## Orders (one position at a time, %s, %s USD = %s USD margin at %dx)" % (plan["instrument"], _fmt(amt), _fmt(amt / lev), lev), "",
          "| id | side | kind | trigger | hard stop | target | risk | reward | why this level |", "|---|---|---|---|---|---|---|---|---|"]
    for r in plan["orders"]:
        sg = 1 if r["side"] == "buy" else -1
        e = r["trigger"]
        o.append("| %s | %s | %s | %s | %s (%s%d) | %s (%s%d) | %.0f USD | %.0f USD | %s |" % (
            r["id"], "long" if sg > 0 else "short", r["kind"], _fmt(e), _fmt(e - sg * r["stop_dist"]), "-" if sg > 0 else "+", r["stop_dist"],
            _fmt(e + sg * r["target_dist"]), "+" if sg > 0 else "-", r["target_dist"], amt * r["stop_dist"] / e, amt * r["target_dist"] / e, r["level"]))
    if not plan["orders"]:
        o.append("| - | - | - | - | - | - | - | - | no order could be built |")
    if plan["skipped"]:
        o += ["", "Not built:", ""] + ["- %s: %s" % (s["id"], s["reason"]) for s in plan["skipped"]]
    stop = plan["orders"][0]["stop_dist"] if plan["orders"] else 0
    if stop:
        o += ["", "Stop %d = about %.2f x ATR(15m) = %.2f %% of price (Habib range 0.08 - 1.43 %%); at %dx the liquidation distance is about %.1f %%, "
              "so the stop is %.1f times closer. Loss at the stop = %.0f %% of margin." % (
                  stop, stop / atr15, stop / price * 100, lev, 100 / lev, (100 / lev) / (stop / price * 100), amt * stop / price / (amt / lev) * 100)]
    o += ["", "## Rules", "", "| # | rule | label |", "|---|---|---|",
          "| 1 | Armed %sZ to %sZ; nothing new after %sZ | OURS |" % (plan["arm_utc"], plan["flat_utc"], plan["flat_utc"]),
          "| 2 | One position at a time; at most %d entries | OURS (cotrade one at a time) |" % plan["max_entries"],
          "| 3 | Breakout trigger = Europe high/low +- 0.2 x ATR(15m), rounded to 10 | OURS |",
          "| 4 | Stop = 1 x ATR(15m), floored at 0.08 %% and capped at 1.43 %% of price | SOURCED Habib range (`imbalance_qriptal_2026-10-16/discord/README.md:15`), 1 x ATR OURS |",
          "| 5 | Target = 2 x stop, or 20 in front of the next level if nearer; an order whose target is under 1R is skipped | OURS |",
          "| 6 | Fades sit 20 in front of the first analyst cluster beyond a breakout target, target 2 x stop, armed only after that breakout is closed | OURS |",
          "| 7 | After a target hit both breakouts are cancelled; after a stop-out the opposite breakout stays armed | OURS |",
          "| 8 | Hard server-side stop on every fill, never widened | SOURCED Habib C11 hard structure stop (`habib_concept_book_2026-11/HABIB_CONCEPT_BOOK.md:38`) |",
          "| 9 | At +1R move the stop to entry | SOURCED Habib C11 break-even after TP1 (same file) |",
          "| 10 | Size: min(5,000, half of the account notional cap) USD; plan refused when stop/price x leverage >= 0.5 | OURS |",
          "| 11 | Time stop: flat at %sZ at market | OURS |" % plan["flat_utc"],
          "| 12 | Levels are read on Binance spot; the order goes on Deribit testnet at the same distances | OURS |", ""]
    return "\n".join(o)


def write(plan, gathered, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / ("plan_%s.json" % plan["day"])).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out / ("PLAN_US_OPEN_%s.md" % plan["day"])).write_text(render_md(plan, gathered), encoding="utf-8", newline="\n")


def main(argv=None, fetch=None, analysts=None):
    ap = argparse.ArgumentParser(description="Build the US-open plan (testnet module).")
    ap.add_argument("--day", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--now", help="UTC time ISO (default: the clock)")
    ap.add_argument("--leverage", type=int, default=LEVERAGE)
    a = ap.parse_args(argv)
    now = dt.datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else dt.datetime.now(lv.UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=lv.UTC)
    g = lv.gather(a.day, now, fetch=fetch, analysts=analysts)
    try:
        plan = build_plan(g, a.day, leverage=a.leverage)
    except PlanRefused as ex:
        print("PLAN REFUSED: %s" % ex, file=sys.stderr)
        return 2
    write(plan, g, a.out_dir)
    print("plan %s: %d orders (%s), %d not built -> %s" % (plan["day"], len(plan["orders"]), ",".join(o["id"] for o in plan["orders"]),
                                                          len(plan["skipped"]), a.out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
