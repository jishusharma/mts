"""T04 first-touch sweep-and-reclaim of prior-day / prior-week high/low (eh-h3-first-touch-sweep).

Rules: see PRE_REG.md (frozen). Modes:
  python first_touch.py count   DEV bars, events per year/side/type (no returns)
  python first_touch.py dev     DEV returns, DEV screen -> dev_screen.json, cells.csv (DEV cuts)
  python first_touch.py val     VALIDATION once, only if dev_screen.json says screened in
Cache: F:/MTS/Dumps/backtest/eh_h3_first_touch (outside the repo). Only small summaries are written here.
"""
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from MyTradingSys.backtest import fees  # noqa: E402  (single cost module, T06-F2)

DAY = 86400000
M15 = 900000
NB = 96              # 15m bars per UTC day
NW = 7 * NB          # 15m bars per ISO week
FEE_RT = round(fees.BINANCE_TAKER * 2 + fees.SLIPPAGE_RT_S13, 12)   # regime A: 2 x 5 bps taker + 2 bps RT slippage (fees.py; FORMULAS s13) = 0.0012 (round: float noise)
HOLD = 96            # time stop, bars after the reclaim bar
RECLAIM = 3          # V-sweep: reclaim close within s..s+3
APPROACH = 12        # close 12 bars before the sweep bar must be inside the level
TARGET_R = 2.0
Z_ONE = 1.959963984540054
Z_POWER = 2.8016        # z(0.975) + z(0.80)
HOLM_FIRST = 0.05 / 15  # Holm first step at m = 15 (PRE_REG s DECISION 7)

CACHE = Path("F:/MTS/Dumps/backtest/eh_h3_first_touch")
OUT = Path(__file__).resolve().parent
SYMBOL = "BTCUSDT"


def ms(s):
    return int(datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


SPLIT_END = {"DEV": ms("2024-06-30") + DAY - M15, "VAL": ms("2025-06-30") + DAY - M15}
VAL_WARMUP_START = ms("2024-06-29")


class SplitViolation(Exception):
    pass


def check_request(split, start_ms, end_ms):
    """Refuse any request past the split end (and any HOLDOUT read). PLAN.md s5."""
    if split == "HOLDOUT":
        raise SplitViolation("HOLDOUT (2025-07-01 onward) is never loaded")
    if split not in SPLIT_END:
        raise SplitViolation("unknown split " + str(split))
    if end_ms > SPLIT_END[split]:
        raise SplitViolation("%s request ends %s, past split end" % (split, end_ms))
    if split == "VAL" and start_ms < VAL_WARMUP_START:
        raise SplitViolation("VAL request starts before the 2-day warm-up")


def arr_from(t0, rows):
    """rows = list of (o, h, l, c). Bars are 15m, open time t0 + i*15m."""
    a = np.asarray(rows, dtype=float)
    n = len(a)
    return {
        "t": (t0 + np.arange(n, dtype=np.int64) * M15),
        "o": a[:, 0].copy(), "h": a[:, 1].copy(), "l": a[:, 2].copy(), "c": a[:, 3].copy(),
    }


def fee_r(stop_frac):
    return FEE_RT / stop_frac


def _months(start_ms, end_ms):
    d0 = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
    d1 = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc)
    y, m = d0.year, d0.month
    out = []
    while (y, m) <= (d1.year, d1.month):
        out.append("%04d-%02d" % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def load_bars(split):
    """15m BTCUSDT klines for a split from the cache. DEV: data start..2024-06-30; VAL: warm-up..2025-06-30."""
    start = ms("2020-01-01") if split == "DEV" else VAL_WARMUP_START
    end = SPLIT_END[split]
    check_request(split, start, end)
    rows = []
    for mo in _months(start, end):
        p = CACHE / "klines" / ("%s-15m-%s.csv" % (SYMBOL, mo))
        with open(p, encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0].strip().isdigit():
                    t = int(row[0])
                    if start <= t <= end:
                        rows.append((t, float(row[1]), float(row[2]), float(row[3]), float(row[4])))
    rows = sorted(set(rows))
    a = np.asarray(rows, dtype=float)
    arr = {"t": a[:, 0].astype(np.int64), "o": a[:, 1], "h": a[:, 2], "l": a[:, 3], "c": a[:, 4]}
    assert arr["t"][-1] <= end
    return arr


def load_funding(split):
    start = ms("2020-01-01") if split == "DEV" else VAL_WARMUP_START
    end = SPLIT_END[split]
    check_request(split, start, end)
    rows = []
    for mo in _months(start, end):
        p = CACHE / "fundingRate" / ("%s-fundingRate-%s.csv" % (SYMBOL, mo))
        with open(p, encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0].strip().isdigit():
                    t = int(row[0])
                    if start <= t <= end:
                        rows.append((t, float(row[2])))
    rows = sorted(set(rows))
    a = np.asarray(rows, dtype=float) if rows else np.zeros((0, 2))
    return a[:, 0].astype(np.int64), a[:, 1]


def windows(arr, kind):
    """Level windows. kind 'D': PDH/PDL of UTC day D-1, active over day D. kind 'W': PWH/PWL of the ISO week
    before the Monday m, active over the week starting at m. A level is usable only once its prior period is complete."""
    t = arr["t"]
    h, l = arr["h"], arr["l"]
    if len(t) == 0:
        return []
    period = 1 if kind == "D" else 7
    plen = period * NB
    first_day = int(t[0] // DAY)
    last_day = int(t[-1] // DAY)
    if kind == "D":
        days = range(first_day + 1, last_day + 1)
    else:
        m0 = first_day + ((-(first_day + 3)) % 7)     # first Monday day index (day 0 = Thursday)
        days = range(m0, last_day + 1, 7)
    out = []
    for d in days:
        fix = d * DAY
        pstart = (d - period) * DAY
        end = (d + period) * DAY
        pi0 = int(np.searchsorted(t, pstart))
        pi1 = int(np.searchsorted(t, fix))
        if pi1 - pi0 != plen:
            continue
        i0 = pi1
        i1 = int(np.searchsorted(t, end))
        if i1 <= i0:
            continue
        out.append({"kind": kind, "fix": fix, "end": end, "i0": i0, "i1": i1,
                    "H": float(h[pi0:pi1].max()), "L": float(l[pi0:pi1].min())})
    return out


def setups(arr, win):
    """First-touch (arm 'first') and repeat (arm 'repeat', exploratory) sweep-and-reclaim setups in one window."""
    t, h, l, c = arr["t"], arr["h"], arr["l"], arr["c"]
    i0, i1 = win["i0"], win["i1"]
    lo = max(i0 - 1, 0)
    out = []
    for side in ("H", "L"):
        lvl = win["H"] if side == "H" else win["L"]
        if side == "H":
            beyond = h[lo:i1] > lvl
            inside = lambda x: x < lvl  # noqa: E731
        else:
            beyond = l[lo:i1] < lvl
            inside = lambda x: x > lvl  # noqa: E731
        ep = 0
        for j in range(1, len(beyond)):
            if not (beyond[j] and not beyond[j - 1]):
                continue
            s = lo + j
            ep += 1
            if ep > 2:
                break
            arm = "first" if ep == 1 else "repeat"
            if s - APPROACH < 0 or not inside(c[s - APPROACH]):
                continue
            r = None
            for k in range(s, min(s + RECLAIM, i1 - 1) + 1):
                if inside(c[k]):
                    r = k
                    break
            if r is None:
                continue
            ext = float(h[s:r + 1].max()) if side == "H" else float(l[s:r + 1].min())
            entry = float(c[r])
            stop_dist = (ext - entry) if side == "H" else (entry - ext)
            if stop_dist <= 0:
                continue
            out.append({"kind": win["kind"], "side": side, "arm": arm, "s": int(s), "r": int(r),
                        "ext": ext, "entry": entry, "stop_frac": stop_dist / entry, "level": lvl,
                        "t_r": int(t[r]), "t_s": int(t[s]), "fix": win["fix"]})
    return out


def outcome(arr, st, fund=None):
    """Gross R, fee R, funding R, net R for one setup. fund = (times_ms, rates) or None.
    Stop wins a same-bar tie. Entry = close of r; hold bars r+1..r+HOLD; time stop at close of r+HOLD."""
    t, h, l, c = arr["t"], arr["h"], arr["l"], arr["c"]
    r = st["r"]
    side = st["side"]
    ext, entry = st["ext"], st["entry"]
    stop_dist = abs(ext - entry)
    sign = -1.0 if side == "H" else 1.0             # position sign (short -1, long +1)
    tgt = entry - TARGET_R * stop_dist if side == "H" else entry + TARGET_R * stop_dist
    n = len(t)
    if r + HOLD >= n:
        return {"censored": True}
    kind, exit_px, k_exit = None, None, None
    for k in range(r + 1, r + HOLD + 1):
        if side == "H":
            stop_hit, tgt_hit = h[k] >= ext, l[k] <= tgt
        else:
            stop_hit, tgt_hit = l[k] <= ext, h[k] >= tgt
        if stop_hit:
            kind, exit_px, k_exit = "stop", ext, k
            break
        if tgt_hit:
            kind, exit_px, k_exit = "target", tgt, k
            break
    if kind is None:
        kind, exit_px, k_exit = "time", float(c[r + HOLD]), r + HOLD
    gross = sign * (exit_px - entry) / stop_dist
    fee = fee_r(st["stop_frac"])
    fund_r = 0.0
    if fund is not None and len(fund[0]):
        ft_, fr = fund
        t_entry, t_exit = int(t[r]) + M15, int(t[k_exit]) + M15
        msk = (ft_ > t_entry) & (ft_ <= t_exit)
        fund_r = sign * float(fr[msk].sum()) / st["stop_frac"]
    net = gross - fee - fund_r
    return {"censored": False, "exit_kind": kind, "gross": gross, "fee": fee, "fund": fund_r,
            "net": net, "k_exit": int(k_exit), "t_exit": int(t[k_exit]) + M15}


def knife(arr, s, side, lookback=12, min_move=0.02, max_counter=0.25):
    """EXPLORATORY (OURS). Prior `lookback` bars moved >= 2 % in the sweep direction and the largest
    counter-move is < 25 % of that move. side 'L' = falling market (low sweep), 'H' = rising."""
    c = arr["c"]
    seg = c[s - lookback - 1:s]
    start = seg[0]
    if side == "L":
        low = seg.min()
        fall = start - low
        if fall / start < min_move:
            return False
        run_min = np.minimum.accumulate(seg)
        counter = float(np.max(seg - run_min))
        return bool(counter < max_counter * fall)
    high = seg.max()
    rise = high - start
    if rise / start < min_move:
        return False
    run_max = np.maximum.accumulate(seg)
    counter = float(np.max(run_max - seg))
    return bool(counter < max_counter * rise)


def add_knife(arr, st):
    st["knife"] = bool(knife(arr, st["s"], st["side"])) if st["s"] - 13 >= 0 else False
    return st


def build_events(arr, fund, want_returns):
    """All setups over D and W windows. Returns list of dicts (arm, side, kind, outcome if requested)."""
    evs = []
    for kind in ("D", "W"):
        for w in windows(arr, kind):
            for st in setups(arr, w):
                add_knife(arr, st)
                st["year"] = datetime.fromtimestamp(st["t_s"] / 1000, tz=timezone.utc).year
                st["day"] = st["t_r"] // DAY
                st["block4h"] = (st["t_s"] % DAY) // (4 * 3600000)
                if want_returns:
                    o = outcome(arr, st, fund)
                    if o["censored"]:
                        st["censored"] = True
                        continue
                    st.update(o)
                evs.append(st)
    return evs


def cluster_stats(vals, days):
    """Mean, day-clustered SE, CI, one-sided p (mean > 0), MDE at 80 % power. vals/days numpy arrays."""
    n = len(vals)
    if n == 0:
        return None
    m = float(vals.mean())
    if n > 1:
        resid = vals - m
        uniq, inv = np.unique(days, return_inverse=True)
        sg = np.bincount(inv, weights=resid)
        se = math.sqrt(float((sg ** 2).sum())) / n
    else:
        se = float("nan")
    p = 0.5 * math.erfc((m / se) / math.sqrt(2)) if se and se > 0 else float("nan")
    return {"n": n, "mean": m, "se": se, "ci_lo": m - Z_ONE * se, "ci_hi": m + Z_ONE * se,
            "p_one": p, "mde": Z_POWER * se}


def summarize(name, evs):
    if not evs:
        return {"cut": name, "n": 0}
    net = np.array([e["net"] for e in evs])
    gross = np.array([e["gross"] for e in evs])
    fee = np.array([e["fee"] for e in evs])
    fund = np.array([e["fund"] for e in evs])
    days = np.array([e["day"] for e in evs])
    st = cluster_stats(net, days)
    st.update({"cut": name, "hit": float((net > 0).mean()), "gross": float(gross.mean()),
               "fee": float(fee.mean()), "fund": float(fund.mean())})
    return st


def regime_mix(arr):
    """research_kit.regime_tag over DEV Mondays (OURS: weekly/monthly closes and RSI14 from the same bars)."""
    try:
        sys.path.insert(0, str(OUT.parents[4]))
        sys.path.insert(0, str(OUT.parents[3] / "backtest"))
        import research_kit as rk
    except Exception as e:  # pragma: no cover
        return "Regime mix: NOT_IN_DATA (research_kit import failed: %s)" % e
    t, c = arr["t"], arr["c"]
    days = t // DAY

    def closes(period_days):
        key = (days - 0) if period_days == 1 else None
        res_t, res_c = [], []
        if period_days == 1:
            ids = days
            tcl = lambda k: (k + 1) * DAY  # noqa: E731
        elif period_days == 7:
            ids = (days + 3) // 7
            tcl = lambda k: (k * 7 - 3 + 7) * DAY  # noqa: E731
        else:
            dt = [datetime.fromtimestamp(x / 1000, tz=timezone.utc) for x in t[::NB]]
            ids = np.array([d.year * 12 + d.month - 1 for d in dt])
            ids = np.repeat(ids, NB)[:len(t)]
            tcl = lambda k: ms("%04d-%02d-01" % (k // 12, k % 12 + 1)) + 0  # noqa: E731
        last = {}
        for i in range(len(t)):
            last[int(ids[i])] = i
        for k in sorted(last):
            res_t.append(tcl(k) if period_days != 30 else tcl(k + 1))
            res_c.append(float(c[last[k]]))
        del key
        return res_t, res_c

    def rsi14(cl):
        out = [None] * len(cl)
        if len(cl) < 15:
            return out
        d = np.diff(np.asarray(cl))
        g, lo_ = np.clip(d, 0, None), np.clip(-d, 0, None)
        ag, al = g[:14].mean(), lo_[:14].mean()
        for i in range(14, len(cl)):
            if i > 14:
                ag = (ag * 13 + g[i - 1]) / 14
                al = (al * 13 + lo_[i - 1]) / 14
            out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
        return out

    try:
        dt_, dc = closes(1)
        wt, wc = closes(7)
        mt, mc = closes(30)
        dser = (np.array(dt_, dtype=np.int64), np.array(dc))
        wr = rsi14(wc)
        mr = rsi14(mc)
        wrs = ([x for x, v in zip(wt, wr) if v is not None], [v for v in wr if v is not None])
        mrs = ([x for x, v in zip(mt, mr) if v is not None], [v for v in mr if v is not None])
        tags = []
        for tm in range(ms("2024-06-03") - 0, SPLIT_END["DEV"], 7 * DAY):
            pass
        mon = [int(x) for x in range(0)]
        del mon
        start_dev = ms("2020-01-01")
        m0 = start_dev + ((-(start_dev // DAY + 3)) % 7) * DAY
        dev_mondays = [x for x in range(m0, SPLIT_END["DEV"], 7 * DAY)]
        for tm in dev_mondays:
            tags.append(rk.regime_tag(tm, (list(dser[0]), list(dser[1])), wrs, mrs)["regime"])
        return rk.regime_mix_line(tags)
    except Exception as e:  # pragma: no cover
        return "Regime mix: NOT_IN_DATA (regime tag failed: %s)" % e


def write_cells(rows, path):
    keys = ["cut", "n", "hit", "gross", "fee", "fund", "mean", "se", "ci_lo", "ci_hi", "p_one", "mde", "censored"]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(r[k], 6) if isinstance(r.get(k), float) else r.get(k)) for k in keys})


def main(argv):
    mode = argv[1] if len(argv) > 1 else "count"
    if mode == "count":
        arr = load_bars("DEV")
        evs = build_events(arr, None, want_returns=False)
        from collections import Counter
        cnt = Counter((e["year"], e["side"], e["kind"], e["arm"]) for e in evs)
        lines = ["year,side,level,arm,count"] + ["%d,%s,%s,%s,%d" % (k[0], k[1], k[2], k[3], v)
                                                 for k, v in sorted(cnt.items())]
        (OUT / "count_pass.csv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print("\n".join(lines))
        print("Regime mix: " + regime_mix(arr).replace("Regime mix: ", ""))
        return
    if mode in ("dev", "val"):
        split = "DEV" if mode == "dev" else "VAL"
        if mode == "val":
            scr = json.loads((OUT / "dev_screen.json").read_text(encoding="utf-8"))
            if not scr.get("screened_in"):
                raise SystemExit("VALIDATION refused: DEV screen not passed")
        arr = load_bars(split)
        fund = load_funding(split)
        evs = build_events(arr, fund, want_returns=True)
        if split == "VAL":
            evs = [e for e in evs if ms("2024-07-01") <= e["t_s"] <= SPLIT_END["VAL"]]
        else:
            evs = [e for e in evs if e["t_s"] < SPLIT_END["DEV"]]
        first = [e for e in evs if e["arm"] == "first"]
        rep = [e for e in evs if e["arm"] == "repeat"]
        rows = [summarize("T04 all first-touch, both sides, 4 level types", first)]
        for k in ("D", "W"):
            rows.append(summarize("level=" + k, [e for e in first if e["kind"] == k]))
        for s_ in ("H", "L"):
            rows.append(summarize("side=" + s_, [e for e in first if e["side"] == s_]))
        for y in sorted({e["year"] for e in first}):
            rows.append(summarize("year=%d" % y, [e for e in first if e["year"] == y]))
        for b in range(6):
            rows.append(summarize("4h_block=%d" % b, [e for e in first if e["block4h"] == b]))
        rows.append(summarize("knife=True", [e for e in first if e["knife"]]))
        rows.append(summarize("knife=False", [e for e in first if not e["knife"]]))
        rows.append(summarize("EXPLORATORY repeat-touch arm (first repeat only)", rep))
        censored_n = sum(1 for e in evs if e.get("censored"))
        main_row = rows[0]
        screened = bool(main_row["n"] >= 30 and main_row["mean"] > 0 and main_row["ci_lo"] > 0)
        if mode == "dev":
            # DEV-cut events exist beyond the DEV end only as censored; record the count
            regime = regime_mix(arr)
            summary = {"split": split, "screened_in": screened, "n": main_row["n"],
                       "mean": main_row["mean"], "se": main_row["se"], "ci_lo": main_row["ci_lo"],
                       "mde": main_row["mde"], "censored": censored_n, "regime": regime}
            (OUT / "dev_screen.json").write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
            write_cells(rows, OUT / "cells.csv")
            print(json.dumps(summary, indent=1))
        else:
            main_row["censored"] = censored_n
            verdict_p = main_row["p_one"]
            summary = {"split": split, "n": main_row["n"], "mean": main_row["mean"], "se": main_row["se"],
                       "p_one": verdict_p, "holm_first_step": HOLM_FIRST,
                       "pass": bool(verdict_p <= HOLM_FIRST and main_row["mean"] > 0)}
            (OUT / "val_result.json").write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
            write_cells(rows, OUT / "cells_val.csv")
            print(json.dumps(summary, indent=1))
        return
    raise SystemExit("unknown mode " + mode)


if __name__ == "__main__":
    main(sys.argv)
