"""CryptoCred 4h/1d redesign, S3 DEV run (card cryptocred-4h-1d-dev-s3). Wraps run_cc_setups / cc_setups
(unchanged) with the PRE_REG redesign stop (structural invalidation + k x 14-period Wilder ATR, no forward
bars), DEV-only bars (splits.assert_dev_only), real funding, day-block bootstrap (FORMULAS 18.7) and Holm.
Frozen design: PRE_REG_ADDENDUM.md. Never reads bars at/after 2024-07-01; the VALIDATION read is a separate
step that calls require_dev_pass() first."""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("MTS_REPO") or HERE.parents[2])
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import splits  # noqa: E402
from MyTradingSys.backtest import research_kit  # noqa: E402
from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as R  # noqa: E402
from MyTradingSys.backtest.layers.cryptocred.cc_setups import _r_target  # noqa: E402

DEV_START_MS = 1640995200000
DEV_END_MS = 1719792000000      # 2024-07-01T00:00Z exclusive
TF_MS = {"4h": 14400000, "1d": 86400000}
MAX_BARS_1M = 42 * 240          # PRE_REG item 1: 42 4h bars = 7 days (OURS), used for 1d too
ATR_N = 14                      # PRE_REG item 6 (OURS)
MIN_N = 100                     # PRE_REG 0e
BOOT_N, BOOT_SEED = 2000, 20261009   # FORMULAS 18.7
ALPHA = 0.05


class DevPassRequired(Exception):
    pass


def _utc(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).replace(tzinfo=None)


def assert_bars_dev_only(bars):
    if bars:
        splits.assert_dev_only(_utc(bars[0]["t"]), _utc(bars[-1]["t"]))


def require_dev_pass(result_md):
    p = Path(result_md)
    if not p.exists():
        raise DevPassRequired(f"{p} missing: no DEV result, no VALIDATION read")
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip() == "DEV_PASS: yes":
            return True
    raise DevPassRequired("RESULT.md has no 'DEV_PASS: yes' line: VALIDATION stays sealed")


def mean_net_r(trades):
    return sum(t["net_r"] for t in trades) / len(trades) if trades else None


def true_ranges(bars):
    out = []
    for i, b in enumerate(bars):
        if i == 0:
            out.append(b["h"] - b["l"])
        else:
            pc = bars[i - 1]["c"]
            out.append(max(b["h"] - b["l"], abs(b["h"] - pc), abs(b["l"] - pc)))
    return out


def wilder_atr(bars, i, n=ATR_N):
    """Wilder ATR at bar index i (bars 0..i only): seed = mean of first n TR, then (prev*(n-1)+TR)/n."""
    if i < n - 1:
        return None
    trs = true_ranges(bars[:i + 1])
    a = sum(trs[:n]) / n
    for j in range(n, i + 1):
        a = (a * (n - 1) + trs[j]) / n
    return a


def atr_series(bars, n=ATR_N):
    trs = true_ranges(bars)
    out = [None] * len(bars)
    if len(bars) < n:
        return out
    a = sum(trs[:n]) / n
    out[n - 1] = a
    for j in range(n, len(bars)):
        a = (a * (n - 1) + trs[j]) / n
        out[j] = a
    return out


def redesign_signal(sig, atr, k):
    """sig['stop'] is the bare structural invalidation (setups run with stop_buffer_pct=0). The stop moves
    k x ATR beyond it; the R target is recomputed from the new risk."""
    sgn = 1.0 if sig["side"] == "long" else -1.0
    stop = sig["stop"] - sgn * k * atr
    out = dict(sig)
    out["stop"] = stop
    out["targets"] = [(_r_target(sig["entry_price"], stop, sig["side"], sig["meta"]["target_r"]), 1.0)]
    return out


def build_signals(name, tf_bars, k):
    """Signals of a CURRENT-default setup with the bare invalidation stop, then the ATR buffer (ATR at the
    bar where the setup is known: placed_t for limits, entry_t otherwise)."""
    sigs = R.SETUPS[name](tf_bars, stop_buffer_pct=0.0)
    idx = {b["t"]: i for i, b in enumerate(tf_bars)}
    atrs = atr_series(tf_bars)
    out, skipped = [], 0
    for s in sigs:
        t_known = s["meta"].get("placed_t", s["entry_t"])
        a = atrs[idx[t_known]] if t_known in idx else None
        if a is None:
            skipped += 1
            continue
        r = redesign_signal(s, a, k)
        bad = r["stop"] >= r["entry_price"] if r["side"] == "long" else r["stop"] <= r["entry_price"]
        if bad:
            skipped += 1
            continue
        out.append(r)
    return out, skipped


def day_block_mean(sums, counts, idx):
    sums, counts = np.asarray(sums, float), np.asarray(counts, float)
    ix = np.asarray(idx)
    return float(sums[ix].sum() / counts[ix].sum())


def day_block_bootstrap(rs, ts, n=BOOT_N, seed=BOOT_SEED):
    """FORMULAS 18.7: group by UTC date, resample days with replacement, stat = sum R / events in them.
    Returns (lo95, hi95, p two-sided for mean = 0 from the resampled-mean sign share)."""
    days = {}
    for r, t in zip(rs, ts):
        days.setdefault(int(t // 86400000), []).append(r)
    keys = sorted(days)
    sums = np.array([sum(days[d]) for d in keys])
    cnt = np.array([len(days[d]) for d in keys], float)
    rng = np.random.default_rng(seed)
    ix = rng.integers(0, len(keys), size=(n, len(keys)))
    means = sums[ix].sum(axis=1) / cnt[ix].sum(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    p_le = (np.sum(means <= 0) + 1) / (n + 1)
    p_ge = (np.sum(means >= 0) + 1) / (n + 1)
    return float(lo), float(hi), float(min(1.0, 2 * min(p_le, p_ge)))


def classify(n, mean, lo, holm_p):
    if n < MIN_N or mean is None:
        return "INCONCLUSIVE"
    if mean > 0 and lo > 0 and holm_p < ALPHA:
        return "PASS"
    if mean <= 0:
        return "FAIL"
    return "INCONCLUSIVE"


def load_dev(root1, funding_root):
    """DEV 1m bars (cut at DEV_END before anything else), HTF bars by resample, funding records < DEV_END."""
    from MyTradingSys.backtest.bt.bt_data import load_klines, load_funding
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    bars = [b for b in load_klines(Path(root1)) if DEV_START_MS <= b["t"] < DEV_END_MS]
    assert_bars_dev_only(bars)
    fund = [f for f in load_funding(Path(funding_root)) if f[0] < DEV_END_MS]
    reg = json.loads(R.REGISTRY_PATH.read_text(encoding="utf-8"))
    htf = {tf: resample(bars, tf, reg) for tf in ("4h", "1d")}
    for tf in htf:
        assert_bars_dev_only(htf[tf])
    return bars, htf, fund


def run_arm(arm, bars, htf, fund, variant="all_taker"):
    tf, name, k = arm["tf"], arm["setup"], arm["k"]
    sigs, skipped = build_signals(name, htf[tf], k)
    stats = {}
    trades = R.build_trades(sigs, bars, fund, variant, TF_MS[tf], max_bars=MAX_BARS_1M, stats=stats)
    risks = sorted(abs(s["entry_price"] - s["stop"]) / s["entry_price"] for s in sigs)
    stats.update({"skipped_no_atr_or_bad_stop": skipped,
                  "median_stop_pct": 100 * risks[len(risks) // 2] if risks else None})
    return trades, stats


def summarize_arm(trades):
    n = len(trades)
    if not n:
        return {"n": 0}
    rs = [t["net_r"] for t in trades]
    lo, hi, p = day_block_bootstrap(rs, [t["t"] for t in trades])
    return {"n": n, "hit_target": sum(1 for t in trades if t["exit_reason"] == "target") / n,
            "win_net_gt0": sum(1 for r in rs if r > 0) / n, "mean_net_r": sum(rs) / n,
            "mean_gross_r": sum(t["gross_r"] for t in trades) / n,
            "mean_net_nofund_r": sum(t["net_nofund_r"] for t in trades) / n,
            "ci_lo": lo, "ci_hi": hi, "p_two": p}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=os.environ.get("MTS_CC_DATA_ROOT"))
    ap.add_argument("--funding-root", default=os.environ.get("MTS_CC_FUNDING_ROOT"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--m-prior", type=int, required=True, help="verdicts.py count --split DEV at freeze")
    a = ap.parse_args(argv)
    arms = []
    for trial, k in (("T1", 1.0), ("T4", 0.5), ("T5", 1.5)):
        for s in ("setup1_sr_flip", "setup2_fib_pullback"):
            arms.append({"trial": trial, "tf": "4h", "setup": s, "k": k, "primary_family": True})
    for tf, s in (("4h", "setup3_failed_msb_reversal"), ("1d", "setup1_sr_flip"), ("1d", "setup2_fib_pullback"),
                  ("1d", "setup3_failed_msb_reversal")):
        arms.append({"trial": "DESC", "tf": tf, "setup": s, "k": 1.0, "primary_family": False})
    bars, htf, fund = load_dev(a.data_root, a.funding_root)
    print(f"DEV 1m bars {len(bars)}, 4h {len(htf['4h'])}, 1d {len(htf['1d'])}, funding {len(fund)}", file=sys.stderr)
    fam = [i for i, x in enumerate(arms) if x["primary_family"]]
    out = []
    for arm in arms:
        row = dict(arm)
        for variant in ("all_taker", "maker_entry"):
            trades, st = run_arm(arm, bars, htf, fund, variant)
            row[variant] = {"stats": st, "summary": summarize_arm(trades)}
        out.append(row)
    ps = [out[i]["all_taker"]["summary"].get("p_two", 1.0) for i in fam]
    hp = research_kit.holm(ps, m=a.m_prior + len(fam))
    for j, i in enumerate(fam):
        out[i]["holm_p"] = float(hp[j])
    for r in out:
        s = r["all_taker"]["summary"]
        if r["primary_family"]:
            r["verdict"] = classify(s["n"], s.get("mean_net_r"), s.get("ci_lo", 0), r["holm_p"])
        else:
            r["verdict"] = "INCONCLUSIVE (declared in advance, PRE_REG 0e/10)"
    dev_pass = any(r["verdict"] == "PASS" for r in out if r["trial"] == "T1")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="\n", encoding="utf-8") as f:
        json.dump({"m_prior": a.m_prior, "m_family": a.m_prior + len(fam), "dev_pass": dev_pass, "arms": out}, f, indent=1)
    for r in out:
        s = r["all_taker"]["summary"]
        print(r["trial"], r["tf"], r["setup"], r["k"], s.get("n"), s.get("mean_net_r"), r["verdict"], file=sys.stderr)
    print("DEV_PASS:", "yes" if dev_pass else "no", file=sys.stderr)


if __name__ == "__main__":
    main()
