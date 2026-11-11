"""US cash open (09:30 New York), BTCUSDT 1m: size of the first 1 and 3 minutes, whether their direction carries on,
and whether the 30 minutes before the open (drift, taker-buy share) say anything about it.

  python study.py [--start 2023-01-01] [--end YYYY-MM-DD]

Operator question 2026-11-11: "how do we know the first 1-3 min move just after US open and positioning just before".
Public data only (Binance spot klines, data-api.binance.vision first). Descriptive, no fees, no entries, never a signal.
Writes results.json here and us_open_first3m_rates.js into tools/live_aid/base_rates_input/ (registry input;
then rebuild the registry by hand, see tools/live_aid/STEPS.md "Base rates").

Definitions (all OURS, fixed before the run; bar 60 of the 121 fetched is the 09:30 New York bar):
  m1, m3   close of minute 1 / minute 3 over the open of the 09:30 bar, minus 1
  f30, f60 close 30 / 60 min after the open over the close of minute 3, minus 1 (the 27 / 57 min after the first 3)
  pre30, pre5  close of the last bar before the open over the open of the bar 30 / 5 min before it, minus 1
  taker    taker-buy base volume / base volume over the 30 one-minute bars before the open
  agree    days where both moves are non-zero and have the same sign, over the days where both are non-zero
  pct(q)   sorted value at index int(q * (n - 1))
  big      the n // 4 days with the largest |m3|;  taker top / bottom = at or beyond its 80th / 20th percentile
"""
import argparse
import json
import statistics
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
JS_OUT = HERE.parents[1] / "tools" / "live_aid" / "base_rates_input" / "us_open_first3m_rates.js"
NY = ZoneInfo("America/New_York")
HOSTS = ("https://data-api.binance.vision/api/v3/klines", "https://api.binance.com/api/v3/klines")
SYMBOL = "BTCUSDT"
PRE, POST = 60, 61   # minutes fetched before the open, and from it


def open_utc(d):
    return datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).astimezone(timezone.utc)


def fetch(d):
    """121 one-minute bars [o, h, l, c, vol, taker_buy_vol] starting 60 min before the open, or None (gap / error)."""
    s = int((open_utc(d) - timedelta(minutes=PRE)).timestamp() * 1000)
    for h in HOSTS:
        try:
            with urllib.request.urlopen(f"{h}?symbol={SYMBOL}&interval=1m&startTime={s}&limit={PRE + POST}", timeout=20) as r:
                k = json.loads(r.read())
        except Exception:  # noqa: BLE001  next host
            continue
        if len(k) == PRE + POST and k[0][0] == s and k[-1][0] == s + (PRE + POST - 1) * 60_000:
            return [[float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])] for x in k]
        return None
    return None


def row_from_bars(day, k):
    """k = 121 bars [o, h, l, c, vol, taker_buy]; k[60] is the 09:30 New York bar."""
    p0, c3 = k[60][0], k[62][3]
    pre_v = sum(x[4] for x in k[30:60])
    vp = sum(x[4] for x in k[57:60])
    return dict(day=day, open_utc=open_utc(date.fromisoformat(day)).strftime("%H:%MZ"), p0=p0,
                pre30=k[59][3] / k[30][0] - 1, pre5=k[59][3] / k[55][0] - 1,
                taker=sum(x[5] for x in k[30:60]) / pre_v if pre_v else None,
                m1=k[60][3] / p0 - 1, m3=c3 / p0 - 1, f30=k[89][3] / c3 - 1, f60=k[119][3] / c3 - 1,
                vol_ratio=sum(x[4] for x in k[60:63]) / vp if vp else None)


def sign(x):
    return (x > 0) - (x < 0)


def pct(xs, q):
    return sorted(xs)[int(q * (len(xs) - 1))]


def agree(rows, a, b):
    xs = [(sign(r[a]), sign(r[b])) for r in rows if sign(r[a]) and sign(r[b])]
    return [sum(1 for p, q in xs if p == q), len(xs)]


def updown(rows, key):
    return [sum(1 for r in rows if r[key] > 0), sum(1 for r in rows if r[key] < 0)]


def summarize(rows, skipped=0):
    size = {}
    for key in ("m1", "m3"):
        a = [abs(r[key]) for r in rows]
        up, down = updown(rows, key)
        size[key] = dict(p50=pct(a, .5), p75=pct(a, .75), p90=pct(a, .9), up=up, down=down)
    big = sorted(rows, key=lambda r: -abs(r["m3"]))[:len(rows) // 4]
    tk = [r for r in rows if r["taker"] is not None]
    hi_cut, lo_cut = pct([r["taker"] for r in tk], .8), pct([r["taker"] for r in tk], .2)
    grp = lambda g, cut: dict(n=len(g), cut=cut, m3=updown(g, "m3"), f60=updown(g, "f60"))  # noqa: E731
    rec = rows[-60:]
    return dict(
        meta=dict(range=[rows[0]["day"], rows[-1]["day"]], days=len(rows), skipped=skipped, symbol=SYMBOL,
                  source="Binance spot 1m klines", open="09:30 America/New_York, weekdays"),
        size=size, vol_ratio_p50=statistics.median(r["vol_ratio"] for r in rows if r["vol_ratio"] is not None),
        follow=dict(m1_m3=agree(rows, "m1", "m3"), m3_f30=agree(rows, "m3", "f30"), m3_f60=agree(rows, "m3", "f60"),
                    big_cut=min(abs(r["m3"]) for r in big) if big else None,
                    big_m3_f30=agree(big, "m3", "f30"), big_m3_f60=agree(big, "m3", "f60"),
                    pre30_m3=agree(rows, "pre30", "m3"), pre5_m3=agree(rows, "pre5", "m3"), pre30_f60=agree(rows, "pre30", "f60"),
                    last60_m3_f30=agree(rec, "m3", "f30"), last60_m3_f60=agree(rec, "m3", "f60"), last60_pre30_m3=agree(rec, "pre30", "m3")),
        taker=dict(top=grp([r for r in tk if r["taker"] >= hi_cut], hi_cut), bottom=grp([r for r in tk if r["taker"] <= lo_cut], lo_cut)),
        recent=[{k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()} for r in rows[-10:]])


def weekdays(start, end, now):
    out, d = [], start
    while d <= end:
        if d.weekday() < 5 and open_utc(d) + timedelta(minutes=POST) <= now:
            out.append(d)
        d += timedelta(days=1)
    return out


def result_md(t):
    f, m, P = t["follow"], t["meta"], lambda x: "%.2f%%" % (100 * x)  # noqa: E731
    fr = lambda v: "%d / %d (%.1f%%)" % (v[0], v[1], 100 * v[0] / v[1])  # noqa: E731
    L = ["# US open: the first 1-3 minutes, what follows, and the 30 minutes before", "",
         "%s 1m %s..%s, %d weekday opens (%d skipped for data gaps). Open = 09:30 New York. Definitions in `study.py` (OURS), "
         "fixed before the run. Descriptive, no fees, no entries, never a signal." % (m["symbol"], m["range"][0], m["range"][1], m["days"], m["skipped"]), "",
         "Regime mix: not split by regime (one pooled window; the last 60 opens are shown as a separate row).", "",
         "| question | count |", "|---|---|"]
    for key in ("m1", "m3"):
        s = t["size"][key]
        L.append("| size of the first %s min (abs move) | p50 %s, p75 %s, p90 %s; up %d, down %d |" % (key[1], P(s["p50"]), P(s["p75"]), P(s["p90"]), s["up"], s["down"]))
    L += ["| volume, first 3 min over the 3 min before (median) | %.2f times |" % t["vol_ratio_p50"],
          "| minute 1 direction = first 3 min direction | %s |" % fr(f["m1_m3"]),
          "| first 3 min direction = next 27 min | %s |" % fr(f["m3_f30"]),
          "| first 3 min direction = next 57 min | %s |" % fr(f["m3_f60"]),
          "| big first 3 min (abs >= %s) = next 27 min | %s |" % (P(f["big_cut"]), fr(f["big_m3_f30"])),
          "| big first 3 min = next 57 min | %s |" % fr(f["big_m3_f60"]),
          "| last 60 opens: first 3 min = next 27 min | %s |" % fr(f["last60_m3_f30"]),
          "| last 60 opens: first 3 min = next 57 min | %s |" % fr(f["last60_m3_f60"]),
          "| pre-open 30 min drift = first 3 min | %s |" % fr(f["pre30_m3"]),
          "| pre-open 5 min drift = first 3 min | %s |" % fr(f["pre5_m3"]),
          "| pre-open 30 min drift = the 57 min after the first 3 | %s |" % fr(f["pre30_f60"])]
    for nm, k in (("heaviest taker buying", "top"), ("heaviest taker selling", "bottom")):
        g = t["taker"][k]
        L.append("| %s before the open (share %s %.3f, n %d) | first 3 min up %d / down %d; next 57 min up %d / down %d |"
                 % (nm, ">=" if k == "top" else "<=", g["cut"], g["n"], g["m3"][0], g["m3"][1], g["f60"][0], g["f60"][1]))
    L += ["", "Read: the first 3 minutes give the size of the opening move (about double the volume of the minutes before), "
          "not its direction. Neither the pre-open drift nor the pre-open taker share separates up from down. "
          "Not measured: open interest and long/short ratios (Binance keeps about 30 days), other symbols, fees.", ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=date.fromisoformat, default=date(2023, 1, 1))
    ap.add_argument("--end", type=date.fromisoformat)
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    days = weekdays(a.start, a.end or now.date(), now)
    with ThreadPoolExecutor(6) as ex:
        bars = list(ex.map(fetch, days))
    rows = [row_from_bars(d.isoformat(), k) for d, k in zip(days, bars) if k]
    t = summarize(rows, skipped=sum(1 for k in bars if not k))
    (HERE / "results.json").write_text(json.dumps(t, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (HERE / "RESULT.md").write_text(result_md(t), encoding="utf-8", newline="\n")
    JS_OUT.parent.mkdir(exist_ok=True)
    JS_OUT.write_text("// built by research/us_open_first3m_2026-11-11/study.py; do not edit\nvar US_OPEN_FIRST3M_RATES = "
                      + json.dumps(t, sort_keys=True, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(result_md(t))


if __name__ == "__main__":
    main()
