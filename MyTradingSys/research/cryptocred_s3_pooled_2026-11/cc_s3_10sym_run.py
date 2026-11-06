"""DEV run of PRE_REG_10SYM.md: CryptoCred 4h Setup 1 (sr_flip, ATR buffer 1.0, fixed 1.5 R bracket, Deribit all_taker),
ten USD-M symbols pooled, no funding. Reuses cc_s3_run (signals, day-block bootstrap) and cc_s3_pooled_count (loader, ticks).
DEV only: bars cut at 2024-07-01 and splits.assert_dev_only. Gap bars (missing 1m rows) are never interpolated."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cc_s3_pooled_count as P  # noqa: E402

S, R = P.S, P.R
SETUP, K, M_FAMILY, MIN_SYMS_SIGN = "setup1_sr_flip", 1.0, 221, 7


def symbol_trades(sym, data_root, registry):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    bars = P.dev_bars(load_klines(Path(data_root), dataset=P.DATASETS[sym]))
    htf = resample(bars, "4h", registry)
    S.assert_bars_dev_only(htf)
    sigs, skipped = S.build_signals(SETUP, htf, K)
    stats = {}
    trades = R.build_trades(sigs, bars, [], "all_taker", S.TF_MS["4h"], max_bars=S.MAX_BARS_1M, stats=stats, tick=P.TICKS[sym])
    return trades, stats, skipped, len(bars)


def verdict(n, mean, lo, holm_p, n_pos, n_sym):
    """PRE_REG_10SYM verdict rule."""
    if n < S.MIN_N or mean is None:
        return "UNDERPOWERED"
    if mean <= 0:
        return "FAIL"
    if lo > 0 and holm_p < S.ALPHA and n_pos >= MIN_SYMS_SIGN:
        return "PASS"
    return "UNDERPOWERED"


def holm_single(p, m=M_FAMILY):
    """Smallest-p step of Holm for one tested cell inside a family of m: min(1, m * p)."""
    return min(1.0, m * p)


def weeks_regime(end_ms):
    """Weekly regime tags over DEV from BTCUSDT spot 1d context (market regime, OURS), via the bb_range_retest_eth_pool helpers."""
    here = HERE.parent / "bb_range_retest_eth_pool_2026-11" / "study.py"
    sp = importlib.util.spec_from_file_location("bb_pool_ctx", here)
    st = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(st)
    regime_at = st.prev.make_regime_at(*st.spot_context("BTCUSDT", end_ms))
    return [regime_at(t) for t in st.prev.week_starts(st.DEV_START_MS, st.DEV_END_MS)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from MyTradingSys.backtest import research_kit as rk
    registry = json.loads(R.REGISTRY_PATH.read_text(encoding="utf-8"))
    per, pooled = {}, []
    for sym in P.DATASETS:
        trades, stats, skipped, nbars = symbol_trades(sym, a.data_root, registry)
        rs = [t["net_r"] for t in trades]
        per[sym] = {"n": len(trades), "mean_net_r": float(np.mean(rs)) if rs else None, "hit_target": (
            sum(1 for t in trades if t["exit_reason"] == "targets") / len(trades) if trades else None),
            "open_at_end": stats["open_at_end"], "unfilled": stats["unfilled"], "signals": stats["signals"], "bars_1m": nbars}
        pooled += trades
        print(sym, per[sym], file=sys.stderr)
    rs = [t["net_r"] for t in pooled]
    n = len(rs)
    mean = float(np.mean(rs)) if n else None
    lo, hi, p = S.day_block_bootstrap(rs, [t["t"] for t in pooled]) if n else (None, None, 1.0)
    hp = holm_single(p)
    n_pos = sum(1 for v in per.values() if v["mean_net_r"] is not None and v["mean_net_r"] > 0)
    word = verdict(n, mean, lo if lo is not None else 0, hp, n_pos, len(per))
    out = {"n": n, "mean_net_r": mean, "ci_lo": lo, "ci_hi": hi, "p_two": p, "holm_p": hp, "m": M_FAMILY,
           "sd_r": float(np.std(rs, ddof=1)) if n > 1 else None, "mean_gross_r": float(np.mean([t["gross_r"] for t in pooled])),
           "symbols_positive": n_pos, "verdict": word, "per_symbol": per,
           "regime_weeks": rk.regime_mix_line(weeks_regime(S.DEV_END_MS))}
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in out.items() if k != "per_symbol"}))


if __name__ == "__main__":
    main()
