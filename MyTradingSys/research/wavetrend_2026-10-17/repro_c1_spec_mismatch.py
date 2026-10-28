"""Synthetic proof that current C1 does not require confirmed WT pivots."""
import numpy as np

from count_events import ev_C, pivots


def main():
    n = 30
    highs = np.zeros(n)
    lows = np.zeros(n)
    highs[10], highs[20] = 10.0, 12.0  # confirmed price highs at p=10 and p=20 (k=2)
    wt1 = np.zeros(n)
    wt1[8:13] = [8.0, 9.0, 10.0, 11.0, 12.0]  # increasing through first price pivot
    wt1[18:23] = [10.0, 9.0, 8.0, 7.0, 6.0]  # decreasing through second price pivot

    c1, _ = ev_C({"H": highs, "L": lows}, wt1, k=2, G=20, L=53)
    price_pivots = pivots(highs, 2, True)
    wt_pivots = pivots(wt1, 2, True)
    print("price pivots:", price_pivots)
    print("WT pivots:", wt_pivots)
    print("C1 events:", c1)
    assert (10, 12) in price_pivots and (20, 22) in price_pivots
    assert not any(p in (10, 20) for p, _ in wt_pivots)
    assert c1 == [(22, 1)]  # C1 fires by comparing WT values at price pivots alone


if __name__ == "__main__":
    main()
