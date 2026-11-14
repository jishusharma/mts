"""Europe-high fade full-history re-test. Rule, data, split, fee, placebo and verdicts are frozen in PRE_REG.md (committed before this ran).

python -I run.py [--cells BTC,ETH,SOL]   -> REPORT.md, events_<cell>.json
Events come from replay_events.js (unchanged Live Aid code); this file scores them.
"""
import csv, glob, importlib.util, json, math, os, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DAY, H, M5 = 86400000, 3600000, 300000
SEED = 1113
MIN_N = 30
RISK_FLOOR_BPS = 10.0
BOOT = 5000
PLACEBO_SETS = 200


def _fees():
    p = os.path.join(REPO, "MyTradingSys", "research", "tom_fabio_course_correction_2026-11-07", "auction_context.py")
    spec = importlib.util.spec_from_file_location("auction_context", p)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, REPO)
    spec.loader.exec_module(m)
    return m.DEFAULT_MAKER_RT_BPS, m.DEFAULT_TAKER_RT_BPS


# ---------------------------------------------------------------- pure logic (tested in test_run.py)
def europe_high(bars5, d0):
    """bars5: iterable of [t,o,h,l,c,...] 5m rows. Europe high/low of UTC day d0 = 15m bars with open >= 07:00 and close < 13:00,
    which on the 5m grid = bars with open >= d0+7h and open+5m-1 < d0+13h."""
    rows = [r for r in bars5 if r[0] >= d0 + 7 * H and r[0] + M5 - 1 < d0 + 13 * H]
    if not rows:
        return None
    return max(r[2] for r in rows), min(r[3] for r in rows)


def trade_outcome(side, entry, exit_, void_at, fee_bps):
    """side 'LONG'/'SHORT'. Returns dict gross_bps, net_bps, risk_bps (floored), r (net R), hit (gross > 0)."""
    s = 1 if side == "LONG" else -1
    gross = s * (exit_ / entry - 1) * 1e4
    risk = max(abs(entry - void_at) / entry * 1e4, RISK_FLOOR_BPS)
    net = gross - fee_bps
    return {"gross_bps": gross, "net_bps": net, "risk_bps": risk, "r": net / risk, "hit": gross > 0}


def day_block_bootstrap(days, vals, draws=BOOT, seed=SEED):
    """Mean of vals with a 95 % percentile CI, resampling whole UTC days."""
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return float("nan"), float("nan"), float("nan")
    ud, inv = np.unique(np.asarray(days), return_inverse=True)
    sums = np.bincount(inv, weights=vals, minlength=len(ud))
    cnt = np.bincount(inv, minlength=len(ud)).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ud), size=(draws, len(ud)))
    means = sums[idx].sum(1) / cnt[idx].sum(1)
    return float(vals.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def verdict_for(n, mean_r, ci_lo, beats_placebo, regime_ns):
    if n < MIN_N:
        return "UNDERPOWERED"
    if not (ci_lo > 0 and beats_placebo):
        return "FAIL"
    return "PASS" if sum(1 for x in regime_ns.values() if x >= MIN_N) >= 2 else "PASS-ONE-REGIME"


def regime_by_day(daily_close):
    """daily_close: dict day_start_ms -> close. Regime of day d from prior-day close vs SMA20 of the prior 20 daily closes (no look-ahead)."""
    days = sorted(daily_close)
    out = {}
    for i, d in enumerate(days):
        if i < 20 or days[i - 1] != d - DAY:
            continue
        prior = [daily_close.get(d - k * DAY) for k in range(1, 21)]
        if any(p is None for p in prior):
            continue
        sma = sum(prior) / 20
        x = prior[0] / sma - 1
        out[d] = "up" if x > 0.02 else "down" if x < -0.02 else "range"
    return out


# ---------------------------------------------------------------- data
def load_btc():
    rows, src = [], {}
    for f in sorted(glob.glob("F:/MTS/data/edge_1111_5m/*.json")):
        d = json.load(open(f))
        for r in d["rows"]:
            rows.append(r)
            src[r[0]] = d["src"]
    return rows, src


def load_alt(folder, prefix, last_month):
    agg = {}
    for f in sorted(glob.glob(f"F:/MTS/data/tom_raw/{folder}/{prefix}-1m-*.csv")):
        with open(f, newline="") as fh:
            rd = csv.reader(fh)
            next(rd)
            for r in rd:
                t = int(r[0])
                b = t - t % M5
                o, h, l, c, v, tb = float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])
                a = agg.get(b)
                if a is None:
                    agg[b] = [b, o, h, l, c, v, tb, t]
                else:
                    a[2] = max(a[2], h); a[3] = min(a[3], l)
                    if t >= a[7]:
                        a[4] = c; a[7] = t
                    if t < a[7] and False:
                        pass
                    a[5] += v; a[6] += tb
    # open must be the first minute's open: recompute properly (1m files are ordered, so the first seen set it)
    return [[a[0], a[1], a[2], a[3], a[4], a[5], a[6]] for _, a in sorted(agg.items())]


class Grid:
    """5m series on a dense slot grid; NaN where a bar is missing."""
    def __init__(self, rows):
        rows = sorted(rows, key=lambda r: r[0])
        self.t0 = rows[0][0]
        n = (rows[-1][0] - self.t0) // M5 + 1
        self.o = np.full(n, np.nan); self.c = np.full(n, np.nan); self.h = np.full(n, np.nan); self.l = np.full(n, np.nan)
        for r in rows:
            i = (r[0] - self.t0) // M5
            self.o[i], self.h[i], self.l[i], self.c[i] = r[1], r[2], r[3], r[4]
        self.n = n
        ok = ~np.isnan(self.o)
        cs = np.concatenate([[0], np.cumsum(~ok)])
        # window [i, i+11] fully present
        self.win_ok = np.zeros(n, bool)
        if n > 12:
            miss = cs[12:] - cs[:-12]
            self.win_ok[: n - 11] = (miss == 0)
        self.rows = rows

    def idx(self, t):
        return (t - self.t0) // M5


def daily_closes(g):
    out = {}
    for i in range(g.n):
        if not math.isnan(g.c[i]):
            out[(g.t0 + i * M5) // DAY * DAY] = g.c[i]  # last write wins = last bar of the day
    return out


def split_cutoff(first_day, last_day):
    a = datetime.fromtimestamp(first_day / 1000, tz=timezone.utc).date()
    b = datetime.fromtimestamp(last_day / 1000, tz=timezone.utc).date()
    n = (b - a).days + 1
    cut = a + timedelta(days=int(0.7 * n))
    return int(datetime(cut.year, cut.month, cut.day, tzinfo=timezone.utc).timestamp() * 1000)


# ---------------------------------------------------------------- cell
def run_cell(name, rows, src, first_day, last_day, maker, taker, outdir):
    with tempfile.TemporaryDirectory() as td:
        inp, outp = os.path.join(td, "in.json"), os.path.join(td, "ev.json")
        json.dump(rows, open(inp, "w"))
        res = subprocess.run(["node", os.path.join(HERE, "replay_events.js"), inp, outp], capture_output=True, text=True, timeout=3000)
        if res.returncode:
            raise RuntimeError(res.stderr[-2000:])
        node_info = json.loads(res.stdout.strip().splitlines()[-1])
        raw_events = json.load(open(outp))
    g = Grid(rows)
    cut = split_cutoff(first_day, last_day)
    reg = regime_by_day(daily_closes(g))
    all_days = [d for d in range(first_day, last_day + DAY, DAY)]
    mix = {k: sum(1 for d in all_days if reg.get(d) == k) for k in ("up", "down", "range")}
    mixn = max(1, sum(mix.values()))

    flag = [e for e in raw_events if e["at"] == "Europe high" and e["state"] in ("REJECTED", "FAILED BREAK")]
    # consistency: level equals the independently computed Europe high of that day
    by_day = {}
    for r in g.rows:
        by_day.setdefault(r[0] // DAY * DAY, []).append(r)
    bad = 0
    for e in flag:
        d0 = e["ts"] // DAY * DAY
        eh = europe_high(by_day[d0], d0)
        if eh is None or abs(eh[0] - e["level"]) > 1e-6:
            bad += 1
    events, skipped = [], 0
    for e in flag:
        i = g.idx(e["ts"])
        if not g.win_ok[i]:
            skipped += 1
            continue
        d0 = e["ts"] // DAY * DAY
        oc = trade_outcome(e["side"], g.o[i], g.c[i + 11], e["voidAt"], maker)
        oc10 = trade_outcome(e["side"], g.o[i], g.c[i + 11], e["voidAt"], taker)
        events.append({**e, "day": d0, "gross_bps": oc["gross_bps"], "net_bps": oc["net_bps"], "risk_bps": oc["risk_bps"], "r": oc["r"],
                       "r_taker": oc10["r"], "net_bps_taker": oc10["net_bps"], "hit": oc["hit"], "regime": reg.get(d0, "n/a"),
                       "split": "VALIDATION" if d0 >= cut else "DEV", "src": src.get(e["ts"], "") if src else "perp",
                       "iso": datetime.fromtimestamp(e["ts"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")})
    # placebo: per event, random 5m step in the same UTC day, 13:00-23:00 UTC, valid 60-min window
    rng = np.random.default_rng(SEED)
    P = np.full((PLACEBO_SETS, len(events)), np.nan)
    for j, e in enumerate(events):
        i0, i1 = g.idx(e["day"] + 13 * H), g.idx(e["day"] + 23 * H)
        cand = np.arange(i0, i1 + 1)
        cand = cand[(cand >= 0) & (cand < g.n)]
        cand = cand[g.win_ok[cand]]
        if len(cand) == 0:
            continue
        pick = cand[rng.integers(0, len(cand), PLACEBO_SETS)]
        s = 1 if e["side"] == "LONG" else -1
        gross = s * (g.c[pick + 11] / g.o[pick] - 1) * 1e4
        P[:, j] = (gross - maker) / e["risk_bps"]
    return {"name": name, "events": events, "skipped": skipped, "flag_raw": len(flag), "bad_level": bad, "node": node_info,
            "cut": cut, "mix": mix, "mixn": mixn, "placebo": P, "first": first_day, "last": last_day, "ndays": len(all_days)}


def stats(evs, P=None, mask=None):
    n = len(evs)
    if n == 0:
        return {"n": 0}
    r = np.array([e["r"] for e in evs]); b = np.array([e["net_bps"] for e in evs]); days = [e["day"] for e in evs]
    m, lo, hi = day_block_bootstrap(days, r)
    mb, blo, bhi = day_block_bootstrap(days, b)
    out = {"n": n, "hit": 100 * float(np.mean([e["hit"] for e in evs])), "gross_bps": float(np.mean([e["gross_bps"] for e in evs])),
           "net_bps": mb, "net_bps_lo": blo, "net_bps_hi": bhi, "r": m, "r_lo": lo, "r_hi": hi,
           "r_taker": float(np.mean([e["r_taker"] for e in evs])), "under": n < MIN_N}
    if P is not None:
        sets = P[:, mask].mean(1) if mask is not None else P.mean(1)
        sets = sets[~np.isnan(sets)]
        out["pl_mean"] = float(np.mean(sets)); out["pl_p95"] = float(np.percentile(sets, 95))
        out["pl_p"] = float(np.mean(sets >= m))
        out["beats"] = bool(m > out["pl_p95"])
    return out


def fmt(s):
    if s["n"] == 0:
        return "| 0 | - | - | - | - | - | UNDERPOWERED |"
    tail = "UNDERPOWERED" if s["under"] else ""
    pl = f"{s['pl_mean']:+.3f} (p95 {s['pl_p95']:+.3f}, p={s['pl_p']:.2f}) {'beats' if s['beats'] else 'no'}" if "pl_mean" in s else "-"
    return (f"| {s['n']} | {s['hit']:.1f} % | {s['net_bps']:+.1f} [{s['net_bps_lo']:+.1f}, {s['net_bps_hi']:+.1f}] | "
            f"{s['r']:+.3f} [{s['r_lo']:+.3f}, {s['r_hi']:+.3f}] | {s['r_taker']:+.3f} | {pl} | {tail} |")


HEAD = "| slice | n | hit (gross) | fee-net mean bps [95 % CI] | fee-net mean R [95 % CI] | R at 10 bp | placebo mean R | note |\n|---|---|---|---|---|---|---|---|\n"


def report_cell(c):
    evs = c["events"]; P = c["placebo"]
    dev = np.array([e["split"] == "DEV" for e in evs], bool); val = ~dev
    iso = lambda ms: datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    L = [f"## Cell {c['name']}  ({iso(c['first'])} .. {iso(c['last'])}, {c['ndays']} days; VALIDATION from {iso(c['cut'])})",
         f"- Node run: {json.dumps(c['node'])}; flag events {c['flag_raw']}, skipped (gap in 60-min window) {c['skipped']}, level-vs-independent-Europe-high mismatches {c['bad_level']}",
         f"- Regime mix: up {100*c['mix']['up']/c['mixn']:.1f} % / down {100*c['mix']['down']/c['mixn']:.1f} % / range {100*c['mix']['range']/c['mixn']:.1f} % (days with a regime: {c['mixn']}, rule in PRE_REG)", ""]
    rows = [("ALL", [e for e in evs], np.ones(len(evs), bool), True),
            ("DEV", [e for e, d in zip(evs, dev) if d], dev, True),
            ("VALIDATION", [e for e, d in zip(evs, val) if d], val, True)]
    tab = HEAD
    res = {}
    for nm, es, mk, pl in rows:
        s = stats(es, P, mk); res[nm] = s
        tab += f"| {nm} " + fmt(s) + "\n"
    for sd in ("SHORT", "LONG"):
        for nm, mk in (("ALL", np.ones(len(evs), bool)), ("VALIDATION", val)):
            es = [e for e, k in zip(evs, mk) if k and e["side"] == sd]
            tab += f"| {sd} {nm} " + fmt(stats(es)) + "\n"
    for rg in ("up", "down", "range"):
        for nm, mk in (("DEV", dev), ("VALIDATION", val)):
            es = [e for e, k in zip(evs, mk) if k and e["regime"] == rg]
            tab += f"| regime {rg} {nm} " + fmt(stats(es)) + "\n"
    for st in ("REJECTED", "FAILED BREAK"):
        es = [e for e in evs if e["state"] == st]
        tab += f"| state {st} ALL " + fmt(stats(es)) + "\n"
    if any(e["src"] for e in evs) and c["name"] == "BTC":
        for sc in ("spot", "um", "um-daily"):
            es = [e for e in evs if e["src"] == sc]
            if es:
                tab += f"| source {sc} ALL " + fmt(stats(es)) + "\n"
    L.append(tab)
    last28 = [e for e in evs if e["ts"] >= c["last"] + DAY - 28 * DAY]
    ng = [e for e in c["events"]]
    s28 = stats(last28)
    L.append(f"- Last 28 days of this cell (replay-window comparison, descriptive): n {s28['n']}, hit {s28.get('hit', float('nan')):.1f} % (learning file: n 30, 60 %, window to 11-13)\n")
    regns = {rg: sum(1 for e, d in zip(evs, val) if d and e["regime"] == rg) for rg in ("up", "down", "range")}
    v = res["VALIDATION"]
    c["verdict"] = verdict_for(v["n"], v.get("r", float("nan")), v.get("r_lo", float("nan")), v.get("beats", False), regns)
    c["res"] = res
    L.append(f"- **{c['name']} VALIDATION verdict: {c['verdict']}** (n {v['n']}, fee-net mean R {v.get('r', float('nan')):+.3f}, CI lower {v.get('r_lo', float('nan')):+.3f}, beats placebo {v.get('beats')}, regimes n>=30 in VALIDATION: {sum(1 for x in regns.values() if x >= MIN_N)})\n")
    return "\n".join(L)


def main():
    cells = (sys.argv[sys.argv.index("--cells") + 1] if "--cells" in sys.argv else "BTC,ETH,SOL").split(",")
    maker, taker = _fees()
    assert abs(maker - 4.0) < 1e-9 and abs(taker - 10.0) < 1e-9
    D = lambda s: int(datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    out, done = [], {}
    for name in cells:
        if name == "BTC":
            rows, src = load_btc(); fd, ld = D("2019-01-01"), D("2026-11-10")
        elif name == "ETH":
            rows, src = load_alt("klines_eth", "ETHUSDT", "2026-09"), None; fd, ld = D("2022-01-01"), D("2026-09-30")
        else:
            rows, src = load_alt("klines_sol", "SOLUSDT", "2024-06"), None; fd, ld = D("2022-01-01"), D("2024-06-30")
        print(name, "bars", len(rows), flush=True)
        c = run_cell(name, rows, src, fd, ld, maker, taker, HERE)
        txt = report_cell(c)
        out.append(txt); done[name] = c
        json.dump([{k: (bool(v) if isinstance(v, (np.bool_,)) else v) for k, v in e.items()} for e in c["events"]], open(os.path.join(HERE, f"events_{name}.json"), "w"))
        print(name, c["verdict"], flush=True)
    head = done["BTC"]
    v = head["res"]["VALIDATION"]
    top = [f"# Europe high fade, full-history re-test ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})",
           "", "Rule, data, split, fee, placebo and verdicts as frozen in PRE_REG.md (committed before the run). The Live Aid code (levelstory.js, pulse.js, live_aid_indicators.js) ran unchanged; no parameter was searched.", ""]
    top.append(f"**VERDICT: {head['verdict']}** - BTC VALIDATION n {v['n']}, hit {v.get('hit', float('nan')):.1f} %, fee-net mean R {v.get('r', float('nan')):+.3f} "
               f"[{v.get('r_lo', float('nan')):+.3f}, {v.get('r_hi', float('nan')):+.3f}], placebo mean {v.get('pl_mean', float('nan')):+.3f} (p95 {v.get('pl_p95', float('nan')):+.3f}).")
    for n2 in cells[1:]:
        if n2 in done:
            vv = done[n2]["res"]["VALIDATION"]
            top.append(f"- Replication {n2}: {done[n2]['verdict']} (VALIDATION n {vv['n']}, mean R {vv.get('r', float('nan')):+.3f}).")
    top.append("")
    open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf-8").write("\n".join(top) + "\n" + "\n".join(out))
    print("\n".join(top))


if __name__ == "__main__":
    main()
