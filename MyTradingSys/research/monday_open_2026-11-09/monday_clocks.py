"""Monday 2026-11-09 open: numbers behind PLAYBOOK.md (public data only, no orders, no indicator code of our own).

Part 1  Krown's month-breach statistic (video e2-KjJdWbgM): re-count on held btc_daily.csv.
Part 2  Levels and the clock observables for the Monday open (Binance spot BTCUSDT 1h via data-api.binance.vision).
Part 3  Monday base rates since 2020 from 1h bars: does Monday sweep the Fri-Sun low, in which session, after what bounce.

Run: python MyTradingSys/research/monday_open_2026-11-09/monday_clocks.py   (cache of 1h bars goes to the OS temp dir, never the repo)
Levels, windows and thresholds are OURS; the 1h order inside a bar is unknown, so a bar that touches both levels is counted BOTH.
"""
import csv
import datetime as dt
import importlib.util
import json
import statistics
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent
CSV = RES / "btc_cycles_2026-11" / "btc_daily.csv"
KL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={iv}&limit=1000&startTime={t0}"
CACHE = Path(tempfile.gettempdir()) / "mts_monday_klines_1h_2020.json"
UTC = dt.timezone.utc
HOUR = 3_600_000


def klines(iv, t0, t1):
    out = []
    while t0 < t1:
        rows = json.load(urllib.request.urlopen(KL.format(iv=iv, t0=t0), timeout=30))
        if not rows:
            break
        out += rows
        t0 = rows[-1][0] + (HOUR if iv == "1h" else 86_400_000)
        if len(rows) < 1000:
            break
    return [(r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in out]  # t, o, h, l, c


def hourly(start=dt.datetime(2020, 1, 1, tzinfo=UTC)):
    t0 = int(start.timestamp() * 1000)
    old = json.loads(CACHE.read_text()) if CACHE.exists() else []
    if old:
        t0 = int(old[-1][0]) + HOUR
    new = klines("1h", t0, int(dt.datetime.now(UTC).timestamp() * 1000))
    bars = [tuple(b) for b in old] + new
    CACHE.write_text(json.dumps(bars))
    return bars


def pct(xs, q):
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    f = int(k)
    return xs[f] + (xs[min(f + 1, len(xs) - 1)] - xs[f]) * (k - f)


def part1():
    daily = {}
    with open(CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            daily[dt.date.fromisoformat(r["date"])] = (float(r["high"]), float(r["low"]), float(r["close"]))
    months = {}
    for d, (h, l, c) in sorted(daily.items()):
        months.setdefault((d.year, d.month), []).append((d, l))
    keys = sorted(months)
    mlow = {k: min(l for _, l in months[k]) for k in keys}
    print("## Part 1: month low below the previous month's low (held csv, to 2026-11-06)")
    full = [k for k in keys if k >= (2011, 1) and k < (2026, 11)]
    for label, lo_year in (("since 2011", 2011), ("since 2018", 2018)):
        deps, n = [], 0
        for k in full:
            if k[0] < lo_year:
                continue
            p = (k[0], k[1] - 1) if k[1] > 1 else (k[0] - 1, 12)
            if p not in mlow:
                continue
            n += 1
            if mlow[k] < mlow[p]:
                deps.append(1 - mlow[k] / mlow[p])
        print(f"{label}: months {n}, breached {len(deps)} ({len(deps)/n:.0%}); undershoot p25 {pct(deps,.25):.1%} median {pct(deps,.5):.1%} p75 {pct(deps,.75):.1%}")
    oct_low = mlow[(2026, 10)]
    print(f"Oct 2026 low {oct_low:,.0f} (csv); x(1-0.105) = {oct_low*(1-.105):,.0f}; 68,100 is {1-68100/oct_low:.1%} below it")
    nov_low = min(l for _, l in months[(2026, 11)])
    print(f"Nov 2026 low so far {nov_low:,.0f} = {1-nov_low/oct_low:.2%} under the Oct low")
    # conditional: already under the previous month's low by day 8 -> how much lower did the month go after day 8
    rem, final, dom, hit = [], [], [], 0
    for k in full:
        p = (k[0], k[1] - 1) if k[1] > 1 else (k[0] - 1, 12)
        if p not in mlow or k[0] < 2011:
            continue
        early = [l for d, l in months[k] if d.day <= 8]
        if not early or min(early) >= mlow[p]:
            continue
        e = min(early)
        m = mlow[k]
        low_day = min(months[k], key=lambda x: x[1])[0].day
        rem.append(1 - m / e)
        final.append(1 - m / mlow[p])
        dom.append(low_day)
    print(f"breach already by day 8: n {len(rem)}; further drop after the day-8 low: p25 {pct(rem,.25):.1%} median {pct(rem,.5):.1%} p75 {pct(rem,.75):.1%}; none lower {sum(r<=0.0005 for r in rem)}; >=10% lower {sum(r>=.10 for r in rem)}; month low day-of-month median {statistics.median(dom):.0f}")
    print(f"  applied to 74,888: p25 {74888*(1-pct(rem,.25)):,.0f} median {74888*(1-pct(rem,.5)):,.0f} p75 {74888*(1-pct(rem,.75)):,.0f}")
    print()


def part2(bars):
    print("## Part 2: levels and clocks (Binance spot 1h, UTC)")
    now = dt.datetime.now(UTC)
    last = bars[-1]
    print(f"now {now:%Y-%m-%d %H:%MZ}; last 1h bar open {dt.datetime.fromtimestamp(last[0]/1000, UTC):%m-%d %H}Z close(live) {last[4]:,.0f}")
    days = {}
    for t, o, h, l, c in bars:
        d = dt.datetime.fromtimestamp(t / 1000, UTC).date()
        e = days.setdefault(d, [o, h, l, c])
        e[1], e[2], e[3] = max(e[1], h), min(e[2], l), c
    for d in sorted(days)[-6:]:
        o, h, l, c = days[d]
        print(f"  {d} {d.strftime('%a')} O {o:,.0f} H {h:,.0f} L {l:,.0f} C {c:,.0f}")
    ses = [b for b in bars if dt.datetime.fromtimestamp(b[0] / 1000, UTC).date() == dt.date(2026, 11, 8)]
    for name, a, z in (("Asia 00-07", 0, 7), ("EU 07-14", 7, 14), ("US-hours 14-19", 14, 19)):
        s = [b for b in ses if a <= dt.datetime.fromtimestamp(b[0] / 1000, UTC).hour < z]
        if s:
            print(f"  Sun 11-08 {name}: H {max(b[2] for b in s):,.0f} L {min(b[3] for b in s):,.0f}")
    wk = [b for b in bars if dt.datetime.fromtimestamp(b[0] / 1000, UTC) >= dt.datetime(2026, 11, 2, tzinfo=UTC)]
    print(f"  week 11-02..now: H {max(b[2] for b in wk):,.0f} L {min(b[3] for b in wk):,.0f}")
    spec = importlib.util.spec_from_file_location("cycle_ma_clock", RES / "ma_layer_2026-11" / "cycle_ma_clock.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rows = m.load()
    have = {r[0] for r in rows}
    for d in sorted(days):
        if d > rows[-1][0] and d <= dt.date(2026, 11, 8):
            rows.append((d, days[d][2], days[d][3]))
    s200, w200, m20, _ = m.clocks(rows, rows[-1][0])
    print(f"  asof {rows[-1][0]} (close live for the last day): 200d SMA {s200:,.0f}, 200w SMA {w200:,.0f}, monthly-20 {m20:,.0f}")
    for n in (2, 3, 5):
        for d in (dt.date(2026, 11, 8) + dt.timedelta(days=i) for i in range(0, 5)):
            ed = (d - dt.date(1970, 1, 1)).days
            if ed % n == n - 1:
                print(f"  {n}-day block (epoch anchor) closes at end of {d} {d.strftime('%a')}")
    print("  weekly bar closes Sun 2026-11-08 24:00Z; Mon 11-09 00:00Z opens the new week, day and 4h bar")
    print()


def part3(bars):
    print("## Part 3: Mondays since 2020 (1h bars, UTC): sweep of the Fri-Sun low")
    by = {b[0]: b for b in bars}
    rows = []
    d = dt.datetime(2020, 1, 6, tzinfo=UTC)
    end = dt.datetime.now(UTC) - dt.timedelta(days=1)
    while d < end:
        t = int(d.timestamp() * 1000)
        ref = [by[x] for x in range(t - 72 * HOUR, t, HOUR) if x in by]
        mon = [by[x] for x in range(t, t + 24 * HOUR, HOUR) if x in by]
        if len(ref) >= 70 and len(mon) >= 23:
            o = mon[0][1]
            low = min(b[3] for b in ref)
            rows.append((d, o, low, mon, ref))
        d += dt.timedelta(days=7)
    print(f"Mondays {len(rows)}")

    def sess(t):
        h = dt.datetime.fromtimestamp(t / 1000, UTC)
        x = h.hour + h.minute / 60
        return "Asia" if x < 7 else ("EU" if x < 14.5 else "US")

    def study(sel, name):
        n = len(sel)
        if n == 0:
            return
        swept = {"Asia": 0, "EU": 0, "US": 0}
        no = 0
        cls = {"straight (no +0.8% first)": 0, "small bounce +0.8..1.4% then sweep": 0, "mid +1.4..2.6% then sweep": 0, "big >=+2.6% before sweep": 0, "no sweep, <+2.6%": 0}
        for d, o, low, mon, ref in sel:
            sw = next((b for b in mon if b[3] <= low), None)
            end_ = sw[0] if sw else mon[-1][0] + HOUR
            pre = [b for b in mon if b[0] < end_] or []
            mx = max([b[2] for b in pre] + [o]) / o - 1
            if sw:
                swept[sess(sw[0])] += 1
                k = "straight (no +0.8% first)" if mx < .008 else ("small bounce +0.8..1.4% then sweep" if mx < .014 else ("mid +1.4..2.6% then sweep" if mx < .026 else "big >=+2.6% before sweep"))
            else:
                no += 1
                k = "big >=+2.6% before sweep" if mx >= .026 else "no sweep, <+2.6%"
            cls[k] += 1
        tot = sum(swept.values())
        print(f"{name}: n {n}; Monday sweeps the Fri-Sun low {tot} ({tot/n:.0%}): Asia {swept['Asia']} EU {swept['EU']} US {swept['US']}; no sweep {no}")
        print("   " + "; ".join(f"{k} {v} ({v/n:.0%})" for k, v in cls.items()))
        close_up = sum(m[-1][4] > o for _, o, _, m, _ in sel)
        print(f"   Monday close above open {close_up}/{n} ({close_up/n:.0%})")

    def lead(sel, name):
        """W = Sat-Sun low, F = Fri-Sun low (F lower than W by 0.5%+). When Monday breaks W, how often F goes next and after how many hours."""
        n = wb = fs = 0
        leads, bysess = [], {"Asia": [0, 0], "EU": [0, 0], "US": [0, 0]}
        for d, o, low, mon, ref in sel:
            w = min(b[3] for b in ref[-48:])
            if not low < w * 0.995:
                continue
            n += 1
            bw = next((b for b in mon if b[3] < w), None)
            if not bw:
                continue
            wb += 1
            bysess[sess(bw[0])][0] += 1
            sw = next((b for b in mon if b[3] <= low), None)
            if sw:
                fs += 1
                bysess[sess(bw[0])][1] += 1
                leads.append((sw[0] - bw[0]) / HOUR)
        med = statistics.median(leads) if leads else float("nan")
        print(f"{name}: n {n}; Monday breaks the Sat-Sun low {wb}; then sweeps the Fri low {fs} ({fs/max(wb,1):.0%}); hours from the Sat-Sun break to the Fri sweep: median {med:.0f}, max {max(leads) if leads else 0:.0f}; by session of the first break (broke/then swept): " + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in bysess.items()))

    study(rows, "all Mondays")
    near = [r for r in rows if 0.010 <= r[1] / r[2] - 1 <= 0.020]
    study(near, "Sun close 1.0-2.0% above the Fri-Sun low")
    near2 = [r for r in rows if 0.008 <= r[1] / r[2] - 1 <= 0.025]
    study(near2, "Sun close 0.8-2.5% above the Fri-Sun low")
    lead(near2, "lead time, Sun close 0.8-2.5% above the Fri low")
    lead(rows, "lead time, all Mondays")
    print()


def main():
    bars = hourly()
    part1()
    part2(bars)
    part3(bars)


if __name__ == "__main__":
    sys.exit(main())
