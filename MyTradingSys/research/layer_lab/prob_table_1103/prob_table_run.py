"""Frozen probability-table experiment; every user-defined choice is labelled OURS in RESULT.md."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
import sys
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest.fees import DERIBIT_TAKER

FIT_DIR = Path(r"F:\MTS\data\tom_raw\klines")
EVAL_DIR = Path(r"F:\MTS\data\dev_ext_2019_2021\klines")
CUTOFF = pd.Timestamp("2024-07-01T00:00:00Z")
MIN_CELL_N = 30
BOOTSTRAPS = 1000
SEED = 1103
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]


def synthetic_bars(closes):
    idx = pd.date_range("2024-01-01", periods=len(closes), freq="h", tz="UTC")
    c = np.asarray(closes, dtype=float)
    return pd.DataFrame({"open": c, "high": c, "low": c, "close": c}, index=idx)


def states(bars):
    """Causal state at each closed bar; BB20/2 population SD and Wilder RSI14."""
    c = bars["close"].astype(float)
    mean = c.rolling(20, min_periods=20).mean()
    sd = c.rolling(20, min_periods=20).std(ddof=0)
    upper, lower = mean + 2 * sd, mean - 2 * sd
    bb = pd.Series(np.where(c > upper, "above_upper",
                            np.where(c > mean, "upper_half",
                                     np.where(c >= lower, "lower_half", "below_lower"))), index=c.index, dtype="object")
    bb[mean.isna()] = None
    delta = c.diff().to_numpy()
    gains = np.maximum(delta[1:], 0.0)
    losses = np.maximum(-delta[1:], 0.0)
    rsi_values = np.full(len(c), np.nan)
    if len(c) > 14:
        ag, al = float(gains[:14].mean()), float(losses[:14].mean())
        for i in range(14, len(c)):
            if i > 14:
                ag = (ag * 13 + gains[i - 1]) / 14
                al = (al * 13 + losses[i - 1]) / 14
            rsi_values[i] = (50.0 if ag == 0 else 100.0) if al == 0 else 100 - 100 / (1 + ag / al)
    rsi = pd.Series(rsi_values, index=c.index)
    rz = pd.cut(rsi, [-np.inf, 30, 50, 70, np.inf], labels=["lt30", "30_50", "50_70", "gt70"], right=False).astype(object)
    rz[rsi.isna()] = None
    out = pd.DataFrame(index=c.index)
    out["regime"] = np.where(c > c.rolling(200, min_periods=200).mean(), "above", "below")
    out.loc[c.rolling(200, min_periods=200).mean().isna(), "regime"] = None
    out["bb"] = bb
    out["rsi"] = rz
    return out


def mean_logloss(labels, probabilities):
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-15, 1 - 1e-15)
    y = np.asarray(labels, dtype=int)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def shrunk_probability(cell, parent):
    return cell["p_up"] if cell["n"] >= MIN_CELL_N else parent["p_up"]


def load_minutes(folder, start, end):
    if pd.Timestamp(end, tz="UTC") > CUTOFF:
        raise ValueError(f"load end {end} exceeds frozen cutoff {CUTOFF}")
    start_ts, end_ts = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    if end_ts <= start_ts:
        raise ValueError(f"empty or reversed data window [{start_ts}, {end_ts})")
    frames = []
    for p in sorted(folder.glob("BTCUSDT-1m-*.csv")):
        # Files are monthly; filter names before reading. End is exclusive.
        month = p.name[11:18]
        month_start = pd.Timestamp(f"{month}-01", tz="UTC")
        month_end = month_start + pd.offsets.MonthBegin(1)
        if month_end <= start_ts or month_start >= end_ts:
            continue
        df = pd.read_csv(p, header=None, names=COLS)
        if str(df.iloc[0, 0]).lower() == "open_time":
            df = df.iloc[1:].copy()
        for col in ("open_time", "open", "high", "low", "close"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["open_time", "open", "high", "low", "close"])
        t = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        keep = (t >= start_ts) & (t < end_ts)
        frames.append(pd.DataFrame({k: df[k].to_numpy() for k in ("open", "high", "low", "close")}, index=t)[keep.to_numpy()])
    if not frames:
        raise FileNotFoundError(f"No BTCUSDT 1m files in {folder} for {start}..{end}")
    return pd.concat(frames).sort_index().loc[lambda x: ~x.index.duplicated(keep="last")]


def aggregate(minutes, tf):
    rule = f"{tf}h"
    if minutes.empty:
        raise ValueError("no source minute bars to aggregate")
    if not minutes.index.is_unique:
        raise ValueError("duplicate source minute timestamps")
    expected_index = pd.date_range(minutes.index[0], minutes.index[-1], freq="min")
    missing_minutes = expected_index.difference(minutes.index)
    if len(missing_minutes):
        raise ValueError(f"missing source minute at {missing_minutes[0]}")
    bars = minutes.resample(rule, label="left", closed="left", origin="start_day").agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), minute_count=("close", "count")).dropna()
    expected_minutes = tf * 60
    incomplete = bars.minute_count != expected_minutes
    if incomplete.any():
        first = bars.index[incomplete][0]
        raise ValueError(f"incomplete {tf}h candle at {first}: {int(bars.loc[first, 'minute_count'])}/{expected_minutes} minute bars")
    bars = bars.drop(columns="minute_count")
    # Timestamp is bar open; shift to the known close for all downstream cuts.
    bars.index = bars.index + pd.Timedelta(hours=tf)
    return bars


def make_rows(bars, horizon):
    st = states(bars)
    rows = []
    bar_rows = list(bars.itertuples())
    state_rows = list(st.itertuples())
    # Rolling endpoints are paired with current rows using zip, never i+h indexing.
    future_high = bars.high.rolling(horizon).max().to_numpy()[horizon:]
    future_low = bars.low.rolling(horizon).min().to_numpy()[horizon:]
    for state, current, future, max_high, min_low in zip(
            state_rows[:-horizon], bar_rows[:-horizon], bar_rows[horizon:], future_high, future_low):
        if any(pd.isna(v) for v in state[1:]):
            continue
        entry = float(current.close)
        if entry <= 0:
            continue
        gross = float(future.close) / entry - 1
        rows.append({"ts": current.Index, "regime": state.regime, "bb": state.bb, "rsi": state.rsi,
                     "up": int(gross > 0), "ret": gross, "mfe": float(max_high / entry - 1),
                     "mae": float(min_low / entry - 1)})
    return pd.DataFrame(rows)


def fit_predict(train, test):
    # OURS: Laplace(1,1) binary probability; cells below 30 use the regime parent.
    parents, cells = {}, {}
    for regime, g in train.groupby("regime", sort=True):
        parents[regime] = {"n": len(g), "p_up": (int(g.up.sum()) + 1) / (len(g) + 2), "mean": float(g.ret.mean())}
    for key, g in train.groupby(["regime", "bb", "rsi"], sort=True):
        cells[key] = {"n": len(g), "p_up": (int(g.up.sum()) + 1) / (len(g) + 2), "mean": float(g.ret.mean())}
    pred = []
    for r in test.itertuples(index=False):
        parent = parents[r.regime]
        cell = cells.get((r.regime, r.bb, r.rsi), {"n": 0, "p_up": parent["p_up"], "mean": parent["mean"]})
        use_cell = cell["n"] >= MIN_CELL_N
        model = cell if use_cell else parent
        # OURS: direction with positive fitted arithmetic EV after Deribit all-taker fee; else flat.
        direction = 1 if model["mean"] > 2 * DERIBIT_TAKER else (-1 if model["mean"] < -2 * DERIBIT_TAKER else 0)
        base_dir = 1 if parent["mean"] > 2 * DERIBIT_TAKER else (-1 if parent["mean"] < -2 * DERIBIT_TAKER else 0)
        pred.append({"p_up": model["p_up"], "base_p_up": parent["p_up"], "n_fit": cell["n"],
                     "cell_used": int(use_cell), "signal": direction, "base_signal": base_dir,
                     "net": direction * r.ret - (2 * DERIBIT_TAKER if direction else 0),
                     "base_net": base_dir * r.ret - (2 * DERIBIT_TAKER if base_dir else 0)})
    return pd.DataFrame(pred, index=test.index), cells


def paired_weekly_ci(rows, diffs, seed=SEED):
    # OURS: resample ISO-week clusters with replacement; preserve within-week dependence.
    weeks = rows.ts.dt.strftime("%G-%V")
    groups = [np.flatnonzero(weeks.to_numpy() == w) for w in weeks.unique()]
    rng = np.random.default_rng(seed)
    vals = np.empty(BOOTSTRAPS)
    for b in range(BOOTSTRAPS):
        picked = rng.integers(0, len(groups), size=len(groups))
        ix = np.concatenate([groups[j] for j in picked])
        vals[b] = float(np.mean(np.asarray(diffs)[ix]))
    return [float(np.quantile(vals, .025)), float(np.quantile(vals, .975))]


def summarize(tf, horizon, fit, test):
    pred, cells = fit_predict(fit, test)
    joined = test.reset_index(drop=True).copy()
    pred = pred.reset_index(drop=True)
    log_diff = np.where(joined.up.to_numpy() == 1,
                        np.log(np.clip(pred.base_p_up, 1e-15, 1)) - np.log(np.clip(pred.p_up, 1e-15, 1)),
                        np.log(np.clip(1 - pred.base_p_up, 1e-15, 1)) - np.log(np.clip(1 - pred.p_up, 1e-15, 1)))
    ev_diff = pred.net.to_numpy() - pred.base_net.to_numpy()
    ll_ci = paired_weekly_ci(joined, log_diff)
    ev_ci = paired_weekly_ci(joined, ev_diff)
    # Inference OURS: keep only when both paired 95% intervals clear zero in favorable direction.
    verdict = "KEEP" if ll_ci[1] < 0 and ev_ci[0] > 0 and float(pred.net.mean()) > 0 else "KILL"
    bins = joined.assign(bb=joined.bb, rsi=joined.rsi).groupby(["regime", "bb", "rsi"], observed=True)
    cell_rows = []
    for key, g in bins:
        cell_rows.append({"tf": tf, "horizon": horizon, "regime": key[0], "bb": key[1], "rsi": key[2], "n": len(g),
                          "mfe_q50": g.mfe.quantile(.5), "mfe_q90": g.mfe.quantile(.9),
                          "mae_q10": g.mae.quantile(.1), "mae_q50": g.mae.quantile(.5)})
    return {"tf": tf, "horizon": horizon, "verdict": verdict, "n_fit": len(fit), "n_test": len(test),
            "logloss_model": mean_logloss(joined.up, pred.p_up), "logloss_baseline": mean_logloss(joined.up, pred.base_p_up),
            "logloss_diff": float(np.mean(log_diff)), "logloss_ci_low": ll_ci[0], "logloss_ci_high": ll_ci[1],
            "ev_model": float(pred.net.mean()), "ev_baseline": float(pred.base_net.mean()),
            "ev_diff": float(ev_diff.mean()), "ev_ci_low": ev_ci[0], "ev_ci_high": ev_ci[1],
            "model_trades": int((pred.signal != 0).sum()), "baseline_trades": int((pred.base_signal != 0).sum()),
            "used_cells": int(pred.cell_used.sum()), "cell_rows": cell_rows}


def main():
    out = Path(__file__).parent
    fit_m = load_minutes(FIT_DIR, "2022-01-01", "2024-07-01")
    test_m = load_minutes(EVAL_DIR, "2020-01-01", "2022-01-01")
    all_results, all_cells = [], []
    for tf in (1, 4):
        fit_bars, test_bars = aggregate(fit_m, tf), aggregate(test_m, tf)
        for h in (4, 24):
            fit_rows, test_rows = make_rows(fit_bars, h), make_rows(test_bars, h)
            result = summarize(tf, h, fit_rows, test_rows)
            all_cells.extend(result.pop("cell_rows"))
            all_results.append(result)
    pd.DataFrame(all_results).to_csv(out / "table.csv", index=False, lineterminator="\n")
    pd.DataFrame(all_cells).to_csv(out / "cell_quantiles.csv", index=False, lineterminator="\n")
    lines = ["# Probability table results", "", "All design choices labelled OURS are experimental choices, not sourced trader rules.",
             "", "Closed UTC bars only. Fit 2022-01-01 through 2024-06-30; evaluation 2020-01-01 through 2021-12-31. No bars after 2024-06-30 were loaded. VALIDATION and HOLDOUT were not read.",
             "Fees: canonical Deribit all-taker 10 bp round trip before slippage (fees.py). Parameters: BB20/2 population SD, Wilder RSI14, SMA200 regime, Laplace binary smoothing, n<30 fallback to regime parent, EV is mean signed close-to-close return net of fee, weekly block bootstrap 1,000 replicates; all OURS.",
             "", "Log-loss difference is model minus regime baseline (negative is better). EV difference is model minus baseline net return per eligible bar; 95% weekly block-bootstrap CIs.", "",
             "| TF | Horizon | Verdict | Fit n | Test n | Model LL | Baseline LL | LL diff [95% CI] | Model EV | Baseline EV | EV diff [95% CI] | Trades model/base | Cells used |",
             "|---:|---:|---|---:|---:|---:|---:|---|---:|---:|---|---:|---:|"]
    for r in all_results:
        lines.append(f"| {r['tf']}h | {r['horizon']} | {r['verdict']} | {r['n_fit']} | {r['n_test']} | {r['logloss_model']:.6f} | {r['logloss_baseline']:.6f} | {r['logloss_diff']:.6f} [{r['logloss_ci_low']:.6f}, {r['logloss_ci_high']:.6f}] | {r['ev_model']:.6%} | {r['ev_baseline']:.6%} | {r['ev_diff']:.6%} [{r['ev_ci_low']:.6%}, {r['ev_ci_high']:.6%}] | {r['model_trades']}/{r['baseline_trades']} | {r['used_cells']} |")
    lines += ["", "Kill line: KEEP requires log-loss difference CI wholly below 0, test EV above 0, and EV-difference CI wholly above 0. Otherwise KILL.",
              "MFE/MAE per evaluation state cell are in cell_quantiles.csv (MFE 50th/90th; MAE 10th/50th percentiles).",
              "Limitations: one asset/venue; no slippage or funding; binary up/down log-loss; the reverse-time fit/evaluation split follows the frozen card. Results are exploratory and do not authorize live trading.", ""]
    (out / "RESULT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
