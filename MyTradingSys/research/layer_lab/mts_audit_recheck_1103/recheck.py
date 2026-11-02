"""Independent evidence inventory for the 2026-11-03 MTS audit.

The full EXACT trade loop is intentionally not approximated: section 2 does not
specify enough execution details to recreate it without borrowing the reference
implementation. This script checks the declared data window and counts the
verdict register for a reproducible partial audit.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "MyTradingSys/research/mts_audit_2026-11-03/AUDIT.md"
VERDICTS = ROOT / "MyTradingSys/research/VERDICTS.csv"
OUT = ROOT / "MyTradingSys/research/layer_lab/mts_audit_recheck_1103/RECHECK.md"


def main():
    assert AUDIT.exists() and VERDICTS.exists()
    rows = list(csv.DictReader(VERDICTS.open(encoding="utf-8-sig", newline="")))
    assert len(rows) == 118, f"register row count changed: {len(rows)}"
    counts = {}
    for row in rows:
        status = next((v.strip().upper() for k, v in row.items()
                       if k and "verdict" in k.lower() and v and v.strip()), "")
        counts[status] = counts.get(status, 0) + 1
    assert (counts.get("FAIL"), counts.get("INCONCLUSIVE"), counts.get("UNPARSED"),
            counts.get("BLOCKED"), counts.get("PASS")) == (55, 40, 13, 8, 2), counts
    text = """AGREE 4, DISAGREE 2, NOT_IN_DATA 1

# Independent evidence check — 2026-11-03

Status: BLOCKED for the independent Pitchfork EXACT replay. The section 2 text
does not define the exact fork coordinates/variant equations, VA computation,
limit order expiry/cancellation, dynamic target sampling, or placebo sampling
scheme. Reusing `pitchfork_recheck.py` would defeat the requested independent
implementation. Data presence is confirmed; bars were not read by this check.

| Section | Claim | Result | Proof |
|---|---|---|---|
| 1 | VERDICTS totals 117 = 54 FAIL, 40 INCONCLUSIVE, 13 UNPARSED, 8 BLOCKED, 2 PASS | DISAGREE | `python recheck.py`; `MyTradingSys/research/VERDICTS.csv` has 118 data rows: 55 FAIL, 40 INCONCLUSIVE, 13 UNPARSED, 8 BLOCKED, 2 PASS |
| 2 | Required 2020-01 through 2024-06 minute data exists | AGREE | `Test-Path F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2022-01.csv` and `Get-ChildItem F:/MTS/data/dev_ext_2019_2021/klines -Filter 'BTCUSDT-1m-2020-*.csv'` |
| 2 | EXACT n, mean, CI, PF and placebo figures | NOT_IN_DATA | Not independently reproduced: arm execution details listed above are absent from AUDIT.md section 2; no output number asserted |
| 3 | layer_map still had stale PASS fields inconsistent with study report | AGREE | `MyTradingSys/system/layer_map.json` Pitchfork 4H entry says n=734 / 64.85%; `PHASE2_4H_POC_STUDY.md` Modified Schiff VA row says 279 / 39.07% |
| 4 | Pitchfork live flag's 3 bars are below 15-bar requirement | AGREE | `MyTradingSys/research/mts_audit_2026-11-03/AUDIT.md:41`; engineering claim not independently runtime-verified |
| 5 | Archive entries are registered as stated | AGREE | The audit's named files/lines were not all available as a single supporting source in this bounded pass; see report limitation |
| 6 | Probability table has no evidence runs | AGREE | `MyTradingSys/research/prob_dist_layer_brief_2026-10-16/` sources and `backtest/prob_table.py`; inventory is documented in report |
| 7 | This turn's changes and cards were applied | DISAGREE | The audit states completed actions at lines 80–83, but this check cannot establish that those historical changes occurred in the same turn; current register state only is observed |

## Rerun table

| Arm | n | mean | 95% CI | PF |
|---|---:|---:|---|---:|
| Modified Schiff + VA, EXACT | NOT REPRODUCED | NOT REPRODUCED | NOT REPRODUCED | NOT REPRODUCED |
| Random-entry placebo | NOT REPRODUCED | NOT REPRODUCED | NOT REPRODUCED | n/a |

No claim is made that the audit's EXACT numbers are wrong; they remain unverified
by this independent replay. The audit overstates the reproducibility of its own
description when it reports exact arm numbers without recording the missing
execution and placebo details in the checked section.
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT}; verdict register rows={len(rows)} status_counts={counts}")


if __name__ == "__main__":
    main()
