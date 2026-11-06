"""MA clock for the Bible: where BTC sat versus the 200-day SMA, 200-week SMA and monthly 20 SMA at each cycle bottom and now.
Data: research/btc_cycles_2026-11/btc_daily.csv (daily close). Weekly close = last daily close of the Monday-Sunday UTC week,
monthly close = last daily close of the calendar month; the week/month containing the as-of date counts with the close up to that date.
Output: markdown table on stdout. Bottoms and dates are the Bible section 1 table (low price from the csv low column)."""
import csv
import datetime as dt
import sys
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "btc_cycles_2026-11" / "btc_daily.csv"
BOTTOMS = [("2015", "2015-01-15"), ("2018", "2018-12-15"), ("2022", "2022-11-21"), ("2026-07", "2026-07-01")]


def load():
    rows = []
    with open(CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((dt.date.fromisoformat(r["date"]), float(r["low"]), float(r["close"])))
    return rows


def mean_last(xs, n):
    return sum(xs[-n:]) / n if len(xs) >= n else None


def clocks(rows, asof):
    sub = [r for r in rows if r[0] <= asof]
    daily = [r[2] for r in sub]
    wk, mo = {}, {}
    for d, _, c in sub:
        wk[d - dt.timedelta(days=d.weekday())] = c  # later days overwrite: last close of the week
        mo[(d.year, d.month)] = c
    w = [wk[k] for k in sorted(wk)]
    m = [mo[k] for k in sorted(mo)]
    return mean_last(daily, 200), mean_last(w, 200), mean_last(m, 20), sub[-1]


def main():
    rows = load()
    out = ["| Moment | Date | Low / close | 200-day SMA | 200-week SMA | Monthly 20 SMA | Low vs 200d | Low vs 200w | Low vs 20m | Close vs 200d |", "|---|---|---|---|---|---|---|---|---|---|"]
    pts = [(n, dt.date.fromisoformat(d)) for n, d in BOTTOMS] + [("now", rows[-1][0])]
    for name, d in pts:
        s200, w200, m20, (_, low, close) = clocks(rows, d)
        f = lambda v: "n/a" if v is None else "{:,.0f}".format(v)
        p = lambda a, b: "n/a" if b is None else "{:+.0f} %".format(100 * (a / b - 1))
        out.append("| %s | %s | %s / %s | %s | %s | %s | %s | %s | %s | %s |" % (
            name, d, f(low), f(close), f(s200), f(w200), f(m20), p(low, s200), p(low, w200), p(low, m20), p(close, s200)))
    print("\n".join(out))


if __name__ == "__main__":
    sys.exit(main())
