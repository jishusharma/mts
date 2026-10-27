"""T06 tables: costs.csv (inventory, lead L3), breakeven.csv, fee_to_stop.csv. Run from the worktree root.
Reads only repo files and out/funding_rerun.json (made by t06_funding.py). Writes next to this script.
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t06_scan  # noqa: E402

ROOT = t06_scan.ROOT
IMPORTS_FEES = re.compile(r"^\s*(?:from\s+[\w.]*\bfees\s+import|import\s+[\w.]*\bfees\b|from\s+[\w.]*\s+import\s+[^#\n]*\bfees\b|.*\b_fees\s*=)", re.M)


def classify(path, name, val, text):
    t = text.lower()
    n = name.lower()
    try:
        v = float(val)
    except ValueError:
        v = float("nan")
    if "usd" in n:
        unit = "usd"
    elif "pts" in n or "tick" in n:
        unit = "points"
    elif "bps" in n or n.endswith("_bp") or "_bp_" in n or "bp" in n.split("_"):
        unit = "bp"
    elif "pct" in n or "percent" in n or (name == "(literal)" and "%" in t):
        unit = "pct"
    elif name.startswith("(literal)") or 0 <= abs(v) < 0.01:
        unit = "fraction"
    else:
        unit = "other"
    if "fund" in n and "skipped" not in n and "bps" not in n:
        side = "per_8h"
    elif re.search(r"(^|_)rt(_|$)|round[ _]?trip|cost_taker|cost_maker|_rt\b", n) or "round trip" in t or "round-trip" in t or re.search(r"\bfee_rt\b|\bslip_rt\b", t):
        side = "round_trip"
    elif "side" in n or "per side" in t or "per leg" in t or "/side" in t or "per fill" in t or n in ("fee", "slip", "taker", "maker", "taker_fee", "maker_fee", "deribit_taker", "deribit_maker", "binance_taker", "binance_maker"):
        side = "per_side"
    else:
        side = "n/a"
    if "maker" in n and "taker" in n:
        mt = "both"
    elif "maker" in n:
        mt = "maker"
    elif "taker" in n:
        mt = "taker"
    elif "taker" in t and "maker" in t:
        mt = "both"
    elif "taker" in t:
        mt = "taker"
    elif "maker" in t:
        mt = "maker"
    elif any(k in n for k in ("fee", "cost", "fee_slip")):
        mt = "both"
    else:
        mt = "n/a"
    parts = path.split("/")
    study = parts[2] if len(parts) > 3 else parts[-1]
    what = "fund" if "fund" in n else "slip" if "slip" in n else "fee" if "fee" in n or "taker" in n or "maker" in n else "cost"
    return unit, side, mt, f"{what} in {study}"


def inventory():
    cache = {}
    rows = []
    for p, ln, name, val, text in t06_scan.scan():
        if p not in cache:
            cache[p] = bool(IMPORTS_FEES.search((ROOT / p).read_text(encoding="utf-8", errors="replace")))
        unit, side, mt, applies = classify(p, name, val, text)
        kind = "assign" if name != "(literal)" else "literal_in_text"
        rows.append(dict(file=p, line=ln, name=name, value=val, unit=unit, side=side, maker_taker=mt, applies_to=applies,
                         imports_fees=int(cache[p]), kind=kind, text=text.replace(",", ";")[:120]))
    return rows


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- break-even
FEE_REGIMES = {"A_all_taker_deribit_10bp": 10.0, "B_maker_in_time_exit_taker_5bp": 5.0, "C_all_maker_deribit_0bp": 0.0, "D_binance_maker_4bp": 4.0}


def breakeven():
    j = json.load(open(HERE / "out" / "funding_rerun.json"))
    rows = []
    g = j["gross"]["arms"]
    for a in ("T", "notF", "C"):
        rows.append(("gross_effect_screen", f"arm {a} d=1 h=60", g[a]["n_base"], g[a]["mean_real"], "measured, real funding"))
    primary = {"mal_bb_mid_engulf_2026-10-16": 2, "opr_bb_mtf_center_2026-10-16": 2, "opr_preopen_tops_2026-10-16": 2,
               "opr_weekly_low_round_sweep_2026-10-16": 2}
    for st, k in primary.items():
        for nm, r in j["g5"][st]["real"]["arms"][:k]:
            rows.append((st, nm, r["n"], r["mean"], "measured, real funding"))
    # brief section 1b only (not rerun): gross derived from the quoted net
    rows.append(("layer_lab/candle_close_2026-10-14", "best of 126 arms (net -4.68 bp at 14 bp => gross +9.32 bp)", "n/a", 0.0932, "derived from AUDIT_BRIEF 1b row 9"))
    rows.append(("mfe_exit_2026-10-13", "turn_of_candle gross about +0.3 bp", "n/a", 0.003, "AUDIT_BRIEF 1b row 14"))
    out = []
    for study, arm, n, gross, src in rows:
        r = dict(study=study, arm=arm, n=n, gross_pct=round(gross, 5), source=src, charged_rt_pct=0.14,
                 breakeven_rt_cost_bp=round(gross * 100, 2), headroom_vs_charged_bp=round(gross * 100 - 14.0, 2))
        for k, fee in FEE_REGIMES.items():
            r["breakeven_slip_per_fill_bp_" + k] = round((gross * 100 - fee) / 2.0, 2)
        out.append(r)
    return out


# ---------------------------------------------------------------- fee to stop
def fee_to_stop():
    cfg = json.load(open(ROOT / "MyTradingSys" / "execution" / "auto_trader_config.json", encoding="utf-8"))
    fee_rt, fee_rt_slip = 0.0010, 0.0014          # 2 x Deribit taker (fees.py:23); + 2 x 2 bp slippage (screen.py:30 convention)
    layer_stop_pct = 1.0                          # auto_trader.py:72 DEFAULTS layers.stop_pct (NO-SOURCE, SAMPLING)
    rows = []

    def add(layer, size, ml, stop_pct, note):
        stop_usd = size * stop_pct / 100.0
        rows.append(dict(layer=layer, size_usd=size, max_loss_usd=ml, stop_pct=stop_pct, stop_usd=round(stop_usd, 4),
                         fee_rt_usd=round(size * fee_rt, 4), fee_to_stop_taker=round(fee_rt / (stop_pct / 100.0), 4),
                         fee_to_stop_with_slip=round(fee_rt_slip / (stop_pct / 100.0), 4), fee_to_maxloss=round(size * fee_rt / ml, 4),
                         cap_pct_of_size=round(ml / size * 100, 2), note=note))

    lay = cfg.get("layers", {})
    add("layers (default)", lay.get("size_usd"), lay.get("max_loss_usd"), layer_stop_pct, "fixed bracket stop_pct 1.0 (auto_trader.py:72)")
    for pre, v in cfg["size_overrides"].items():
        add(pre, v["size_usd"], v["max_loss_usd"], layer_stop_pct, "fixed bracket stop_pct 1.0")
    tom = cfg["tom"]
    for sp in (0.044, 0.07, 0.13, 0.333, 0.5, 1.0):
        add(f"tom (stop {sp}% of price)", tom["size_usd"], tom["max_loss_usd"], sp,
            "stop comes from the alert; max_fee_to_stop %s rejects fee/stop > cut (needs stop >= %.3f %%)" % (tom.get("max_fee_to_stop"), fee_rt / tom.get("max_fee_to_stop", 1) * 100))
    return rows


def main():
    inv = inventory()
    cols = ["file", "line", "name", "value", "unit", "side", "maker_taker", "applies_to", "imports_fees", "kind", "text"]
    write_csv(HERE / "costs.csv", inv, cols)
    be = breakeven()
    write_csv(HERE / "breakeven.csv", be, list(be[0].keys()))
    fs = fee_to_stop()
    write_csv(HERE / "fee_to_stop.csv", fs, list(fs[0].keys()))
    print("costs.csv rows", len(inv), "files", len({r["file"] for r in inv}), "imports_fees files",
          len({r["file"] for r in inv if r["imports_fees"]}))
    print("breakeven rows", len(be), "fee_to_stop rows", len(fs))
    from collections import Counter
    print(Counter((r["unit"], r["side"]) for r in inv).most_common(12))


if __name__ == "__main__":
    main()
