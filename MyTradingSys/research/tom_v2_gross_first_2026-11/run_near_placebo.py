import sys
sys.dont_write_bytecode = True
"""tom-v2-gross-first-dev-ext runner: Tom return-to-value, near-band placebo (|d|<=1) primary, on DEV_EXT 2020-01..2021-12.
Pre-reg: PRE_REG.md in this folder. Usage: python run_near_placebo.py <dev_ext_dir> <out_dir>   (dev_ext_dir has klines/BTCUSDT-1m-YYYY-MM.csv)"""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backtest"))
import vp_pivot_probe as P  # noqa: E402
import vp_return_to_value as V  # noqa: E402

START = datetime(2020, 1, 1, tzinfo=timezone.utc)
END = datetime(2022, 1, 1, tzinfo=timezone.utc)          # DEV starts here: exclusive, asserted below


def main():
    ext, od = Path(sys.argv[1]), Path(sys.argv[2])
    P.KLINE_DIRS = (ext / "klines",)
    s_ms, e_ms = int(START.timestamp() * 1000), int(END.timestamp() * 1000)
    bars = P.load_bars(s_ms, e_ms)
    assert int(bars["t5"].max()) < e_ms and int(bars["t5"].min()) >= s_ms, "bars outside DEV_EXT"
    days, dropped = V.build_days(bars, s_ms, e_ms)
    res, dvals = V.study(days)
    fmt = lambda d: datetime.fromtimestamp(d * V.DAY_MS / 1000, timezone.utc).strftime("%Y-%m-%d")  # noqa: E731
    meta = {"first_day": fmt(days[0]["d"]), "last_day": fmt(days[-1]["d"]), "bars_meta": {k: v for k, v in bars["meta"].items() if k != "largest_gaps"},
            "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")}
    out = V.compute(res, days, dvals, dropped, meta)
    pr = V.near_band_primary(res, dvals)
    lo = pr["diff"]["ci"][0]
    out["primary_near"] = pr
    out["primary_verdict"] = "PASS" if (pr["diff"]["diff"] > 0 and lo > 0) else "FAIL"
    far = np.abs(dvals) >= 2
    out["far_descriptive"] = {"real": V.share(res["real"]["ret"], res["real"]["event"], far), "placebo": V.share(res["placebo"]["ret"], res["placebo"]["event"], far),
                              "diff": V.diff(res["real"]["ret"], res["real"]["event"], res["placebo"]["ret"], res["placebo"]["event"], far)}
    od.mkdir(parents=True, exist_ok=True)
    (od / "results.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("days_used", "dropped", "primary_near", "primary_verdict", "fire_rate")}, indent=1))
    (od / "full_report.md").write_text(V.render_md(out), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
