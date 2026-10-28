import sys
sys.dont_write_bytecode = True
"""T080: maker execution model for the Tom core trades (research, offline, stdlib only).

Scores ONE set of signals (entry = zone price E, stop, target, side, signal time, from the 2026-10-07 verdict rows) under
four execution regimes on the 1m archive. Same bar conventions as tom_bt.sim_limit_trade (order lives 8 zone-tf bars,
cancelled if price touches the target before the fill = "ran away"; fill bar evaluates only the stop; stop first when
stop and target share a bar; gap through the stop fills at the bar open; timeout = 8 zone-tf bars after the fill, exit at
the close, taker). R = |E - stop|.

Regimes (fees per side as a fraction of price; Deribit BTC-PERPETUAL maker 0, taker 0.0005, from fees.py):
  A  all-taker: 5 bp on every leg, touch fills (isolates the fee difference to B: same fills as B).
  B  limit entry + limit target (fee 0), taker stop/timeout (5 bp), touch fills.
  C  like B, but a limit fills only if price trades THROUGH the level by TICK (0.5 USD). Applies to the entry and the
     target. A touch of the target does not fill it (the trade carries on). "Ran away" cancellation stays on touch
     (the trader cancels the entry when price reaches the target; that is not a fill).
  D  like B plus an adverse-selection cost of ADV_BP per limit fill (entry always, target when it is the exit), charged
     on the fill price. Two cells, values from the P1 report (see ADV_CELLS).
Funding, slippage on stop fills, queue position and partial fills are NOT modelled (1m bars cannot show them).

Usage: python MyTradingSys/backtest/maker_model.py   (writes the report from the Tom rows; HOLDOUT is never read)
"""
import datetime as dt
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from MyTradingSys.backtest.fees import DERIBIT_MAKER, DERIBIT_TAKER  # noqa: E402

TICK = 0.5   # USD, Deribit BTC-PERPETUAL tick size (instrument spec; stated in the task, not in fees.py)
# Adverse-selection cells. Source: research/_archive/loose_2026-10/P1_BREAKDOWNS_20261006.md ("mean adverse selection +0.02 bp", 6.4M signal-less fills,
# 2024-12..2026-09, review banner: INCOMPLETE, one pooled number) and research/_archive/loose_2026-10/P1_COST_FLOOR_2026-10-06.md section 3C (4.7-day
# run, mean -0.08 .. -0.95 bp; 1.0 bp is the rounded-up worst cell). A signal-triggered adverse selection is NOT_IN_DATA.
ADV_CELLS = {"D_0.02bp": 0.02, "D_1bp": 1.0}


def regime_params():
    t, m = DERIBIT_TAKER, DERIBIT_MAKER
    return {
        "A": dict(fee_entry=t, fee_target=t, fee_stop=t, fee_timeout=t, tick=0.0, adv_bp=0.0),
        "B": dict(fee_entry=m, fee_target=m, fee_stop=t, fee_timeout=t, tick=0.0, adv_bp=0.0),
        "C": dict(fee_entry=m, fee_target=m, fee_stop=t, fee_timeout=t, tick=TICK, adv_bp=0.0),
        **{k: dict(fee_entry=m, fee_target=m, fee_stop=t, fee_timeout=t, tick=0.0, adv_bp=v) for k, v in ADV_CELLS.items()},
    }


def score_trade(b, i0, side, entry, stop, target, fill_window, hold_bars, p):
    """One signal under regime params p. Returns dict(status=...) ; status 'filled' adds reason/gross_r/fee_r/adv_r/net_r."""
    sgn = 1.0 if side == "long" else -1.0
    if not (sgn * (stop - entry) < 0 and sgn * (target - entry) > 0):
        return dict(status="bad_geometry")
    risk = abs(entry - stop)
    n = b.n
    tick = p["tick"]
    fill_i = None
    for i in range(i0, min(i0 + fill_window, n)):
        lo, hi = b.l[i], b.h[i]
        if (lo <= entry - tick) if sgn > 0 else (hi >= entry + tick):
            fill_i = i
            break
        if (hi >= target) if sgn > 0 else (lo <= target):
            return dict(status="ran")
    if fill_i is None:
        return dict(status="no_fill" if i0 + fill_window <= n else "open_at_end")

    def done(kind, px, j):
        gross = sgn * (px - entry) / risk
        fee_r = (p["fee_entry"] * entry + p["fee_" + kind] * px) / risk
        adv_px = entry + (px if kind == "target" else 0.0)
        adv_r = p["adv_bp"] * 1e-4 * adv_px / risk
        return dict(status="filled", reason=kind, gross_r=gross, fee_r=fee_r, adv_r=adv_r,
                    net_r=gross - fee_r - adv_r, fill_i=fill_i, exit_i=j)

    if (b.l[fill_i] <= stop) if sgn > 0 else (b.h[fill_i] >= stop):
        return done("stop", min(b.o[fill_i], stop) if sgn > 0 else max(b.o[fill_i], stop), fill_i)
    last = fill_i + hold_bars
    for j in range(fill_i + 1, last + 1):
        if j >= n:
            return dict(status="open_at_end")
        s_hit = (b.l[j] <= stop) if sgn > 0 else (b.h[j] >= stop)
        t_hit = (b.h[j] >= target + tick) if sgn > 0 else (b.l[j] <= target - tick)
        if s_hit:
            return done("stop", min(b.o[j], stop) if sgn > 0 else max(b.o[j], stop), j)
        if t_hit:
            return done("target", target, j)
        if j == last:
            return done("timeout", b.c[j], j)
    return dict(status="open_at_end")


def summarize(results, boot_ci):
    """results: list of score_trade dicts for one regime over one signal set. Means are per FILLED trade unless 'per signal'."""
    sig = len(results)
    f = [r for r in results if r["status"] == "filled"]
    ran = sum(1 for r in results if r["status"] == "ran")
    out = dict(n_signals=sig, n_filled=len(f), fill_rate=len(f) / sig if sig else float("nan"),
               ran_rate=ran / sig if sig else float("nan"))
    if not f:
        return out
    m = lambda k: sum(r[k] for r in f) / len(f)
    out.update(gross=m("gross_r"), gross_ci=boot_ci([r["gross_r"] for r in f]), fee=m("fee_r"), adv=m("adv_r"), net=m("net_r"), net_ci=boot_ci([r["net_r"] for r in f]),
               net_per_signal=sum(r["net_r"] for r in f) / sig,
               net_per_signal_ci=boot_ci([r["net_r"] if r["status"] == "filled" else 0.0 for r in results]),
               target=sum(1 for r in f if r["reason"] == "target") / len(f))
    s = sorted(r["net_r"] for r in f)
    out["net_med"] = (s[len(s) // 2] + s[(len(s) - 1) // 2]) / 2
    sf = sorted(r["fee_r"] + r["adv_r"] for r in f)
    out["cost_med"] = (sf[len(sf) // 2] + sf[(len(sf) - 1) // 2]) / 2
    return out


# ---------------------------------------------------------------- driver (needs the F: data)
WORK = Path(os.environ.get("TOM_WORK_DIR", r"F:\MTS\data\tom_bt_2026-10-07"))
RAW = Path(os.environ.get("TOM_RAW_DIR", r"F:\MTS\data\tom_raw")) / "klines"
OUT = ROOT / "MyTradingSys" / "research" / "fast_track_2026-09-27" / "T080_MAKER_MODEL_2026-10-09.md"
HOLDOUT_START = dt.datetime(2026, 6, 26, tzinfo=dt.timezone.utc).timestamp()
DEV_START = dt.datetime(2025, 9, 1, tzinfo=dt.timezone.utc).timestamp()
BUCKETS = [(0.0, 0.001, "<0.10%"), (0.001, 0.002, "0.10-0.20%"), (0.002, 0.004, "0.20-0.40%"), (0.004, 9.0, ">=0.40%")]
ORDER = ["A", "B", "C"] + list(ADV_CELLS)


def common_signals(sigs, bars, T):
    """The common signal set: orders the B regime (touch fills, one pending/open position at a time, as tom_bt.run_variant)
    admits. Every regime is then scored on exactly these signals, independently (no cross-regime one-at-a-time interplay)."""
    out = []
    for r in T.run_variant(sigs, bars, fees=T.FEES_DERIBIT):
        if r.get("reason") != "bad_geometry":
            out.append(r)
    return out


def fmt_ci(ci):
    return "[%+.3f, %+.3f]" % ci


def main():
    import json
    import tom_bt as T
    rows = []
    for p in sorted(WORK.glob("*.rows.jsonl")):
        with open(p, encoding="utf-8") as fh:
            rows.extend(json.loads(line) for line in fh)
    rows.sort(key=lambda r: r["t"])
    rows = [r for r in rows if DEV_START <= r["t"] < HOLDOUT_START]   # HOLDOUT never read past this line
    print("dev rows:", len(rows), flush=True)
    bars = T.load_bars_1m(RAW)
    params = regime_params()
    L = ["# T080 maker execution model, %s" % dt.date.today().isoformat(), "",
         "Rows: %s, DEV only (%s .. 2026-06-25); HOLDOUT 2026-06-26.. not read. Bars: %s." % (
             WORK, dt.datetime.fromtimestamp(DEV_START, dt.timezone.utc).date(), RAW),
         "Code: `MyTradingSys/backtest/maker_model.py`, tests `test_maker_model.py`. Signals: tom_bt `watch_episode` (WATCH or "
         "SETUP_FORMING) and `p4_episode` (proof>=4), both SENSITIVITY variants; the live rule has 0 signals.", ""]
    summary = {}
    for variant in ("watch_episode", "p4_episode"):
        sigs = T.signals(rows, variant)
        placed = common_signals(sigs, bars, T)
        L += ["## %s: %d signals in the common set" % (variant, len(placed)), ""]
        recs = []
        for r in placed:
            tfm = T.ZONE_TF_MIN[T.zone_tf(r["ztype"])]
            i0 = bars.idx(int(round(r["t"] * 1000)))
            sf = abs(float(r["zprice"]) - float(r["stop"])) / float(r["zprice"])
            res = {k: score_trade(bars, i0, r["dir"], float(r["zprice"]), float(r["stop"]), float(r["target"]),
                                  8 * tfm, 8 * tfm, p) for k, p in params.items()}
            recs.append((sf, res))
        cuts = [("ALL", 0.0, 9.0)] + [(nm, lo, hi) for lo, hi, nm in BUCKETS]
        for nm, lo, hi in cuts:
            sel = [res for sf, res in recs if lo <= sf < hi]
            L += ["### %s / stop width %s (n signals %d)" % (variant, nm, len(sel)), "",
                  "| regime | n sig | n filled | fill rate | ran-away rate | gross R [95% CI] | fee R | adv R | net R | net R 95% CI | net R median | "
                  "net R per signal [CI] | fee R diff vs A | cost (fee+adv) diff vs A |", "|" + "---|" * 14]
            sm = {k: summarize([res[k] for res in sel], T.boot_ci) for k in ORDER}
            for k in ORDER:
                s = sm[k]
                if not s["n_signals"]:
                    L.append("| %s | 0 | - | - | - | - | - | - | - | - | - | - | - | - |" % k)
                    continue
                if not s["n_filled"]:
                    L.append("| %s | %d | 0 | 0.0%% | %.1f%% | - | - | - | - | - | - | - | - | - |" % (k, s["n_signals"], 100 * s["ran_rate"]))
                    continue
                a = sm["A"]
                dfee = ("%+.3f" % (s["fee"] - a["fee"])) if a["n_filled"] else "-"
                dcost = ("%+.3f" % (s["fee"] + s["adv"] - a["fee"])) if a["n_filled"] else "-"
                L.append("| %s | %d | %d | %.1f%% | %.1f%% | %+.3f %s | %.3f | %.3f | %+.3f | %s | %+.3f | %+.3f %s | %s | %s |" % (
                    k, s["n_signals"], s["n_filled"], 100 * s["fill_rate"], 100 * s["ran_rate"], s["gross"], fmt_ci(s["gross_ci"]), s["fee"], s["adv"],
                    s["net"], fmt_ci(s["net_ci"]), s["net_med"], s["net_per_signal"], fmt_ci(s["net_per_signal_ci"]), dfee, dcost))
            L.append("")
            summary[(variant, nm)] = sm
    L += ["## Notes", "", "- A has the same fills as B (touch); A-vs-B is a pure fee difference. A also gives the all-taker order a "
          "fill at the zone price with no spread crossing, so it is generous to all-taker.",
          "- D charges ADV_BP on the fill price of every limit fill (entry; target when it is the exit). Sources in the module header.",
          "- fee R / net R are means per FILLED trade; 'net R per signal' counts unfilled signals as 0 R."]
    MARK = "<!-- TABLES -->"
    head = ""
    if OUT.exists():   # keep the hand-written verdict above the marker; regenerate only the tables
        old = OUT.read_text(encoding="utf-8")
        head = old.split(MARK)[0] if MARK in old else ""
    OUT.write_text(head + MARK + "\n" + "\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, flush=True)
    return summary


if __name__ == "__main__":
    main()
