"""News study: the BTC move 15 m and 60 m after each saved Tree News item, per class (card news-weight-bias-flash-1108).

Counts only, no edge claim: 20 items are far too few to say any class moves the market; this prints what happened after each saved headline
so the W and chip rules in news_weight.js can be read against real minutes. Context only; nothing here feeds a gate, size or order.
Items: research/news_feeds_2026-10-30/sample_tree_news.json (the existing 20-item sample). Class = news_weight.js classify() (called through node).
Prices: public Binance 1m klines (no key). Move = close of the 15th (60th) minute from the headline minute vs the close of the minute before it,
the same definition as research/news_effects_2026-11/news_events.csv btc_r15 / btc_r60. An item younger than 15 m (60 m) reads NA.
Usage: python MyTradingSys/tools/live_aid/news_study.py
"""
import datetime
import json
import shutil
import subprocess
import sys
import urllib.request
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE = HERE.parent.parent / "research" / "news_feeds_2026-10-30" / "sample_tree_news.json"
JS = HERE / "news_weight.js"
MIN = 60000
URLS = ("https://fapi.binance.com/fapi/v1/klines", "https://api.binance.com/api/v3/klines")


def move(rows, t, minutes):
    """% move over `minutes` closed 1m bars starting at the headline minute, vs the close of the minute before; None if a bar is missing.

    rows: {openTime ms: close}."""
    m0 = t // MIN * MIN
    a, b = rows.get(m0 - MIN), rows.get(m0 + (minutes - 1) * MIN)
    if a is None or b is None or a <= 0:
        return None
    return (b / a - 1) * 100


def classify(titles):
    node = shutil.which("node")
    if not node:
        return ["OTHER"] * len(titles)
    js = "const NW=require(process.argv[1]);const t=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(t.map(x=>NW.classify(x))));"
    p = subprocess.run([node, "-e", js, str(JS)], input=json.dumps(titles), capture_output=True, text=True, timeout=30)
    return json.loads(p.stdout) if p.returncode == 0 else ["OTHER"] * len(titles)


def fetch(t_from, t_to):
    err = []
    for base in URLS:
        try:
            rows = {}
            t = t_from
            while t < t_to:
                u = "%s?symbol=BTCUSDT&interval=1m&limit=1000&startTime=%d&endTime=%d" % (base, t, t_to)
                with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "news_study"}), timeout=20) as r:
                    page = json.loads(r.read().decode("utf-8"))
                if not page:
                    break
                for k in page:
                    rows[int(k[0])] = float(k[4])
                t = int(page[-1][0]) + MIN
            if rows:
                return rows, base
        except Exception as e:  # noqa: BLE001 - report and try the next public host
            err.append("%s: %s" % (base, e))
    raise RuntimeError("; ".join(err) or "no klines returned")


def fmt(x):
    return "NA" if x is None else "%+.2f" % x


def report(items, classes, rows):
    by = OrderedDict()
    for it, c in zip(items, classes):
        by.setdefault(c, []).append(it)
    out = []
    for c, its in by.items():
        out.append("%s  n %d" % (c, len(its)))
        n15 = n60 = u15 = u60 = 0
        for it in sorted(its, key=lambda x: x["time"]):
            r15, r60 = move(rows, it["time"], 15), move(rows, it["time"], 60)
            n15 += r15 is not None
            n60 += r60 is not None
            u15 += bool(r15 is not None and r15 > 0)
            u60 += bool(r60 is not None and r60 > 0)
            ts = datetime.datetime.fromtimestamp(it["time"] / 1000, datetime.timezone.utc).strftime("%m-%d %H:%M")
            out.append("  %s  imp %-4s  r15 %6s %%  r60 %6s %%  %s" % (ts, it.get("importance", "?"), fmt(r15), fmt(r60), str(it.get("title", "")).split("\n")[0][:60]))
        out.append("  counts: 15 m measured %d (up %d, down %d); 60 m measured %d (up %d, down %d)" % (n15, u15, n15 - u15, n60, u60, n60 - u60))
    return out


def main():
    items = json.loads(SAMPLE.read_text(encoding="utf-8"))
    classes = classify([str(x.get("title", "")).split("\n")[0] for x in items])
    t0 = min(x["time"] for x in items) // MIN * MIN - 2 * MIN
    t1 = max(x["time"] for x in items) // MIN * MIN + 62 * MIN
    try:
        rows, host = fetch(t0, t1)
    except RuntimeError as e:
        print("NOT_IN_DATA: public Binance 1m klines unreachable (%s)" % e)
        return 2
    print("news_study: %d saved Tree News items, BTCUSDT 1m from %s, counts only, no edge claim" % (len(items), host.split("/")[2]))
    print("\n".join(report(items, classes, rows)))
    print("Counts only: 20 items, no class has enough rows to say it moves BTC; the catalogue (news_events.csv, 123 verified rows) is the evidence, not this.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
