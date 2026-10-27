import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stability as S

D = S.DAY_MS
Y22 = 1_650_000_000_000          # 2022-04-15
Y23 = 1_690_000_000_000          # 2023-07-22


def planted():
    """20 trades on 20 distinct days. Day 0 holds +20.0 of a +22.0 positive total (91%); days 1-4 are +0.5;
    days 5-19 are -1.0. Hand sums: all = 20 + 4*0.5 - 15 = 7.0; top-5 days are days 0-4, so the rest are 15 x -1.0."""
    rows = [(Y22, 1, 20.0)]
    rows += [(Y22 + i * D, -1, 0.5) for i in range(1, 5)]
    rows += [(Y23 + i * D, 1, -1.0) for i in range(5, 20)]
    return rows


def test_top5_removed_mean_negative():
    c = S.cuts(planted())
    assert c["all"]["n"] == 20 and abs(c["all"]["sum"] - 7.0) < 1e-9
    assert c["top5_removed"]["n"] == 15 and abs(c["top5_removed"]["mean"] + 1.0) < 1e-9
    assert S.sign_changes(c)


def test_year_and_side_splits_sum_to_total():
    c = S.cuts(planted())
    assert abs(sum(v["sum"] for v in c["year"].values()) - c["all"]["sum"]) < 1e-9
    assert abs(c["long"]["sum"] + c["short"]["sum"] - c["all"]["sum"]) < 1e-9
    assert abs(sum(v["sum"] for v in c["year_side"].values()) - c["all"]["sum"]) < 1e-9
    assert c["year"][2022]["n"] == 5 and c["year"][2023]["n"] == 15


def test_same_day_trades_removed_together():
    rows = [(Y22, 1, 5.0), (Y22 + 1000, 1, 5.0)] + [(Y22 + i * D, 1, -1.0) for i in range(1, 6)]
    assert S.drop_top_days(rows, 1) == rows[2:]
