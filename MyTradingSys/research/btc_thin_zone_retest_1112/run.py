"""DEV run of PREREG.md (T1 thin zone, T2 accepted-breakdown retest). DEV only: months 2022-01 .. 2024-05 are the only files opened.
python run.py [--out RESULT_RAW.json]   writes RESULT_raw.json; RESULT.md is written from it by hand-free text in write_result().
"""
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "backtest"))
import rules  # noqa: E402
import trade_sanity  # noqa: E402

KLINES = "F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv"
FIRST, LAST = "2022-01", "2024-05"
T0 = np.datetime64("2022-01-01T00:00", "ms").astype("int64")
DEV_START_DAY = int((np.datetime64("2022-02-01") - np.datetime64("2022-01-01")).astype(int))
DEV_END_DAY = int((np.datetime64("2024-05-31") - np.datetime64("2022-01-01")).astype(int))
HALF_B_IDX = int((np.datetime64("2023-04-01") - np.datetime64("2022-01-01")).astype(int)) * 1440
DRAWS, SEED = 1000, 1112


def month_files():
    out = []
    for f in sorted(glob.glob(KLINES)):
        tag = os.path.basename(f)[len("BTCUSDT-1m-"):-4][:7]
        if FIRST <= tag <= LAST:
            out.append((tag, f))
    return out


def load():
    rows = []
    for _tag, f in month_files():
        with open(f) as fh:
            for r in csv.reader(fh):
                if r and r[0][:1].isdigit():
                    t = int(r[0])
                    if t > 1e14:
                        t //= 1000
                    rows.append((t, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])))
    a = np.array(rows, dtype=float)
    n = (DEV_END_DAY + 1) * 1440
    a = a[(a[:, 0] >= T0) & (a[:, 0] < T0 + n * 60000)]
    out = np.full((5, n), np.nan)
    idx = ((a[:, 0] - T0) // 60000).astype(int)
    for k in range(5):
        out[k, idx] = a[:, 1 + k]
    return out  # o h l c v


def regime_label(c, day):
    j, j0 = day * 1440 + 1439, (day - 90) * 1440 + 1439
    if j0 < 0 or j >= len(c) or np.isnan(c[j]) or np.isnan(c[j0]):
        return "n/a"
    r = c[j] / c[j0] - 1
    return "bull" if r > .2 else "bear" if r < -.2 else "range"


def stats(net):
    net = np.asarray(net, float)
    n = len(net)
    if n == 0:
        return dict(n=0)
    sd = net.std(ddof=1) if n > 1 else float("nan")
    cum = np.cumsum(net)
    dd = float(np.max(np.maximum.accumulate(np.concatenate([[0.0], cum]))[1:] - cum)) if n else 0.0
    return dict(n=n, win=float((net > 0).mean()), mean=float(net.mean()), median=float(np.median(net)), sd=float(sd),
                t=float(net.mean() / (sd / np.sqrt(n))) if n > 1 and sd > 0 else float("nan"), maxdd_bp=dd, sum=float(net.sum()))


def placebo(o, h, l, c, trades, step, rng):
    """Mean net per draw over 1000 draws: each real trade re-entered at a random same-hour bar with its own geometry."""
    nan = np.isnan(o) | np.isnan(h) | np.isnan(l) | np.isnan(c)
    cs = np.concatenate([[0], np.cumsum(nan)])
    n = len(o)
    tot = np.zeros(DRAWS)
    cnt = 0
    for t in trades:
        hold = t["hold"]
        hour = (t["entry_idx"] % 1440) // 60
        cand = np.arange(DEV_START_DAY * 1440, n - hold, step)
        cand = cand[((cand % 1440) // 60 == hour)]
        cand = cand[(cs[cand + hold] - cs[cand]) == 0]
        e = rng.choice(cand, DRAWS)
        idx = e[:, None] + np.arange(hold)[None, :]
        O, H, L, C = o[idx], h[idx], l[idx], c[idx]
        pe = O[:, 0]
        sp = abs(t["stop"] / t["entry_px"] - 1.0)
        tp = abs(t["target"] / t["entry_px"] - 1.0)
        side = t["side"]
        if side > 0:
            stop, tgt = pe * (1 - sp), pe * (1 + tp)
            sh, th = L <= stop[:, None], H >= tgt[:, None]
            spx = np.minimum(O, stop[:, None])
        else:
            stop, tgt = pe * (1 + sp), pe * (1 - tp)
            sh, th = H >= stop[:, None], L <= tgt[:, None]
            spx = np.maximum(O, stop[:, None])
        s = np.where(sh.any(1), sh.argmax(1), hold + 1)
        tt = np.where(th.any(1), th.argmax(1), hold + 1)
        rows = np.arange(DRAWS)
        px = np.where((s <= tt) & (s <= hold), spx[rows, np.minimum(s, hold - 1)],
                      np.where(tt <= hold, tgt, C[:, -1]))
        tot += side * (px / pe - 1.0) * 1e4 - rules.FEE_BP
        cnt += 1
    return tot / max(cnt, 1)


def to_sanity(trades):
    out = []
    for t in trades:
        out.append(dict(side=t["side"], entry_ms=int(T0 + t["entry_idx"] * 60000), exit_ms=int(T0 + t["exit_idx"] * 60000),
                        entry_px=t["entry_px"], exit_px=t["exit_px"], ret=t["net_bp"], reason=t["reason"]))
    return out


def sanity_block(trades, n=5):
    """log_sanity (PREREG: before any metric). Entry vs bar open always. Exit: time = bar close; stop/target = px inside the exit bar
    high/low (stop/target fills are not an open or close, so the helper's open/close test is replaced for them, OURS)."""
    sub = sorted(to_sanity(trades), key=lambda x: x["entry_ms"])[-n:]
    need = set()
    for t in sub:
        for ms in (t["entry_ms"], t["exit_ms"]):
            need.add(np.datetime_as_string(np.datetime64(int(ms), "ms"), unit="D")[:7])
    files = [f for tag, f in month_files() if tag in need]
    kl = trade_sanity.load_klines(files)
    rows = []
    for t in sub:
        leg = "close" if t["reason"] == "time" else "open"
        r = trade_sanity.check_trades([t], kl, 1, exit_leg=leg)[0]
        if t["reason"] in ("stop", "target"):
            bar = kl.get(int(t["exit_ms"]))
            r["exit_ok"] = bar is not None and bar[2] - 1e-9 <= t["exit_px"] <= bar[1] + 1e-9
        rows.append(r)
    text = "\n".join(trade_sanity.sanity_lines(rows))
    print(text)
    if not all(r["entry_ok"] and r["exit_ok"] for r in rows):
        raise trade_sanity.LogSanityError(text)
    return text


def analyse(name, o, h, l, c, trades, drop, step, rng):
    san = sanity_block(trades) if trades else "no trades"
    net = np.array([t["net_bp"] for t in trades])
    gross = np.array([t["gross_bp"] for t in trades])
    st = stats(net)
    st["gross_mean"] = float(gross.mean()) if len(gross) else float("nan")
    ha = [t["net_bp"] for t in trades if t["entry_idx"] < HALF_B_IDX]
    hb = [t["net_bp"] for t in trades if t["entry_idx"] >= HALF_B_IDX]
    halves = dict(A=stats(ha), B=stats(hb))
    ys = "\n".join(trade_sanity.year_side_lines(to_sanity(trades))) if trades else ""
    reg = {}
    for t in trades:
        k = regime_label(c, t["entry_idx"] // 1440)
        reg[k] = reg.get(k, 0) + 1
    exits = {}
    for t in trades:
        exits[t["reason"]] = exits.get(t["reason"], 0) + 1
    pb = None
    if trades:
        pm = placebo(o, h, l, c, trades, step, rng)
        pb = dict(mean=float(pm.mean()), p1=float(np.percentile(pm, 1)), p99=float(np.percentile(pm, 99)))
    ok = (st["n"] >= 30 and st["mean"] > 0 and st["t"] >= 2 and halves["A"].get("mean", -1) > 0 and halves["B"].get("mean", -1) > 0) \
        if trades else False
    verdict = "INCONCLUSIVE" if st["n"] < 30 else "PASS" if ok else "FAIL"
    return dict(name=name, stats=st, halves=halves, year_side=ys, regime=reg, exits=exits, drop=drop, placebo=pb,
                verdict=verdict, sanity=san,
                trade_rows=[dict(e=int(t["entry_idx"]), x=int(t["exit_idx"]), s=t["side"], net=t["net_bp"], why=t["reason"])
                            for t in trades])


def main():
    o, h, l, c, v = load()
    n = len(o)
    print("grid minutes", n, "missing 1m bars", int(np.isnan(o).sum()))
    rng = np.random.default_rng(SEED)
    t1, d1 = rules.run_t1(o, h, l, c, v, DEV_START_DAY, DEV_END_DAY)
    t2, d2 = rules.run_t2(o, h, l, c, v, DEV_START_DAY * 24, n // 60 - 1)
    res = dict(T1=analyse("T1 thin-zone pass-through", o, h, l, c, t1, d1, 5, rng),
               T2=analyse("T2 accepted-breakdown retest", o, h, l, c, t2, d2, 60, rng),
               missing_bars=int(np.isnan(o).sum()))
    with open(os.path.join(HERE, "result_raw.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for k in ("T1", "T2"):
        r = res[k]
        print(k, r["verdict"], {a: (round(b, 3) if isinstance(b, float) else b) for a, b in r["stats"].items()})
        print("  halves", {a: (b.get("n"), round(b.get("mean", float("nan")), 2)) for a, b in r["halves"].items()},
              "placebo", r["placebo"], "drop", r["drop"], "exits", r["exits"], "regime", r["regime"])
        print(r["year_side"])


if __name__ == "__main__":
    main()
