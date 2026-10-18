"""Carry basis modeling with real spot-vs-perp basis mark-to-market, fees, and margin.

Research study: carry_basis_2026-10-18
Evaluates:
  - CARRY_always unlevered (1x)
  - CARRY_switch unlevered (1x)
  - CARRY_always 3x margin with liquidation check at 1h lows
Windows:
  - DEV: 2021-01-01 to 2023-07-01
  - VAL: 2023-07-01 to 2024-07-01
  - HOLD: 2024-07-01 to 2025-07-01
  - Sealed window 2025-07+ is NOT read.
"""
import sys, os, glob, datetime as dt
from pathlib import Path
import numpy as np

# Add published_strats to path for run_pub reuse
PUB_DIR = Path(__file__).resolve().parents[1] / "published_strats_2026-10-13"
if str(PUB_DIR) not in sys.path:
    sys.path.insert(0, str(PUB_DIR))

import run_pub as R

DUMPS = os.environ.get("MTS_DUMPS", r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest")
SYMBOL = "BTCUSDT"
FEE = 0.0010  # 0.10% per side per leg (SOURCED: run_pub.py:15)
HOUR = 3600_000
DAY = 24 * HOUR


def compute_carry_pnl_daily(spot_ret, perp_ret, funding):
    """Daily mark-to-market gross return for long spot + short perp carry.

    Formula (OURS):
      spot price return: spot_ret
      perp short price return: -perp_ret
      basis price change PnL: spot_ret - perp_ret
      funding received: +funding
      gross daily PnL: (spot_ret - perp_ret) + funding
    """
    return (spot_ret - perp_ret) + funding


def simulate_carry(spot_ret, perp_ret, funding, fee_per_leg=FEE, mode="always_on", pos_signal=None):
    """Simulate carry strategy with transaction fees.

    fee_per_leg: fee per leg (0.10% default).
    mode:
      - 'always_on': 2 legs fee at day 0 entry, held continuously, 0 exit fee.
      - 'round_trip': 2 legs fee at day 0 entry, 2 legs fee at final day exit.
      - 'switched': 2 legs on every 0->1 transition, 2 legs on every 1->0 transition (4 legs round-trip).
    """
    n = len(spot_ret)
    gross_ret = compute_carry_pnl_daily(spot_ret, perp_ret, funding)

    if mode == "always_on":
        pos = np.ones(n)
        net_ret = gross_ret.copy()
        # 2 legs at entry (buy spot + sell perp)
        net_ret[0] -= 2 * fee_per_leg
    elif mode == "round_trip":
        pos = np.ones(n)
        net_ret = gross_ret.copy()
        # 2 legs entry at day 0, 2 legs exit at day n-1
        net_ret[0] -= 2 * fee_per_leg
        net_ret[-1] -= 2 * fee_per_leg
    elif mode == "switched":
        assert pos_signal is not None, "pos_signal required for switched mode"
        pos = pos_signal.copy()
        prev = np.r_[0.0, pos[:-1]]
        # 2 legs on entry (pos - prev > 0), 2 legs on exit (prev - pos > 0)
        # That is 2 * fee * abs(pos - prev)
        trans_fee = 2 * fee_per_leg * np.abs(pos - prev)
        net_ret = pos * gross_ret - trans_fee
    else:
        raise ValueError(f"Unknown mode: {mode}")

    cum_ret = np.cumprod(1 + net_ret) - 1.0
    return dict(gross_ret=gross_ret, net_ret=net_ret, cum_ret=cum_ret, pos=pos)


def _loadcsv(f, cols):
    with open(f) as fh:
        first = fh.readline()
    skip = 0 if first[:1].isdigit() or first[:1] == "-" else 1
    a = np.loadtxt(f, delimiter=",", skiprows=skip, usecols=cols)
    if len(a) > 0 and a[0, 0] > 1e14:  # Handle 2025 microsecond timestamps
        a[:, 0] //= 1000
    return a


def load_spot_1d():
    files = sorted(glob.glob(f"{DUMPS}/spot_1d/klines/{SYMBOL}-1d-*.csv"))
    rows = [_loadcsv(f, (0, 1, 2, 3, 4, 5)).reshape(-1, 6) for f in files]
    a = np.vstack(rows)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    diffs = np.diff(a[:, 0])
    assert (diffs == DAY).all(), "gap in spot 1d data"
    return a


def load_spot_1h():
    files = sorted(glob.glob(f"{DUMPS}/spot_1h/klines/{SYMBOL}-1h-*.csv"))
    rows = [_loadcsv(f, (0, 1, 2, 3, 4, 5)).reshape(-1, 6) for f in files]
    a = np.vstack(rows)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    return a


def check_liquidation_1h(a_spot_1h, a_perp_1h, days, lev=3.0, spot_maint_ratio=1.10, perp_mmr=0.005):
    """Check intraday liquidation at 1h lows/highs for a 3x margin position.

    At 3x leverage (3:1 leverage):
      Assets = 3E, Borrowed Debt = 2E.
      Spot liquidation: Assets / Debt <= 1.10 => S_1h_low / S_open <= 1.10 * 2 / 3 = 0.7333 (-26.67% drop).
      Perp liquidation: Equity <= MMR * Notional => P_1h_high / P_open >= 1 + (1/3 - 3*0.005)/1 = 1.3283 (+32.83% rise).
    Returns list of liquidation events: dict(timestamp, day_idx, type, drop_or_rise, time_utc).
    """
    events = []
    for idx, d in enumerate(days):
        p_mask = (a_perp_1h[:, 0] >= d) & (a_perp_1h[:, 0] < d + DAY)
        s_mask = (a_spot_1h[:, 0] >= d) & (a_spot_1h[:, 0] < d + DAY)
        if not p_mask.any() or not s_mask.any():
            continue

        s_bars = a_spot_1h[s_mask]
        p_bars = a_perp_1h[p_mask]

        s_open = s_bars[0, 1]
        p_open = p_bars[0, 1]

        # Spot 1h low check
        s_min_idx = np.argmin(s_bars[:, 3])
        s_min_low = s_bars[s_min_idx, 3]
        s_drop = (s_min_low - s_open) / s_open
        spot_thresh = spot_maint_ratio * (lev - 1) / lev - 1.0  # -0.2667 at 3x

        if s_drop <= spot_thresh:
            t_event = s_bars[s_min_idx, 0]
            dt_utc = dt.datetime.fromtimestamp(t_event / 1000, dt.timezone.utc)
            events.append(dict(
                type="spot_margin_liquidation",
                timestamp=t_event,
                day_idx=idx,
                metric=s_drop,
                threshold=spot_thresh,
                dt_utc=str(dt_utc)
            ))

        # Perp 1h high check
        p_max_idx = np.argmax(p_bars[:, 2])
        p_max_high = p_bars[p_max_idx, 2]
        p_rise = (p_max_high - p_open) / p_open
        perp_thresh = (1.0 / lev - perp_mmr)  # +0.3283 at 3x

        if p_rise >= perp_thresh:
            t_event = p_bars[p_max_idx, 0]
            dt_utc = dt.datetime.fromtimestamp(t_event / 1000, dt.timezone.utc)
            events.append(dict(
                type="perp_short_liquidation",
                timestamp=t_event,
                day_idx=idx,
                metric=p_rise,
                threshold=perp_thresh,
                dt_utc=str(dt_utc)
            ))

    return events


def worst_30d_annualized(ret_series):
    """Worst 30-day rolling return annualized."""
    if len(ret_series) < 30:
        return np.nan
    roll = np.convolve(ret_series, np.ones(30) / 30, mode="valid") * 365 * 100
    return float(roll.min())


def run_all_analysis():
    print("Loading data...")
    a_perp = R.load_1h()
    f = R.load_funding()
    b_perp = R.Bars(R.resample(a_perp, "1d"), f, "1d")

    a_spot_1d = load_spot_1d()
    a_spot_1h = load_spot_1h()

    # Filter perp to strictly before sealed window 2025-07-01
    valid_mask = b_perp.t < R.SEALED_FROM
    perp_t = b_perp.t[valid_mask]
    perp_c = b_perp.c[valid_mask]
    perp_o = b_perp.o[valid_mask]
    fund = b_perp.fund[valid_mask]

    # Align spot 1d to perp 1d
    spot_dict = {int(row[0]): (row[1], row[4]) for row in a_spot_1d}
    spot_c = np.array([spot_dict[int(t)][1] for t in perp_t])
    spot_o = np.array([spot_dict[int(t)][0] for t in perp_t])

    # Price change returns: mark-to-market close-to-close
    spot_ret = np.r_[0.0, spot_c[1:] / spot_c[:-1] - 1]
    perp_ret = np.r_[0.0, perp_c[1:] / perp_c[:-1] - 1]

    # Trailing 3-day funding signal for CARRY_switch (SOURCED: run_pub.py:334-338)
    f3 = np.convolve(fund, np.ones(3), mode="full")[:len(fund)]
    pos_switch_sig = np.where(f3 > 0, 1.0, 0.0)
    pos_switch_sig[:3] = 0
    held_switch = np.r_[0.0, pos_switch_sig[:-1]]

    # Simulations
    res_always = simulate_carry(spot_ret, perp_ret, fund, fee_per_leg=FEE, mode="always_on")
    res_switch = simulate_carry(spot_ret, perp_ret, fund, fee_per_leg=FEE, mode="switched", pos_signal=held_switch)

    # 3x margin simulation
    res_always_3x = res_always["net_ret"] * 3.0

    # Liquidation check on 1h bars
    days = perp_t
    liq_events = check_liquidation_1h(a_spot_1h, a_perp, days, lev=3.0)

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY ACROSS WINDOWS")
    print("=" * 80)

    results = {}
    windows = ("DEV", "VAL", "HOLD")

    # Baseline numbers from supp_carry.txt (SOURCED: published_strats_2026-10-13/supp_carry.txt:1-3)
    supp_baseline = {
        "DEV": {"net_ann": 15.4, "sharpe": 10.70, "mdd": -0.4, "fund_ann": 15.4, "worst_30d": -3.9},
        "VAL": {"net_ann": 12.1, "sharpe": 18.65, "mdd": -0.0, "fund_ann": 12.1, "worst_30d": 0.7},
        "HOLD": {"net_ann": 6.2, "sharpe": 18.40, "mdd": -0.1, "fund_ann": 6.2, "worst_30d": -0.9},
    }

    for w in windows:
        lo, hi = R.WIN[w]
        m = (perp_t >= lo) & (perp_t < hi)
        n_bars = int(m.sum())

        st_always = R.stats(res_always["net_ret"][m], 365)
        w30_always = worst_30d_annualized(res_always["net_ret"][m])

        st_switch = R.stats(res_switch["net_ret"][m], 365)
        w30_switch = worst_30d_annualized(res_switch["net_ret"][m])

        st_3x = R.stats(res_always_3x[m], 365)
        w30_3x = worst_30d_annualized(res_always_3x[m])

        basis_ann = float((spot_ret - perp_ret)[m].mean() * 365 * 100)
        fund_ann = float(fund[m].mean() * 365 * 100)

        # Check if liquidation falls in this window
        w_liqs = [e for e in liq_events if lo <= e["timestamp"] < hi]

        results[w] = {
            "n": n_bars,
            "basis_ann": basis_ann,
            "fund_ann": fund_ann,
            "always": {**st_always, "worst_30d": w30_always},
            "switch": {**st_switch, "worst_30d": w30_switch},
            "margin3x": {**st_3x, "worst_30d": w30_3x, "liq_count": len(w_liqs), "liqs": w_liqs},
            "supp": supp_baseline[w]
        }

        print(f"\n--- WINDOW: {w} ({n_bars} days) ---")
        print(f"  Funding alone (supp_carry.txt): ann={supp_baseline[w]['net_ann']:6.2f}%  sharpe={supp_baseline[w]['sharpe']:5.2f}  mdd={supp_baseline[w]['mdd']:5.2f}%")
        print(f"  Spot-perp basis drag:           ann={basis_ann:6.2f}%/yr")
        print(f"  CARRY_always (unlevered):       ann={st_always['ann']:6.2f}%  sharpe={st_always['sharpe']:5.2f}  mdd={st_always['mdd']*100:5.2f}%  worst_30d={w30_always:6.2f}%")
        print(f"  CARRY_switch (unlevered):       ann={st_switch['ann']:6.2f}%  sharpe={st_switch['sharpe']:5.2f}  mdd={st_switch['mdd']*100:5.2f}%  worst_30d={w30_switch:6.2f}%")
        print(f"  CARRY_always (3x margin):       ann={st_3x['ann']:6.2f}%  sharpe={st_3x['sharpe']:5.2f}  mdd={st_3x['mdd']*100:5.2f}%  liq_events={len(w_liqs)}")
        if w_liqs:
            for lq in w_liqs:
                print(f"    * LIQUIDATION: {lq['type']} at {lq['dt_utc']} (move={lq['metric']*100:.2f}%)")

    # Haircut Sensitivity Table
    print("\n" + "=" * 80)
    print("HAIRCUT SENSITIVITY TABLE (DEV Window)")
    print("=" * 80)
    fee_levels = [0.0000, 0.0002, 0.0005, 0.0010, 0.0015, 0.0020]
    dev_lo, dev_hi = R.WIN["DEV"]
    dev_m = (perp_t >= dev_lo) & (perp_t < dev_hi)

    print(f"{'Fee/leg':10s} | {'CARRY_always Ann%':18s} | {'CARRY_switch Ann%':18s} | {'Switched Trades':15s}")
    haircut_rows = []
    for f_lvl in fee_levels:
        sim_al = simulate_carry(spot_ret, perp_ret, fund, fee_per_leg=f_lvl, mode="always_on")
        sim_sw = simulate_carry(spot_ret, perp_ret, fund, fee_per_leg=f_lvl, mode="switched", pos_signal=held_switch)
        ann_al = R.stats(sim_al["net_ret"][dev_m], 365)["ann"]
        ann_sw = R.stats(sim_sw["net_ret"][dev_m], 365)["ann"]
        n_trades = R.trades_of(held_switch[dev_m])
        haircut_rows.append((f_lvl, ann_al, ann_sw, n_trades))
        print(f"{f_lvl*100:6.2f}%    | {ann_al:18.2f}% | {ann_sw:18.2f}% | {n_trades:15d}")

    # Basis drag sensitivity
    print("\nBasis move required to wipe out DEV funding carry:")
    dev_fund_ann = results["DEV"]["fund_ann"]
    dev_basis_ann = results["DEV"]["basis_ann"]
    print(f"  DEV Funding rate: +{dev_fund_ann:.2f}%/yr")
    print(f"  DEV Real Basis:   {dev_basis_ann:.2f}%/yr")
    print(f"  Net before fee:   {dev_fund_ann + dev_basis_ann:.2f}%/yr")
    print(f"  Adverse basis drag required to kill unlevered carry: -{(dev_fund_ann + dev_basis_ann):.2f}%/yr")

    return results, haircut_rows, liq_events


if __name__ == "__main__":
    run_all_analysis()
