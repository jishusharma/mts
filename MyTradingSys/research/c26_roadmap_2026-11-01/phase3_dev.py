"""C26 Phase 3, DEV run: the DOWN-regime fade (single short after a held high is taken out) with TWO definitions of the held high H1
and the pre-registered H2 filters of PHASE1_RANGE.md Q5. Fee-net, DEV only (2022-04-01 .. 2024-06-30). Research, no orders.

H1 sets
  c26    C26 pivot high +-16 15m bars (OURS), pull-back >= 0.8 %, first retest within 0.4 %, held 4 bars, age <= 72h (phase1_recent.py).
  krown  Krown KR-S12 / KR-L09 "dominant lower high" (SOURCED principle: "the most recent high from which a new low was made",
         KROWN_SETUP_CATALOG.md line 820). Implementation OURS: swing high = FORMULAS 18.2 strict fractal, width KR_K = 2;
         the high H becomes dominant at the first bar that prints a low below the lowest low between the previous swing high and H
         (the low H rallied from) AND that low is a record against the last KR_M = 12 bars (a break inside the bounce of a bigger
         leg is not a "new low"); a high taken out before that break is not a lower high. KR_K and KR_M were set once so that the
         operator's six 2026-10-30/31 lines come out as PHASE1_RANGE.md Q4 says Krown names them (4 kept, 2 dropped); not tuned on P&L.
         Known at the close of bar max(break, H + KR_K). Retest, hold and take-out then use the same machine as c26.

Regime (OURS, known at the time): DOWN = close of the bar before the take-out below its 200-bar mean of 15m closes (REG_N).
Trade (OURS; book() of phase1_ladder_look.py): entry = first 15m close back under H1 from the take-out bar on (signal bar s); ONE stop at
  H1 + 1.0 %, target = L1 touch (a bar touching both counts the stop), time = close of bar take-out + 96 (24h). Shifted run (primary) =
  enter at the OPEN of s + 1; unshifted = at the close of s. P&L in % of the entry price minus FEE_PCT (fees.py BINANCE_TAKER x 2).
H2 filters, one arm each, pre-registered in PHASE1_RANGE.md Q5 (never fitted after):
  F0 none | F1 StochRSI(14,14,3,3) K >= 80 at the take-out bar (FORMULAS s23) | F2 no CVD up-impulse at the take-out bar |
  F3 no CVD up-impulse in the 8 bars after entry (known only after entry, so an EXIT RULE: close the short at the close of the first
  up-impulse bar s+1..s+8) | F4 OI not rising from the close before the take-out to 4 bars after (pre-registered window; when s <
  take-out + 4 it reads bars after the entry: counted as look-ahead) | F4c same OI read but only to the signal bar s (causal).
  CVD = 15m sum of 2 x taker_buy - volume of the 1m bars; impulse = |delta| > 1.5 x std of the prior 96 bars (phase1_touch_look.py).
Power gate: the design effect is +0.20 % per trade (OURS); an arm whose MDE (80 % power) is above it is "underpowered, no verdict". Power at the
  observed effect is printed too, but it is a function of the p-value and cannot gate a null.
Base (for the p-value): per event the SAME exit geometry (stop 1.0 %, target = that event's L1 depth, same hold, same F3 rule when the
  arm has it) on 20 random DOWN-regime bars, entered at the open of the next bar. Test = paired difference (event minus its base mean),
  normal p, Holm over all 12 arms (2 sets x F0..F4c). Power: observed effect and +0.20 % (OURS), at the Holm-level alpha 0.05/12.
Stats are per DISTINCT take-out bar (one position per bar: the event with the highest H1); overlapping holds are not modelled.
Usage: python phase3_dev.py <repo> <cache_dir> [--dev 2022-04-01:2024-06-30] [--md FILE] [--sim-json FILE] [--registry FILE]
  1m spot klines from F:/MTS/data/bigtrade/spot_raw (public Binance data, never committed); OI from F:/MTS/data/binance_metrics.
"""
import csv, importlib.util, json, math, os, random, statistics, sys
from bisect import bisect_right
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

_spec = importlib.util.spec_from_file_location("mts_fees", os.path.join(REPO, "MyTradingSys", "backtest", "fees.py"))
_fees = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fees)
FEE_PCT = _fees.BINANCE_TAKER * 2 * 100  # % of price, round trip, SOURCED from fees.py

W, PB, NEAR, MAXAGE, CONF = 16, 0.008, 0.004, 288, 4      # C26, OURS (phase1_recent.py)
KR_K, KR_M = 2, 12                                          # Krown finder: fractal width, record-low look-back (bars); OURS
REG_N = 200                                                 # DOWN regime: close below the 200-bar mean of closes; OURS
STOP_PCT, HOLD, TF = 1.0, 96, 900000                        # stop above H1 in %, 24h in 15m bars, 15m in ms
STOCH_TOP, IMP_K, IMP_W, F3_BARS, OB = 80, 1.5, 96, 8, 53  # H2 thresholds, OURS (phase1_touch_look.py)
BASE_DRAWS, SEED, ALPHA, EFFECT = 20, 20261101, 0.05, 0.20  # random-entry base draws per event, rng seed, family alpha, design effect in %
FAMILY = 12                                                 # Holm family: 2 H1 sets x 6 arms
DEV_START_MS = int(datetime(2022, 4, 1, tzinfo=timezone.utc).timestamp() * 1000)
DEV_END_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)  # exclusive: the sealed split starts here
WARM_FROM = datetime(2022, 3, 1, tzinfo=timezone.utc)
LAST_MONTH = (2024, 6)
SPOT_1M = "F:/MTS/data/bigtrade/spot_raw"
METRICS_DIRS = ["F:/MTS/data/binance_metrics", os.path.join(REPO, "Dumps", "backtest", "raw", "metrics")]
ARMS = ("F0", "F1", "F2", "F3", "F4", "F4c")
SETS = (("c26", "C26 pivot +-16 (OURS)"), ("krown", "Krown dominant lower high (KR-S12)"))


def utc(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc)


def guard_dev(times):
    """Refuse any bar time at or after the sealed VALIDATION start (2024-07-01)."""
    bad = [t for t in times if t >= DEV_END_MS]
    if bad:
        raise ValueError("bar at %s is outside DEV (VALIDATION/HOLDOUT are sealed)" % utc(bad[0]))


# ---------------------------------------------------------------- data

def load_bars(cache):
    """15m bars [t, o, h, l, c, v, taker_buy, minutes] built from the 1m spot files 2022-03 .. 2024-06 (no later month is opened)."""
    path = os.path.join(cache, "p3_bars_15m_dev.json")
    if os.path.exists(path):
        rows = json.load(open(path))
        guard_dev([r[0] for r in rows])
        return rows
    rows, cur = [], None
    y, mth = WARM_FROM.year, WARM_FROM.month
    while (y, mth) <= LAST_MONTH:
        with open(os.path.join(SPOT_1M, "BTCUSDT-1m-%04d-%02d.csv" % (y, mth)), encoding="utf-8") as f:
            for line in f:
                x = line.split(",")
                t = int(x[0])
                if t > 10 ** 14:
                    t //= 1000
                if t >= DEV_END_MS:
                    raise ValueError("1m row %s is outside DEV" % utc(t))
                b = t // TF * TF
                o, h, lo, c, v, tb = float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])
                if cur is None or cur[0] != b:
                    cur = [b, o, h, lo, c, v, tb, 1]
                    rows.append(cur)
                else:
                    cur[2] = max(cur[2], h); cur[3] = min(cur[3], lo); cur[4] = c; cur[5] += v; cur[6] += tb; cur[7] += 1
        y, mth = (y, mth + 1) if mth < 12 else (y + 1, 1)
    guard_dev([r[0] for r in rows])
    json.dump(rows, open(path, "w"))
    return rows


def load_oi(first_ms, last_ms):
    """5m open interest rows (Binance USDT-M metrics sum_open_interest), local daily csv files only. -> times, values, missing days."""
    t, v, missing = [], [], []
    d = utc(first_ms).date()
    while d <= utc(last_ms).date():
        name = "BTCUSDT-metrics-%s.csv" % d.isoformat()
        p = next((os.path.join(x, name) for x in METRICS_DIRS if os.path.exists(os.path.join(x, name))), None)
        if p is None:
            missing.append(d.isoformat())
        else:
            for r in csv.DictReader(open(p, encoding="utf-8")):
                ts = datetime.strptime(r["create_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                t.append(int(ts.timestamp() * 1000)); v.append(float(r["sum_open_interest"]))
        d += timedelta(days=1)
    z = sorted(zip(t, v))
    return [a for a, _ in z], [b for _, b in z], missing


def oi_at(OIt, OIv, close_ms):
    k = bisect_right(OIt, close_ms) - 1
    return OIv[k] if k >= 0 and close_ms - OIt[k] <= 15 * 60000 else None


def impulses(D):
    """+1 / -1 / 0 per bar: |delta| above IMP_K x std of the prior IMP_W deltas."""
    out = [0] * len(D)
    for i in range(IMP_W, len(D)):
        w = D[i - IMP_W:i]
        m = sum(w) / IMP_W
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / IMP_W)
        if sd and abs(D[i]) > IMP_K * sd:
            out[i] = 1 if D[i] > 0 else -1
    return out


def sma(C, n):
    out, s = [None] * len(C), 0.0
    for i, c in enumerate(C):
        s += c
        if i >= n:
            s -= C[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


# ---------------------------------------------------------------- H1 sets

def krown_dominant(H, L, K=KR_K, M=KR_M):
    """Krown KR-S12 dominant lower highs, known at the time. -> [(h, known, brk)]: swing-high bar, bar at whose close it is known,
    bar that printed the new low. See the module docstring for the rule."""
    N = len(H)
    sh = [p for p in range(K, N - K) if all(H[p] > H[q] for q in range(p - K, p + K + 1) if q != p)]
    out = []
    for n, h in enumerate(sh):
        if n == 0:
            continue
        ref = min(L[sh[n - 1]:h + 1])  # the low H rallied from
        for k in range(h + 1, N):
            if H[k] > H[h]:
                break  # taken out before a lower low: not a lower high
            if L[k] < ref:
                if k >= M and L[k] < min(L[k - M:k]):
                    out.append((h, max(k, h + K), k))
                break
    return out


def take_out(H, j, lvl):
    for k in range(j + 1, min(len(H), j + 1 + MAXAGE)):
        if H[k] > lvl:
            return k
    return None


def c26_events(H, L, C, i0):
    """C26 held highs (phase1_recent.run(side=+1) rebuilt without its module-level side effects)."""
    N, pivots, ev = len(H), [], []
    for i in range(2 * W, N - 1):
        p = i - W
        if H[p] == max(H[i - 2 * W:i + 1]):
            pivots.append(dict(p=p, lvl=H[p], pulled=False, done=False, l1=L[p]))
        for pv in pivots:
            if pv["done"]:
                continue
            if i - pv["p"] > MAXAGE or H[i] > pv["lvl"]:
                pv["done"] = True; continue
            if i <= pv["p"] + W:
                pv["l1"] = min(pv["l1"], L[i]); continue
            pv["l1"] = min(pv["l1"], L[i])
            if L[i] <= pv["lvl"] * (1 - PB):
                pv["pulled"] = True
            if not pv["pulled"]:
                continue
            if H[i] >= pv["lvl"] * (1 - NEAR):
                pv["done"] = True
                j = i + CONF
                if j >= N or any(H[m] > pv["lvl"] for m in range(i, j + 1)) or C[j] >= pv["lvl"]:
                    continue
                if pv["p"] >= i0:
                    ev.append(dict(h=pv["p"], lvl=pv["lvl"], l1=pv["l1"], i=i, j=j))
        pivots = [pv for pv in pivots if not pv["done"]]
    return ev


def krown_events(H, L, C, i0):
    N, ev = len(H), []
    for h, known, _ in krown_dominant(H, L):
        if h < i0:
            continue
        lvl, l1 = H[h], min(L[h:known + 1])
        for i in range(known + 1, N):
            l1 = min(l1, L[i])
            if i - h > MAXAGE or H[i] > lvl:
                break
            if H[i] >= lvl * (1 - NEAR):
                j = i + CONF
                if j < N and not any(H[m] > lvl for m in range(i, j + 1)) and C[j] < lvl:
                    ev.append(dict(h=h, lvl=lvl, l1=l1, i=i, j=j))
                break
    return ev


def with_take_outs(ev, m, regime):
    out = []
    for e in ev:
        t = take_out(m["H"], e["j"], e["lvl"])
        if t is None or t < 1 or regime[t - 1] is None:
            continue
        out.append(dict(e, take=t, down=m["C"][t - 1] < regime[t - 1]))
    return out


def distinct(evs):
    """One event per take-out bar: the one with the highest H1."""
    best = {}
    for e in evs:
        if e["take"] not in best or e["lvl"] > best[e["take"]]["lvl"]:
            best[e["take"]] = e
    return sorted(best.values(), key=lambda e: e["take"])


# ---------------------------------------------------------------- the single short

def walk(m, entry, first, end, stop_px, tgt_px, imp, f3):
    """Short from `entry`, bars first..end checked in order: stop (a gap above fills at the open), target touch, F3 up-impulse in the
    first F3_BARS bars (exit at that close), time at end. A bar touching both stop and target counts the stop. -> (exit, why, bar)."""
    for k in range(first, end + 1):
        if m["H"][k] >= stop_px:
            return max(stop_px, m["O"][k]), "stop", k
        if m["L"][k] <= tgt_px:
            return tgt_px, "L1", k
        if f3 and imp is not None and k < first + F3_BARS and imp[k] == 1:
            return m["C"][k], "F3", k
    return m["C"][end], "24h", end


def simulate(m, ev, shift, imp, f3):
    """One event, one short. None = the 24h window runs past the data. why 'nofill' = no 15m close back under H1 (or, shifted, none in time)."""
    lvl, l1, take = ev["lvl"], ev["l1"], ev["take"]
    end = take + HOLD
    if end >= m["N"]:
        return None
    s = next((k for k in range(take, end + 1) if m["C"][k] < lvl), None)
    if s is None or (shift and s + 1 > end):
        return dict(why="nofill", net=None, s=s)
    entry = m["O"][s + 1] if shift else m["C"][s]
    bar_in = s + 1 if shift else s
    geo = dict(stop=STOP_PCT * lvl / entry, target=(entry - l1) / entry * 100)
    if entry <= l1:
        return dict(why="past", net=-FEE_PCT, entry=entry, bar_in=bar_in, bar_out=bar_in, s=s, **geo)
    if s + 1 > end:
        return dict(why="24h", net=-FEE_PCT, entry=entry, bar_in=bar_in, bar_out=s, s=s, **geo)
    exit_px, why, bar = walk(m, entry, s + 1, end, lvl * (1 + STOP_PCT / 100), l1, imp, f3)
    return dict(why=why, net=(entry - exit_px) / entry * 100 - FEE_PCT, entry=entry, bar_in=bar_in, bar_out=bar, s=s, **geo)


def base_mean(m, ev, sim, pool, imp, f3, rng):
    """Mean net of BASE_DRAWS random DOWN-regime entries (open of the next bar) with this event's exit geometry."""
    depth = (ev["lvl"] - ev["l1"]) / ev["lvl"] * 100
    hold = ev["take"] + HOLD - (sim["s"] + 1)
    vals = []
    for _ in range(BASE_DRAWS):
        for _try in range(20):
            k0 = rng.choice(pool)
            if k0 + 1 + hold < m["N"]:
                break
        else:
            continue
        entry = m["O"][k0 + 1]
        exit_px, _, _ = walk(m, entry, k0 + 1, k0 + 1 + hold, entry * (1 + STOP_PCT / 100), entry * (1 - depth / 100), imp, f3)
        vals.append((entry - exit_px) / entry * 100 - FEE_PCT)
    return sum(vals) / len(vals)


# ---------------------------------------------------------------- statistics

def stats(x):
    if not x:
        return None
    return dict(n=len(x), mean=sum(x) / len(x), median=statistics.median(x), win=100.0 * sum(1 for v in x if v > 0) / len(x),
                sum=sum(x), worst=min(x))


def paired(d):
    """Paired difference vs the base: mean, se, t, two-sided normal p, power at the observed effect and at EFFECT (Holm-level alpha)."""
    from MyTradingSys.backtest.research_kit import norm_p_two, mde
    nd = statistics.NormalDist()
    n = len(d)
    if n < 3:
        return None
    mean, sd = sum(d) / n, statistics.stdev(d)
    se = sd / math.sqrt(n) if sd > 0 else float("nan")
    z = nd.inv_cdf(1 - ALPHA / (2 * FAMILY))
    t = mean / se
    return dict(mean=mean, se=se, t=t, p=norm_p_two(t), power=nd.cdf(abs(mean) / se - z), power_design=nd.cdf(EFFECT / se - z), mde=mde(se))


def read_line(st, pr, p_holm):
    """Power gate first. Power at the OBSERVED effect is a function of the p-value (post-hoc), so it cannot gate a null result: the gate is
    the power to see the design effect EFFECT at this n (MDE <= EFFECT, power >= 0.8). Below it: no verdict, whatever the p."""
    if pr is None or st is None:
        return "too few trades"
    if pr["power_design"] < 0.8:
        return "underpowered, no verdict (MDE %.2f %%)" % pr["mde"]
    if p_holm < ALPHA and pr["mean"] > 0 and st["mean"] > 0:
        return "beats base, net > 0"
    if p_holm < ALPHA and pr["mean"] < 0:
        return "worse than base"
    return "powered, no edge vs base (MDE %.2f %%)" % pr["mde"]


# ---------------------------------------------------------------- run

def run_set(name, ev_all, m, ctx, rng):
    """All arms of one H1 set. -> dict with counts, per-arm rows (distinct take-out bars, shifted primary) and replay trades."""
    imp, K, WT, OIt, OIv = ctx["imp"], ctx["K"], ctx["WT"], ctx["OIt"], ctx["OIv"]
    pool = ctx["pool"]
    down = [e for e in ev_all if e["down"]]
    up = [e for e in ev_all if not e["down"]]
    cache = {}

    def sims(e, f3):
        key = (e["take"], e["lvl"], f3)
        if key not in cache:
            cache[key] = (simulate(m, e, True, imp, f3), simulate(m, e, False, imp, f3))
        return cache[key]

    def base(e, f3):
        key = ("b", e["take"], e["lvl"], f3)
        if key not in cache:
            sh = sims(e, f3)[0]
            cache[key] = base_mean(m, e, sh, pool, imp, f3, rng) if sh and sh["net"] is not None else None
        return cache[key]

    def doi(e, last):
        a, b = oi_at(OIt, OIv, m["T"][e["take"] - 1] + TF), oi_at(OIt, OIv, m["T"][last] + TF)
        return (b / a - 1) * 100 if a and b else None

    def keep(arm, e):
        t = e["take"]
        if arm == "F1":
            return K[t] is not None and K[t] >= STOCH_TOP
        if arm == "F2":
            return imp[t] != 1
        if arm == "F4":
            x = doi(e, min(m["N"] - 1, t + 4))
            return x is not None and x <= 0
        if arm == "F4c":
            s = sims(e, False)[0]
            if not s or s.get("s") is None:
                return False
            x = doi(e, s["s"])
            return x is not None and x <= 0
        return True
    rows = {}
    for arm in ARMS:
        f3 = arm == "F3"
        evs = [e for e in down if keep(arm, e)]
        dis = distinct(evs)
        net, net_un, bse, diff, trades = [], [], [], [], []
        for e in dis:
            sh, un = sims(e, f3)
            if sh is None or sh["net"] is None:
                continue
            b = base(e, f3)
            net.append(sh["net"]); bse.append(b); diff.append(sh["net"] - b); trades.append((e, sh))
            if un and un["net"] is not None:
                net_un.append(un["net"])
        look = sum(1 for e, sh in trades if arm == "F4" and sh["s"] < e["take"] + 4)
        why = {w: sum(1 for _, sh in trades if sh["why"] == w) for w in ("L1", "stop", "24h", "F3", "past")}
        rows[arm] = dict(events=len(evs), distinct=len(dis), traded=len(net), st=stats(net), un=stats(net_un), pr=paired(diff),
                         base=sum(bse) / len(bse) if bse else None, why=why, lookahead=look, trades=trades, net=net)
    # context: UP regime F0 and WaveTrend OB at the take-out of the DOWN F0 trades (not filters, not in the family)
    upn = []
    for e in distinct(up):
        sh = sims(e, False)[0]
        if sh and sh["net"] is not None:
            upn.append(sh["net"])
    wt = {}
    def cross(e):  # wt1 under wt2 on some bar of the take-out bar + 7 (2h), as the Q5 look; read after the fact, context only
        return any(WT[k].wt1 < WT[k].wt2 for k in range(e["take"], min(m["N"], e["take"] + 8)))
    for lab, fn in (("wt1 >= 53 at take-out", lambda e: WT[e["take"]].wt1 >= OB), ("wt1 < 53 at take-out", lambda e: WT[e["take"]].wt1 < OB),
                    ("WT cross down within 2h of the take-out", cross), ("no WT cross down within 2h", lambda e: not cross(e))):
        wt[lab] = stats([sh["net"] for e, sh in rows["F0"]["trades"] if WT[e["take"]].wt1 == WT[e["take"]].wt1 and fn(e)])
    counts = dict(taken=len(ev_all), down=len(down), up=len(up), down_distinct=len(distinct(down)), up_distinct=len(distinct(up)))
    return dict(name=name, rows=rows, up=stats(upn), wt=wt, counts=counts)


def f(x, fmt="%+.3f"):
    return "-" if x is None or x != x else fmt % x


def tables(results, meta):
    """Markdown for PHASE1_RANGE.md Q6. Holm is applied here over the whole family."""
    from MyTradingSys.backtest.research_kit import holm
    keys = [(r["name"], a) for r in results for a in ARMS]
    ps = [r["rows"][a]["pr"]["p"] if r["rows"][a]["pr"] else 1.0 for r in results for a in ARMS]
    ph = dict(zip(keys, holm(ps, FAMILY)))
    out = []
    for r in results:
        out.append("\n**%s**: %d take-outs (%d distinct bars), DOWN %d (%d distinct), UP %d (%d distinct)\n" % (
            dict(SETS)[r["name"]], r["counts"]["taken"], r["counts"]["down_distinct"] + r["counts"]["up_distinct"], r["counts"]["down"],
            r["counts"]["down_distinct"], r["counts"]["up"], r["counts"]["up_distinct"]))
        out.append("| arm | events | distinct bars | traded | mean net % | median | win % | sum % | worst % | mean net % unshifted | base mean % | mean minus base % | p | Holm p | power (observed) | MDE 80 % | power at +0.20 % | read |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for a in ARMS:
            x = r["rows"][a]
            st, pr = x["st"], x["pr"]
            out.append("| %s | %d | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                a, x["events"], x["distinct"], x["traded"], f(st and st["mean"]), f(st and st["median"]), f(st and st["win"], "%.0f"),
                f(st and st["sum"], "%+.1f"), f(st and st["worst"], "%+.2f"), f(x["un"] and x["un"]["mean"]), f(x["base"]),
                f(pr and pr["mean"]), f(pr and pr["p"], "%.3f"), f(ph[(r["name"], a)], "%.3f"), f(pr and pr["power"], "%.2f"),
                f(pr and pr["mde"], "%.2f"), f(pr and pr["power_design"], "%.2f"), read_line(st, pr, ph[(r["name"], a)])))
        out.append("")
        out.append("exits (shifted, distinct): " + "; ".join("%s: L1 %d / stop %d / 24h %d%s" % (
            a, r["rows"][a]["why"]["L1"], r["rows"][a]["why"]["stop"], r["rows"][a]["why"]["24h"],
            " / F3 %d" % r["rows"][a]["why"]["F3"] if a == "F3" else "") for a in ARMS)
            + "; F4 pre-registered window read bars after the entry in %d of %d trades" % (r["rows"]["F4"]["lookahead"], r["rows"]["F4"]["traded"]))
        up, wt = r["up"], r["wt"]
        out.append("\ncontext (not in the family): F0 in the UP regime, n=%s mean net %s %%; WaveTrend at the take-out, DOWN F0 trades: %s" % (
            up and up["n"], f(up and up["mean"]), "; ".join("%s: n=%s, %s %%" % (k, v and v["n"], f(v and v["mean"])) for k, v in wt.items())))
    return "\n".join(out), ph


def sim_card(results, ph, meta):
    def row(r, a):
        x = r["rows"][a]; st, pr = x["st"], x["pr"]
        return [dict(SETS)[r["name"]], a, str(x["distinct"]), str(x["traded"]), f(st and st["mean"]), f(st and st["win"], "%.0f"),
                f(x["base"]), f(pr and pr["mean"]), f(ph[(r["name"], a)], "%.3f"), f(pr and pr["power"], "%.2f"), read_line(st, pr, ph[(r["name"], a)])]
    cols = ["H1 set", "arm", "distinct take-out bars", "traded", "mean net % (shifted)", "win %", "random-entry base %", "mean minus base %", "Holm p",
            "power (observed)", "read"]
    rows = [row(r, a) for r in results for a in ARMS]
    replay = []
    for r in results:
        tr, cum, s = [], [], 0.0
        for e, sh in r["rows"]["F0"]["trades"]:
            R = sh["net"] / sh["stop"]
            s += R; cum.append(round(s, 3))
            tr.append({"d": utc(meta["T"][sh["bar_in"]]).strftime("%Y-%m-%d"), "s": -1,
                       "f": "%s H1 taken, short back under it (exit: %s)" % (r["name"], sh["why"]),
                       "l2": round(-sh["stop"], 3), "t1": round(sh["target"], 3), "t2": round(sh["target"], 3), "r": round(R, 3)})
        replay.append({"kind": "replay", "title": "F0 replay, %s (every trade, in time order)" % dict(SETS)[r["name"]],
                       "caption": "Distance from the entry in %; up is in favour of the short. No prices.", "trades": tr, "cum": cum})
    tradable = [(r["name"], a) for r in results for a in ARMS
                if r["rows"][a]["pr"] and r["rows"][a]["pr"]["power"] >= 0.8 and ph[(r["name"], a)] < ALPHA and r["rows"][a]["pr"]["mean"] > 0]
    pos = sum(1 for r in results for a in ARMS if r["rows"][a]["st"] and r["rows"][a]["st"]["mean"] > 0)
    under = ["%s %d/6" % (r["name"], sum(1 for a in ARMS if r["rows"][a]["pr"] and r["rows"][a]["pr"]["power_design"] < 0.8)) for r in results]
    verdict = ("YES on DEV: " + ", ".join("%s %s" % x for x in tradable)) if tradable else         "NO on DEV: %d of 12 arms net above zero after fees, none beats random entries after Holm; underpowered arms (MDE above +0.20 %%): %s" % (
            pos, ", ".join(under))
    kp = []
    for r in results:
        x = r["rows"]["F0"]
        kp.append({"label": "%s F0 mean net, shifted (n %d)" % (r["name"], x["traded"]), "value": f(x["st"] and x["st"]["mean"]) + " %",
                   "tone": "good" if x["st"] and x["st"]["mean"] > 0 else "bad"})
    mk = lambda n, v, l="OURS": {"name": n, "value_plain": v, "label": l}
    return {
        "id": "c26-h1-structural-lower-high", "kind": "backtest", "family": "Eagle_Eyes chart ideas (operator, 10-30/31)",
        "provenance": "run", "title": "C26 DOWN-regime fade on DEV: C26 pivot vs Krown dominant lower high as H1, with the pre-registered H2 filters",
        "date": meta["date"],
        "what": [
            mk("Setup", "a held 15m high H1 is taken out in a DOWN regime; short at the first 15m close back under H1, next-bar open (shifted)"),
            mk("H1 set 1", "C26 pivot +-16, pull-back >= 0.8 %, retest within 0.4 % held 4 bars, age <= 72h"),
            mk("H1 set 2", "Krown dominant lower high: the high from which a new low was made (KR-S12, KROWN_SETUP_CATALOG.md line 820)", "SOURCED"),
            mk("H1 set 2 implementation", "swing high = fractal +-2 (FORMULAS 18.2); new low = below the low H rallied from and a 12-bar record low"),
            mk("DOWN regime", "close before the take-out below the 200-bar mean of 15m closes"),
            mk("Exits", "one stop at H1 + 1.0 %, target = the pull-back low L1, 24h time stop"),
            mk("H2 filters", "F1 StochRSI K >= 80; F2 no CVD up-impulse at the take-out; F3 exit at the first CVD up-impulse in 8 bars; F4 / F4c OI not rising"),
            mk("Costs", "0.10 % per round trip (Binance taker x2, backtest/fees.py); slippage and funding not modelled", "SOURCED"),
            mk("Base", "same exits on 20 random DOWN-regime entries per event; paired test, Holm over 12 arms; power at Holm-level alpha")],
        "how": "phase3_dev.py on Binance spot BTCUSDT 1m -> 15m, DEV 2022-04-01 .. 2024-06-30 only (VALIDATION and HOLDOUT never loaded); "
               "OI from the USDT-M 5m metrics. One distinct position per take-out bar. Re-run: python phase3_dev.py <repo> <cache> --dev 2022-04-01:2024-06-30.",
        "window": "DEV 2022-04-01 to 2024-06-30 (VALIDATION 2024-07+ and HOLDOUT sealed)",
        "verdict": {"label": verdict, "tone": "good" if tradable else "bad"},
        "why": meta["why"], "kpis": kp,
        "examples": [{"kind": "table", "title": "Every arm: fee-net, shifted, distinct take-out bars", "cols": cols, "rows": rows,
                      "caption": "Holm over 12 arms; 'read' needs power >= 0.8 at the observed effect before any p is read"}] + replay,
        "evidence": ["MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RANGE.md"], "missing": [],
        "source_files": ["MyTradingSys/research/c26_roadmap_2026-11-01/phase3_dev.py", "MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RANGE.md"],
        "commit": "this card"}


def main():
    repo, cache = sys.argv[1], sys.argv[2]
    opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    lo, hi = (opt.get("--dev") or "2022-04-01:2024-06-30").split(":")
    if hi > "2024-06-30" or lo < "2022-04-01":
        raise SystemExit("--dev must stay inside 2022-04-01 .. 2024-06-30 (DEV); later bars are sealed")
    sys.path.insert(0, repo)
    spec = importlib.util.spec_from_file_location("chart_verify", os.path.join(repo, "scripts", "dev", "chart_verify.py"))
    CV = importlib.util.module_from_spec(spec); spec.loader.exec_module(CV)
    from MyTradingSys.backtest.layers.wavetrend.wavetrend import compute as wt_compute
    os.makedirs(cache, exist_ok=True)
    rows = load_bars(cache)
    T = [r[0] for r in rows]
    guard_dev(T)
    m = dict(T=T, O=[r[1] for r in rows], H=[r[2] for r in rows], L=[r[3] for r in rows], C=[r[4] for r in rows], N=len(rows))
    gaps = sum(1 for i in range(1, m["N"]) if T[i] - T[i - 1] != TF)
    thin = sum(1 for r in rows if r[7] < 15)
    i0 = bisect_right(T, DEV_START_MS - 1)
    OIt, OIv, miss = load_oi(DEV_START_MS - 4 * 86400000, T[-1])
    D = [2 * r[6] - r[5] for r in rows]
    K, _ = CV.stochrsi(m["C"])
    WT = wt_compute([(T[i], m["H"][i], m["L"][i], m["C"][i]) for i in range(m["N"])], TF)
    regime = sma(m["C"], REG_N)
    pool = [k for k in range(max(i0, REG_N), m["N"] - 2) if m["C"][k] < regime[k]]
    ctx = dict(imp=impulses(D), K=K, WT=WT, OIt=OIt, OIv=OIv, pool=pool)
    rng = random.Random(SEED)
    results = []
    for name, _lbl in SETS:
        raw = c26_events(m["H"], m["L"], m["C"], i0) if name == "c26" else krown_events(m["H"], m["L"], m["C"], i0)
        print("%s: %d held retests -> take-outs ..." % (name, len(raw)), file=sys.stderr)
        results.append(run_set(name, with_take_outs(raw, m, regime), m, ctx, rng))
        results[-1]["retests"] = len(raw)
    meta = dict(T=T, date=datetime.now(timezone.utc).strftime("%Y-%m-%d"), why=[])
    md, ph = tables(results, meta)
    head = ("Bars: %d 15m bars %s .. %s UTC (spot BTCUSDT, built from 1m; %d gaps in the 15m series, %d bars with < 15 minutes); DEV window events: "
            "H1 pivot on or after %s; OI days missing: %s; random-entry pool %d DOWN-regime bars." % (
                m["N"], utc(T[0]).strftime("%Y-%m-%d"), utc(T[-1]).strftime("%Y-%m-%d %H:%M"), gaps, thin, lo, ",".join(miss) or "none", len(pool)))
    meta["why"] = []
    for r in results:
        x = r["rows"]["F0"]
        meta["why"].append("%s F0: %d traded, mean net %s %%, random-entry base %s %%, Holm p %s." % (
            dict(SETS)[r["name"]], x["traded"], f(x["st"] and x["st"]["mean"]), f(x["base"]), f(ph[(r["name"], "F0")], "%.3f")))
    for r in results:
        pr = [r["rows"][a]["pr"] for a in ARMS if r["rows"][a]["pr"]]
        pos = sum(1 for a in ARMS if r["rows"][a]["st"] and r["rows"][a]["st"]["mean"] > 0)
        meta["why"].append("%s: MDE (80 %% power) %.2f-%.2f %% per trade against a design effect of +%.2f %%; %d of 6 arms have a positive mean net; "
                           "lowest Holm p %s; F0 in the UP regime: mean net %s %% (n %s)." % (
                               dict(SETS)[r["name"]], min(x["mde"] for x in pr), max(x["mde"] for x in pr), EFFECT, pos,
                               f(min(ph[(r["name"], a)] for a in ARMS), "%.3f"), f(r["up"] and r["up"]["mean"]), r["up"] and r["up"]["n"]))
    meta["why"].append("Power gate first: an arm whose MDE is above the +0.20 % design effect is 'underpowered, no verdict' whatever its p.")
    text = head + "\n" + md + "\n"
    print(text)
    if "--md" in opt:
        open(opt["--md"], "w", encoding="utf-8", newline="\n").write(text)
    if "--sim-json" in opt:
        with open(opt["--sim-json"], "w", encoding="utf-8", newline="\n") as fh:
            json.dump(sim_card(results, ph, meta), fh, indent=1, ensure_ascii=False); fh.write("\n")
    if "--registry" in opt:
        with open(opt["--registry"], "a", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            for r in results:
                for a in ARMS:
                    x = r["rows"][a]
                    w.writerow(["c26_roadmap_2026-11-01", "P3_%s_%s" % (r["name"], a), meta["date"], "DEV",
                                "Binance spot BTCUSDT 1m->15m 2022-04..2024-06 + USDT-M metrics",
                                "DOWN-regime fade, H1=%s, filter %s: traded %d, mean net %s %%, Holm p %s" % (
                                    r["name"], a, x["traded"], f(x["st"] and x["st"]["mean"]), f(ph[(r["name"], a)], "%.3f")), "pre-registered"])


if __name__ == "__main__":
    main()
