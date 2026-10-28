"""context-composite-dev-read: ONE outcome read of the frozen PRE_REG.md (operator context composite C, DEV only).

  python study.py counts   -> frames -> ledger -> C; prints n events / days per side and pooled, NO outcome (PRE_REG s.2 check)
  python study.py run      -> counts check (abort on mismatch), then trades, controls, READ cell, report-only rows, files

This file implements PRE_REG.md as written; it chooses nothing. Where the text left a detail open the choice is marked
`DECISION (OURS)` in a comment and again in RESULT.md. No bar with open >= 2024-07-01 is read (see `load_1m`).
The pure trade simulator (`simulate`, `settle`) has no I/O and is tested by test_study.py on a hand fixture.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest"))

MIN = 60_000
HOUR = 3_600_000
DAY = 86_400_000
WEEK = 7 * DAY
DEV_START_MS = 1_640_995_200_000       # 2022-01-01 00:00 UTC
DEV_END_MS = 1_719_792_000_000         # 2024-07-01 00:00 UTC: first VALIDATION bar, never read
HOLD_BARS = 1440                       # 24 h time stop = the 1m bar ending entry + 24 h is the 1440th bar from the entry bar
FEE_SLIP = 0.0007                      # 5 bp taker + 2 bp slippage per side (PRE_REG s.1, SOURCED)
FEE_SLIP_MAKER_IN = 0.0002             # maker-in readout: 2 bp on entry (PRE_REG s.1 report-only)
R_TARGET = 2.0                         # OURS (PRE_REG s.2)
HOLM_M = 37                            # PRE_REG s.4
T_CRIT = 3.205                         # z_holm, PRE_REG s.4
N_NEEDED_DAYS = 387                    # PRE_REG s.4
EXPECT = {"long": (554, 254), "short": (456, 202), "pooled": (1010, 456)}   # PRE_REG s.2 counted events / days
YEARS = (("2022", 1_648_771_200_000, 1_672_531_200_000), ("2023", 1_672_531_200_000, 1_704_067_200_000),
         ("2024H1", 1_704_067_200_000, DEV_END_MS))
KLINE_DIR = Path("F:/MTS/data/tom_raw/klines")
FUND_CSV_DIR = Path("F:/MTS/Dumps/backtest/raw/fundingRate")
CACHE_1M = Path("C:/Users/E-NGIN~1/AppData/Local/Temp/claude/context_factors_cache") / "btcusdt_1m_dev.npz"


# ======================================================================================= pure trade simulator (tested)
def settle(side, entry, stop, exit_px, fund_sum):
    """net_R of one trade per PRE_REG s.1: (sgn*(exit-entry) - 0.0007*entry - 0.0007*exit - funding*entry) / R.
    fund_sum = sum of the realised 8h rates of the settlements inside the trade (raw sign, as in the archive); a long pays a
    positive rate, a short receives it, so the cost term is sgn * fund_sum. Returns (net_R, R)."""
    sgn = 1 if side == "long" else -1
    r = abs(entry - stop)
    gross = sgn * (exit_px - entry)
    cost = FEE_SLIP * entry + FEE_SLIP * exit_px
    fund = sgn * fund_sum * entry
    return (gross - cost - fund) / r, r


def simulate(side, stop, bars_o, bars_h, bars_l, bars_c):
    """One trade on the 1m bars from the entry bar on (arrays start AT the entry bar; entry = bars_o[0]).

    Stop = `stop` (fixed at T), target = entry +- 2 R, time stop = close of bars index HOLD_BARS - 1 (the 1m bar ending
    entry + 24 h). Per bar in order: stop first when one bar holds both; a bar that opens beyond the stop fills at its open
    (fill = min(open, stop) long, max short); else target (fill at the target price); else the time stop at the last close.
    Returns None when the entry is already at/beyond the stop (R <= 0 on the wrong side: skipped, `entry_beyond_stop`),
    else dict(kind in stop|target|time, exit, idx (exit bar index), entry, R, cut (window shorter than 24 h))."""
    o, h, l, c = (np.asarray(x, float)[:HOLD_BARS] for x in (bars_o, bars_h, bars_l, bars_c))
    entry = float(o[0])
    if side == "long":
        if entry <= stop:
            return None
        r = entry - stop
        target = entry + R_TARGET * r
        hit_s, hit_t = l <= stop, h >= target
    else:
        if entry >= stop:
            return None
        r = stop - entry
        target = entry - R_TARGET * r
        hit_s, hit_t = h >= stop, l <= target
    any_hit = hit_s | hit_t
    cut = len(o) < HOLD_BARS
    if any_hit.any():
        k = int(np.argmax(any_hit))
        if hit_s[k]:                                            # stop first when the bar holds both
            px = min(float(o[k]), stop) if side == "long" else max(float(o[k]), stop)   # gap through the stop fills at the open
            return dict(kind="stop", exit=px, idx=k, entry=entry, R=r, cut=False)
        return dict(kind="target", exit=target, idx=k, entry=entry, R=r, cut=False)
    k = len(c) - 1
    return dict(kind="time", exit=float(c[k]), idx=k, entry=entry, R=r, cut=cut)


def entry_index(ot, T):
    """Index of the 1m bar that opens at T + 60 s (one-bar latency, template s.3.2); -1 if that bar is not in the archive
    (never the bar at T, never the next available bar)."""
    i = int(np.searchsorted(ot, T + MIN, "left"))
    return i if i < len(ot) and int(ot[i]) == T + MIN else -1


def funding_sum(ft, fr, t_in, t_out_end):
    """Sum of the realised funding rates with entry bar open <= settlement time < end of the exit bar (the trade holds the
    position at that settlement). DECISION (OURS): the exit instant inside the exit bar is unknown, so the whole exit bar
    counts as held."""
    a = np.searchsorted(ft, t_in, "left")
    b = np.searchsorted(ft, t_out_end, "left")
    return float(np.sum(fr[a:b]))


# ======================================================================================= data
def load_funding_csv():
    """(calc_time ms, last_funding_rate) of the monthly Binance fundingRate archive 2022-01..2024-06, settlement < 2024-07-01.
    DECISION (OURS): F:/MTS/data/candle_close_dev_2022_2024 (the PRE_REG path) is absent on this machine; the same Binance
    monthly series sits as CSV in F:/MTS/Dumps/backtest/raw/fundingRate (identical columns); build_frames.py uses it too."""
    rows = []
    for y in (2022, 2023, 2024):
        for m in range(1, 13):
            if y == 2024 and m > 6:
                break
            rows.append(pd.read_csv(FUND_CSV_DIR / f"BTCUSDT-fundingRate-{y}-{m:02d}.csv"))
    f = pd.concat(rows, ignore_index=True).sort_values("calc_time")
    f = f[f["calc_time"] < DEV_END_MS]
    return f["calc_time"].to_numpy(np.int64), f["last_funding_rate"].to_numpy(float)


def load_1m():
    """1m bars (dict of arrays ot,o,h,l,c) with open time in [2022-01-01, 2024-07-01). A bar at/after the split is refused."""
    if CACHE_1M.exists():
        z = np.load(CACHE_1M)
        b = {k: z[k] for k in z.files}
    else:
        parts = []
        for y in (2022, 2023, 2024):
            for m in range(1, 13):
                if y == 2024 and m > 6:
                    break
                f = KLINE_DIR / f"BTCUSDT-1m-{y}-{m:02d}.csv"
                first = f.open().readline()
                df = pd.read_csv(f, header=0 if first.startswith("open_time") else None, usecols=range(5))
                df.columns = ["ot", "o", "h", "l", "c"]
                parts.append(df)
        d = pd.concat(parts, ignore_index=True).drop_duplicates("ot").sort_values("ot")
        d = d[(d["ot"] >= DEV_START_MS) & (d["ot"] < DEV_END_MS)]
        b = {"ot": d["ot"].to_numpy(np.int64), **{k: d[k].to_numpy(float) for k in "ohlc"}}
        CACHE_1M.parent.mkdir(parents=True, exist_ok=True)
        np.savez(CACHE_1M, **b)
    if len(b["ot"]) and int(b["ot"].max()) >= DEV_END_MS:
        raise ValueError("VALIDATION bar in the DEV 1m load")
    return b


# ======================================================================================= ledger and the composite C
def frames():
    import context_asof as C
    return {s: pd.read_pickle(C.CACHE / f"frame_{s}.pkl") for s in ("long", "short")}


def tradeable_ledger(f):
    import counts
    e = counts.ledger(f)
    return e[e["f3_stop_tf"] != "none"].copy()


PHASE_OK = {"long": ("markup", "accumulation"), "short": ("markdown", "distribution")}   # PRE_REG s.2 (direction map OURS)


def form_c(led, side):
    """PRE_REG s.2 verbatim: ledger event AND f2_conf_obj >= 2 AND f3_armed AND NOT f5_veto AND f6_phaseA in the side's pair."""
    m = (led["f2_conf_obj"] >= 2) & led["f3_armed"].astype(bool) & ~led["f5_veto"].astype(bool) & led["f6_phaseA"].isin(PHASE_OK[side])
    return led[m].copy()


def counts_report(led, cset):
    out = {}
    for s in ("long", "short"):
        out[s] = (len(cset[s]), int(cset[s]["T"].floordiv(DAY).nunique()))
    allT = pd.concat([cset["long"]["T"], cset["short"]["T"]])
    out["pooled"] = (len(allT), int(allT.floordiv(DAY).nunique()))
    return out


def counts_main():
    fr = frames()
    led = {s: tradeable_ledger(fr[s]) for s in fr}
    cset = {s: form_c(led[s], s) for s in led}
    rep = counts_report(led, cset)
    print(f"tradeable ledger: long {len(led['long'])} events / {led['long']['T'].floordiv(DAY).nunique()} days, "
          f"short {len(led['short'])} / {led['short']['T'].floordiv(DAY).nunique()}")
    for k in ("long", "short", "pooled"):
        print(f"C {k}: {rep[k][0]} events / {rep[k][1]} days   (PRE_REG {EXPECT[k][0]} / {EXPECT[k][1]})")
    ok = all(rep[k] == EXPECT[k] for k in EXPECT)
    print("COUNTS MATCH PRE_REG" if ok else "COUNTS MISMATCH: BLOCKED")
    return ok, fr, led, cset


# ======================================================================================= the run
def load_context_null():
    import importlib.util
    p = REPO / "MyTradingSys" / "research" / "context_null_2026-10-16" / "context_null.py"
    spec = importlib.util.spec_from_file_location("context_null_ro", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hourly_closes(b):
    """1h close array on the regular grid from 2022-01-01 00:00 (bar 0 opens at DEV_START_MS); a missing hour is forward
    filled and counted (expected 0)."""
    hr = b["ot"] // HOUR
    last = pd.Series(b["c"]).groupby(hr).last()
    grid = np.arange(DEV_START_MS // HOUR, DEV_END_MS // HOUR)
    s = last.reindex(grid)
    return s.ffill().to_numpy(float), int(s.isna().sum())


def max_dd(x):
    """Max peak-to-trough drop of the cumulative sum of x (in R, start at 0), reported >= 0."""
    cs = np.concatenate(([0.0], np.cumsum(np.asarray(x, float))))
    return float((np.maximum.accumulate(cs) - cs).max())


def add_stop(led, side):
    """Ladder stop price at T: f3_stop_pct is (close - low)/close*100 (long) or (high - close)/close*100 (short) of the last
    completed D / 12h / 8h candle, so stop = close*(1 -+ pct/100). DECISION (OURS): rounded to the 0.01 price grid of the
    archive (the candle low/high is an archive price); the rounding moved no stop by more than 1e-6."""
    c = led["close"].to_numpy(float)
    w = led["f3_stop_pct"].to_numpy(float)
    raw = c * (1 - w / 100) if side == "long" else c * (1 + w / 100)
    stop = np.round(raw, 2)
    assert np.abs(raw - stop).max() < 1e-6, "stop price is off the 0.01 grid"
    out = led[["T", "close", "f3_stop_tf", "f3_stop_pct"]].copy().reset_index(drop=True)
    out["side"] = side
    out["stop"] = stop
    return out


def run_trades(ev, b, ft, fr, rng_syn=None):
    """One row per ledger event: status ok | entry_beyond_stop | no_entry_bar, then the trade. rng_syn is the smoke-test
    switch: the real simulator still runs (so a crash shows up) but the P&L columns are replaced by random numbers."""
    ot, O, H, L, Cl = b["ot"], b["o"], b["h"], b["l"], b["c"]
    rows = []
    for T, side, stop in zip(ev["T"].to_numpy(np.int64), ev["side"], ev["stop"].to_numpy(float)):
        i = entry_index(ot, int(T))
        if i < 0:
            rows.append(dict(status="no_entry_bar"))
            continue
        ent_ot = int(ot[i])
        j = int(np.searchsorted(ot, ent_ot + HOLD_BARS * MIN, "left"))
        tr = simulate(side, float(stop), O[i:j], H[i:j], L[i:j], Cl[i:j])
        if tr is None:
            rows.append(dict(status="entry_beyond_stop", entry=float(O[i])))
            continue
        exit_bar_ot = int(ot[i + tr["idx"]])
        fs = funding_sum(ft, fr, ent_ot, exit_bar_ot + MIN)
        net, r = settle(side, tr["entry"], float(stop), tr["exit"], fs)
        net_m = net + (FEE_SLIP - FEE_SLIP_MAKER_IN) * tr["entry"] / r          # maker-in readout: 2 bp instead of 7 bp on entry
        sgn = 1 if side == "long" else -1
        row = dict(status="ok", entry=tr["entry"], exit=tr["exit"], kind=tr["kind"], net_R=net, net_R_maker=net_m, R=r,
                   gross_pct=sgn * (tr["exit"] - tr["entry"]) / tr["entry"] * 100, fund_sum=fs, ent_ot=ent_ot,
                   exit_bar_ot=exit_bar_ot, cut_split=bool(ent_ot + HOLD_BARS * MIN > DEV_END_MS),
                   gap_short=bool(tr["cut"] and ent_ot + HOLD_BARS * MIN <= DEV_END_MS))
        if rng_syn is not None:
            row.update(kind=str(rng_syn.choice(["stop", "target", "time"])), net_R=float(rng_syn.normal(0, 1.2)))
            row["net_R_maker"] = row["net_R"] + 0.03
            row["gross_pct"] = row["net_R"]
            row["exit"] = row["entry"]
        rows.append(row)
    return pd.DataFrame(rows, index=ev.index)


def year_of(T):
    for name, a, b_ in YEARS:
        if a <= T < b_:
            return name
    return "pre"


def draw_controls(cn, cfg, ev, keys, rv_unused=None):
    """Context-matched controls for the C events of one side (PRE_REG s.3): same context_key (hour, vol, trend), K = 20
    without replacement from the pool, seed 0, controls spaced > cooldown apart, fewer than kmin -> unmatched.
    ev: this side's ledger frame with columns T, inC, pool (bool), status. keys: tuple or None per row."""
    pool_idx = np.flatnonzero(ev["pool"].to_numpy())
    by_key = {}
    for q in pool_idx:
        by_key.setdefault(keys[q], []).append(int(q))
    Tn = ev["T"].to_numpy(np.int64)
    rng = np.random.default_rng(cfg.seed)
    out, unmatched, ncand = {}, dict(no_context=0, too_few_controls=0), {}
    for q in np.flatnonzero(ev["inC"].to_numpy() & (ev["status"].to_numpy() == "ok")):
        key = keys[q]
        if key is None:
            unmatched["no_context"] += 1
            continue
        cand = np.array(by_key.get(key, []), int)
        ncand[int(q)] = len(cand)
        rng.shuffle(cand)
        chosen = []
        for j in cand:
            if len(chosen) >= cfg.K:
                break
            if any(abs(int(Tn[j]) - int(Tn[c])) <= cfg.cooldown * HOUR for c in chosen):
                continue
            chosen.append(int(j))
        if len(chosen) < cfg.kmin:
            unmatched["too_few_controls"] += 1
            continue
        out[int(q)] = chosen
    return out, unmatched, ncand


def fmt(x, n=4):
    return "nan" if x != x else f"{x:+.{n}f}"


def run(out_dir, synthetic=False):
    import csv
    import datetime as dt
    import hashlib

    import research_kit as RK

    ok, fr_, led, cset = counts_main()
    if not ok:
        (out_dir / "BLOCKED.md").write_text("BLOCKED: C counts do not match PRE_REG s.2. See study.py counts output.\n",
                                            encoding="utf-8", newline="\n")
        raise SystemExit(2)
    b = load_1m()
    ft, fund_r = load_funding_csv()
    cn = load_context_null()
    cfg = cn.Config(bar_min=60, cooldown=4, seed=0)
    assert (cfg.K, cfg.kmin, cfg.ts0_ms) == (20, 10, DEV_START_MS), (cfg.K, cfg.kmin, cfg.ts0_ms)
    Cc, n_missing_hours = hourly_closes(b)
    rv = cn.rolling_rv(Cc, cfg.vol_win_min // cfg.bar_min)
    rng_syn = np.random.default_rng(12345) if synthetic else None
    print(f"1m bars {len(b['ot'])}, first {b['ot'][0]}, last {b['ot'][-1]} (< {DEV_END_MS}); funding settlements {len(ft)}; "
          f"missing hours filled {n_missing_hours}")

    sides = ("long", "short")
    ev, drawn, unmatched, pool_info, ncands = {}, {}, {}, {}, {}
    for s in sides:
        e = add_stop(led[s], s)
        e["inC"] = e["T"].isin(cset[s]["T"]).to_numpy()
        tr = run_trades(e, b, ft, fund_r, rng_syn)
        e = pd.concat([e, tr], axis=1)
        t_idx = ((e["T"].to_numpy(np.int64) - HOUR - DEV_START_MS) // HOUR)
        keys = [cn.context_key(Cc, int(t), cfg, rv=rv) for t in t_idx]
        Tc = e.loc[e["inC"], "T"].to_numpy(np.int64)
        near = (np.abs(e["T"].to_numpy(np.int64)[:, None] - Tc[None, :]) <= DAY).any(axis=1)
        e["pool"] = (~e["inC"].to_numpy()) & (~near) & (e["status"].to_numpy() == "ok") & np.array([k is not None for k in keys])
        pool_info[s] = dict(ledger=len(e), in_c=int(e["inC"].sum()), near_c=int((near & ~e["inC"].to_numpy()).sum()),
                            pool=int(e["pool"].sum()), status=e.loc[~e["inC"].to_numpy(), "status"].value_counts().to_dict())
        drawn[s], unmatched[s], ncands[s] = draw_controls(cn, cfg, e, keys)
        e["key"] = [None if k is None else "-".join(map(str, k)) for k in keys]
        ev[s] = e
    for s in sides:
        print(f"{s}: ledger {pool_info[s]['ledger']}, C {pool_info[s]['in_c']}, within 24h of C (excluded) {pool_info[s]['near_c']}, "
              f"pool {pool_info[s]['pool']}, non-C status {pool_info[s]['status']}")

    # ------------------------------------------------------------- assemble matched events and tables
    mrows, crows, lrows = [], [], []
    skipped = dict(entry_beyond_stop=0, no_entry_bar=0, no_context=0, too_few_controls=0, cut_at_split_end=0, short_window_not_at_split=0)
    exit_mix_c, exit_mix_ctrl = {"stop": 0, "target": 0, "time": 0}, {"stop": 0, "target": 0, "time": 0}
    for s in sides:
        e = ev[s]
        for k in ("no_context", "too_few_controls"):
            skipped[k] += unmatched[s][k]
        for q in np.flatnonzero(e["inC"].to_numpy()):
            r = e.iloc[q]
            base = dict(T=int(r["T"]), T_utc=dt.datetime.fromtimestamp(int(r["T"]) / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
                        side=s, stop_tf=r["f3_stop_tf"], stop=r["stop"], status=r["status"])
            if r["status"] != "ok":
                skipped[r["status"]] += 1
                lrows.append(dict(base, entry=r.get("entry", np.nan), exit=np.nan, exit_kind="", net_R=np.nan, n_controls=0,
                                  ctrl_mean_net_R=np.nan, control_Ts=""))
                continue
            exit_mix_c[r["kind"]] += 1
            skipped["cut_at_split_end"] += int(r["cut_split"])
            skipped["short_window_not_at_split"] += int(r["gap_short"])
            ch = drawn[s].get(int(q))
            if ch is None:
                lrows.append(dict(base, entry=r["entry"], exit=r["exit"], exit_kind=r["kind"], net_R=r["net_R"], n_controls=0,
                                  ctrl_mean_net_R=np.nan, control_Ts="", net_R_maker=r["net_R_maker"], gross_pct=r["gross_pct"]))
                continue
            ce = e.iloc[ch]
            for _, c_ in ce.iterrows():
                exit_mix_ctrl[c_["kind"]] += 1
                crows.append(dict(C_T=int(r["T"]), side=s, ctrl_T=int(c_["T"]), ctrl_stop_tf=c_["f3_stop_tf"], ctrl_stop=c_["stop"],
                                  ctrl_entry=c_["entry"], ctrl_exit=c_["exit"], ctrl_exit_kind=c_["kind"], ctrl_net_R=c_["net_R"]))
            m, mm = float(ce["net_R"].mean()), float(ce["net_R_maker"].mean())
            lrows.append(dict(base, entry=r["entry"], exit=r["exit"], exit_kind=r["kind"], net_R=r["net_R"], n_controls=len(ch),
                              ctrl_mean_net_R=m, control_Ts=";".join(str(int(x)) for x in ce["T"]),
                              net_R_maker=r["net_R_maker"], gross_pct=r["gross_pct"]))
            mrows.append(dict(side=s, T=int(r["T"]), day=int(r["T"] // DAY), week=int((r["T"] - 4 * DAY) // WEEK), year=year_of(int(r["T"])),
                              e=float(r["net_R"]), m=m, e_mk=float(r["net_R_maker"]), m_mk=mm, gross_pct=float(r["gross_pct"]),
                              R=float(r["R"]), n_ctrl=len(ch)))
    M = pd.DataFrame(mrows).sort_values(["T", "side"], kind="stable").reset_index(drop=True)
    Lc = pd.DataFrame(lrows).sort_values(["T", "side"], kind="stable").reset_index(drop=True)
    allC = Lc[Lc["status"] == "ok"]
    M["x"] = M["e"] - M["m"]
    M["x_mk"] = M["e_mk"] - M["m_mk"]

    # ------------------------------------------------------------- READ cell: C pooled
    E, se = RK.cluster_mean_se(M["x"], M["day"])
    t = RK.t_stat(E, se)
    p2 = RK.norm_p_two(t)
    p_holm = float(RK.holm([p2], HOLM_M)[0]) if p2 == p2 else float("nan")
    matched_days = int(M["day"].nunique())
    mean_all, se_all = RK.cluster_mean_se(allC["net_R"].to_numpy(float), (allC["T"] // DAY).to_numpy())
    mean_matched, se_matched = RK.cluster_mean_se(M["e"], M["day"])
    e_year = {y: float(M.loc[M["year"] == y, "x"].mean()) if (M["year"] == y).any() else float("nan") for y, _, _ in YEARS}
    n_year = {y: int((M["year"] == y).sum()) for y, _, _ in YEARS}
    dd_c_matched, dd_ctrl = max_dd(M["e"]), max_dd(M["m"])
    dd_c_all = max_dd(allC["net_R"])
    mde = RK.mde(se)
    conds = {
        "matched days >= 387": matched_days >= N_NEEDED_DAYS,
        "E > 0": E > 0,
        "|t| >= 3.205 (Holm m=37, p <= 0.05)": bool(abs(t) >= T_CRIT),
        "mean net_R of C > 0 (all executed C trades AND matched C trades)": bool(mean_all > 0 and mean_matched > 0),
        "E > 0 in 2022, 2023 and 2024H1": all(v > 0 for v in e_year.values()),
        "MDD(C) <= MDD(matched controls' mean path) (matched events AND all executed C trades)": bool(dd_c_matched <= dd_ctrl and dd_c_all <= dd_ctrl),
    }
    if matched_days < N_NEEDED_DAYS:
        verdict = "INCONCLUSIVE"
    elif all(conds.values()):
        verdict = "PASS"
    else:
        verdict = "FAIL"
    se_wk = RK.cluster_mean_se(M["x"], M["week"])[1]
    t_wk = RK.t_stat(E, se_wk)
    verdict_line = verdict
    if verdict == "PASS" and not (abs(t_wk) >= 2):
        verdict_line = "PASS (day-clustered only)"

    # ------------------------------------------------------------- report-only rows (no verdict)
    side_rows = []
    for s in sides:
        Ms = M[M["side"] == s]
        es, ss = RK.cluster_mean_se(Ms["x"], Ms["day"])
        side_rows.append((s, len(Ms), int(Ms["day"].nunique()), es, ss, RK.t_stat(es, ss)))
    E_mk, se_mk = RK.cluster_mean_se(M["x_mk"], M["day"])
    mean_c_mk = float(allC["net_R_maker"].mean())
    allled = pd.concat([ev[s].loc[ev[s]["status"] == "ok", ["T", "net_R"]] for s in sides])
    ctx_diff, ctx_se = RK.cluster_diff(M["m"].to_numpy(), M["day"].to_numpy(), allled["net_R"].to_numpy(), (allled["T"] // DAY).to_numpy())
    reuse = len(crows) / max(len({(c_["ctrl_T"], c_["side"]) for c_ in crows}), 1)

    # ------------------------------------------------------------- files
    ledger_cols = ["T", "T_utc", "side", "stop_tf", "stop", "entry", "exit", "exit_kind", "net_R", "status", "n_controls", "ctrl_mean_net_R", "control_Ts"]
    Lc[ledger_cols].to_csv(out_dir / "ledger_C.csv", index=False, float_format="%.10g", lineterminator="\n")
    pd.DataFrame(crows).to_csv(out_dir / "controls.csv", index=False, float_format="%.10g", lineterminator="\n")
    pre = HERE / "PRE_REG.md"
    rule_sha = hashlib.sha256(pre.read_bytes()).hexdigest()
    asof_sha = hashlib.sha256((HERE / "context_asof.py").read_bytes()).hexdigest()
    run_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    with open(out_dir / "EXPOSURE_LEDGER.csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["study", "run_utc", "data_source", "window_read", "split", "rule_sha256", "verdict", "decision_informed"])
        w.writerow(["context_factors_2026-10-16 (context-composite-dev-read; PRE_REG frozen at 3e961c2f)", run_utc,
                    "F:/MTS/data/tom_raw/klines 1m BTCUSDT + F:/MTS/Dumps/backtest/raw/fundingRate (Binance monthly funding, same series as the PRE_REG archive path)",
                    "DEV 2022-04-01..2024-06-30 decisions; 1m bars 2022-01-01..2024-06-30 23:59", "DEV", rule_sha, verdict_line,
                    "whether the operator context composite C beats context-matched controls on the daily-candle stop-ladder trade (DEV, one run)"])

    # ------------------------------------------------------------- RESULT.md
    L = [verdict_line, "",
         "# RESULT: operator context composite C vs context-matched controls, BTCUSDT 1h decisions, daily-candle stop-ladder trade, DEV only, one run",
         "" if not synthetic else "SYNTHETIC SMOKE RUN (random P&L, plumbing check only; not a result)", "",
         f"Verdict above is per PRE_REG.md s.4, applied verbatim. Run {run_utc}. PRE_REG.md sha256 `{rule_sha}` (frozen at commit 3e961c2f, "
         f"unchanged); context_asof.py sha256 `{asof_sha}` (same commit). Trade: entry at the open of the 1m bar opening at T + 60 s, ladder stop "
         "(prior D / 12h / 8h extreme), 2 R target, 24 h time stop, 7 bp per side, realised funding. net_R in R.", "",
         "## READ cell: C pooled (long + short; the short trade's P&L is already sign-flipped in net_R)", "",
         "| item | value |", "|---|---|",
         f"| C events (counted, PRE_REG s.2) | {EXPECT['pooled'][0]} events / {EXPECT['pooled'][1]} days (long {EXPECT['long'][0]}/{EXPECT['long'][1]}, short {EXPECT['short'][0]}/{EXPECT['short'][1]}): MATCH |",
         f"| executed C trades | {len(allC)} |",
         f"| matched C events (>= {cfg.kmin} controls) | {len(M)} on {matched_days} UTC days (need >= {N_NEEDED_DAYS}) |",
         f"| trigger effect E (mean of event net_R minus mean of its controls' net_R) | {fmt(E)} R |",
         f"| day-clustered SE of E | {se:.4f} R |", f"| t = E / SE | {fmt(t, 2)} |",
         f"| two-sided p / Holm-adjusted p (m = {HOLM_M}) | {p2:.4g} / {p_holm:.4g} |",
         f"| MDE of this cell (2.8 x SE) | {mde:.4f} R |",
         f"| mean net_R of C, all executed trades (SE day-clustered) | {fmt(mean_all)} ({se_all:.4f}) over {len(allC)} |",
         f"| mean net_R of C, matched events only | {fmt(mean_matched)} ({se_matched:.4f}) over {len(M)} |",
         f"| E by year (matched events): 2022 Apr-Dec / 2023 / 2024H1 | {fmt(e_year['2022'])} (n {n_year['2022']}) / {fmt(e_year['2023'])} (n {n_year['2023']}) / {fmt(e_year['2024H1'])} (n {n_year['2024H1']}) |",
         f"| max drawdown of cumulative net_R: C matched / C all executed / controls' mean path (matched) | {dd_c_matched:.2f} R / {dd_c_all:.2f} R / {dd_ctrl:.2f} R |", "",
         "Gate by gate:", ""]
    for k, v in conds.items():
        L.append(f"- {'yes' if v else 'NO '}: {k}")
    L += ["", f"Week-clustered SE of E {se_wk:.4f} R, t_week {fmt(t_wk, 2)} (day-clustered t {fmt(t, 2)}). "
          + ("PASS with |t_week| < 2 is labelled PASS (day-clustered only)." if verdict == "PASS" else ""), "",
          "## Report-only rows (printed beside the READ cell, no verdict, never a gate)", "",
          "| row | n matched events | days | E (R) | SE | t |", "|---|---|---|---|---|---|"]
    for s, n_, d_, es, ss, ts in side_rows:
        L.append(f"| E, {s} only | {n_} | {d_} | {fmt(es)} | {ss:.4f} | {fmt(ts, 2)} |")
    L += ["", f"- Maker-in readout (0.09 % round trip: 2 bp on entry instead of 7 bp): mean net_R of C (all executed) {fmt(mean_c_mk)} R; E {fmt(E_mk)} R (SE {se_mk:.4f}). Never rescues a FAIL.",
          f"- Context-only line (matched controls' mean net_R minus the mean net_R of the whole tradeable ledger, both sides, {len(allled)} trades): {fmt(ctx_diff)} R (SE {ctx_se:.4f}).",
          f"- Controls: {len(crows)} draws, each distinct control used {reuse:.1f}x on average (heavy reuse understates the SE when above 5).",
          f"- Skipped / flagged: entry_beyond_stop {skipped['entry_beyond_stop']}, no_entry_bar {skipped['no_entry_bar']}, no_context {skipped['no_context']}, "
          f"too_few_controls (< {cfg.kmin}) {skipped['too_few_controls']}, cut_at_split_end {skipped['cut_at_split_end']} (24 h window runs past 2024-06-30 23:59; exit at the last DEV 1m close), "
          f"short window not at split end (data gap) {skipped['short_window_not_at_split']}.",
          f"- Exit mix, C executed trades: stop {exit_mix_c['stop']}, target {exit_mix_c['target']}, time {exit_mix_c['time']}. Controls (all draws): stop {exit_mix_ctrl['stop']}, target {exit_mix_ctrl['target']}, time {exit_mix_ctrl['time']}.",
          "- Matching diagnostics (counts only, independent of any outcome): " + "; ".join(
              f"{s}: C events with a defined key {len(ncands[s])}, with >= {cfg.kmin} pool candidates in their key cell (before spacing) "
              f"{sum(1 for v in ncands[s].values() if v >= cfg.kmin)}, median candidates {np.median(list(ncands[s].values())):.0f}, "
              f"key cells with a C event {len({k for q, k in enumerate(ev[s]['key']) if ev[s]['inC'].iloc[q] and k is not None})}" for s in sides) + ".",
          f"- Pools: " + "; ".join(f"{s}: ledger {pool_info[s]['ledger']}, C {pool_info[s]['in_c']}, excluded within 24 h of C {pool_info[s]['near_c']}, pool {pool_info[s]['pool']}" for s in sides) + ".",
          "", "## Cells not read (PRE_REG s.4): REFUSED_POWER, no number computed or looked at", "",
          "| cell | days available | verdict |", "|---|---|---|",
          "| C long only | 254 | REFUSED_POWER |", "| C short only | 202 | REFUSED_POWER |",
          "| every single factor value, each side (F1-F7, 24 factors, 86 values) | largest bucket 768 | REFUSED_POWER |",
          "| candle confidence (O2) as a condition | not in C | REFUSED_POWER |", "",
          "The two per-side E lines above are the s.4 'E per side' print-beside rows of the READ cell; they carry no verdict.", "",
          "## DECISION (OURS) lines (details PRE_REG s.0-8 left open; each is the conservative or the literal reading)", "",
          "- Funding data: `F:/MTS/data/candle_close_dev_2022_2024` does not exist on this machine (JIS-NB). The same Binance monthly fundingRate series (identical columns) is read from `F:/MTS/Dumps/backtest/raw/fundingRate/*.csv`, months 2022-01..2024-06, settlements before 2024-07-01. Funding is not part of C; it enters only net_R (and the unused `f7_funding` frame column, built by `build_frames.py` with that loader).",
          "- Frames were built by the frozen `run_dev.py vec` through `build_frames.py` (a wrapper that only swaps the funding loader; no frozen file was edited, context_asof.py sha unchanged).",
          "- Stop price = close x (1 -+ f3_stop_pct/100) of the T row, rounded to the archive's 0.01 grid (off-grid error < 1e-6 asserted).",
          "- Entry beyond the stop = entry at or past the stop (R <= 0 on the wrong side); skipped.",
          "- Funding: a settlement counts when entry-bar open <= settlement time < end of the exit bar; funding term = sign x sum of rates x entry.",
          "- Controls pool = tradeable-ledger events (valid ladder stop, entry bar present, entry not beyond stop, context key defined) of the same side, not in C, not within 24 h (inclusive) of any C event of that side. One `default_rng(0)` per side, C events in time order, candidates shuffled, K = 20 without replacement, spacing > 4 h, kmin = 10.",
          "- Mean net_R of C > 0 is required both over all executed C trades and over the matched events; the MDD gate is required both on the matched events and on all executed C trades against the controls' mean path (cumulative sum in time order). Where the text allows two readings the stricter one gates.",
          "- Holm: m = 37, p two-sided from the normal approximation; the |t| >= 3.205 rule gates.", "",
          "## Provenance", "",
          f"- Counts: `python study.py counts` printed C long 554/254, short 456/202, pooled 1010/456 before any outcome: MATCH PRE_REG s.2.",
          f"- DEV data: 1m archive F:/MTS/data/tom_raw/klines; {len(b['ot'])} bars with open < 2024-07-01; missing 1h grid hours filled: {n_missing_hours}.",
          "- Files: ledger_C.csv (every C event, executed or skipped), controls.csv (every control draw), EXPOSURE_LEDGER.csv, VERDICTS.csv row (kill scope PRE_REG s.5)."]
    (out_dir / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L))
    return dict(verdict=verdict_line, E=E, se=se, t=t, matched=len(M), days=matched_days, mean_all=mean_all, gross_pct=float(allC["gross_pct"].mean()),
                gross_se=RK.cluster_mean_se(allC["gross_pct"].to_numpy(float), (allC["T"] // DAY).to_numpy())[1], n_exec=len(allC))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "counts"
    if cmd == "counts":
        sys.exit(0 if counts_main()[0] else 2)
    elif cmd == "smoke":                      # plumbing check with RANDOM P&L into a scratch dir; reads no real outcome
        od = Path(sys.argv[2])
        od.mkdir(parents=True, exist_ok=True)
        run(od, synthetic=True)
    elif cmd == "run":                        # THE ONE RUN
        run(HERE)
    else:
        raise SystemExit("usage: study.py counts | smoke <scratch dir> | run")
