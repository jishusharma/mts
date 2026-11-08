"""build_events.py - assemble news_events.csv from the fetched calendars + events_seed.py, measure BTC/ETH reaction on
public Binance 1m klines (data-api.binance.vision), write class_summary.csv, baseline.csv and raw/derive_sample.csv.

Reaction definitions (OURS):
  ref = OPEN of the 1m candle that starts at t0 (price at the event minute).
  ret_Hm = close of the candle that starts at t0+H-1m divided by ref, minus 1, in bps.
  maxabs60 = largest |high/ref-1| or |low/ref-1| in the 60 candles from t0, bps; peak_min = minute (1..60) of that candle.
  vol_x = base volume traded in the first 15 m (exact) or 60 m (approx) / the average for the same span over the prior 120 m.
Quality gates: exact = every column; approx = 60m/240m/1440m + maxabs60/peak/vol_x (hour only); day = ret_1440m only
(t0 = 00:00 UTC, i.e. the daily candle). No precision is invented for rows without a minute.
"""
import csv
import datetime as dt
import json
import statistics as st
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import check_catalogue as cc  # noqa: E402
from events_seed import SEED  # noqa: E402

API = "https://data-api.binance.vision/api/v3/klines"
CACHE = Path(tempfile.gettempdir()) / "news_kcache"
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
# Dates the BLS snapshots list but that were not held on that day (shutdown reschedule, 2025-10..12); both the old and the
# new date appear across snapshots. INFERRED from that double listing and recall, flagged inferred=yes on neighbours.
DROP = {("CPI", "2025-10-15"), ("CPI", "2025-11-13"), ("CPI", "2025-12-10"),
        ("NFP", "2025-10-03"), ("NFP", "2025-11-07"), ("NFP", "2025-12-05")}
DISRUPTED = (dt.date(2025, 10, 1), dt.date(2026, 2, 28))
CAL_TITLE = {"CPI": "US CPI release", "NFP": "US jobs report (NFP)", "PPI": "US PPI release", "FOMC": "FOMC statement (14:00 ET)"}


def get_json(url):
    for k in range(6):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=30).read())
        except Exception:
            time.sleep(1 + 2 * k)
    raise RuntimeError("fetch failed " + url)


def klines(sym, start_ms, n_min):
    """n_min consecutive 1m candles from start_ms: {open_time: (o,h,l,c,v)}; cached on disk (temp dir, not committed)."""
    CACHE.mkdir(exist_ok=True)
    f = CACHE / ("%s_%d_%d.json" % (sym, start_ms, n_min))
    if f.exists():
        return {int(k): tuple(v) for k, v in json.loads(f.read_text()).items()}
    out, cur, end = {}, start_ms, start_ms + n_min * 60000
    while cur < end:
        ks = get_json("%s?symbol=%s&interval=1m&startTime=%d&limit=1000" % (API, sym, cur))
        if not ks:
            break
        for k in ks:
            if int(k[0]) < end:
                out[int(k[0])] = (float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5]))
        cur = int(ks[-1][0]) + 60000
    f.write_text(json.dumps(out))
    return out


def reaction(sym, t0, quality):
    """Return dict of reaction values (floats or '') for one symbol; t0 is epoch ms."""
    res = {"5m": "", "15m": "", "60m": "", "240m": "", "1440m": "", "maxabs60": "", "peak": "", "vol_x": ""}
    ks = klines(sym, t0 - 121 * 60000, 121 + 1440)
    if t0 not in ks:
        return res, ks
    ref = ks[t0][0]

    def ret(m):
        c = ks.get(t0 + (m - 1) * 60000)
        return round((c[3] / ref - 1) * 1e4, 2) if c else ""
    res["1440m"] = ret(1440)
    if quality == "day":
        return res, ks
    for m in (60, 240):
        res["%dm" % m] = ret(m)
    if quality == "exact":
        res["5m"], res["15m"] = ret(5), ret(15)
    best, at = 0.0, 0
    for i in range(60):
        k = ks.get(t0 + i * 60000)
        if not k:
            continue
        for v in (abs(k[1] / ref - 1), abs(k[2] / ref - 1)):
            if v > best:
                best, at = v, i + 1
    res["maxabs60"], res["peak"] = round(best * 1e4, 2), at
    span = 15 if quality == "exact" else 60
    now = sum(ks[t0 + i * 60000][4] for i in range(span) if t0 + i * 60000 in ks)
    prior = [ks[t0 - j * 60000][4] for j in range(1, 121) if t0 - j * 60000 in ks]
    if prior:
        res["vol_x"] = round(now / (sum(prior) / len(prior) * span), 2)
    return res, ks


def calendar_rows():
    out = []
    with open(HERE / "raw" / "calendar_dates.csv", newline="") as f:
        for r in csv.DictReader(f):
            cls, d = r["class"], dt.date.fromisoformat(r["date"])
            if (cls, r["date"]) in DROP:
                continue
            if cls == "PPI" and DISRUPTED[0] <= d <= DISRUPTED[1]:
                continue
            hh, mm = (14, 0) if cls == "FOMC" else (8, 30)
            t = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=ET).astimezone(UTC)
            inferred = "yes" if (cls in ("CPI", "NFP") and DISRUPTED[0] <= d <= DISRUPTED[1]) else "no"
            out.append(dict(cls=cls, sub="release" if cls != "FOMC" else "statement", d=t.date(), tm=t.strftime("%H:%M"),
                            q="exact", title=CAL_TITLE[cls], src=r["source"], check="fetched", inferred=inferred, label="SOURCED"))
    return out


def seed_rows():
    return [dict(cls=c, sub=s, d=dt.date.fromisoformat(d), tm=tm, q=q, title=ti, src=sh, check="recalled", inferred="no",
                 label="OURS") for c, s, d, tm, q, ti, sh in SEED]


def build():
    ev = calendar_rows() + seed_rows()
    for e in ev:
        h, m = (e["tm"] or "00:00").split(":")
        e["t0"] = dt.datetime(e["d"].year, e["d"].month, e["d"].day, int(h), int(m), tzinfo=UTC)
    ev.sort(key=lambda e: (e["cls"], e["t0"], e["sub"]))
    seqs, rows = {}, []
    for e in ev:
        seqs[e["cls"]] = seqs.get(e["cls"], 0) + 1
        t0ms = int(e["t0"].timestamp() * 1000)
        row = {"event_id": "%s-%s-%s" % (e["cls"], e["d"], e["sub"]), "class": e["cls"], "subclass": e["sub"],
               "class_label": e["label"], "date_utc": str(e["d"]), "time_utc": e["tm"], "ts_quality": e["q"],
               "era": "post" if e["t0"].replace(tzinfo=None) >= cc.INAUG else "pre", "title": e["title"],
               "source_hint": e["src"], "date_check": e["check"], "inferred": e["inferred"], "seq_in_class": seqs[e["cls"]]}
        for sym, p in (("BTCUSDT", "btc"), ("ETHUSDT", "eth")):
            r, _ = reaction(sym, t0ms, e["q"])
            for h in cc.HOR:
                row["%s_ret_%s_bps" % (p, h)] = r[h]
            row["%s_maxabs60_bps" % p], row["%s_peak_min" % p], row["%s_vol_x" % p] = r["maxabs60"], r["peak"], r["vol_x"]
        rows.append(row)
    ids = [r["event_id"] for r in rows]
    dup = {i for i in ids if ids.count(i) > 1}
    for r in rows:  # same class+date+subclass twice would collide: disambiguate
        if r["event_id"] in dup:
            r["event_id"] += "-%d" % r["seq_in_class"]
    rows.sort(key=lambda r: (r["date_utc"], r["time_utc"], r["event_id"]))
    with open(HERE / "news_events.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cc.REQUIRED, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows


def write_sample(rows):
    with open(cc.SAMPLE, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["event_id", "symbol", "open_time_ms", "open", "close"])
        for r in cc.pick20(rows):
            t0 = int(cc.t0_of(r).replace(tzinfo=UTC).timestamp() * 1000)
            for sym in ("BTCUSDT", "ETHUSDT"):
                ks = klines(sym, t0 - 121 * 60000, 121 + 1440)
                for i in range(-1, 61):
                    k = ks.get(t0 + i * 60000)
                    if k:
                        w.writerow([r["event_id"], sym, t0 + i * 60000, k[0], k[3]])


def baseline():
    """Median |open->close| of every 1h and every 1d candle, BTC and ETH, 2024-01-01 .. 2026-11-07 (all hours, all days)."""
    out = {}
    s0 = int(dt.datetime(2024, 1, 1, tzinfo=UTC).timestamp() * 1000)
    s1 = int(dt.datetime(2026, 11, 8, tzinfo=UTC).timestamp() * 1000)
    for sym in ("BTCUSDT", "ETHUSDT"):
        for iv, ms in (("1h", 3600000), ("1d", 86400000)):
            vals, cur = [], s0
            while cur < s1:
                ks = get_json("%s?symbol=%s&interval=%s&startTime=%d&limit=1000" % (API, sym, iv, cur))
                if not ks:
                    break
                vals += [abs(float(k[4]) / float(k[1]) - 1) * 1e4 for k in ks if int(k[0]) < s1]
                cur = int(ks[-1][0]) + ms
            out[(sym, iv)] = (round(st.median(vals), 2), len(vals))
    with open(HERE / "baseline.csv", "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["symbol", "interval", "median_abs_ret_bps", "n_candles"])
        for (s, iv), (m, n) in out.items():
            w.writerow([s, iv, m, n])
    return out


def num(x):
    return float(x) if x != "" else None


def summary(rows, base):
    out = []
    by = {}
    for r in rows:
        by.setdefault(r["class"], []).append(r)
    for c, rs in sorted(by.items()):
        rs.sort(key=lambda r: (cc.t0_of(r), r["event_id"]))
        d = [abs(num(r["btc_ret_1440m_bps"])) for r in rs if r["btc_ret_1440m_bps"] != ""]
        t = [abs(num(r["btc_ret_60m_bps"])) for r in rs if r["btc_ret_60m_bps"] != ""]
        t15 = [abs(num(r["btc_ret_15m_bps"])) for r in rs if r["btc_ret_15m_bps"] != ""]
        e60 = [abs(num(r["eth_ret_60m_bps"])) for r in rs if r["eth_ret_60m_bps"] != ""]
        half = len(d) // 2
        first, later = d[:half], d[half:]
        dec = round(st.median(later) / st.median(first), 2) if len(d) >= 2 * 4 and st.median(first) else ""
        n = len(rs)
        ok = n >= cc.MIN_CLASS
        med = lambda x: round(st.median(x), 1) if x and ok else ""
        b60, b1d = base[("BTCUSDT", "1h")][0], base[("BTCUSDT", "1d")][0]
        out.append({"class": c, "label": rs[0]["class_label"], "n": n,
                    "n_pre": sum(r["era"] == "pre" for r in rs), "n_post": sum(r["era"] == "post" for r in rs),
                    "n_exact": sum(r["ts_quality"] == "exact" for r in rs), "n_day_only": sum(r["ts_quality"] == "day" for r in rs),
                    "btc_med_abs_15m_bps": med(t15) if len(t15) >= cc.MIN_CLASS else "",
                    "btc_med_abs_60m_bps": med(t) if len(t) >= cc.MIN_CLASS else "",
                    "btc_med_abs_1440m_bps": med(d),
                    "eth_med_abs_60m_bps": med(e60) if len(e60) >= cc.MIN_CLASS else "",
                    "x_base_60m": round(st.median(t) / b60, 2) if ok and len(t) >= cc.MIN_CLASS else "",
                    "x_base_1d": round(st.median(d) / b1d, 2) if ok and d else "",
                    "decay_later_over_first_1440m": dec if ok else "",
                    "verdict": "measured" if ok else "unknown"})
    with open(HERE / "class_summary.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    return out


if __name__ == "__main__":
    rows = build()
    print("events", len(rows))
    write_sample(rows)
    base = baseline()
    s = summary(rows, base)
    print("classes", len(s), "baseline", base)
