"""T4 report numbers: reads trades*.csv + summary.json (outputs of step A/C) and the BTC miner cache, writes report_numbers.json.
No rule, no bar: descriptive tables for RESULT.md only."""
import json
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t4_core as C  # noqa: E402
import t4_stats as S  # noqa: E402

MINER = r"F:\MTS\data_cache\binance\combo-edge-miner-1114"


def row(d):
    if not len(d):
        return dict(n=0)
    ci = S.week_bootstrap(d.R, d.entry_week)
    return dict(n=int(len(d)), weeks=int(d.entry_week.nunique()), win=float((d.R > 0).mean()),
                gross_R=float((d.gross / d.risk).mean()), fee_R=float((d.cost / d.risk).mean()),
                funding_R=float((d.funding / d.risk).mean()), net_R=float(d.R.mean()), sd_R=float(d.R.std()),
                ci_lo=ci["lo"], ci_hi=ci["hi"], p=ci["p"], hold_days=float(d.hold_days.mean()),
                R6=float(d.R6.mean()) if "R6" in d else None)


def main():
    tr = pd.read_csv(os.path.join(HERE, "trades.csv"))
    ctl = pd.read_csv(os.path.join(HERE, "trades_control.csv"))
    old = pd.read_csv(os.path.join(HERE, "trades_old20.csv"))
    out = {}
    for kind in ("RIDE", "T3R"):
        k = tr[tr.kind == kind]
        out[kind] = dict(DEV=row(k[k.split == "DEV"]), VAL=row(k[k.split == "VAL"]), POOLED=row(k))
        kc = ctl[ctl.kind == kind]
        out[kind]["CONTROL_DEV"] = row(kc[kc.split == "DEV"])
        out[kind]["CONTROL_VAL"] = row(kc[kc.split == "VAL"])
        ko = old[old.kind == kind]
        out[kind]["OLD20_DEV"] = row(ko[ko.split == "DEV"])
        out[kind]["OLD20_VAL"] = row(ko[ko.split == "VAL"])
        both = pd.concat([k, ko])
        out[kind]["OLD20_PLUS_FRESH_VAL"] = row(both[both.split == "VAL"])
    # regime mix
    btc = C.load_bars(os.path.join(MINER, "spot_1d", "BTCUSDT.csv"), "1d")
    table = C.phase_table(btc["ts"], btc["c"])
    last = int(btc["ts"][-1] // C.DAY)
    mix = {}
    for name, lo, hi in (("DEV", C.START_DAY, C.DEV_END_DAY), ("VAL", C.VAL_START_DAY, last)):
        lab = C.phase_for_days(table, np.arange(lo, hi + 1))
        days = {C.PHASES[i]: int((lab == i).sum()) for i in range(6)}
        days["none"] = int(np.isnan(lab).sum())
        sig = tr[(tr.kind == "RIDE") & (tr.split == name)].phase.value_counts().to_dict()
        cyc = tr[(tr.kind == "RIDE") & (tr.split == name)].brain_cycle.value_counts().to_dict()
        ctl_sig = ctl[(ctl.kind == "RIDE") & (ctl.split == name)].phase.value_counts().to_dict()
        old_sig = old[(old.kind == "RIDE") & (old.split == name)].phase.value_counts().to_dict()
        mix[name] = dict(days=days, ndays=int(hi - lo + 1), fresh_signals=sig, cycle_signals=cyc, control_signals=ctl_sig, old20_signals=old_sig)
    out["regime_mix"] = mix
    out["last_signals"] = dict(
        fresh_last_signal=str(tr.signal_utc.max()), control_last_signal=str(ctl.signal_utc.max()),
        old20_last_signal=str(old.signal_utc.max()), btc_last_close_day=int(last))
    # by phase / year pooled DEV+VAL RIDE, small
    r = tr[tr.kind == "RIDE"]
    out["pooled_by_phase"] = {p: row(r[r.phase == p]) for p in sorted(r.phase.unique())}
    # win/loss shape
    out["ride_val_shape"] = dict(stop_share=float((r[r.split == "VAL"].exit_reason == "STOP").mean()),
                                 best_R=float(r[r.split == "VAL"].R.max()), q90=float(np.sort(r[r.split == "VAL"].R.to_numpy())[int(0.9 * (len(r[r.split == "VAL"]) - 1))]),
                                 median=float(r[r.split == "VAL"].R.median()),
                                 top5_trades_sum=float(r[r.split == "VAL"].R.nlargest(5).sum()), val_sum=float(r[r.split == "VAL"].R.sum()))
    with open(os.path.join(HERE, "report_numbers.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print("ok")


if __name__ == "__main__":
    C.lower_priority()
    main()
