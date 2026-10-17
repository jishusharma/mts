"""Evidence for bug B187: DEV data is too short for the PRE_REG_V2 power gate.

Reads the committed COUNT.txt and COUNTS_DEV_EXT.md, recomputes the gate arithmetic from
PRE_REG_V2 item 2 and the calendar ceilings from every pre-2024-07-01 history that exists.
Counts and arithmetic only: no outcome column is read, no bar at or after 2024-07-01 is loaded.
Run: python bug_b187_evidence.py  (writes bug_b187_evidence.txt next to this file)
"""
import re
from datetime import date
from pathlib import Path
from statistics import NormalDist

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "bug_b187_evidence.txt"
lines = []


def say(s=""):
    lines.append(s)


count_txt = (HERE / "COUNT.txt").read_text(encoding="utf-8")
dev_days = int(re.search(r"DEV (\d+) days", count_txt).group(1))
feasible_days = int(re.search(r"FEASIBLE subset.*?days (\d+)", count_txt).group(1))
n_t = int(re.search(r"FEASIBLE subset \(stop >= 0.40 %\): n = ([\d,]+)", count_txt).group(1).replace(",", ""))

ext_txt = (ROOT / "MyTradingSys/research/context_factors_2026-10-16/COUNTS_DEV_EXT.md").read_text(encoding="utf-8")
ext_days_decisions = int(re.search(r"of which (\d+) in DEV_EXT", ext_txt).group(1))

sd, cost, plausible = 1.46, 0.179, 0.30   # PRE_REG_V2 item 2 (sd, cost SOURCED from COUNT.txt; plausible OURS)
say("== B187 evidence: PRE_REG_V2 item-2 power gate ==")
say(f"source COUNT.txt: DEV days={dev_days}, feasible T days={feasible_days}, feasible n_T={n_t}")
say(f"inputs: sd={sd} R, cost={cost} R, plausible gross effect={plausible} R (OURS)")
for m in (42, 62):
    z = NormalDist().inv_cdf(1 - 0.05 / (2 * m))
    mde = (z + NormalDist().inv_cdf(0.8)) * sd / feasible_days ** 0.5
    need = ((z + NormalDist().inv_cdf(0.8)) * sd / (plausible - cost)) ** 2
    say(f"m={m}: z_holm={z:.3f} MDE={mde:.3f} R MDE+cost={mde + cost:.3f} R "
        f"days needed={need:,.0f} vs available {feasible_days} -> "
        f"{'BLOCK' if mde + cost > plausible or feasible_days < need else 'FREEZE OK'}")

say()
say("== calendar ceilings (pre-2024-07-01 history, this study's sealed cut) ==")
cal_dev = (date(2024, 6, 30) - date(2020, 1, 1)).days + 1
cal_spot = (date(2024, 6, 30) - date(2017, 8, 17)).days + 1
ratio = feasible_days / dev_days
say(f"DEV window 2022-01-01..2024-06-30: {dev_days} days (file says so)")
say(f"calendar 2020-01-01..2024-06-30: {cal_dev} days; est feasible at DEV ratio {ratio:.3f}: {cal_dev * ratio:,.0f}")
say(f"calendar 2017-08-17..2024-06-30: {cal_spot} days; est feasible: {cal_spot * ratio:,.0f}")
say(f"needed (m=42, plausible 0.30 R): 2,427 -> from 2020 no pre-2024 history reaches it even at 100 % feasible ({cal_dev} < 2,427)")
say(f"from 2017 (Binance spot era, assumed start) it needs {2427 / cal_spot:.1%} of calendar days feasible; the DEV ratio gives {cal_spot * ratio:,.0f}")
say(f"DEV_EXT 2020-2021 decision days in context study: {ext_days_decisions} (COUNTS_DEV_EXT.md)")
say(f"pit study with DEV_EXT added (estimate): {feasible_days} + {ext_days_decisions * ratio:,.0f} = "
    f"{feasible_days + ext_days_decisions * ratio:,.0f} days, still < 2,427")

say()
say("== where the data is on this machine ==")
ext = Path("F:/MTS/data/dev_ext_2019_2021")
say(f"F:/MTS/data/dev_ext_2019_2021 exists: {ext.exists()}  (dev_ext.py EXT_DIR points here)")
raw = Path("F:/MTS/data/binance_raw")
say(f"F:/MTS/data/binance_raw contents: {sorted(p.name for p in raw.iterdir()) if raw.exists() else 'missing'}")
say(f"F:/MTS/data/tom_raw/klines files: {len(list((Path('F:/MTS/data/tom_raw/klines')).glob('*.csv')))}")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print("\n".join(lines))
