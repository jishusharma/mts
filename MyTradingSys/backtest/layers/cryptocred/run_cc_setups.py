"""
MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py

Standalone runner: CryptoCred setups (cc_setups.setup1_sr_flip, setup2_fib_pullback,
setup3_failed_msb_reversal) backtested NET of fees. Modelled on layers/run_t055.py.

- Data: BTCUSDT 1m klines via bt_data.load_klines (same roots as run_t055: --data-root =
  raw_1m_2022, --data-root2 = raw; env MTS_CC_DATA_ROOT / MTS_CC_DATA_ROOT2), resampled with
  tf_resample to --tf (default 1h; 15m/4h allowed).
- Signals: cc_setups functions with their CURRENT defaults. No parameter grid (layer provenance
  audit forbids tuning), so PBO is N/A and is NOT part of the verdict.
- Trades, simulated on the 1m bars (stop/target ordering at 1m resolution):
  * setups 1 and 2 are RESTING LIMIT orders at the level (entry_price), placed at the close of the
    MSB confirm bar (meta placed_t) and valid to meta valid_until_t; filled on the first later 1m bar
    whose range reaches the level (gap bar: fill at its open). The fill bar can only stop the trade
    (stop_first); exits are simulated from the fill. Unfilled limits are no trade and are counted.
  * setup 3 enters at the close of the signal bar (entry_price = close of its last 1m bar).
- Fees (fees.py), two variants: all_taker (Deribit taker on every leg, conservative) and
  maker_entry (Deribit maker on entry and targets, taker on stop/timeout; the entry fee is
  refunded on top of the engine's taker-entry charge). Funding from the funding files when
  present; otherwise the headline is net_nofund and is labelled so.
- Split: chronological 70/30 by bar index; a trade belongs to IS if its signal bar is before the
  split bar. Exits of late-IS trades may run past the split (no parameter is fitted, so no leak
  into any choice).
- Verdict (T055 rule): OOS n>=30, OOS net mean>0, net Sharpe>=0.3, same IS/OOS sign,
  >=2 positive OOS calendar years.

Alert-only research code; never touches execution or Tom core. Output goes to --out (default:
a temp dir, never the repo unless --allow-repo-out).
"""
import argparse
import bisect
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get("MTS_REPO") or Path(__file__).resolve().parents[4])
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import fees as F
from MyTradingSys.backtest.bt.bt_engine import simulate_trade
from MyTradingSys.backtest.bt.bt_stats import sharpe
from MyTradingSys.backtest.layers.cryptocred import cc_setups
from MyTradingSys.backtest.layers.cryptocred.cc_setups import _r_target
from MyTradingSys.backtest.layers.cryptocred.cc_bt_adapter import signals_to_trades

REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"
DEFAULT_ROOT1 = REPO / "Dumps" / "backtest" / "raw_1m_2022"
DEFAULT_ROOT2 = REPO / "Dumps" / "backtest" / "raw"

SETUPS = {
    "setup1_sr_flip": cc_setups.setup1_sr_flip,
    "setup2_fib_pullback": cc_setups.setup2_fib_pullback,
    "setup3_failed_msb_reversal": cc_setups.setup3_failed_msb_reversal,
}
TF_MS = {"1m": 60000, "15m": 900000, "1h": 3600000, "4h": 14400000}
MIN_OOS_N = 30
MIN_SHARPE = 0.3
MIN_POS_YEARS = 2

# variant -> (taker_fee, maker_fee, entry_refund as fraction of entry price)
FEE_VARIANTS = {
    "all_taker": (F.DERIBIT_TAKER, F.DERIBIT_TAKER, 0.0),
    "maker_entry": (F.DERIBIT_TAKER, F.DERIBIT_MAKER, F.DERIBIT_TAKER - F.DERIBIT_MAKER),
}


class DataError(Exception):
    pass


# ---------------------------------------------------------------- split / trades

def chronological_split(bars, is_frac=0.70):
    n_is = int(len(bars) * is_frac)
    return bars[:n_is], bars[n_is:], n_is


def split_trades(trades, split_t):
    """IS = signal bar open time < split_t, OOS = >= split_t. Input order preserved."""
    return ([t for t in trades if t["t"] < split_t], [t for t in trades if t["t"] >= split_t])


LIMIT_SETUPS = ("sr_flip", "fib_pullback")


def _record(sig, entry, risk, tr, entry_refund, fill_t):
    refund_r = entry_refund * entry / risk
    funding_r = (tr["funding_paid_pct"] / 100.0) * entry / risk
    net_r = tr["net_r"] + refund_r
    net_nf_r = net_r + funding_r
    k = risk / entry
    return {"t": sig["entry_t"], "side": sig["side"], "exit_reason": tr["exit_reason"],
            "gross_r": tr["gross_r"], "net_r": net_r, "net_nofund_r": net_nf_r,
            "net_pct": net_r * k, "net_nofund_pct": net_nf_r * k, "gross_pct": tr["gross_r"] * k,
            "entry_price": entry, "fill_t": fill_t}


TICK = 0.1  # BTCUSDT price tick; BACKTEST_PROTOCOL: a resting limit fills only if price trades THROUGH it by 1 tick


def find_limit_fill(sig, sim_bars, tf_ms, times=None, tick=TICK):
    """Resting LIMIT at sig['entry_price'], placed at the close of the MSB confirm bar
    (meta placed_t + tf_ms), valid through the close of the bar opened at meta valid_until_t.
    Fills on the FIRST 1m bar strictly after placement that trades THROUGH the level by one tick:
    low<=level-tick (long) / high>=level+tick (short); a mere touch does not fill.
    Fill price = level when the bar range contains it; otherwise (bar entirely beyond the level,
    i.e. a gap) the bar open. Returns (index, fill_price) or None."""
    meta = sig["meta"]
    times = times if times is not None else [b["t"] for b in sim_bars]
    lo = bisect.bisect_left(times, meta["placed_t"] + tf_ms)
    hi = bisect.bisect_left(times, meta["valid_until_t"] + tf_ms)
    level, long_ = sig["entry_price"], sig["side"] == "long"
    for k in range(lo, hi):
        b = sim_bars[k]
        if (b["l"] <= level - tick) if long_ else (b["h"] >= level + tick):
            inside = b["l"] <= level <= b["h"]
            return k, (level if inside else b["o"])
    return None


def _limit_trade(sig, hit, sim_bars, taker, maker, entry_refund, funding, max_bars, tick=0.0):
    """Trade record for a limit filled at hit=(index, price); None if the data ends open."""
    k, fill = hit
    fb = sim_bars[k]
    long_ = sig["side"] == "long"
    stop = sig["stop"]
    if (fill <= stop) if long_ else (fill >= stop):
        # gapped through the stop: filled and stopped at the same open (gross 0, two taker legs)
        risk_orig = abs(sig["entry_price"] - stop)
        tr = {"exit_reason": "stop", "gross_r": 0.0, "net_r": -2 * taker * fill / risk_orig,
              "funding_paid_pct": 0.0}
        return _record(sig, fill, risk_orig, tr, entry_refund, fb["t"])
    # Fill bar: keep its real excursion toward the stop but cap the favourable side at the fill
    # price (order of events inside the 1m bar is unknown), so only the stop can act in it
    # (stop_first) and no target is credited before the fill. entry_t = 1ms before the fill bar.
    syn = ({"t": fb["t"], "o": fill, "h": fill, "l": fb["l"], "c": fill} if long_
           else {"t": fb["t"], "o": fill, "h": fb["h"], "l": fill, "c": fill})
    seq = [syn] + sim_bars[k + 1:]
    call = {kk: v for kk, v in sig.items() if kk not in ("meta", "entry_price", "entry_t")}
    tr = simulate_trade(entry_price=fill, entry_t=fb["t"] - 1, bars=seq, funding=funding or [],
                        taker_fee=taker, maker_fee=maker, max_bars=max_bars, stop_first=True,
                        target_through=tick, **call)
    if tr.get("net_r") is None:
        return None
    return _record(sig, fill, abs(fill - stop), tr, entry_refund, fb["t"])


def _market_trade(sig, sim_bars, by_t, tf_ms, taker, maker, entry_refund, funding, max_bars, tick=0.0):
    """Entry at the close of the signal bar (setup 3 and generic signals): entry_t moved to the last
    1m bar of the signal bar. For setup 3 the entry price is that 1m bar's close (= HTF close)."""
    s2 = dict(sig)
    s2["entry_t"] = sig["entry_t"] + tf_ms - 60000
    if sig.get("meta", {}).get("setup") == "failed_msb_reversal" and s2["entry_t"] in by_t:
        c = by_t[s2["entry_t"]]["c"]
        if c != sig["entry_price"]:
            s2["entry_price"] = c
            s2["targets"] = [(_r_target(c, sig["stop"], sig["side"], sig["meta"]["target_r"]), 1.0)]
    r = signals_to_trades([s2], sim_bars, funding=funding or [], taker_fee=taker,
                          maker_fee=maker, max_bars=max_bars, target_through=tick)[0]["trade_result"]
    if r.get("net_r") is None:  # open at end of data
        return None
    return _record(sig, s2["entry_price"], abs(s2["entry_price"] - sig["stop"]), r, entry_refund,
                   s2["entry_t"])


def build_trades(signals, sim_bars, funding, variant, tf_ms, max_bars=1440, stats=None, tick=TICK):
    """Simulate signals on sim_bars (1m) and return per-trade records.
    Setups 1/2 (sr_flip, fib_pullback) are resting limit orders at the level, placed when the setup
    is known (close of the MSB confirm bar) and filled on the first later 1m bar that trades through
    the level; no fill within the validity window = no trade (counted in stats['unfilled']).
    Other signals (setup 3, generic) enter at the close of the signal bar.
    r values are per unit risk; pct = fraction of entry notional (net_r * risk / entry).
    net_* = with funding (equals net_nofund_* when no funding is supplied)."""
    taker, maker, entry_refund = FEE_VARIANTS[variant]
    times = [b["t"] for b in sim_bars]
    by_t = {b["t"]: b for b in sim_bars}
    out = []
    if stats is None:
        stats = {}
    stats.update({"signals": len(signals), "unfilled": 0, "filled": 0, "open_at_end": 0})
    for sig in signals:
        meta = sig.get("meta", {})
        if meta.get("setup") in LIMIT_SETUPS and "placed_t" in meta:
            hit = find_limit_fill(sig, sim_bars, tf_ms, times, tick)
            if hit is None:
                stats["unfilled"] += 1
                continue
            rec = _limit_trade(sig, hit, sim_bars, taker, maker, entry_refund, funding, max_bars, tick)
        else:
            rec = _market_trade(sig, sim_bars, by_t, tf_ms, taker, maker, entry_refund, funding, max_bars, tick)
        if rec is None:
            stats["open_at_end"] += 1  # filled but still open when data ends: reported, not dropped silently
        else:
            stats["filled"] += 1
            out.append(rec)
    return out


# ---------------------------------------------------------------- stats / verdict

def _year(t):
    return datetime.fromtimestamp(t / 1000, tz=timezone.utc).year


def summarize(trades, key="net"):
    """key 'net' or 'net_nofund'. Mean R, mean %, hit rate, Sharpe on per-trade fractional returns."""
    n = len(trades)
    if n == 0:
        return {"n": 0, "mean_r": None, "mean_pct": None, "mean_gross_r": None, "hit": None, "sharpe": None}
    rs = [t[f"{key}_r"] for t in trades]
    ps = [t[f"{key}_pct"] for t in trades]
    return {"n": n, "mean_r": sum(rs) / n, "mean_pct": sum(ps) / n * 100.0,
            "mean_gross_r": sum(t["gross_r"] for t in trades) / n,
            "hit": sum(1 for r in rs if r > 0) / n, "sharpe": sharpe(ps) if n >= 2 else None}


def yearly(trades, key="net"):
    by = {}
    for t in trades:
        by.setdefault(_year(t["t"]), []).append(t[f"{key}_pct"])
    return {y: {"n": len(v), "mean_pct": sum(v) / len(v) * 100.0, "sign": "+" if sum(v) > 0 else "-"}
            for y, v in sorted(by.items())}


def verdict(is_s, oos_s, years):
    """T055 rule without PBO (no grid): returns (PASS|FAIL, criteria dict)."""
    crit = {
        "oos_n>=30": oos_s["n"] >= MIN_OOS_N,
        "oos_mean_net>0": oos_s["mean_pct"] is not None and oos_s["mean_pct"] > 0,
        "oos_net_sharpe>=0.3": oos_s["sharpe"] is not None and oos_s["sharpe"] >= MIN_SHARPE,
        "same_sign_is_oos": (oos_s["mean_pct"] is not None and is_s["mean_pct"] is not None
                             and is_s["mean_pct"] * oos_s["mean_pct"] > 0),
        ">=2_positive_oos_years": sum(1 for y in years.values() if y["mean_pct"] > 0) >= MIN_POS_YEARS,
    }
    return ("PASS" if all(crit.values()) else "FAIL"), crit


def evaluate(trades, split_t, key):
    tr_is, tr_oos = split_trades(trades, split_t)
    s_is, s_oos = summarize(tr_is, key), summarize(tr_oos, key)
    yrs = yearly(tr_oos, key)
    v, crit = verdict(s_is, s_oos, yrs)
    return {"is": s_is, "oos": s_oos, "oos_years": yrs, "criteria": crit, "verdict": v}


def run_setup(name, tf_bars, sim_bars, funding, tf_ms, is_frac=0.70, max_bars=1440, setup_fn=None, dev_only=False):
    """dev_only=True scores the IS (DEV) span only: signals before the split, 1m bars only up to split + max_bars
    (so a DEV trade still open at the split can close; no later trade is simulated, so funding records that end
    before the OOS span cannot trip the B103 span check). The OOS block is then empty (n=0)."""
    fn = setup_fn or SETUPS[name]
    signals = fn(tf_bars)  # CURRENT defaults, no grid
    _, bars_oos, n_is = chronological_split(tf_bars, is_frac)
    split_t = bars_oos[0]["t"] if bars_oos else (tf_bars[-1]["t"] + 1 if tf_bars else 0)
    if dev_only:
        signals = [g for g in signals if g["entry_t"] < split_t]
        end_t = split_t + max_bars * 60000
        sim_bars = [b for b in sim_bars if b["t"] < end_t]
    has_fund = bool(funding)
    res = {"setup": name, "n_signals": len(signals), "split_t": split_t, "pbo": None,
           "pbo_note": "N/A: no parameter grid (defaults only; provenance audit forbids tuning)",
           "funding_included": has_fund, "variants": {}}
    for variant in FEE_VARIANTS:
        fstats = {}
        trades = build_trades(signals, sim_bars, funding, variant, tf_ms, max_bars, stats=fstats)
        key = "net" if has_fund else "net_nofund"
        v = evaluate(trades, split_t, key)
        v["headline_basis"] = "net_with_funding" if has_fund else "net_nofund (NO funding files: fees only)"
        v["nofund"] = evaluate(trades, split_t, "net_nofund") if has_fund else None
        v["n_trades"] = len(trades)
        v["n_unfilled"] = fstats.get("unfilled", 0)
        v["n_open_at_end"] = fstats.get("open_at_end", 0)
        res["variants"][variant] = v
    return res


# ---------------------------------------------------------------- report

def _f(x, nd=4, suffix=""):
    return "n/a" if x is None else f"{x:.{nd}f}{suffix}"


def write_markdown(results, meta, path):
    fund = (f"included ({meta['n_funding']} records)" if meta["n_funding"]
            else "NOT AVAILABLE - headline is net_nofund (fees only)")
    L = ["# CryptoCred setups - net-of-fees backtest", "",
         f"tf {meta['tf']}; bars {meta['n_bars']} (IS {meta['n_is_bars']} / OOS {meta['n_oos_bars']}); "
         f"funding: {fund}.",
         "Fees (fees.py): all_taker = Deribit taker on every leg incl. targets; maker_entry = maker entry+targets, "
         "taker stop/timeout. Defaults only, no grid: PBO N/A, not part of the verdict.",
         "Verdict rule: OOS n>=30, OOS net mean>0, net Sharpe>=0.3, same IS/OOS sign, >=2 positive OOS years.", ""]
    for r in results:
        for variant, v in r["variants"].items():
            L += [f"## {r['setup']} / {variant}: **{v['verdict']}**", "",
                  f"signals {r['n_signals']}, trades {v['n_trades']}, unfilled limits {v['n_unfilled']}, open at end {v.get('n_open_at_end', 0)}; basis: {v['headline_basis']}", "",
                  "| split | n | mean net R | mean net % | hit | net Sharpe |", "|---|---|---|---|---|---|"]
            for k in ("is", "oos"):
                s = v[k]
                L.append(f"| {k.upper()} | {s['n']} | {_f(s['mean_r'])} | {_f(s['mean_pct'], 4, '%')} | "
                         f"{_f(s['hit'], 3)} | {_f(s['sharpe'], 3)} |")
            yrs = ", ".join(f"{y}: n={d['n']} {d['sign']} ({d['mean_pct']:.4f}%)"
                            for y, d in v["oos_years"].items()) or "none"
            L += ["", "OOS per year: " + yrs, "", "| criterion | result |", "|---|---|"]
            L += [f"| {k} | {'PASS' if ok else 'FAIL'} |" for k, ok in v["criteria"].items()]
            if v.get("nofund"):
                nf = v["nofund"]["oos"]
                L += ["", f"Same trades without funding, OOS: mean net {_f(nf['mean_pct'], 4, '%')}, n={nf['n']}."]
            L.append("")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- data + CLI

def load_data(root1, root2, tf):
    """Returns (bars_1m, tf_bars, funding). Raises DataError when a required path is missing."""
    from MyTradingSys.backtest.bt.bt_data import load_klines, load_funding
    r1 = Path(root1)
    if not (r1 / "klines").is_dir():
        raise DataError(f"data path missing: {r1 / 'klines'} (set --data-root or MTS_CC_DATA_ROOT)")
    bars = load_klines(r1)
    funding = []
    if root2 and (Path(root2) / "klines").is_dir():
        last = bars[-1]["t"] if bars else 0
        bars += [b for b in load_klines(root2) if b["t"] > last]
        bars.sort(key=lambda b: b["t"])
    for r in (root2, root1):
        if r and not funding:
            funding = load_funding(r)
    if not bars:
        raise DataError(f"no 1m bars loaded from {r1 / 'klines'}")
    if tf == "1m":
        return bars, bars, funding
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return bars, resample(bars, tf, registry), funding


def _inside(path, parent):
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description="CryptoCred setups net-of-fees backtest")
    ap.add_argument("--data-root", default=os.environ.get("MTS_CC_DATA_ROOT", str(DEFAULT_ROOT1)))
    ap.add_argument("--data-root2", default=os.environ.get("MTS_CC_DATA_ROOT2", str(DEFAULT_ROOT2)))
    ap.add_argument("--tf", default="1h", choices=["15m", "1h", "4h"])
    ap.add_argument("--setups", default="all", help="comma list of setup names, or all")
    ap.add_argument("--out", default=str(Path(tempfile.gettempdir()) / "cc_setups_run"))
    ap.add_argument("--allow-repo-out", action="store_true", help="permit --out inside the repo")
    ap.add_argument("--max-bars", type=int, default=1440, help="max 1m bars a trade may stay open")
    a = ap.parse_args(argv)

    if _inside(a.out, REPO) and not a.allow_repo_out:
        print(f"ERROR: --out {a.out} is inside the repo; pass --allow-repo-out or choose another dir",
              file=sys.stderr)
        sys.exit(2)
    names = list(SETUPS) if a.setups == "all" else a.setups.split(",")
    bad = [n for n in names if n not in SETUPS]
    if bad:
        print(f"ERROR: unknown setup(s) {bad}", file=sys.stderr)
        sys.exit(2)
    try:
        bars_1m, tf_bars, funding = load_data(a.data_root, a.data_root2, a.tf)
    except DataError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    tf_ms = TF_MS[a.tf]
    print(f"Loaded {len(bars_1m)} 1m bars, {len(tf_bars)} {a.tf} bars, {len(funding)} funding records",
          file=sys.stderr)
    _, bars_oos, n_is = chronological_split(tf_bars)
    results = [run_setup(n, tf_bars, bars_1m, funding, tf_ms, max_bars=a.max_bars) for n in names]
    meta = {"tf": a.tf, "n_bars": len(tf_bars), "n_is_bars": n_is, "n_oos_bars": len(bars_oos),
            "n_funding": len(funding), "data_root": a.data_root, "data_root2": a.data_root2}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "cc_setups_result.json", "w", newline="\n", encoding="utf-8") as f:
        json.dump({"meta": meta, "results": results}, f, indent=1, default=str)
    write_markdown(results, meta, out / "cc_setups_result.md")
    for r in results:
        print(r["setup"], {k: v["verdict"] for k, v in r["variants"].items()}, file=sys.stderr)
    return results


if __name__ == "__main__":
    main()
