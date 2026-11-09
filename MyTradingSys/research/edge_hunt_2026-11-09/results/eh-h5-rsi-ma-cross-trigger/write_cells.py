"""DEV-only: writes cells.csv (summary cells, no raw bars) and prints the DEV regime mix. Run after rsi_ma_cross.py dev."""
import csv
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rsi_ma_cross as M  # noqa: E402

FIELDS = ["cell", "split", "n", "hit", "mean_gross_r", "mean_fee_r", "mean_funding_r", "mean_net_r", "se_cluster_week",
          "ci95_lo", "ci95_hi", "mde_80", "p_one_sided", "holm_p_m15", "clusters", "dev_screen"]


def row(name, split, s):
    if s.get("n", 0) == 0:
        return {"cell": name, "split": split, "n": 0}
    return {"cell": name, "split": split, "n": s["n"], "hit": round(s["hit"], 4), "mean_gross_r": round(s["gross"], 4),
            "mean_fee_r": round(s["fee"], 4), "mean_funding_r": round(s["fund"], 4), "mean_net_r": round(s["net"], 4),
            "se_cluster_week": round(s["se"], 4), "ci95_lo": round(s["ci_lo"], 4), "ci95_hi": round(s["ci_hi"], 4),
            "mde_80": round(s["mde"], 4), "p_one_sided": round(s["p_one"], 4), "holm_p_m15": round(s["holm15"], 4),
            "clusters": s["clusters"], "dev_screen": "PASS" if M.dev_screen_pass(s) else "not passed"}


def main():
    tr, dropped = M.run(["BTCUSDT", "ETHUSDT"], ["short", "long"], M._ms(2017, 8, 1), M.DEV_END_MS)
    rows = [row("T06 pooled both sides both symbols", "DEV", M.stats(tr))]
    for side in ("short", "long"):
        rows.append(row("T06 side=" + side, "DEV", M.stats([t for t in tr if t["side"] == side])))
    for sym in ("BTCUSDT", "ETHUSDT"):
        rows.append(row("sym=" + sym, "DEV", M.stats([t for t in tr if t["symbol"] == sym])))
    for side in ("short", "long"):
        rows.append(row("EXPL daily-RSI filter on, side=" + side, "DEV",
                        M.stats([t for t in tr if t["side"] == side and t["daily_ok"]])))
        rows.append(row("EXPL daily-RSI filter off, side=" + side, "DEV",
                        M.stats([t for t in tr if t["side"] == side and not t["daily_ok"]])))
    for y in sorted({t["year"] for t in tr}):
        rows.append(row("year=%d" % y, "DEV", M.stats([t for t in tr if t["year"] == y])))
    out = HERE / "cells.csv"
    with open(out, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    print("wrote", out, "rows", len(rows), "dropped", dropped)
    # regime mix over DEV weeks (BTC daily/weekly/monthly; research_kit-style tag)
    btc = M.load_spot_4h("BTCUSDT", end_ms=M.DEV_END_MS)
    M.dev_only(btc)
    starts = []
    t = M._iso_week_start(btc[0]["t"] // M.D1 * M.D1) + 7 * M.D1
    while t + 7 * M.D1 <= M.DEV_END_MS:
        starts.append(t)
        t += 7 * M.D1
    tags = M.regime_tags(btc, starts)
    mix = {k: tags.count(k) for k in ("bull", "bear", "range", None)}
    print("Regime mix: DEV weeks", len(tags), mix)


if __name__ == "__main__":
    main()
