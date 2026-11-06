"""US-session prep brief (card us-session-prep-1106, decision d-us-session-prep-1106). T0, no LLM.

  python scripts/dev/us_prep.py --phase P1|P2|P3|P4 [--date YYYY-MM-DD]

Phases (UTC): P1 09:00 pre-market, P2 13:15 before the 13:30 releases, P3 14:45 after the open, P4 21:15 scoring.
Writes MyTradingSys/runtime/us_prep/<date>_<phase>.md + .json (git-ignored; repo is public).
Context, never a signal. Fail closed: a source that cannot be read gives the string UNKNOWN, never a number.
Public market data only. Thresholds NQ -0.5% / Kospi -3% are premarket_risk.js PM (OURS, from the 11-05 case).
"""
import argparse
import datetime as dt
import importlib.util
import json
import math
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote as urlquote

ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "MyTradingSys" / "runtime" / "us_prep"
LEDGER_PY = ROOT / "MyTradingSys" / "research" / "eagle_eyes_picture_2026-10-28" / "scenario_ledger.py"
UNKNOWN = "UNKNOWN"
PM = {"nqPct": -0.5, "kospiPct": -3.0}  # same values as premarket_risk.js PM (OURS)
PHASE_UTC = {"P1": (9, 0), "P2": (13, 15), "P3": (14, 45), "P4": (21, 15)}
SPOT = "https://data-api.binance.vision/api/v3/klines"
FAPI = "https://fapi.binance.com"
BIN_USD = 50.0  # OURS
VA_FRAC = 0.70  # OURS (spec)
MIN = 60_000
TF_MS = {"1m": MIN, "15m": 15 * MIN, "1h": 60 * MIN, "4h": 240 * MIN, "1d": 1440 * MIN}
SYMS = {"NQ": "NQ=F", "ES": "ES=F", "VIX": "^VIX", "DXY": "DX-Y.NYB", "US10Y": "^TNX", "KOSPI": "^KS11", "NIKKEI": "^N225"}


def http_json(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _safe(fn, *a):
    """Any failure or empty result -> UNKNOWN."""
    try:
        r = fn(*a)
    except Exception:
        return UNKNOWN
    return UNKNOWN if r is None else r


# ---------- macro ----------
def quote(sym, fetch):
    j = fetch(f"https://query1.finance.yahoo.com/v8/finance/chart/{urlquote(sym, safe='')}?range=1d&interval=1d")
    m = j["chart"]["result"][0]["meta"]
    p, v = _num(m.get("regularMarketPrice")), _num(m.get("chartPreviousClose", m.get("previousClose")))
    if p is None or v is None or v <= 0:
        return None
    return {"price": p, "prev": v, "pct": round(100 * (p - v) / v, 3)}


def macro(fetch):
    out = {k: _safe(quote, s, fetch) for k, s in SYMS.items()}
    nq = out["NQ"]["pct"] if out["NQ"] != UNKNOWN else UNKNOWN
    ko = out["KOSPI"]["pct"] if out["KOSPI"] != UNKNOWN else UNKNOWN
    reasons = []
    if nq != UNKNOWN and nq < PM["nqPct"]:
        reasons.append(f"Nasdaq-100 futures {nq:.2f}% vs prior close (< {PM['nqPct']}%)")
    if ko != UNKNOWN and ko < PM["kospiPct"]:
        reasons.append(f"Kospi {ko:.2f}% vs prior close (< {PM['kospiPct']}%)")
    flag = "ON" if reasons else ("UNKNOWN" if UNKNOWN in (nq, ko) else "OFF")
    return {"flag": flag, "reasons": reasons, "nq_pct": nq, "kospi_pct": ko, "quotes": out}


# ---------- klines ----------
def klines(fetch, interval, start_ms, end_ms):
    """[(open_ms, o, h, l, c, v)] for bars opening in [start, end). Raises on failure."""
    rows, t0 = [], start_ms
    while t0 < end_ms:
        page = fetch(f"{SPOT}?symbol=BTCUSDT&interval={interval}&limit=1000&startTime={t0}&endTime={end_ms - 1}")
        if not page:
            break
        for r in page:
            if r[0] < end_ms:
                rows.append((int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])))
        nxt = int(page[-1][0]) + TF_MS[interval]
        if nxt <= t0:
            break
        t0 = nxt
    return rows


def value_area(pv, bin_usd=BIN_USD, frac=VA_FRAC):
    """pv: [(price, volume)]. POC = centre of the heaviest bin; VA grows from the POC by the heavier neighbour until frac of volume."""
    bins = {}
    for p, v in pv:
        if _num(p) is None or _num(v) is None or v < 0:
            continue
        k = math.floor(p / bin_usd)
        bins[k] = bins.get(k, 0.0) + v
    tot = sum(bins.values())
    if not bins or tot <= 0:
        return UNKNOWN
    poc = max(sorted(bins), key=lambda k: bins[k])
    lo = hi = poc
    acc = bins[poc]
    kmin, kmax = min(bins), max(bins)
    while acc < frac * tot and (lo > kmin or hi < kmax):
        a, b = bins.get(lo - 1, 0.0), bins.get(hi + 1, 0.0)
        if b >= a:
            hi += 1
            acc += b
        else:
            lo -= 1
            acc += a
    return {"POC": poc * bin_usd + bin_usd / 2, "VAL": lo * bin_usd, "VAH": (hi + 1) * bin_usd}


def hlc(bars):
    if not bars:
        return None
    return {"H": max(b[2] for b in bars), "L": min(b[3] for b in bars), "C": bars[-1][4]}


def bollinger(closes, n=20, k=2.0):
    if len(closes) < n:
        return None
    w = closes[-n:]
    mid = sum(w) / n
    sd = math.sqrt(sum((x - mid) ** 2 for x in w) / n)
    return {"lower": round(mid - k * sd, 2), "mid": round(mid, 2), "upper": round(mid + k * sd, 2)}


def _ms(d):
    return int(d.timestamp() * 1000)


def btc(date, asof, fetch):
    day0 = dt.datetime.fromisoformat(date).replace(tzinfo=dt.timezone.utc)
    prev0, a_ms, d0 = day0 - dt.timedelta(days=1), _ms(asof), _ms(day0)
    out = {"last": UNKNOWN}

    def prior():
        bars = klines(fetch, "1m", _ms(prev0), d0)
        if len(bars) < 1400:  # a day with gaps is not a day
            return None
        r = hlc(bars)
        r["value_area"] = value_area([((b[2] + b[3] + b[4]) / 3, b[5]) for b in bars])
        return r

    def window(h0, h1):
        s, e = d0 + h0 * 3600_000, min(d0 + h1 * 3600_000, a_ms)
        if e <= s:
            return None
        return hlc(klines(fetch, "1m", s, e))

    today = _safe(klines, fetch, "1m", d0, a_ms)
    if today != UNKNOWN and today:
        out["last"] = today[-1][4]
        vv = sum(b[5] for b in today)
        out["vwap"] = round(sum((b[2] + b[3] + b[4]) / 3 * b[5] for b in today) / vv, 2) if vv > 0 else UNKNOWN
        out["day"] = hlc(today)
    else:
        out["vwap"] = UNKNOWN
        out["day"] = UNKNOWN
    out["prior_day"] = _safe(prior)
    out["asia"] = _safe(window, 0, 8)
    out["london"] = _safe(window, 8, 13)

    def bb(tf):
        step = TF_MS[tf]
        end = (a_ms // step) * step  # only closed bars
        return bollinger([b[4] for b in klines(fetch, tf, end - 25 * step, end)])

    out["bb"] = {tf: _safe(bb, tf) for tf in ("15m", "1h", "4h", "1d")}
    return out


def derivs(fetch):
    """Funding / OI only where fapi is reachable (not from JIS-NB: run on the NUC). Liquidation clusters have no public REST source: UNKNOWN."""
    def funding():
        return _num(fetch(f"{FAPI}/fapi/v1/premiumIndex?symbol=BTCUSDT")["lastFundingRate"])

    def oi():
        return _num(fetch(f"{FAPI}/fapi/v1/openInterest?symbol=BTCUSDT")["openInterest"])

    return {"funding": _safe(funding), "oi": _safe(oi), "oi_24h_change": UNKNOWN, "liquidations": UNKNOWN}


def build_brief(phase, date, fetch=http_json):
    h, m = PHASE_UTC[phase]
    asof = dt.datetime.fromisoformat(date).replace(hour=h, minute=m, tzinfo=dt.timezone.utc)
    return {
        "phase": phase, "date": date, "asof_utc": asof.strftime("%Y-%m-%dT%H:%MZ"),
        "macro": macro(fetch), "btc": btc(date, asof, fetch), "derivs": derivs(fetch),
        "econ": UNKNOWN,  # no public calendar source wired: never guessed (spec)
        "context_only": True,
        "note": "Context, never a signal. UNKNOWN = source unreachable or not wired.",
    }


# ---------- output ----------
def _f(x):
    return f"{x:,.1f}" if isinstance(x, (int, float)) else str(x)


def render_md(b):
    m, c, d = b["macro"], b["btc"], b["derivs"]
    L = [f"# US prep {b['date']} {b['phase']} (as of {b['asof_utc']}) - context, never a signal", "",
         f"- macro flag {m['flag']}: " + ("; ".join(m["reasons"]) or "no reason") + f" | NQ {_f(m['nq_pct'])}% Kospi {_f(m['kospi_pct'])}%"]
    for k, v in m["quotes"].items():
        L.append(f"  - {k}: " + (f"{_f(v['price'])} ({_f(v['pct'])}%)" if v != UNKNOWN else UNKNOWN))
    pd = c["prior_day"]
    if pd == UNKNOWN:
        L.append("- BTC prior day: UNKNOWN")
    else:
        va = pd["value_area"]
        vas = va if va == UNKNOWN else f"POC {_f(va['POC'])} VAL {_f(va['VAL'])} VAH {_f(va['VAH'])}"
        L.append(f"- BTC prior day H {_f(pd['H'])} L {_f(pd['L'])} C {_f(pd['C'])} | {vas}")
    for k in ("asia", "london"):
        v = c[k]
        L.append(f"- {k} H/L: " + (UNKNOWN if v == UNKNOWN else f"{_f(v['H'])} / {_f(v['L'])}"))
    L.append(f"- last {_f(c['last'])} | day VWAP {_f(c['vwap'])}")
    for tf, v in c["bb"].items():
        L.append(f"- BB(20,2) {tf}: " + (UNKNOWN if v == UNKNOWN else f"{_f(v['lower'])} / {_f(v['mid'])} / {_f(v['upper'])}"))
    L.append(f"- funding {d['funding']} | OI {d['oi']} | OI 24h {d['oi_24h_change']} | liquidations {d['liquidations']}")
    L.append(f"- econ calendar / earnings: {b['econ']}")
    return "\n".join(L) + "\n"


def _dump(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_brief(b, outdir=OUTDIR):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"{b['date']}_{b['phase']}"
    _dump(outdir / f"{stem}.json", json.dumps(b, indent=1) + "\n")
    _dump(outdir / f"{stem}.md", render_md(b))
    return outdir / f"{stem}.md"


# ---------- P4 scorer ----------
def _ledger():
    spec = importlib.util.spec_from_file_location("scenario_ledger", LEDGER_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def score_p4(date, fetch=http_json, ledger_rows=None, outdir=OUTDIR):
    sl = _ledger()
    rows = sl.load() if ledger_rows is None else ledger_rows
    found = [p for p in ("P1", "P2", "P3") if (Path(outdir) / f"{date}_{p}.json").exists()]
    day0 = dt.datetime.fromisoformat(date).replace(tzinfo=dt.timezone.utc)
    sess = _safe(lambda: hlc(klines(fetch, "1m", _ms(day0) + (13 * 60 + 30) * MIN, _ms(day0) + 21 * 3600_000)))
    res = {"date": date, "phases_found": found, "phases_missing": [p for p in ("P1", "P2", "P3") if p not in found],
           "session": sess, "scenarios": [], "context_only": True}
    for r in rows:
        if not str(r["given_utc"]).startswith(date):
            continue
        try:
            bars = klines(fetch, "1m", _ms(sl.parse_utc(r["given_utc"])), _ms(sl.parse_utc(r["end_utc"])))
            if not bars:
                raise ValueError("no bars")
            out, _t = sl.first_touch([(b[0], b[2], b[3]) for b in bars], float(r["up"]), float(r["down"]))
            score = sl.score_of(r["likely"], out)
        except Exception:
            out, score = UNKNOWN, UNKNOWN
        res["scenarios"].append({"id": r["id"], "likely": r["likely"], "up": r["up"], "down": r["down"], "outcome": out, "score": score})
    return res


def render_p4_md(res):
    L = [f"# US prep {res['date']} P4 score - context, never a signal", "",
         f"- phases found {res['phases_found']} missing {res['phases_missing']} (a missed phase is logged, never skipped silently)"]
    s = res["session"]
    L.append("- session 13:30-21:00Z H/L/C: " + (UNKNOWN if s == UNKNOWN else f"{_f(s['H'])} / {_f(s['L'])} / {_f(s['C'])}"))
    for x in res["scenarios"]:
        L.append(f"- {x['id']} likely {x['likely']} up {x['up']} down {x['down']}: {x['outcome']} -> {x['score']}")
    if not res["scenarios"]:
        L.append("- no scenarios in scenario_ledger.py for this date")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=sorted(PHASE_UTC), required=True)
    ap.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"))
    a = ap.parse_args(argv)
    b = build_brief(a.phase, a.date)
    p = write_brief(b)
    print(render_md(b))
    if a.phase == "P4":
        res = score_p4(a.date)
        OUTDIR.mkdir(parents=True, exist_ok=True)
        _dump(OUTDIR / f"{a.date}_P4_score.json", json.dumps(res, indent=1) + "\n")
        _dump(OUTDIR / f"{a.date}_P4_score.md", render_p4_md(res))
        print(render_p4_md(res))
    print("wrote", p)


if __name__ == "__main__":
    sys.exit(main())
