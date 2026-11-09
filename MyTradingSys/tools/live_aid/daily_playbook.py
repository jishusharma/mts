"""Daily session playbook for the live aid (card daily-session-playbook-live-aid-1109, operator 2026-11-09).

  python MyTradingSys/tools/live_aid/daily_playbook.py [--day YYYY-MM-DD] [--offline] [--artifact out.html]

Writes playbook_data.js (window.PLAYBOOK_DATA) for one UTC day: Asia 00-08Z, Europe 07-13Z, US 13-21Z. Per session: base rates
of the session range and the swing from its open (history before the day, 1h bars since 2020), key levels (prior day and week
H/L, day and week open, prior-day value area), 2-3 scenarios with the historical first-touch counts and an invalidation line,
CBP analyst levels near price, scheduled events, notes. Every scenario is also a row in scenario_ledger.csv (scored by 1m first
touch at the session end); yesterday's rows come back on the page as HIT / MISS / NA / UNSCORED.

Reuses research/monday_open_2026-11-09/monday_clocks.py (hourly bar cache, pct) and scenario_ledger.py (first_touch, add_row,
score_rows); nothing is copied. Session windows, the 0.2% level gap, MIN_N 20, 50 USD value-area bins and the 10% lean margin are
OURS. Descriptive only: no orders, no size, nothing gates. A 1h bar that touches both levels counts BOTH (order inside the bar
is unknown), as in monday_clocks.py. playbook_data.js carries CBP analyst text and stays out of git (.gitignore).
"""
import argparse
import datetime as dt
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent.parent / "research"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mc = _load("monday_clocks", RES / "monday_open_2026-11-09" / "monday_clocks.py")
sl = _load("scenario_ledger", RES / "eagle_eyes_picture_2026-10-28" / "scenario_ledger.py")
pct = mc.pct
HOUR = mc.HOUR
UTC = mc.UTC
OUT = HERE / "playbook_data.js"
SCHEDULE_JS = HERE / "events_strip_data.js"

SESSIONS = {"Asia": (0, 8), "Europe": (7, 13), "US": (13, 21)}   # UTC hours [start, end), OURS; 07-08Z is in both Asia and Europe
GAP = 0.002          # a level closer than 0.2% to the reference is not a map level (OURS)
MIN_N = 20           # fewer complete history sessions than this: no swing size, no lean (OURS)
LEAN = 0.10          # lean UP/DOWN when one first-touch count leads by 10% of n (OURS)
VA_BIN = 50          # value-area bin in USD (R19 of the live aid, OURS)
BAND = 0.10          # analyst levels shown within 10% of price
KINDS = {"near": (1, "nearest levels"), "swing": (2, "typical swing"), "prior": (3, "prior-day range")}
NAMES = {"PDH": "Prior day high", "PDL": "Prior day low", "PDC": "Prior day close", "PWH": "Prior week high", "PWL": "Prior week low",
         "DAY_OPEN": "Day open 00Z", "WEEK_OPEN": "Week open Mon 00Z", "VAL": "Prior-day VAL", "POC": "Prior-day POC", "VAH": "Prior-day VAH"}
TAG = re.compile(r"^\[PB (\d{4}-\d\d-\d\d) (\w+) (\d)\]\s*([^:]*)")


# ---------- clocks and splits ----------

def sessions_at(hour):
    return [n for n, (a, z) in SESSIONS.items() if a <= hour < z]


def default_day(now):
    """The UTC day to build for: today until the US session ends at 21Z, then tomorrow."""
    return now.date() + dt.timedelta(days=1) if now.hour >= SESSIONS["US"][1] else now.date()


def _hr(t):
    return dt.datetime.fromtimestamp(t / 1000, UTC)


def _ms(d, h=0):
    return int(dt.datetime(d.year, d.month, d.day, h, tzinfo=UTC).timestamp() * 1000)


def _days(bars):
    out = {}
    for b in bars:
        out.setdefault(_hr(b[0]).date(), []).append(b)
    return out


def _stat(sel, a, z):
    if not sel:
        return None
    h, l = max(b[2] for b in sel), min(b[3] for b in sel)
    return {"o": sel[0][1], "h": h, "l": l, "c": sel[-1][4], "range_pct": h / l - 1, "bars": len(sel), "complete": len(sel) == z - a}


def session_stats(bars, day):
    """{session: {o,h,l,c,range_pct,bars,complete} or None} for one UTC day. Windows overlap: 07:00Z is Asia and Europe."""
    ds = _days(bars).get(day, [])
    return {n: _stat([b for b in ds if a <= _hr(b[0]).hour < z], a, z) for n, (a, z) in SESSIONS.items()}


def _hist(bars, day, name):
    """Complete sessions of that name on days before `day`: [(date, stat, bars)]."""
    a, z = SESSIONS[name]
    out = []
    for d, ds in sorted(_days([b for b in bars if b[0] < _ms(day)]).items()):
        sel = [b for b in ds if a <= _hr(b[0]).hour < z]
        s = _stat(sel, a, z)
        if s and s["complete"]:
            out.append((d, s, sel))
    return out


def _rates(hist, day):
    if not hist:
        return {"n": 0}
    rg = [s["range_pct"] for _, s, _ in hist]
    wd = [s["range_pct"] for d, s, _ in hist if d.weekday() == day.weekday()]
    return {"n": len(hist), "range_p25": pct(rg, .25), "range_p50": pct(rg, .5), "range_p75": pct(rg, .75),
            "up_p50": pct([s["h"] / s["o"] - 1 for _, s, _ in hist], .5), "down_p50": pct([1 - s["l"] / s["o"] for _, s, _ in hist], .5),
            "up_share": sum(s["c"] > s["o"] for _, s, _ in hist) / len(hist),
            "wd_n": len(wd), "wd_range_p50": pct(wd, .5) if wd else None, "since": hist[0][0].isoformat()}


def base_rates(bars, day, name):
    """Session range quantiles, median excursion up/down from the open and share of up closes, history before `day` only."""
    return _rates(_hist(bars, day, name), day)


def touch_counts(bars, day, name, up_pct, down_pct):
    """From each history session open: which of open*(1+up_pct) / open*(1-down_pct) the 1h bars touch first."""
    c = {"n": 0, "UP": 0, "DOWN": 0, "BOTH": 0, "NEITHER": 0}
    for _, s, sel in _hist(bars, day, name):
        o = sel[0][1]
        out, _ = sl.first_touch([(b[0], b[2], b[3]) for b in sel], o * (1 + up_pct), o * (1 - down_pct))
        c["n"] += 1
        c[out] += 1
    return c


# ---------- levels ----------

def value_area(bars, bin_size=VA_BIN):
    """(VAL, POC, VAH): each 1h bar adds one count to every price bin it spans (time at price, no volume); POC = fullest bin,
    the area grows one bin at a time toward the fuller neighbour (tie: up) until it holds 70% of the counts."""
    cnt = {}
    for b in bars:
        for i in range(int(b[3] // bin_size), int(b[2] // bin_size) + 1):
            cnt[i] = cnt.get(i, 0) + 1
    if not cnt:
        return None
    poc = min(i for i, v in cnt.items() if v == max(cnt.values()))
    lo = hi = poc
    acc, goal = cnt[poc], 0.7 * sum(cnt.values())
    while acc < goal and (lo > min(cnt) or hi < max(cnt)):
        up = cnt.get(hi + 1, 0) if hi < max(cnt) else -1
        dn = cnt.get(lo - 1, 0) if lo > min(cnt) else -1
        if up >= dn:
            hi += 1
            acc += max(up, 0)
        else:
            lo -= 1
            acc += max(dn, 0)
    return lo * bin_size, (poc + 0.5) * bin_size, (hi + 1) * bin_size


def key_levels(bars, day, now):
    """Prior day H/L/C, prior Mon-Sun week H/L, day open, week open, prior-day value area, last closed price (LAST).
    DAY_OPEN / WEEK_OPEN are None while that bar does not exist yet (day not started)."""
    now_ms = int(now.timestamp() * 1000)
    closed = [b for b in bars if b[0] + HOUR <= now_ms]
    ds = _days(closed)
    lv = {"DAY_OPEN": None, "WEEK_OPEN": None, "LAST": closed[-1][4] if closed else None}
    mon = day - dt.timedelta(days=day.weekday())
    for key, d in (("DAY_OPEN", day), ("WEEK_OPEN", mon)):
        first = ds.get(d, [None])[0]
        if first and _hr(first[0]).hour == 0:
            lv[key] = first[1]
    pd = ds.get(day - dt.timedelta(days=1), [])
    if pd:
        lv.update(PDH=max(b[2] for b in pd), PDL=min(b[3] for b in pd), PDC=pd[-1][4])
        va = value_area(pd)
        lv.update(VAL=va[0], POC=va[1], VAH=va[2])
    pw = [b for d in range(1, 8) for b in ds.get(mon - dt.timedelta(days=d), [])]
    if pw:
        lv.update(PWH=max(b[2] for b in pw), PWL=min(b[3] for b in pw))
    return lv


# ---------- scenarios ----------

def _lean(c, m):
    """UP / DOWN / NONE from the first-touch counts c and the mirror counts m (same two distances, sides swapped). The level that is
    nearer trades first more often just because it is nearer; that part is in m too and cancels: excess = (c.UP - c.DOWN + m.UP - m.DOWN) / 2.
    Without it the ledger would score 'the nearer level first' as a hit rate (OURS, 2026-11-09)."""
    if c["n"] < MIN_N:
        return "NONE"
    d = (c["UP"] - c["DOWN"] + m["UP"] - m["DOWN"]) / 2
    return "UP" if d >= LEAN * c["n"] else "DOWN" if -d >= LEAN * c["n"] else "NONE"


def lean(bars, day, name, up_pct, down_pct):
    """(likely, counts, mirror counts) for a map of +up_pct / -down_pct from the session open."""
    c = touch_counts(bars, day, name, up_pct, down_pct)
    m = touch_counts(bars, day, name, down_pct, up_pct)
    return _lean(c, m), c, m


def _words(likely, up, down):
    if likely == "UP":
        return "invalid if %s trades first" % f"{down:,.0f}", "Long watch: %s first, risk line %s (watch idea, not backtested, no size)" % (f"{up:,.0f}", f"{down:,.0f}")
    if likely == "DOWN":
        return "invalid if %s trades first" % f"{up:,.0f}", "Short watch: %s first, risk line %s (watch idea, not backtested, no size)" % (f"{down:,.0f}", f"{up:,.0f}")
    return ("no side: the first of %s or %s to trade closes the map" % (f"{down:,.0f}", f"{up:,.0f}"),
            "No lean: wait for %s or %s to trade and see if it holds (watch idea, not backtested, no size)" % (f"{up:,.0f}", f"{down:,.0f}"))


def _specs(ref, lv, rates):
    """Up to three (kind, up, down, up_label, down_label) maps around ref; levels closer than GAP are skipped, near duplicates dropped."""
    px = {k: v for k, v in lv.items() if k in NAMES and v}
    above = sorted((v, k) for k, v in px.items() if v >= ref * (1 + GAP))
    below = sorted(((v, k) for k, v in px.items() if v <= ref * (1 - GAP)), reverse=True)
    out = []
    if above and below:
        out.append(("near", above[0][0], below[0][0], NAMES[above[0][1]], NAMES[below[0][1]]))
    if rates["n"] >= MIN_N and rates["up_p50"] >= GAP and rates["down_p50"] >= GAP:
        out.append(("swing", round(ref * (1 + rates["up_p50"]), 1), round(ref * (1 - rates["down_p50"]), 1),
                    "median high +%.2f%% from the open" % (rates["up_p50"] * 100), "median low -%.2f%% from the open" % (rates["down_p50"] * 100)))
    if px.get("PDH", 0) >= ref * (1 + GAP) and px.get("PDL") and px["PDL"] <= ref * (1 - GAP):
        out.append(("prior", px["PDH"], px["PDL"], NAMES["PDH"], NAMES["PDL"]))
    kept = []
    for s in out:
        if not any(abs(s[1] / k[1] - 1) < 0.001 and abs(s[2] / k[2] - 1) < 0.001 for k in kept):
            kept.append(s)
    return kept


def _rank(vals, x):
    return sum(v <= x for v in vals) / len(vals) if vals else None


def _fmt_p(x):
    return "%.2f%%" % (x * 100)


# ---------- the day ----------

def _analysts(calls, ref, now):
    out = []
    for c in calls or []:
        try:
            exp = c.get("expires_at")
            if exp and sl.parse_utc(exp) <= now:
                continue
            if abs(float(c["level"]) / ref - 1) <= BAND:
                out.append({"level": float(c["level"]), "analyst": str(c.get("analyst", "")), "bias": str(c.get("bias", "")),
                            "published": str(c.get("published", "")), "said": str(c.get("said", ""))[:140]})
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(out, key=lambda x: abs(x["level"] - ref))[:8]


def _yesterday(rows, day, now):
    y = (day - dt.timedelta(days=1)).isoformat()
    out = []
    for r in rows:
        m = TAG.match(r["text"])
        if not m or m.group(1) != y:
            continue
        if r["score"] in ("HIT", "MISS", "NA"):
            g = r["score"]
        elif not r["outcome"]:
            g = "UNSCORED" if sl.parse_utc(r["end_utc"]) <= now else "OPEN"
        else:
            g = "NA"
        out.append({"id": r["id"], "session": m.group(2), "name": m.group(4).strip(), "likely": r["likely"], "up": float(r["up"]), "down": float(r["down"]),
                    "outcome": r["outcome"], "touched": r["touched_utc"], "grade": g})
    c = lambda *gs: sum(x["grade"] in gs for x in out)  # noqa: E731
    return {"day": y, "rows": out, "hit": c("HIT"), "miss": c("MISS"), "na": c("NA"), "open": c("UNSCORED", "OPEN")}


def build(bars, day, now, ledger_path=None, analysts=None, schedule=None, fetch=None):
    """The data block for one UTC day, and its scenarios logged in the ledger (idempotent: a tag already there keeps its row)."""
    ledger_path = Path(ledger_path) if ledger_path else sl.LEDGER
    now_ms = int(now.timestamp() * 1000)
    bars = sorted(b for b in bars if b[0] + HOUR <= now_ms)
    lv = key_levels(bars, day, now)
    price = lv["LAST"]
    rows = sl.load(ledger_path)
    if fetch:
        try:
            sl.score_rows(rows, now, fetch)
        except (OSError, ValueError) as ex:
            print("ledger scoring skipped: %s" % ex, file=sys.stderr)
    dirty = fetch is not None
    cur = session_stats(bars, day)
    prev = session_stats(bars, day - dt.timedelta(days=1))
    sched = [e for e in (schedule or []) if not e.get("stale")]
    d_end = _ms(day + dt.timedelta(days=1))
    cards = []
    for name, (a, z) in SESSIONS.items():
        start, end = _ms(day, a), _ms(day, z)
        status = "done" if now_ms >= end else "live" if now_ms >= start else "next"
        hist = _hist(bars, day, name)
        rates = _rates(hist, day)
        ranges = [s["range_pct"] for _, s, _ in hist]
        today = dict(cur[name]) if cur[name] else None
        if today:
            today["pctile"] = _rank(ranges, today["range_pct"])
        ev = [{"id": e["id"], "cls": e["cls"], "t0": e["t0"], "hhmm": _hr(e["t0"]).strftime("%H:%M")} for e in sched if start <= e["t0"] < end]
        scs = []
        if status != "done" and price:
            first = cur[name]["o"] if status == "live" and cur[name] else price
            for kind, up, down, ul, dl in _specs(first, lv, rates):
                up, down = float(up), float(down)
                n = KINDS[kind][0]
                tag = "[PB %s %s %d]" % (day.isoformat(), name, n)
                row = sl.find_tag(rows, tag)
                if row:
                    up, down = float(row["up"]), float(row["down"])
                likely, counts, mirror = lean(bars, day, name, up / first - 1, 1 - down / first)
                likely = row["likely"] if row else likely
                inv, idea = _words(likely, up, down)
                given = dt.datetime.fromtimestamp(max(now_ms, start) / 1000, UTC).replace(second=0, microsecond=0)
                if not row:
                    text = ("%s %s: up %s (%s) vs down %s (%s), reference %s. History %s since %s: n %d, up first %d, down first %d, both %d, neither %d; mirror (same distances, sides swapped) up first %d, down first %d "
                            "(1h bars, a bar touching both counts BOTH, from the session open). Lean %s (nearer-level effect removed); %s. OURS, daily_playbook.py."
                            % (tag, KINDS[kind][1], f"{up:,.0f}", ul, f"{down:,.0f}", dl, f"{first:,.0f}", name, rates.get("since", "?"), counts["n"],
                               counts["UP"], counts["DOWN"], counts["BOTH"], counts["NEITHER"], mirror["UP"], mirror["DOWN"], likely, inv))
                    row = sl.add_row(rows, given, dt.datetime.fromtimestamp(end / 1000, UTC), likely, up, down, text)
                    dirty = True
                scs.append({"n": n, "kind": kind, "name": KINDS[kind][1], "id": row["id"], "ref": first, "up": up, "down": down, "up_label": ul, "down_label": dl,
                            "likely": likely, "counts": counts, "mirror": mirror, "invalid": inv, "idea": idea, "given_utc": row["given_utc"], "end_utc": row["end_utc"]})
        notes = []
        if rates["n"]:
            notes.append("Base rate (n %d complete %s sessions since %s): range p25 / p50 / p75 %s / %s / %s; median high +%s and low -%s from the open; closed above the open %.0f%% of days."
                         % (rates["n"], name, rates["since"], _fmt_p(rates["range_p25"]), _fmt_p(rates["range_p50"]), _fmt_p(rates["range_p75"]),
                            _fmt_p(rates["up_p50"]), _fmt_p(rates["down_p50"]), rates["up_share"] * 100))
            if rates["wd_n"]:
                notes.append("%ss only (n %d): median range %s." % (day.strftime("%A"), rates["wd_n"], _fmt_p(rates["wd_range_p50"])))
        else:
            notes.append("Base rate: NOT_IN_DATA (no complete %s session in the bars)." % name)
        if today:
            notes.append("%s: range %s = %.0f%% of history at or below it%s." % ("Today so far" if not today["complete"] else "Today", _fmt_p(today["range_pct"]),
                                                                                (today["pctile"] or 0) * 100, "" if today["complete"] else " (session still open)"))
        if prev[name] and prev[name]["complete"]:
            notes.append("Yesterday's %s: range %s, %s." % (name, _fmt_p(prev[name]["range_pct"]), "closed up" if prev[name]["c"] > prev[name]["o"] else "closed down"))
        if name in ("Asia", "Europe"):
            notes.append("Asia and Europe overlap 07-08Z: a 07:00Z bar counts in both.")
        if ev:
            notes.append("Scheduled: " + ", ".join("%s %sZ" % (e["cls"], e["hhmm"]) for e in ev) + ".")
        cards.append({"name": name, "hours": "%02d-%02dZ" % (a, z), "start_ms": start, "end_ms": end, "status": status, "today": today,
                      "base": rates, "scenarios": scs, "events": ev, "notes": notes})
    if dirty:
        sl.save(rows, ledger_path)
    nxt = next((e for e in sorted(sched, key=lambda e: e["t0"]) if e["t0"] >= d_end), None)
    levels = sorted(({"k": k, "name": NAMES[k], "price": v} for k, v in lv.items() if k in NAMES and v), key=lambda x: -x["price"])
    return {"day": day.isoformat(), "built_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "price": price,
            "levels": levels, "sessions": cards, "yesterday": _yesterday(rows, day, now),
            "analysts": _analysts(analysts, price, now) if price else [],
            "analysts_note": "analyst calls NOT_IN_DATA (CBP store not read)" if analysts is None else "" if analysts else "no analyst level on the list",
            "next_event": ({"id": nxt["id"], "cls": nxt["cls"], "t0": nxt["t0"]} if nxt else None),
            "ledger": sl.summary(rows),
            "notes": ["Sessions in UTC: Asia 00-08Z, Europe 07-13Z, US 13-21Z; windows, the 0.2% level gap, n 20 minimum, 10% lean margin and 50 USD value-area bins are OURS.",
                      "Counts are history first touches from the session open on 1h bars (BOTH = one bar touched both). The nearer level trades first more often just for being nearer, so the lean is the excess over the same distances swapped (mirror), by 10% of n; below n 20 there is none.",
                      "Watch ideas are not backtested and carry no size or order; fee-net out-of-sample results decide what trades. Context only."]}


def render(data):
    return "// generated by daily_playbook.py; do not edit\nwindow.PLAYBOOK_DATA = " + json.dumps(data) + ";\n"


# ---------- cli ----------

def _read_schedule(path=SCHEDULE_JS):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8").split("= ", 1)[1].rstrip().rstrip(";")).get("schedule", [])
    except (OSError, IndexError, ValueError):
        return []


def _bars(a):
    if a.bars:
        raw = json.loads(Path(a.bars).read_text(encoding="utf-8"))
    elif a.offline:
        raw = json.loads(mc.CACHE.read_text(encoding="utf-8"))
    else:
        raw = mc.hourly()
    return [tuple(b) for b in raw]


def _cbp_levels():
    try:
        import build_analyst_data as bad
        return bad.build(offline=True, days=5)["levels"]
    except Exception as ex:  # CBP store absent: the page says NOT_IN_DATA, nothing is guessed
        print("analyst levels NOT_IN_DATA: %s" % ex, file=sys.stderr)
        return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=dt.date.fromisoformat)
    ap.add_argument("--now", help="UTC time, default the clock (tests)")
    ap.add_argument("--offline", action="store_true", help="cached bars only, no ledger scoring")
    ap.add_argument("--bars", help="json list of [t,o,h,l,c] 1h bars (tests)")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--ledger", default=str(sl.LEDGER))
    ap.add_argument("--no-analysts", action="store_true")
    ap.add_argument("--artifact", help="also write the phone-width page here (build_artifact.py)")
    a = ap.parse_args(argv)
    now = sl.parse_utc(a.now) if a.now else dt.datetime.now(UTC)
    day = a.day or default_day(now)
    data = build(_bars(a), day, now, ledger_path=a.ledger, analysts=None if a.no_analysts else _cbp_levels(), schedule=_read_schedule(),
                 fetch=None if a.offline or a.bars else sl.fetch_bars)
    Path(a.out).write_text(render(data), encoding="utf-8", newline="\n")
    ids = [s["id"] for c in data["sessions"] for s in c["scenarios"]]
    print("playbook %s: %d scenarios %s; yesterday HIT %d MISS %d NA %d open %d -> %s" % (
        data["day"], len(ids), ",".join(ids), data["yesterday"]["hit"], data["yesterday"]["miss"], data["yesterday"]["na"], data["yesterday"]["open"], a.out))
    if a.artifact:
        import build_artifact
        Path(a.artifact).write_text(build_artifact.build_playbook(render(data)), encoding="utf-8", newline="\n")
        print("artifact page ->", a.artifact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
