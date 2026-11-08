"""check_catalogue.py - schema, minimum counts, timestamp sanity, 20-row re-derivation of news_events.csv.

Run: python check_catalogue.py [--online]. Exit 0 = pass. Offline by default (uses raw/derive_sample.csv written by
build_events.py); --online refetches the 20 windows from public Binance klines and compares again.
The re-derivation here is deliberately separate code from build_events.py (own formula, own parsing).
"""
import csv
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).parent
CSV = HERE / "news_events.csv"
SUMMARY = HERE / "class_summary.csv"
REPORT = HERE / "REPORT.md"
SAMPLE = HERE / "raw" / "derive_sample.csv"
REQUIRED = ["event_id", "class", "subclass", "class_label", "date_utc", "time_utc", "ts_quality", "era", "title",
            "source_hint", "date_check", "inferred", "seq_in_class"]
HOR = ["5m", "15m", "60m", "240m", "1440m"]
for _s in ("btc", "eth"):
    REQUIRED += ["%s_ret_%s_bps" % (_s, h) for h in HOR] + ["%s_maxabs60_bps" % _s, "%s_peak_min" % _s, "%s_vol_x" % _s]
MIN_TOTAL, MIN_PER_ERA, MIN_CLASS = 150, 30, 8
START, END = dt.date(2024, 1, 1), dt.date(2026, 11, 7)
INAUG = dt.datetime(2025, 1, 20, 17, 0)
EXPECT_UTC = {"CPI": {"12:30", "13:30"}, "NFP": {"12:30", "13:30"}, "PPI": {"12:30", "13:30"}, "FOMC": {"18:00", "19:00"}}
TOL_BPS = 0.02


def load():
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def t0_of(r):
    d = dt.date.fromisoformat(r["date_utc"])
    hh, mm = (r["time_utc"] or "00:00").split(":")
    return dt.datetime(d.year, d.month, d.day, int(hh), int(mm))


def errors(rows=None, online=False):
    err = []
    if not CSV.exists():
        return ["news_events.csv missing"]
    rows = rows if rows is not None else load()
    if not rows:
        return ["news_events.csv empty"]
    miss = [c for c in REQUIRED if c not in rows[0]]
    if miss:
        return ["missing columns: %s" % miss]
    if len(rows) < MIN_TOTAL:
        err.append("only %d events, need %d" % (len(rows), MIN_TOTAL))
    ids = [r["event_id"] for r in rows]
    if len(set(ids)) != len(ids):
        err.append("duplicate event_id")
    per_era = {"pre": 0, "post": 0}
    seq = {}
    for r in sorted(rows, key=lambda r: (r["class"], t0_of(r), r["event_id"])):
        d = dt.date.fromisoformat(r["date_utc"])
        t0 = t0_of(r)
        if not (START <= d <= END):
            err.append("%s date out of range %s" % (r["event_id"], d))
        if r["ts_quality"] not in ("exact", "approx", "day"):
            err.append("%s bad ts_quality" % r["event_id"])
        if (r["ts_quality"] == "day") != (r["time_utc"] == ""):
            err.append("%s quality/time mismatch" % r["event_id"])
        if r["class_label"] not in ("SOURCED", "OURS"):
            err.append("%s class_label" % r["event_id"])
        want = "post" if t0 >= INAUG else "pre"
        if r["era"] != want:
            err.append("%s era %s want %s" % (r["event_id"], r["era"], want))
        per_era[want] += 1
        exp = EXPECT_UTC.get(r["class"])
        if exp and r["time_utc"] not in exp:
            err.append("%s calendar time %s not in %s" % (r["event_id"], r["time_utc"], sorted(exp)))
        if exp and d.weekday() >= 5:
            err.append("%s calendar event on a weekend" % r["event_id"])
        seq[r["class"]] = seq.get(r["class"], 0) + 1
        if int(r["seq_in_class"]) != seq[r["class"]]:
            err.append("%s seq_in_class %s want %d" % (r["event_id"], r["seq_in_class"], seq[r["class"]]))
        for s in ("btc", "eth"):
            if r["ts_quality"] == "exact" and r["%s_ret_5m_bps" % s] == "":
                err.append("%s %s ret_5m empty for exact" % (r["event_id"], s))
            if r["ts_quality"] == "day" and r["%s_ret_5m_bps" % s] != "":
                err.append("%s %s ret_5m filled for day-only (invented precision)" % (r["event_id"], s))
            if r["%s_ret_1440m_bps" % s] == "" and r["date_utc"] < "2026-11-06":
                err.append("%s %s ret_1440m empty" % (r["event_id"], s))
    for k, v in per_era.items():
        if v < MIN_PER_ERA:
            err.append("era %s has %d events, need %d" % (k, v, MIN_PER_ERA))
    small = sorted(c for c, n in seq.items() if n < MIN_CLASS)
    if not SUMMARY.exists():
        err.append("class_summary.csv missing")
    else:
        with open(SUMMARY, newline="", encoding="utf-8") as f:
            sm = {r["class"]: r for r in csv.DictReader(f)}
        for c, n in seq.items():
            if c not in sm or int(sm[c]["n"]) != n:
                err.append("class_summary n mismatch for %s" % c)
            elif n < MIN_CLASS and sm[c]["verdict"] != "unknown":
                err.append("class %s has n=%d<%d but verdict %s (must be unknown)" % (c, n, MIN_CLASS, sm[c]["verdict"]))
    if not REPORT.exists():
        err.append("REPORT.md missing")
    else:
        txt = REPORT.read_text(encoding="utf-8")
        if not txt.splitlines()[0].startswith("Regime mix:"):
            err.append("REPORT.md line 1 must start with 'Regime mix:'")
        for c in small:
            if c not in txt:
                err.append("small class %s not named in REPORT gaps" % c)
        for w in ("Gaps", "SOURCED", "OURS"):
            if w not in txt:
                err.append("REPORT.md lacks %s" % w)
    err += rederive(rows, online)
    return err


def pick20(rows):
    cand = [r for r in rows if r["ts_quality"] in ("exact", "approx")]
    cand.sort(key=lambda r: r["event_id"])
    step = max(1, len(cand) // 20)
    return cand[::step][:20]


def rederive(rows, online):
    out = []
    picks = pick20(rows)
    if len(picks) < 20:
        return ["fewer than 20 timed events to re-derive"]
    smp = {}
    if online:
        import json
        import urllib.request
    else:
        if not SAMPLE.exists():
            return ["raw/derive_sample.csv missing"]
        with open(SAMPLE, newline="") as f:
            for x in csv.DictReader(f):
                smp.setdefault((x["event_id"], x["symbol"]), {})[int(x["open_time_ms"])] = (float(x["open"]), float(x["close"]))
    for r in picks:
        t0 = int(t0_of(r).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        for sym, pre in (("BTCUSDT", "btc"), ("ETHUSDT", "eth")):
            if online:
                u = "https://api.binance.com/api/v3/klines?symbol=%s&interval=1m&startTime=%d&limit=62" % (sym, t0 - 60000)
                ks = json.loads(urllib.request.urlopen(u, timeout=30).read())
                bars = {int(k[0]): (float(k[1]), float(k[4])) for k in ks}
            else:
                bars = smp.get((r["event_id"], sym))
                if not bars:
                    out.append("no sample for %s %s" % (r["event_id"], sym))
                    continue
            if t0 not in bars or any(t0 + (m - 1) * 60000 not in bars for m in (5, 15, 60)):
                out.append("rederive %s %s: no candle at event minute (timestamp or sample wrong)" % (r["event_id"], sym))
                continue
            ref = bars[t0][0]
            for m, col in ((5, "5m"), (15, "15m"), (60, "60m")):
                if r["ts_quality"] != "exact" and m < 60:
                    continue
                want = (bars[t0 + (m - 1) * 60000][1] / ref - 1) * 1e4
                got = float(r["%s_ret_%s_bps" % (pre, col)])
                if abs(want - got) > TOL_BPS:
                    out.append("rederive %s %s %s: csv %.2f vs %.2f bps" % (r["event_id"], sym, col, got, want))
    return out


if __name__ == "__main__":
    e = errors(online="--online" in sys.argv)
    for x in e:
        print("FAIL", x)
    print("catalogue check: %s (%d problems)" % ("PASS" if not e else "RED", len(e)))
    sys.exit(1 if e else 0)
