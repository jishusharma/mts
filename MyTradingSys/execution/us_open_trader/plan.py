"""plan.py - build the US-open plan (JSON + markdown) from gathered levels. TESTNET module, no exchange call here.

build_plan(gathered, day, risk_usd=18) -> plan dict (DESIGN.md section 1 + V2-5: no leverage input, size from risk);
raises PlanRefused when the risk-sized amount rounds to zero. render_md(plan, gathered, know=None) -> markdown;
knowledge_md(day) -> the "What we already know" section (reads files at build time, never crashes). CLI:
    python MyTradingSys/execution/us_open_trader/plan.py --day YYYY-MM-DD --out-dir <dir> [--now <UTC iso>] [--risk-usd 18]
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # MyTradingSys/execution (risk_guard)
import open_levels as lv  # noqa: E402
import risk_guard  # noqa: E402

ARM_UTC = "13:35"          # OURS: 5 min after PPI-style 13:30Z data, 55 min before the 14:30Z cash open
FLAT_UTC = "16:30"         # OURS: 2 h after the cash open
MAX_ENTRIES = 3            # OURS (cotrade "one at a time")
RISK_USD = 18              # OURS (V2-5: loss at the stop; amount_usd = round_down_to_10(risk_usd * price / stop_dist), capped below)
AMOUNT_CAP_DIV = 2         # OURS: amount capped at risk_guard.MAX_ACCOUNT_NOTIONAL_USD / 2
AMOUNT_STEP = 10           # SOURCED (Deribit BTC-PERPETUAL contract size is 10 USD)
KNOW_BIBLE_LINES = 3       # SOURCED (task: quote at most 3 short lines from the Bible)
KNOW_LEDGER_MAX = 8        # OURS: at most 8 open scenario rows listed
KNOW_LINE_CHARS = 160      # OURS: every quoted line is cut to this length
BE_AT_R = 1.0              # SOURCED (research/habib_concept_book_2026-11/HABIB_CONCEPT_BOOK.md:38, C11 break-even after TP1)
FEE_PER_SIDE = 0.0005      # OURS (taker fee assumption)
BREAKOUT_ATR = 0.2         # OURS: breakout trigger = session high/low +- 0.2 * ATR15
STOP_ATR = 1.0             # OURS: stop distance = 1 * ATR15
STOP_MIN_PCT = 0.0008      # SOURCED (research/imbalance_qriptal_2026-10-16/discord/README.md:15, Habib range 0.08 %)
STOP_MAX_PCT = 0.0143      # SOURCED (same file, Habib range 1.43 %)
TARGET_R = 2.0             # OURS: target = 2 * stop_dist unless the next level is nearer
LEVEL_BUFFER = 20          # OURS: exit / fade 20 USD in front of a level
MIN_TARGET_R = 1.0         # OURS: skip an order whose target is under 1R
ROUND = 10                 # OURS: trigger and stop rounded to 10 USD
CONFLUENCE_ATR = 0.5       # OURS: another level within 0.5 * ATR15 of the order's level counts as confluence


class PlanRefused(ValueError):
    """The plan must not be traded (risk-sized amount rounds to zero)."""


def _r10(x):
    return int(round(x / ROUND)) * ROUND


def _amount(risk_usd, price, stop):
    """V2-5: round_down_to_10(risk_usd * price / stop_dist), capped at half the account notional cap (read at call time)."""
    raw = int(risk_usd * price / stop // AMOUNT_STEP * AMOUNT_STEP)
    return int(min(raw, risk_guard.MAX_ACCOUNT_NOTIONAL_USD / AMOUNT_CAP_DIV))


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


def build_plan(gathered, day, risk_usd=RISK_USD):
    price, atr15, levels = gathered["price"], gathered["atr15"], gathered["levels"]
    day = day.isoformat() if hasattr(day, "isoformat") else str(day)
    lo_stop = math.ceil(price * STOP_MIN_PCT / ROUND) * ROUND   # floor, kept on the 10 grid, never below the 0.08 %
    hi_stop = math.floor(price * STOP_MAX_PCT / ROUND) * ROUND  # cap, kept on the 10 grid, never above the 1.43 %
    stop = min(max(_r10(STOP_ATR * atr15), lo_stop), hi_stop)
    amount = _amount(risk_usd, price, stop)
    if amount < AMOUNT_STEP:
        raise PlanRefused("risk %s USD at stop %d on price %d sizes to %d USD, under one %d USD contract" % (risk_usd, stop, price, amount, AMOUNT_STEP))
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
            "arm_utc": ARM_UTC, "flat_utc": FLAT_UTC, "max_entries": MAX_ENTRIES, "risk_usd": risk_usd, "amount_usd": amount,
            "be_at_r": BE_AT_R, "fee_per_side": FEE_PER_SIDE, "orders": sorted(orders, key=lambda o: o["id"]),
            "skipped": skipped, "notes": notes}


def render_md(plan, gathered, know=None):
    amt = plan["amount_usd"]
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
          "## Orders (one position at a time, %s, %s USD notional, risk %s USD at the stop)" % (plan["instrument"], _fmt(amt), _fmt(plan["risk_usd"])), "",
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
        o += ["", "Stop %d = about %.2f x ATR(15m) = %.2f %% of price (Habib range 0.08 - 1.43 %%). Size = risk %s USD x price / stop, rounded down "
              "to 10 USD, capped at half the account notional cap. No leverage is set: %s is inverse and cross-margined, so leverage is "
              "reported after the fill as notional / account equity." % (stop, stop / atr15, stop / price * 100, _fmt(plan["risk_usd"]), plan["instrument"])]
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
          "| 10 | Size: risk %s USD / stop x price, rounded down to 10 USD, capped at half the account notional cap; no leverage input | OURS |" % _fmt(plan["risk_usd"]),
          "| 11 | Time stop: flat at %sZ at market | OURS |" % plan["flat_utc"],
          "| 12 | Levels are read on Binance spot; the order goes on Deribit testnet at the same distances | OURS |", ""]
    if know:
        o += [know.rstrip("\n"), ""]
    return "\n".join(o)


# ---------------------------------------------------------------- "What we already know" (read at build time)
def prev_weekday(day):
    d = day - dt.timedelta(days=1)
    while d.weekday() >= 5:  # OURS: the module trades the US cash open, weekdays only (DESIGN.md section 8)
        d -= dt.timedelta(days=1)
    return d


def _cut(t, n=KNOW_LINE_CHARS):
    t = " ".join(str(t).split())
    return t if len(t) <= n else t[:n - 3] + "..."


def _rel(p, root):
    try:
        return Path(p).relative_to(root).as_posix()
    except ValueError:
        return Path(p).as_posix()


def _know_bible(root):
    p = Path(root) / "MyTradingSys/research/mts_bible/BIBLE.md"
    if not p.exists():
        return ["- Bible: %s not found." % _rel(p, root)]
    rows = []
    for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        m = re.match(r"^#{2,3}\s.*?(20\d\d-\d\d-\d\d)", line)
        if m:  # a dated reading heading (OURS: the Bible dates every reading in its heading)
            rows.append((m.group(1), -i, i, line.lstrip("# ").strip()))
    rows.sort(reverse=True)  # newest date first, later line first on ties
    if not rows:
        return ["- Bible: %s has no dated readings." % _rel(p, root)]
    return ["- Bible (%s:%d): %s" % (_rel(p, root), i, _cut(t)) for _, _, i, t in rows[:KNOW_BIBLE_LINES]]


def _know_ledger(root):
    p = Path(root) / "MyTradingSys/research/eagle_eyes_picture_2026-10-28/scenario_ledger.csv"
    if not p.exists():
        return ["- Scenario ledger: %s not found." % _rel(p, root)]
    with open(p, encoding="utf-8", errors="replace", newline="") as f:  # read-only
        rows = [r for r in csv.DictReader(f) if r.get("id") and not (r.get("outcome") or "").strip()]
    if not rows:
        return ["- Scenario ledger (%s): no open rows." % _rel(p, root)]
    out = ["- Scenario ledger (%s, read-only): %d open." % (_rel(p, root), len(rows)),
           "", "| id | given | likely | up | down | text |", "|---|---|---|---|---|---|"]
    for r in rows[-KNOW_LEDGER_MAX:]:
        out.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], r.get("given_utc", ""), r.get("likely", ""), r.get("up", ""), r.get("down", ""),
                                                       _cut(r.get("text", "")).replace("|", "/")))
    return out


def _know_study(root, rel, what):
    p = Path(root) / rel
    if not p.exists():
        return ["- %s: %s not found." % (what, rel)]
    lines = [l.strip() for l in p.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    title = lines[0].lstrip("# ").strip() if lines else rel
    body = next((l for l in lines[1:] if not l.startswith(("#", "|"))), "")
    return ["- %s (%s): %s. %s" % (what, rel, _cut(title, 100), _cut(body, KNOW_LINE_CHARS))]


def _jsonl(path):
    out = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            v = json.loads(line)
        except ValueError:
            continue
        if isinstance(v, dict):
            out.append(v)
    return out


def _know_yesterday(day, runtime_dir):
    y = prev_weekday(day).isoformat()
    sp, rp = Path(runtime_dir) / ("%s.jsonl" % y), Path(runtime_dir) / ("readings_%s.jsonl" % y)
    out = []
    if sp.exists():
        rows = _jsonl(sp)
        trades = [r for r in rows if "order_id" in r and "summary" not in r]
        r_sum = sum(float(r["r_net"]) for r in trades if isinstance(r.get("r_net"), (int, float)))
        out.append("- Yesterday %s score (%s): %d trades, r_net sum %+.2f (from the trade rows)." % (y, sp.name, len(trades), r_sum))
    if rp.exists():
        rows = _jsonl(rp)
        if rows:
            touched = sorted({str(t) for r in rows for t in (r.get("levels_touched") or [])})
            gaps = sorted({str(g) for r in rows for g in (r.get("gaps") or [])})
            hhmm = lambda r: str(r.get("ts_utc", ""))[11:16]
            last = rows[-1].get("binance_spot")
            out.append("- Yesterday %s readings (%s): %d readings, %sZ to %sZ, last Binance spot %s; levels touched: %s; gaps: %s." % (
                y, rp.name, len(rows), hhmm(rows[0]), hhmm(rows[-1]), format(round(last), ",") if isinstance(last, (int, float)) else "n/a",
                ", ".join(touched) or "none", ", ".join(gaps) or "none"))
    if not out:
        out.append("- Yesterday %s: no score or readings in %s." % (y, runtime_dir.name if hasattr(runtime_dir, "name") else runtime_dir))
    return out


def knowledge_md(day, repo_root=None, runtime_dir=None):
    """The plan's "What we already know" section. Each source is read at build time; a missing or unreadable file gives a line saying so."""
    root = Path(repo_root) if repo_root else lv.ROOT
    rt = Path(runtime_dir) if runtime_dir else Path(os.environ.get("US_OPEN_TRADER_DIR") or (root / "runtime_data" / "us_open_trader"))
    parts = [("Bible", lambda: _know_bible(root)), ("Ledger", lambda: _know_ledger(root)),
             ("Levels study", lambda: _know_study(root, "MyTradingSys/research/us_open_levels_2026-10-30/RESULT.md", "US-open levels study")),
             ("First-3-minutes study", lambda: _know_study(root, "MyTradingSys/research/us_open_first3m_2026-11-11/RESULT.md", "US-open first 3 minutes study")),
             ("Yesterday", lambda: _know_yesterday(day, rt))]
    out = ["## What we already know", "",
           "Context for reading the plan, read from the files at build time. None of it is a signal or a measured edge.", ""]
    for name, fn in parts:
        try:
            out += fn() + [""]
        except Exception as ex:  # one broken source never stops the plan
            out += ["- %s: could not be read (%s: %s)." % (name, type(ex).__name__, str(ex)[:100]), ""]
    return "\n".join(out)


def write(plan, gathered, out_dir, know=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / ("plan_%s.json" % plan["day"])).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out / ("PLAN_US_OPEN_%s.md" % plan["day"])).write_text(render_md(plan, gathered, know), encoding="utf-8", newline="\n")


def main(argv=None, fetch=None, analysts=None):
    ap = argparse.ArgumentParser(description="Build the US-open plan (testnet module).")
    ap.add_argument("--day", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--now", help="UTC time ISO (default: the clock)")
    ap.add_argument("--risk-usd", type=float, default=RISK_USD, help="loss at the stop in USD (OURS default 18)")
    a = ap.parse_args(argv)
    now = dt.datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else dt.datetime.now(lv.UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=lv.UTC)
    g = lv.gather(a.day, now, fetch=fetch, analysts=analysts)
    try:
        plan = build_plan(g, a.day, risk_usd=a.risk_usd)
    except PlanRefused as ex:
        print("PLAN REFUSED: %s" % ex, file=sys.stderr)
        return 2
    write(plan, g, a.out_dir, knowledge_md(a.day))
    print("plan %s: %d orders (%s), %d not built -> %s" % (plan["day"], len(plan["orders"]), ",".join(o["id"] for o in plan["orders"]),
                                                          len(plan["skipped"]), a.out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
