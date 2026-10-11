"""
MyTradingSys/backtest/bigtrade/capture.py - score any layer's fire list against the big-move ground truth (backtest A, PLAN section 3).

Inputs
  fires_*.csv   in F:/MTS/data/bigtrade/fires/ (PLAN section 5): layer, key, tf, side, t_fire_ms (close of the bar that fired), price, params_id,
                params_json, code_commit. Optional columns: stop_dist_atr (stop distance in ATR of the fire's TF), atr_kind (wilder|sma, default wilder),
                fee_R, fee_dominated (used as given when present).
  legs_<TF>.csv + labels_<TF>.csv  written by bigmoves.py.

One output row per layer x key x tf x side x fire_set x (r, k). fire_set "all" = every fire; "ok" = fires not fee-dominated (only emitted for a
group that has at least one fee-dominated fire). Definitions:
  legs        same-side legs flagged in (r, k) (hindsight zigzag legs, see bigmoves.py).
  EARLY/MID/LATE  a same-side fire at time t falls in [start, start+25% dur] / (25%, 50%] / (50%, end]. Recall X = share of legs with >= 1 fire in X
              (buckets are not exclusive across legs: a leg can have an EARLY and a LATE fire). recall_catch = share with an EARLY or MID fire.
              LATE is reported but is NOT a capture.
  median_lead_bars   over captured legs: bars from the first EARLY/MID fire to the end of the leg (how much of the move was still ahead).
  median_delay_bars  over captured legs: bars from the leg start to that first fire.
  hit_H       share of fires whose forward MFE over H bars (entry = next open, unit = ATR at the fire bar) is >= k ATR, same side. base_H = the same
              share over ALL bars of the TF inside the layer's own fire span (first to last fire), lift_H = hit_rate / base_rate, z_H = binomial z of
              the hit rate against the base rate (fires cluster in time, so z overstates significance). med_mae_H = median adverse excursion before
              the MFE among the hits (ATR).
  fee_R       round-trip fee / stop distance = 2 x DERIBIT_TAKER x price / (stop_dist_atr x ATR); fee_dominated when fee_R > 1 (stop under the round-trip
              fee, F-BT-01). Blank when the fire file carries no stop_dist_atr / fee_R.
A fire time that is not exactly a bar close is mapped to the last bar closed at or before it and counted as misaligned (never moved forward).
"""
import csv
import datetime
import glob
import math
import sys
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from MyTradingSys.backtest import fees as _fees  # noqa: E402
from MyTradingSys.backtest.bigtrade import bigmoves as bm  # noqa: E402

FIRES_DIR = bm.DATA_DIR / "fires"
RESEARCH_DIR = _REPO / "MyTradingSys/research/bigtrade_2026-10-09"
RT_FEE = 2 * _fees.DERIBIT_TAKER  # both legs taker (FORMULAS.md section 17): 0.001 of price
EARLY_FRAC, MID_FRAC = 0.25, 0.50


# ----------------------------------------------------------------------------------------------- fires

def _f(row, name):
    v = row.get(name)
    if v is None or str(v).strip() == "":
        return float("nan")
    try:
        return float(v)
    except ValueError:
        return float("nan")


def read_fires(paths):
    """Parse fires_*.csv rows into dicts. Rows without a usable side or time are counted, not dropped silently."""
    out, bad = [], 0
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                side = (row.get("side") or "").strip().lower()
                tf = (row.get("tf") or "").strip()
                try:
                    t = int(float(row["t_fire_ms"]))
                except (KeyError, ValueError, TypeError):
                    bad += 1
                    continue
                if side not in ("long", "short") or not tf:
                    bad += 1
                    continue
                dom = (row.get("fee_dominated") or "").strip().lower()
                out.append({
                    "layer": row.get("layer", ""), "key": row.get("key", ""), "tf": tf, "side": side, "t": t, "price": _f(row, "price"),
                    "stop_dist_atr": _f(row, "stop_dist_atr"), "fee_R": _f(row, "fee_R"),
                    "fee_dominated": (dom in ("1", "true", "yes")) if dom != "" else None,
                    "atr_kind": (row.get("atr_kind") or "wilder").strip().lower(), "file": Path(p).name,
                })
    return out, bad


def group_fires(fires):
    groups = {}
    for f in fires:
        groups.setdefault((f["layer"], f["key"], f["tf"], f["side"]), []).append(f)
    return groups


def map_fires_to_bars(fires, t_close, tf_ms):
    """Per fire: bar index j of the last bar closed at or before t. Returns (j array of unique sorted bars, row->j list, stats)."""
    t = np.array([f["t"] for f in fires], dtype=np.int64)
    j = np.searchsorted(t_close, t, side="right") - 1
    before = j < 0
    after = (~before) & (t - t_close[np.clip(j, 0, len(t_close) - 1)] >= tf_ms)
    keep = ~(before | after)
    aligned = keep & (t_close[np.clip(j, 0, len(t_close) - 1)] == t)
    return j, keep, {"n_rows": int(len(t)), "n_outside_data": int((~keep).sum()), "n_misaligned": int((keep & ~aligned).sum())}


def fee_info(fires, j, labels):
    """Per fire: fee_R (nan when unknown) and fee_dominated (bool). File-given values win; otherwise computed from stop_dist_atr x ATR."""
    n = len(fires)
    fee_r = np.full(n, np.nan)
    dom = np.zeros(n, dtype=bool)
    for i, f in enumerate(fires):
        jj = int(j[i])
        if math.isfinite(f["fee_R"]):
            fee_r[i] = f["fee_R"]
        elif math.isfinite(f["stop_dist_atr"]) and f["stop_dist_atr"] > 0:
            a = labels["atr_sma" if f["atr_kind"] == "sma" else "atr_wilder"][jj]
            price = f["price"] if math.isfinite(f["price"]) else labels["close"][jj]
            if math.isfinite(a) and a > 0:
                fee_r[i] = RT_FEE * price / (f["stop_dist_atr"] * a)
        if f["fee_dominated"] is not None:
            dom[i] = f["fee_dominated"]
        elif math.isfinite(fee_r[i]):
            dom[i] = fee_r[i] > 1.0
    return fee_r, dom


# ----------------------------------------------------------------------------------------------- scoring

def leg_capture(fire_t, ts, te):
    """fire_t: sorted unique int64 fire times (bar closes). ts, te: leg start/end times of same-side legs.
    Returns bool arrays early/mid/late and t_first (first fire in [ts, ts + 50% dur], -1 if none)."""
    fire_t = np.asarray(fire_t, dtype=np.int64)
    ts = np.asarray(ts, dtype=np.int64)
    te = np.asarray(te, dtype=np.int64)
    d = (te - ts).astype(float)
    lo = np.searchsorted(fire_t, ts, side="left")  # first fire >= ts
    c_e = np.searchsorted(fire_t, ts + d * EARLY_FRAC, side="right")  # fires <= ts + 25%
    c_m = np.searchsorted(fire_t, ts + d * MID_FRAC, side="right")
    c_l = np.searchsorted(fire_t, te, side="right")
    early, mid, late = c_e > lo, c_m > c_e, c_l > c_m
    t_first = np.full(len(ts), -1, dtype=np.int64)
    if len(fire_t):
        idx = np.clip(lo, 0, len(fire_t) - 1)
        ok = (lo < len(fire_t)) & (fire_t[idx] <= ts + d * MID_FRAC)
        t_first[ok] = fire_t[idx][ok]
    return {"early": early, "mid": mid, "late": late, "t_first": t_first}


def leg_metrics(fire_t, legs, r, k, side_sign, tf_ms):
    m = (legs["flags"][(r, k)] == 1) & (legs["side"] == side_sign)
    ts, te = legs["t_start"][m], legs["t_end"][m]
    n = int(m.sum())
    out = {"n_legs": n, "n_early": 0, "n_mid": 0, "n_late": 0, "recall_early": float("nan"), "recall_mid": float("nan"),
           "recall_late": float("nan"), "recall_catch": float("nan"), "median_lead_bars": float("nan"), "median_delay_bars": float("nan")}
    if n == 0:
        return out
    cap = leg_capture(fire_t, ts, te)
    catch = cap["early"] | cap["mid"]
    out.update({"n_early": int(cap["early"].sum()), "n_mid": int(cap["mid"].sum()), "n_late": int(cap["late"].sum()),
                "recall_early": float(cap["early"].mean()), "recall_mid": float(cap["mid"].mean()), "recall_late": float(cap["late"].mean()),
                "recall_catch": float(catch.mean())})
    if catch.any():
        tf_ = cap["t_first"][catch]
        out["median_lead_bars"] = float(np.median((te[catch] - tf_) / tf_ms))
        out["median_delay_bars"] = float(np.median((tf_ - ts[catch]) / tf_ms))
    return out


def event_metrics(j, labels, side_name, H, k, span_ms):
    """Forward-event hit rate of fires (bar indices j) vs the base rate over all bars inside span_ms=(first, last) fire time."""
    mfe = labels["mfe_%s_%d" % (side_name, H)]
    mae = labels["mae_%s_%d" % (side_name, H)]
    v = mfe[j]
    valid = np.isfinite(v)
    hit = valid & (v >= k)
    n_valid, hits = int(valid.sum()), int(hit.sum())
    t_close = labels["t_close_ms"]
    bm_mask = (t_close >= span_ms[0]) & (t_close <= span_ms[1]) & np.isfinite(mfe)
    base = float((mfe[bm_mask] >= k).mean()) if bm_mask.any() else float("nan")
    rate = hits / n_valid if n_valid else float("nan")
    z = float("nan")
    if n_valid and 0.0 < base < 1.0:
        z = (rate - base) / math.sqrt(base * (1.0 - base) / n_valid)
    return {"n_valid": n_valid, "hits": hits, "hit_rate": rate, "base_rate": base,
            "lift": (rate / base) if (base and base > 0 and n_valid) else float("nan"), "z": z,
            "med_mae": float(np.median(mae[j][hit])) if hits else float("nan")}


def score_group(key4, fires, legs, labels, r_list, k_list, h_list):
    """All rows for one (layer, key, tf, side) group. Returns (rows, info)."""
    layer, key, tf, side = key4
    tf_ms = bm.TF_MS[tf]
    t_close = labels["t_close_ms"]
    side_sign = 1 if side == "long" else -1
    j_all, keep, stat = map_fires_to_bars(fires, t_close, tf_ms)
    fires = [f for f, kp in zip(fires, keep) if kp]
    j_all = j_all[keep]
    fee_r, dom = fee_info(fires, j_all, labels)
    info = dict(stat, layer=layer, key=key, tf=tf, side=side, n_fire_rows=len(fires), n_fee_known=int(np.isfinite(fee_r).sum()),
                n_dominated=int(dom.sum()))
    sets = [("all", np.ones(len(fires), dtype=bool))]
    if dom.any():
        sets.append(("ok", ~dom))
    rows = []
    for set_name, sel in sets:
        j_sel = np.unique(j_all[sel])  # one fire per bar
        if len(j_sel) == 0:
            continue
        fire_t = t_close[j_sel]
        span = (int(fire_t[0]), int(fire_t[-1]))
        fr = fee_r[sel]
        fr = fr[np.isfinite(fr)]
        base_row = {"layer": layer, "key": key, "tf": tf, "side": side, "fire_set": set_name, "n_fires": int(len(j_sel)),
                    "n_fire_rows": int(sel.sum()), "fee_known": int(len(fr)), "fee_R_median": float(np.median(fr)) if len(fr) else float("nan"),
                    "fee_dominated_share": float((fr > 1.0).mean()) if len(fr) else float("nan"),
                    "span_from_ms": span[0], "span_to_ms": span[1]}
        ev = {(H, k): event_metrics(j_sel, labels, side, H, k, span) for H in h_list for k in k_list}
        for r in r_list:
            for k in k_list:
                row = dict(base_row, r=r, k=k)
                row.update(leg_metrics(fire_t, legs, r, k, side_sign, tf_ms))
                for H in h_list:
                    e = ev[(H, k)]
                    for name in ("n_valid", "hits", "hit_rate", "base_rate", "lift", "z", "med_mae"):
                        row["%s_%d" % (name, H)] = e[name]
                rows.append(row)
    return rows, info


def run_capture(fires, legs_by_tf, labels_by_tf, r_list=bm.R_LIST, k_list=bm.K_LIST, h_list=bm.H_LIST):
    """fires: parsed fire dicts. Returns (rows, infos, skipped) - skipped = groups whose tf has no ground truth loaded."""
    rows, infos, skipped = [], [], []
    for key4, fl in sorted(group_fires(fires).items()):
        tf = key4[2]
        if tf not in legs_by_tf or tf not in labels_by_tf:
            skipped.append({"layer": key4[0], "key": key4[1], "tf": tf, "side": key4[3], "n_fire_rows": len(fl)})
            continue
        r_, i_ = score_group(key4, fl, legs_by_tf[tf], labels_by_tf[tf], r_list, k_list, h_list)
        rows += r_
        infos.append(i_)
    return rows, infos, skipped


# ----------------------------------------------------------------------------------------------- output

COLS = ["layer", "key", "tf", "side", "fire_set", "r", "k", "n_legs", "n_early", "n_mid", "n_late", "recall_early", "recall_mid", "recall_late",
        "recall_catch", "median_lead_bars", "median_delay_bars", "n_fires", "n_fire_rows"]
COLS += ["%s_%d" % (n, H) for H in bm.H_LIST for n in ("n_valid", "hits", "hit_rate", "base_rate", "lift", "z", "med_mae")]
COLS += ["fee_known", "fee_R_median", "fee_dominated_share", "span_from_ms", "span_to_ms"]


def _fmt(v):
    if isinstance(v, (float, np.floating)):
        return "" if not math.isfinite(v) else "%.6g" % v
    return str(v)


def write_matrix_csv(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLS)
        for r in rows:
            w.writerow([_fmt(r.get(c, "")) for c in COLS])


def _p(v, nd=2):
    return "-" if (v is None or (isinstance(v, float) and not math.isfinite(v))) else ("%.*f" % (nd, v))


def render_md(rows, infos, skipped, meta, headline):
    L = []
    title = "CAPTURE MATRIX" + ("  -  SYNTHETIC FIXTURE, NOT LAYER OUTPUT" if meta.get("synthetic") else "")
    L.append("# %s" % title)
    L.append("")
    L.append("Generated %s by capture.py. Fire files: %s." % (meta["generated"], ", ".join(meta["fire_files"]) or "none"))
    if meta.get("synthetic"):
        L.append("The fires here are generated from the ground-truth legs themselves (oracle / random / anti-oracle) to exercise the tool. "
                 "They say nothing about any real layer.")
    L.append("Ground truth: bigmoves.py legs + labels, TFs %s, coverage %s." % (", ".join(meta["tfs"]), meta["coverage"]))
    if meta.get("n_unparsable"):
        L.append("%d fire rows were not scored because they carry no long/short side or no time (for the RSI event files these are the tradable=0 rows: "
                 "cross / support / rejection events with an empty side)." % meta["n_unparsable"])
    L.append("Settings: ATR(14) Wilder per TF; legs = ATR zigzag, r in %s (reversal), k in %s (leg size, ATR); H in %s bars; round-trip fee %.4f of price "
             "(2 x Deribit taker)." % (list(bm.R_LIST), list(bm.K_LIST), list(bm.H_LIST), RT_FEE))
    L.append("Columns: legs = same-side legs flagged (r,k); E/M/L = share of legs with a same-side fire in the first 25% / 25-50% / last 50% of the leg; "
             "catch = E or M; lead = median bars of leg still ahead at the first E/M fire; hitH = share of fires with forward MFE(H) >= k ATR; "
             "baseH = same share over all bars in the layer's fire span; lift = hit/base; feeDom = share of fires with stop < round-trip fee.")
    L.append("")
    for (r, k) in headline:
        L.append("## r=%s  k=%s" % (r, k))
        L.append("")
        L.append("| layer key | tf | side | set | legs | E | M | L | catch | lead | fires | hit24 | base24 | lift24 | hit96 | base96 | lift96 | feeDom |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for x in rows:
            if x["r"] != r or x["k"] != k:
                continue
            L.append("| %s | %s | %s | %s | %d | %s | %s | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |" % (
                x["key"] or x["layer"], x["tf"], x["side"], x["fire_set"], x["n_legs"], _p(x["recall_early"]), _p(x["recall_mid"]),
                _p(x["recall_late"]), _p(x["recall_catch"]), _p(x["median_lead_bars"], 1), x["n_fires"],
                _p(x.get("hit_rate_24")), _p(x.get("base_rate_24")), _p(x.get("lift_24")), _p(x.get("hit_rate_96")), _p(x.get("base_rate_96")), _p(x.get("lift_96")),
                _p(x["fee_dominated_share"])))
        L.append("")
    if skipped:
        L.append("## Groups with no ground truth (tf not built)")
        for s in skipped:
            L.append("- %s %s %s: %d fire rows" % (s["key"], s["tf"], s["side"], s["n_fire_rows"]))
        L.append("")
    mis = [i for i in infos if i["n_misaligned"] or i["n_outside_data"]]
    if mis:
        L.append("## Fire-time alignment")
        for i in mis:
            L.append("- %s %s %s: %d misaligned (mapped back to the last closed bar), %d outside the data span" % (
                i["key"], i["tf"], i["side"], i["n_misaligned"], i["n_outside_data"]))
        L.append("")
    L.append("Full matrix (all r, k, fire sets, counts, z, MAE): %s" % meta["csv_path"])
    L.append("")
    return "\n".join(L)


# ----------------------------------------------------------------------------------------------- synthetic fixture

def make_synthetic_fires(legs_by_tf, labels_by_tf, out_path, tfs=("1h",), r=1.5, k=3, seed=7):
    """Fixture only. Three pseudo-layers per TF built from the legs: ORACLE fires on the close of the pivot bar of every flagged leg (side = leg side),
    ANTI fires on the same bars with the opposite side, RANDOM fires on 2000 seeded random bars with a random side. NOT written to the fires dir."""
    rng = np.random.default_rng(seed)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["layer", "key", "tf", "side", "t_fire_ms", "price", "params_id", "params_json", "code_commit", "stop_dist_atr"])
        for tf in tfs:
            legs, lab = legs_by_tf[tf], labels_by_tf[tf]
            m = legs["flags"][(r, k)] == 1
            t_close = lab["t_close_ms"]
            close = lab["close"]
            for ts, sd in zip(legs["t_start"][m], legs["side"][m]):
                j = int(np.searchsorted(t_close, ts))
                for layer, side in (("synthetic_oracle", sd), ("synthetic_anti", -sd)):
                    w.writerow([layer, "synthetic:oracle_at_pivot:%s" % tf if layer == "synthetic_oracle" else "synthetic:anti_at_pivot:%s" % tf,
                                tf, "long" if side == 1 else "short", int(ts), "%.2f" % close[j], "synth", "{}", "synthetic", "1.0"])
            idx = rng.choice(len(t_close) - 1, size=min(2000, len(t_close) - 1), replace=False)
            for j in sorted(idx):
                side = "long" if rng.random() < 0.5 else "short"
                w.writerow(["synthetic_random", "synthetic:random:%s" % tf, tf, side, int(t_close[j]), "%.2f" % close[j], "synth", "{}", "synthetic",
                            "0.05" if rng.random() < 0.3 else "1.0"])


# ----------------------------------------------------------------------------------------------- driver

def load_ground_truth(data_dir, tfs):
    legs_by_tf, labels_by_tf = {}, {}
    for tf in tfs:
        lp, bp = Path(data_dir) / ("legs_%s.csv" % tf), Path(data_dir) / ("labels_%s.csv" % tf)
        if lp.exists() and bp.exists():
            legs_by_tf[tf] = bm.read_legs_csv(lp)
            labels_by_tf[tf] = bm.read_labels_csv(bp)
    return legs_by_tf, labels_by_tf


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Score layer fire lists against the big-move ground truth.")
    ap.add_argument("--fires-dir", default=str(FIRES_DIR))
    ap.add_argument("--data-dir", default=str(bm.DATA_DIR))
    ap.add_argument("--research-dir", default=str(RESEARCH_DIR))
    ap.add_argument("--out-prefix", default="CAPTURE_MATRIX")
    ap.add_argument("--tfs", default=",".join(bm.TFS))
    ap.add_argument("--synthetic", action="store_true", help="no real fires yet: build and score a labelled synthetic fixture instead")
    a = ap.parse_args(argv)
    tfs = a.tfs.split(",")
    legs_by_tf, labels_by_tf = load_ground_truth(a.data_dir, tfs)
    if not legs_by_tf:
        print("no legs_*/labels_* in", a.data_dir, "- run bigmoves.py first")
        return 2
    prefix = a.out_prefix
    fires_dir = Path(a.fires_dir)
    if a.synthetic:
        fires_dir = Path(a.data_dir) / "synthetic"
        make_synthetic_fires(legs_by_tf, labels_by_tf, fires_dir / "fires_synthetic.csv", tfs=[t for t in ("1h", "4h") if t in legs_by_tf])
        prefix = a.out_prefix + "_SYNTHETIC"
    paths = sorted(glob.glob(str(fires_dir / "fires_*.csv")))
    if not paths:
        print("no fires_*.csv in", fires_dir, "- nothing to score (use --synthetic for a fixture)")
        return 3
    fires, bad = read_fires(paths)
    rows, infos, skipped = run_capture(fires, legs_by_tf, labels_by_tf)
    data_dir = Path(a.data_dir)
    csv_path = data_dir / (prefix + ".csv")
    write_matrix_csv(csv_path, rows)
    any_tf = next(iter(labels_by_tf.values()))
    meta = {"generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "fire_files": [Path(p).name for p in paths], "tfs": list(legs_by_tf),
            "coverage": "%s .. %s UTC" % (bm.iso(int(any_tf["t_close_ms"][0])), bm.iso(int(any_tf["t_close_ms"][-1]))),
            "synthetic": a.synthetic, "csv_path": str(csv_path), "n_unparsable": bad}
    all_pairs = [(r, k) for r in bm.R_LIST for k in bm.K_LIST]
    (data_dir / (prefix + ".md")).write_text(render_md(rows, infos, skipped, meta, all_pairs), encoding="utf-8", newline="\n")
    rd = Path(a.research_dir)
    rd.mkdir(parents=True, exist_ok=True)
    (rd / (prefix + ".md")).write_text(render_md(rows, infos, skipped, meta, [(1.5, 3), (1.5, 5)]), encoding="utf-8", newline="\n")
    print("scored %d fire rows (%d unparsable) -> %d matrix rows; skipped groups: %d" % (len(fires), bad, len(rows), len(skipped)))
    print("wrote", csv_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
