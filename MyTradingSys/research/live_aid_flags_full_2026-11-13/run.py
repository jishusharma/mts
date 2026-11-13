"""All Live Aid idea-flag groups, full-history test. Frozen in PRE_REG.md (committed before this ran).

python -I run.py [--cells BTC,ETH,SOL] [--only "<group>|<side>,..."]  -> REPORT_RAW_<cell>.md, cells_<cell>.json
Events come from replay_events.js (unchanged Live Aid code); this file groups, scores, corrects.
"""
import csv, glob, importlib.util, json, math, os, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DAY, H, M5 = 86400000, 3600000, 300000
SEED, MIN_N, BOOT, PLACEBO_SETS, BH_Q = 1113, 100, 5000, 200, 0.10
FADE_STATES = ("REJECTED", "FAILED BREAK")
LEVELS = ["Day open", "2-day-ago low", "2-day-ago high", "Asia low", "Asia high", "Yesterday low", "Yesterday high",
          "Europe low", "Europe high", "Last week low", "Last week high"]
GROUPS = ["idea", "idea REJECTED", "idea ACCEPTED", "idea FAILED BREAK"] + ["idea fade @ " + x for x in LEVELS]
SIDES = ("LONG", "SHORT")
CELLS = [(g, s) for g in GROUPS for s in SIDES]


def _fees():
    p = os.path.join(REPO, "MyTradingSys", "research", "tom_fabio_course_correction_2026-11-07", "auction_context.py")
    spec = importlib.util.spec_from_file_location("auction_context", p)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, REPO)
    spec.loader.exec_module(m)
    return m.DEFAULT_MAKER_RT_BPS, m.DEFAULT_TAKER_RT_BPS


# ---------------------------------------------------------------- pure logic (tested in test_run.py)
def groups_of(e):
    """Groups an idea event belongs to, exactly as live_aid_learn.score(): idea, idea <state>, idea fade @ <level> (REJECTED / FAILED BREAK only)."""
    g = ["idea"]
    if e.get("state"):
        g.append("idea " + e["state"])
    if e.get("state") in FADE_STATES and e.get("at"):
        g.append("idea fade @ " + e["at"])
    return g


def outcome(side, entry, exit_, fee_bps):
    s = 1 if side == "LONG" else -1
    gross = s * (exit_ / entry - 1) * 1e4
    return gross, gross - fee_bps


def day_block_bootstrap(days, vals, draws=BOOT, seed=SEED):
    """Mean, 95 % percentile CI, one-sided p = P(mean <= 0), resampling whole UTC days."""
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return float("nan"), float("nan"), float("nan"), 1.0
    ud, inv = np.unique(np.asarray(days), return_inverse=True)
    sums = np.bincount(inv, weights=vals, minlength=len(ud))
    cnt = np.bincount(inv, minlength=len(ud)).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ud), size=(draws, len(ud)))
    means = sums[idx].sum(1) / cnt[idx].sum(1)
    p = (int(np.sum(means <= 0)) + 1) / (draws + 1)
    return float(vals.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)), p


def benjamini_hochberg(pvals, q=BH_Q):
    """Step-up BH: list of bool (True = rejected = survives), family order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    kmax = 0
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            kmax = rank
    out = [False] * m
    for rank, i in enumerate(order, 1):
        if rank <= kmax:
            out[i] = True
    return out


def verdict_for(n, ci_lo, beats_placebo, survives, regime_ns):
    if n < MIN_N:
        return "UNDERPOWERED"
    if not (ci_lo > 0 and beats_placebo and survives):
        return "FAIL"
    return "PASS" if sum(1 for x in regime_ns.values() if x >= 30) >= 2 else "PASS-ONE-REGIME"


def regime_by_day(daily_close):
    days = sorted(daily_close)
    out = {}
    for i, d in enumerate(days):
        if i < 20 or days[i - 1] != d - DAY:
            continue
        prior = [daily_close.get(d - k * DAY) for k in range(1, 21)]
        if any(p is None for p in prior):
            continue
        x = prior[0] / (sum(prior) / 20) - 1
        out[d] = "up" if x > 0.02 else "down" if x < -0.02 else "range"
    return out


# ---------------------------------------------------------------- data
def load_btc():
    rows = []
    for f in sorted(glob.glob("F:/MTS/data/edge_1111_5m/*.json")):
        rows.extend(json.load(open(f))["rows"])
    return rows


def load_alt(folder, prefix):
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
                    a[2] = max(a[2], h)
                    a[3] = min(a[3], l)
                    if t >= a[7]:
                        a[4] = c
                        a[7] = t
                    a[5] += v
                    a[6] += tb
    return [[a[0], a[1], a[2], a[3], a[4], a[5], a[6]] for _, a in sorted(agg.items())]


class Grid:
    def __init__(self, rows):
        rows = sorted(rows, key=lambda r: r[0])
        self.t0 = rows[0][0]
        n = (rows[-1][0] - self.t0) // M5 + 1
        self.o = np.full(n, np.nan)
        self.c = np.full(n, np.nan)
        for r in rows:
            i = (r[0] - self.t0) // M5
            self.o[i], self.c[i] = r[1], r[4]
        self.n = n
        ok = ~np.isnan(self.o)
        cs = np.concatenate([[0], np.cumsum(~ok)])
        self.win_ok = np.zeros(n, bool)
        if n > 12:
            self.win_ok[: n - 11] = (cs[12:] - cs[:-12]) == 0

    def idx(self, t):
        return (t - self.t0) // M5


def daily_closes(g):
    out = {}
    for i in range(g.n):
        if not math.isnan(g.c[i]):
            out[(g.t0 + i * M5) // DAY * DAY] = g.c[i]
    return out


def split_cutoff(first_day, last_day):
    a = datetime.fromtimestamp(first_day / 1000, tz=timezone.utc).date()
    b = datetime.fromtimestamp(last_day / 1000, tz=timezone.utc).date()
    cut = a + timedelta(days=int(0.7 * ((b - a).days + 1)))
    return int(datetime(cut.year, cut.month, cut.day, tzinfo=timezone.utc).timestamp() * 1000)


# ---------------------------------------------------------------- cell
def prepare(name, rows, first_day, last_day, maker, taker):
    with tempfile.TemporaryDirectory() as td:
        inp, outp = os.path.join(td, "in.json"), os.path.join(td, "ev.json")
        json.dump(rows, open(inp, "w"))
        res = subprocess.run(["node", os.path.join(HERE, "replay_events.js"), inp, outp], capture_output=True, text=True, timeout=6000)
        if res.returncode:
            raise RuntimeError(res.stderr[-2000:])
        node_info = json.loads(res.stdout.strip().splitlines()[-1])
        raw = json.load(open(outp))
    g = Grid(rows)
    cut = split_cutoff(first_day, last_day)
    reg = regime_by_day(daily_closes(g))
    all_days = list(range(first_day, last_day + DAY, DAY))
    mix = {k: sum(1 for d in all_days if reg.get(d) == k) for k in ("up", "down", "range")}
    evs, skipped = [], 0
    for e in raw:
        i = g.idx(e["ts"])
        if i < 0 or i + 11 >= g.n or not g.win_ok[i]:
            skipped += 1
            continue
        d0 = e["ts"] // DAY * DAY
        gr, nt = outcome(e["side"], g.o[i], g.c[i + 11], maker)
        _, nt10 = outcome(e["side"], g.o[i], g.c[i + 11], taker)
        evs.append({"ts": e["ts"], "day": d0, "side": e["side"], "at": e["at"], "state": e["state"], "gross": gr, "net": nt, "net10": nt10,
                    "hit": gr > 0, "regime": reg.get(d0, "n/a"), "split": "VALIDATION" if d0 >= cut else "DEV", "i": int(i), "groups": groups_of(e)})
    # placebo: unsigned 60-min return at a random same-UTC-day step (any time with a full window), 200 draws per VALIDATION event
    rng = np.random.default_rng(SEED)
    ret = np.concatenate([(g.c[11:] / g.o[:-11] - 1) * 1e4, np.full(11, np.nan)])
    cache = {}
    PL = np.full((len(evs), PLACEBO_SETS), np.nan, dtype=np.float32)
    for k, e in enumerate(evs):
        if e["split"] != "VALIDATION":
            continue
        d = e["day"]
        if d not in cache:
            c0 = max(int(g.idx(d)), 0)
            c = np.arange(c0, min(c0 + 288, g.n))
            cache[d] = c[g.win_ok[c]]
        c = cache[d]
        if len(c):
            PL[k] = ret[c[rng.integers(0, len(c), PLACEBO_SETS)]]
    return {"name": name, "events": evs, "skipped": skipped, "raw": len(raw), "node": node_info, "cut": cut, "mix": mix, "PL": PL,
            "first": first_day, "last": last_day, "ndays": len(all_days)}


def score_cell(c, group, side, maker):
    evs = c["events"]
    mem = np.array([group in e["groups"] and e["side"] == side for e in evs], bool)
    isv = np.array([e["split"] == "VALIDATION" for e in evs], bool)
    sel = np.where(mem & isv)[0]
    dev = [evs[k] for k in np.where(mem & ~isv)[0]]
    out = {"group": group, "side": side, "n": int(len(sel)), "n_dev": len(dev)}
    out["dev_net"] = float(np.mean([e["net"] for e in dev])) if dev else float("nan")
    if len(sel) == 0:
        out.update(hit=float("nan"), net=float("nan"), lo=float("nan"), hi=float("nan"), p=1.0, pl_p=1.0, beats=False,
                   pl_mean=float("nan"), pl_p95=float("nan"), regns={"up": 0, "down": 0, "range": 0}, net10=float("nan"))
        return out
    ve = [evs[k] for k in sel]
    m, lo, hi, p = day_block_bootstrap([e["day"] for e in ve], [e["net"] for e in ve])
    s = 1 if side == "LONG" else -1
    sets = np.nanmean(s * c["PL"][sel].astype(float) - maker, axis=0)
    out.update(hit=100 * float(np.mean([e["hit"] for e in ve])), net=m, lo=lo, hi=hi, p=p, net10=float(np.mean([e["net10"] for e in ve])),
               pl_mean=float(np.mean(sets)), pl_p95=float(np.percentile(sets, 95)), pl_p=(int(np.sum(sets >= m)) + 1) / (len(sets) + 1),
               beats=bool(m > np.percentile(sets, 95)), regns={r: sum(1 for e in ve if e["regime"] == r) for r in ("up", "down", "range")})
    return out


def judge(rows, correct=True):
    """rows: score_cell outputs for the whole family. BH over all cells (n < MIN_N enters with p = 1), then verdicts."""
    ps = [r["p"] if r["n"] >= MIN_N else 1.0 for r in rows]
    sv = benjamini_hochberg(ps) if correct else [True] * len(rows)
    for r, s in zip(rows, sv):
        r["bh"] = bool(s)
        r["verdict"] = verdict_for(r["n"], r["lo"], r["beats"], s, r["regns"]) if r["n"] else "UNDERPOWERED"
    return rows


def fmt_row(r):
    if r["n"] == 0:
        return f"| {r['group']} | {r['side']} | 0 | - | - | - | - | UNDERPOWERED |"
    return (f"| {r['group']} | {r['side']} | {r['n']} | {r['hit']:.1f} | {r['net']:+.1f} [{r['lo']:+.1f}, {r['hi']:+.1f}] | "
            f"{r['pl_p']:.2f}{'*' if r['beats'] else ''} | {r['p']:.3f} {'Y' if r['bh'] else 'n'} | {r['verdict']} |")


HEAD = ("| group | side | VAL n | hit % | fee-net bps [95 % CI] | placebo p (* beats p95) | boot p, BH survive | verdict |\n"
        "|---|---|---|---|---|---|---|---|")


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def main():
    cells = (sys.argv[sys.argv.index("--cells") + 1] if "--cells" in sys.argv else "BTC").split(",")
    only = None
    if "--only" in sys.argv:
        only = [tuple(x.split("|")) for x in sys.argv[sys.argv.index("--only") + 1].split(",")]
    maker, taker = _fees()
    assert abs(maker - 4.0) < 1e-9 and abs(taker - 10.0) < 1e-9
    D = lambda s: int(datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    for name in cells:
        if name == "BTC":
            rows, fd, ld = load_btc(), D("2019-01-01"), D("2026-11-10")
        elif name == "ETH":
            rows, fd, ld = load_alt("klines_eth", "ETHUSDT"), D("2022-01-01"), D("2026-09-30")
        else:
            rows, fd, ld = load_alt("klines_sol", "SOLUSDT"), D("2022-01-01"), D("2024-06-30")
        print(name, "bars", len(rows), flush=True)
        c = prepare(name, rows, fd, ld, maker, taker)
        fam = [score_cell(c, g, s, maker) for g, s in CELLS]
        judge(fam, correct=(name == "BTC"))
        if only:
            fam = [r for r in fam if (r["group"], r["side"]) in only]
        mixn = max(1, sum(c["mix"].values()))
        L = [f"# Live Aid idea-flag groups, full-history test, cell {name} ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})", "",
             f"Frozen in PRE_REG.md. Cell {name} {iso(c['first'])}..{iso(c['last'])}, VALIDATION from {iso(c['cut'])}; node {json.dumps(c['node'])}; events scored {len(c['events'])}, skipped {c['skipped']}.",
             f"Regime mix: up {100*c['mix']['up']/mixn:.1f} % / down {100*c['mix']['down']/mixn:.1f} % / range {100*c['mix']['range']/mixn:.1f} %", "", HEAD]
        L += [fmt_row(r) for r in fam]
        npass = [r for r in fam if r["verdict"].startswith("PASS")]
        L += ["", f"PASS cells: {len(npass)} " + ", ".join(f"{r['group']} {r['side']}" for r in npass)]
        open(os.path.join(HERE, "REPORT_RAW_%s.md" % name), "w", encoding="utf-8").write("\n".join(L) + "\n")
        json.dump(fam, open(os.path.join(HERE, f"cells_{name}.json"), "w"), indent=1)
        print("\n".join(L))


if __name__ == "__main__":
    main()
