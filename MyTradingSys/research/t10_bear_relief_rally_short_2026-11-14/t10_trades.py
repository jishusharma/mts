"""T10 runner. Usage:  python t10_trades.py count    -> counts.json (signal and unit counts only, no outcomes)
                     python t10_trades.py trades   -> trades.csv (one row per trade, no pooled statistic)
Reads F:/MTS/data_cache (read-only). BelowNormal priority and a heavy-job slot are taken first.
"""
import sys
import csv
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t10_core as core  # noqa: E402

ROOT = pathlib.Path(r"F:/MTS/data_cache")
W2 = ROOT / "binance" / "wave2-1114"
CM = ROOT / "binance" / "combo-edge-miner-1114"
PHASE = ROOT / "mts_brains" / "phase_daily.csv"


def universe():
    """Union of the two folders' spot_1d file lists (wave2 file preferred where a coin is in both)."""
    names = {}
    for folder in (CM, W2):                      # wave2 written last so it wins
        for p in (folder / "spot_1d").glob("*USDT.csv"):
            names[p.name[:-8]] = folder
    return dict(sorted(names.items()))


def load_all():
    uni = universe()
    btc = core.load_rows(W2 / "spot_1d" / "BTCUSDT.csv")
    pull_ms = int(btc[-1, 0]) + core.DAY
    gate = core.btc_gate(btc)
    coins, all_runs = {}, []
    for name, folder in uni.items():
        runs = core.make_runs(name, core.load_rows(folder / "spot_1d" / (name + "USDT.csv")), pull_ms)
        fund = core.load_funding(folder / "funding" / (name + "USDT.csv"))
        if fund is None:
            for other in (W2, CM):
                fund = fund or core.load_funding(other / "funding" / (name + "USDT.csv"))
        coins[name] = (runs, fund)
        all_runs.extend(runs)
    alive_n = core.alive_counts(all_runs)
    return dict(uni=uni, gate=gate, coins=coins, alive_n=alive_n, pull_ms=pull_ms, btc=btc)


def load_phase():
    raw = []
    with open(PHASE, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            raw.append((r["date"], r.get("cycle") or "BASE", r.get("label") or "NA"))
    sm = core.smooth_cycle([(d, c) for d, c, _l in raw if d >= "2017-01-01"])
    return {d: (sm.get(d, "NA"), l) for d, _c, l in raw if d >= "2017-01-01"}


def build(D, rally="12"):
    """All screened trades (rows) and a skip log for one rally threshold."""
    rows, skips = [], {}
    for name, (runs, fund) in D["coins"].items():
        for run in runs:
            acc, _ = core.scan_signals(run, D["gate"], D["alive_n"], rally)
            for t in acc:
                row, why = core.make_trade(run, t, fund, rally)
                if row is None:
                    skips[why] = skips.get(why, 0) + 1
                else:
                    rows.append(row)
    rows.sort(key=lambda r: (r["entry_day"], r["coin"]))
    return rows, skips


def count(D, rally):
    """Counts only: no price outcome is read. Uses entry_screen (feasibility), never make_trade."""
    tot = dict(raw=0, alive_excluded=0, cooldown_blocked=0, accepted=0)
    skips, ok_days, ok = {}, [], []
    for name, (runs, fund) in D["coins"].items():
        for run in runs:
            acc, c = core.scan_signals(run, D["gate"], D["alive_n"], rally)
            for k in tot:
                tot[k] += c[k]
            for t in acc:
                why, info = core.entry_screen(run, t)
                if why:
                    skips[why] = skips.get(why, 0) + 1
                else:
                    ok.append((name, int(run.day[t]), int(run.day[t + 1])))
    out = dict(rally=rally, **tot, skipped=skips, feasible=len(ok))
    for sp in ("DEV", "VAL"):
        sel = [x for x in ok if core.split_of_day(x[1]) == sp]
        wk = {core.iso_week_of_day(x[2]) for x in sel}
        ed = [x[2] for x in sel]
        eps = len(set(core.episodes(ed))) if ed else 0
        out[sp] = dict(entries=len(sel), entry_weeks=len(wk), episodes=eps, coins=len({x[0] for x in sel}))
    return out


def gate_days(D):
    g = D["gate"]
    d = {"DEV": 0, "VAL": 0}
    for day, v in g.items():
        if v:
            d[core.split_of_day(day)] += 1
    return d


COLS = ["coin", "signal_date", "entry_date", "exit_date", "entry_px", "exit_px", "stop_px", "target_px", "stop_pct", "tgt_pct",
        "exit_reason", "hold_days", "gross", "fee", "net", "gross_R", "fee_R", "net_R", "fund", "fund_R", "total_R",
        "fund_rule", "split", "iso_week", "rally", "cycle", "label", "episode"]


def write_trades(rows, path, phase):
    eps = core.episodes([r["entry_day"] for r in rows])
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLS)
        for r, ep in zip(rows, eps):
            cyc, lab = phase.get(core.day_str(r["entry_day"]), ("NA", "NA"))
            r.update(cycle=cyc, label=lab, episode=ep, signal_date=core.day_str(r["signal_day"]),
                     entry_date=core.day_str(r["entry_day"]), exit_date=core.day_str(r["exit_day"]))
            out = []
            for k in COLS:
                v = r[k]
                out.append("" if (isinstance(v, float) and v != v) else (repr(round(v, 10)) if isinstance(v, float) else v))
            w.writerow(out)


def main(mode):
    core.lower_priority()
    lk = core.slot_acquire("t10-" + mode)
    try:
        D = load_all()
        if mode == "count":
            out = dict(universe=list(D["uni"]), n_coins=len(D["uni"]), pull_day=core.day_str(D["pull_ms"] // core.DAY),
                       btc_gate_days=gate_days(D), primary=count(D, "12"), rescue_8pct=count(D, "8"),
                       funding_coins=sum(1 for _n, (_r, f) in D["coins"].items() if f is not None),
                       alive_ge30_first_day=core.day_str(min(d for d, n in D["alive_n"].items() if n >= core.MIN_ALIVE)))
            (HERE / "counts.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
            print(json.dumps({k: v for k, v in out.items() if k != "universe"}, indent=1))
        else:
            phase = load_phase()
            rows, skips = build(D, "12")
            rows8, skips8 = build(D, "8")
            write_trades(rows, HERE / "trades.csv", phase)
            write_trades(rows8, HERE / "trades_rescue8.csv", phase)
            (HERE / "trade_skips.json").write_text(json.dumps(dict(primary=skips, rescue8=skips8), indent=1), encoding="utf-8")
            print("trades primary", len(rows), "rescue8", len(rows8), "skips", skips, skips8)
    finally:
        core.slot_release(lk)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "count")
