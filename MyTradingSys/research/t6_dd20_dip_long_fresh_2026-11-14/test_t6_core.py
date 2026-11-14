"""Synthetic-bar tests for T6 (core + stats). No data cache, no files outside the repo. Run: pytest test_t6_core.py"""
import sys
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t6_core as core  # noqa: E402
import t6_stats as st  # noqa: E402

DAY = 86400000
RT_HAND = 12 / 10000.0          # hand number: 12 bp round trip


def epoch_day(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


MON0 = epoch_day(2023, 10, 16)  # a Monday
assert (MON0 + 3) % 7 == 0


def rows_from(closes, start=MON0, r=0.01, over=None):
    """Daily rows: open = previous close, high/low = +-r around the body; over = {i: (o,h,l,c)}."""
    over = over or {}
    out = []
    for i, c in enumerate(closes):
        o = closes[i - 1] if i else c
        row = (o, max(o, c) * (1 + r), min(o, c) * (1 - r), c)
        row = over.get(i, row)
        out.append(((start + i) * DAY,) + tuple(row))
    return np.array(out, float)


def mk(closes, start=MON0, ended=False, over=None, r=0.01, name="SYN"):
    rows = rows_from(closes, start, r, over)
    last = rows[-1, 0]
    pull = last + DAY if not ended else last + 400 * DAY
    return core.Coin(name, rows, pull_ms=int(pull))


def weekly_levels(levels):
    return [lv for lv in levels for _ in range(7)]


# ------------------------------------------------------------------ look-ahead
def _walk(seed, n=420):
    rs = np.random.RandomState(seed)
    return 100 * np.exp(np.cumsum(rs.normal(0, 0.04, n)))


def test_signal_and_bull_flag_use_only_bars_through_signal_week():
    closes = _walk(5, 7 * 60 + 1)
    full = mk(closes)
    evs = core.events_dd20(full)
    assert len(evs) >= 3, "walk must produce events for the test to mean something"
    for ev in evs:
        w, d0 = ev["w"], ev["d0"]
        trunc = mk(closes[:d0 + 1])                      # bars through the entry-day bar only
        same = [e for e in core.events_dd20(trunc) if e["w"] <= w]
        assert same == [e for e in evs if e["w"] <= w]
        # rewrite everything from the entry day on: signal and bull flag must not move
        rs = np.random.RandomState(w)
        alt = closes.copy()
        alt[d0:] = alt[d0:] * np.exp(rs.normal(0, 0.3, len(alt) - d0))
        mut = mk(alt)
        same2 = [e for e in core.events_dd20(mut) if e["w"] <= w]
        assert same2 == [e for e in evs if e["w"] <= w]


def test_phase_same_day_read_is_caught_and_tag_uses_entry_day_row():
    days = [dt.date(2022, 1, 3) + dt.timedelta(days=i) for i in range(10)]
    ds = [d.strftime("%Y-%m-%d") for d in days]
    closes = {d: 100.0 + i for i, d in enumerate(ds)}
    clean = {ds[i]: ("L%d" % i, "C%d" % i, closes[ds[i - 1]]) for i in range(1, 10)}      # close_used = prior close
    leaky = {ds[i]: ("L%d" % i, "C%d" % i, closes[ds[i]]) for i in range(1, 10)}          # same-day close
    assert core.phase_leak_count(clean, closes) == (9, 0)
    c, leaks = core.phase_leak_count(leaky, closes)
    assert c == 9 and leaks == 9
    ems = int(dt.datetime(2022, 1, 7, tzinfo=dt.timezone.utc).timestamp() * 1000)
    assert core.phase_tag(clean, ems) == ("L4", "C4")                                     # row of the entry day itself
    other = dict(clean)
    other[ds[5]] = ("X", "X", 0.0)                                                        # a later row must not matter
    assert core.phase_tag(other, ems) == ("L4", "C4")
    assert core.phase_tag(clean, 0) == ("NA", "NA")


# ------------------------------------------------------------------ stops, gaps, ties
def _flat(n=100, p=100.0):
    return [p] * n


def test_stop_row_hand_numbers_flat_world():
    # every bar 100 / 101 / 99 / 100: TR = 2 each day, ATR14 = 2 exactly, stop = 100 - 2.5*2 = 95
    c = mk(_flat())
    t = core.trade_at(c, 70)
    assert abs(t["stop"] - 95.0) < 1e-9
    assert abs(t["risk_unit"] - 0.05) < 1e-12
    assert t["stop_reason"] == "TIME" and abs(t["stop_gross"]) < 1e-12


def test_stop_wins_ties_on_low_equal_stop():
    c = mk(_flat(), over={73: (100, 101, 95.0, 100)})        # low exactly at the stop, close back at 100
    t = core.trade_at(c, 70)
    assert t["stop_reason"] == "STOP" and t["stop_exit_ts"] == int(c.ms[73])
    assert abs(t["stop_exit_px"] - 95.0) < 1e-12
    sg = 95.0 / 100.0 - 1.0
    sf, _ = core.funding_cost(None, int(c.ms[70]), int(c.ms[73]) + DAY)
    assert abs(t["stop_net"] - (sg - RT_HAND - sf)) < 1e-12
    assert abs(t["stop_R"] - t["stop_net"] / 0.05) < 1e-9
    assert t["exit_reason"] == "TIME"                        # primary row has no stop


def test_stop_on_entry_day_and_gap_fill_at_open():
    c = mk(_flat(), over={70: (100, 101, 95.0, 100)})
    t = core.trade_at(c, 70)
    assert t["stop_reason"] == "STOP" and t["stop_exit_ts"] == int(c.ms[70])
    c2 = mk(_flat(), over={75: (93.0, 94.0, 90.0, 92.0)})     # opens below the stop: fills at the open, not the stop
    t2 = core.trade_at(c2, 70)
    assert t2["stop_reason"] == "STOP-GAP" and abs(t2["stop_exit_px"] - 93.0) < 1e-12
    assert abs(t2["stop_gross"] - (-0.07)) < 1e-12


def test_stop_skipped_when_atr_undefined_or_stop_nonpositive():
    c = mk(_flat(60))
    t = core.trade_at(c, 7)                                   # d0-1 = 6 < 13: ATR undefined
    assert t["stop_reason"] == "" and t["stop_R"] != t["stop_R"]
    assert t["gross_R"] != t["gross_R"]                        # R columns excluded too
    wild = [100.0] * 50
    c2 = mk(wild, r=0.9)                                      # range so wide that entry - 2.5 ATR <= 0
    t2 = core.trade_at(c2, 20)
    assert t2["stop_reason"] == "" and t2["net"] == t2["net"]


# ------------------------------------------------------------------ fee, funding
def _fee_world(over_extra=None):
    cl = _flat()
    cl[83] = 110.0                                            # exit day = 70 + 13
    over = {83: (100, 111, 99, 110)}
    over.update(over_extra or {})
    return mk(cl, over=over)


def test_fee_and_flat_funding_hand_numbers():
    c = _fee_world()
    t = core.trade_at(c, 70)
    assert abs(t["gross"] - 0.10) < 1e-12
    assert abs(core.ROUND_TRIP - RT_HAND) < 1e-15
    assert t["funding_rule"] == "FLAT" and abs(t["funding"] - 14 * 3 * 0.0001) < 1e-12     # 42 bp
    assert abs(t["net_nofund"] - (0.10 - RT_HAND)) < 1e-12
    assert abs(t["net"] - (0.10 - RT_HAND - 0.0042)) < 1e-12
    assert abs(t["gross_R"] - 0.10 / 0.05) < 1e-9 and abs(t["net_R"] - t["net"] / 0.05) < 1e-9


def _prints(entry_ms, end_ms, base, first_off=-1, last_off=2):
    ts, rate = [], []
    t = entry_ms + first_off * 8 * 3600000
    while t <= end_ms + last_off * 8 * 3600000:
        ts.append(t)
        rate.append(base)
        t += 8 * 3600000
    ts, rate = np.array(ts, float), np.array(rate, float)
    return ts, rate


def test_real_funding_window_boundaries_and_sign():
    c = _fee_world()
    entry_ms, end_ms = int(c.ms[70]), int(c.ms[83]) + DAY
    ts, rate = _prints(entry_ms, end_ms, 0.0001)
    rate[ts == entry_ms] = 0.0003                              # entry-instant print: excluded
    rate[ts == end_ms] = 0.0002                                # end-of-exit-day print: included
    rate[ts == end_ms + 8 * 3600000] = 0.0007                  # after the exit: excluded
    ts[ts == entry_ms + 8 * 3600000] += 1                      # millisecond jitter is rounded to the second
    t = core.trade_at(c, 70, core.Funding(ts, rate))
    assert t["funding_rule"] == "REAL"
    assert abs(t["funding"] - (41 * 0.0001 + 0.0002)) < 1e-12  # 42 prints in (entry, end]
    assert abs(t["net"] - (0.10 - RT_HAND - 0.0043)) < 1e-12
    credit = core.trade_at(c, 70, core.Funding(ts, -np.abs(rate)))
    assert credit["funding"] < 0 and credit["net"] > t["net_nofund"]


def test_funding_flat_fallback_when_cache_does_not_cover_window():
    c = _fee_world()
    entry_ms, end_ms = int(c.ms[70]), int(c.ms[83]) + DAY
    ts, rate = _prints(entry_ms, end_ms, 0.0005, first_off=2, last_off=2)       # first print after entry
    assert core.trade_at(c, 70, core.Funding(ts, rate))["funding_rule"] == "FLAT"
    ts, rate = _prints(entry_ms, end_ms, 0.0005, first_off=-1, last_off=-1)     # last print before the exit
    t = core.trade_at(c, 70, core.Funding(ts, rate))
    assert t["funding_rule"] == "FLAT" and abs(t["funding"] - 0.0042) < 1e-12
    assert core.trade_at(c, 70, None)["funding_rule"] == "FLAT"


def test_data_end_skip_for_live_coin_and_delist_exit_for_ended_coin():
    cl = _flat(80)
    live = mk(cl)
    assert core.trade_at(live, 70) is None                     # window runs past the data of a coin that still trades
    gone = mk(cl, ended=True)
    t = core.trade_at(gone, 70)
    assert t["exit_reason"] == "DELIST-EXIT" and t["exit_ts"] == int(gone.ms[79])
    assert abs(t["funding"] - 10 * 3 * 0.0001) < 1e-12         # 10 days held, flat rule


# ------------------------------------------------------------------ cooldown / lockout / overlap
def _decline():
    lv = [100.0] * 8 + [75.0 * 0.97 ** (k) for k in range(0, 24)]
    return weekly_levels(lv) + [lv[-1]]


def test_cooldown_gap_of_exactly_8_weeks_allowed_nothing_in_between():
    c = mk(_decline())
    evs = core.events_dd20(c)
    assert [e["w"] for e in evs] == [8, 16, 24]
    assert min(e["w"] for e in evs) >= 8                       # warm-up lockout
    trades = core.event_trades(c)
    assert len(trades) == 3
    for a, b in zip(trades, trades[1:]):
        assert b["entry_ts"] - a["entry_ts"] >= 56 * DAY and a["exit_ts"] < b["entry_ts"]   # no overlap


def test_no_event_before_week_8_even_if_falling_from_the_start():
    lv = [100 * 0.75 ** k for k in range(12)]
    c = mk(weekly_levels(lv) + [lv[-1]])
    assert all(e["w"] >= 8 for e in core.events_dd20(c))


def test_threshold_boundary_is_inclusive_at_080():
    lv = [100.0] * 8 + [80.0, 80.001]
    c = mk(weekly_levels(lv) + [80.001])
    assert [e["w"] for e in core.events_dd20(c)] == [8]


# ------------------------------------------------------------------ split by signal bar
def test_split_is_by_entry_instant_not_exit():
    assert core.split_of(int(dt.datetime(2023, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc).timestamp() * 1000)) == "DEV"
    assert core.split_of(int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)) == "VAL"
    lv = [100.0] * 9 + [70.0]
    cl = weekly_levels(lv) + [70.0] * 30
    a = mk(cl, start=epoch_day(2023, 10, 16))                  # entry Monday 2023-12-25, exit runs into 2024
    b = mk(cl, start=epoch_day(2023, 10, 23))                  # entry Monday 2024-01-01
    ta, tb = core.event_trades(a)[0], core.event_trades(b)[0]
    assert (ta["split"], tb["split"]) == ("DEV", "VAL")
    assert core.iso_week_of(ta["entry_ts"]) == "2023-W52" and tb["iso_week"] == "2024-W01"


def test_primary_row_matches_independent_entry_exit():
    cl = _decline()
    c = mk(cl)
    t = core.event_trades(c)[0]
    d0 = 7 * 9
    prior_close = cl[d0 - 1]
    fwd_close = cl[d0 + 13]
    assert t["entry_px"] == prior_close and t["exit_px"] == fwd_close
    assert t["bull"] == "NA"


# ------------------------------------------------------------------ planted edge (stats code)
def _world(seed, drift, ncoin=14, ndays=900, p_sig=0.15):
    """Random walks, random Monday signals; a planted drift is added to the 14 bars after each signal."""
    rs = np.random.RandomState(seed)
    start = epoch_day(2023, 3, 6)
    coins, funds_events = [], []
    for k in range(ncoin):
        r = rs.normal(0, 0.03, ndays)
        sig = []
        for d0 in range(70, ndays - 15, 7):
            if rs.rand() < p_sig:
                sig.append(d0)
                r[(np.arange(ndays) >= d0) & (np.arange(ndays) < d0 + 14)] += drift
        px = 100 * np.exp(np.cumsum(r))
        # entry open = previous close; signals live on Mondays because d0 % 7 == 0 and start is a Monday
        coins.append(mk(list(px), start=start, name="S%d" % k))
        funds_events.append(sig)
    return coins, funds_events


def _trades_pool(coins, sigs):
    trades, pool = [], []
    for c, sig in zip(coins, sigs):
        for d0 in sig:
            t = core.trade_at(c, d0)
            if t:
                trades.append(core.tag_row(c, t))
        pool.extend(core.all_monday_trades(c))
    return trades, pool


def test_planted_edge_is_found_by_the_stats_code():
    coins, sigs = _world(11, 0.01)
    trades, pool = _trades_pool(coins, sigs)
    S, tabs = st.run_stats(trades, pool, nboot=500, ndraw=300)
    assert S["n_val"] > 100 and S["val_net"]["mean"] > 0.08
    assert S["val_boot_net"]["ci_low"] > 0.04 and S["val_boot_net"]["p_le0"] < 0.01
    b = S["val_boot_net"]
    assert b["ci_low"] < b["mean"] - 0.005 < b["mean"] + 0.005 < b["ci_high"]      # a real interval, not a point
    p = S["placebo_net"]
    assert p["excess"] > 0.05 and p["real_mean"] >= p["p975"] and p["p"] < 0.05
    assert S["bars"]["2_val_ci"] and S["bars"]["4_placebo"] and S["bars"]["5_ex_best5"] and S["bars"]["7_top_coin"]
    assert "by year" in tabs


def test_no_drift_world_reads_about_zero():
    coins, sigs = _world(11, 0.0)
    trades, pool = _trades_pool(coins, sigs)
    S, _ = st.run_stats(trades, pool, nboot=500, ndraw=300)
    assert abs(S["val_net"]["mean"]) < 0.03
    assert S["val_boot_net"]["ci_low"] < 0.0
    p = S["placebo_net"]
    assert abs(p["excess"]) < 0.03 and p["p"] > 0.01
    assert not S["bars"]["2_val_ci"]


# ------------------------------------------------------------------ small stats units, hand numbers
def _r(coin, week, net, split="VAL", bull="BEAR"):
    return dict(coin=coin, iso_week=week, net=net, split=split, bull=bull, delist=False, entry_ts=hash(week) % 1000)


def test_ex_best_weeks_and_top_coin_removal_hand_numbers():
    rows = [_r("A", "2024-W01", 0.10), _r("B", "2024-W01", 0.10), _r("A", "2024-W02", 0.05),
            _r("C", "2024-W03", -0.02), _r("C", "2024-W04", -0.04), _r("B", "2024-W05", 0.01)]
    e = st.ex_best_weeks(rows, k=2)
    assert e["dropped"] == ["2024-W01", "2024-W02"] and e["n"] == 3
    assert abs(e["mean"] - (-0.02 - 0.04 + 0.01) / 3) < 1e-12
    t = st.top_coin_removal(rows, k=2)
    assert t[0]["removed"] == ["A"] and abs(t[0]["mean"] - (0.10 - 0.02 - 0.04 + 0.01) / 4) < 1e-12
    assert t[1]["removed"] == ["A", "B"] and abs(t[1]["mean"] - (-0.06 / 2)) < 1e-12


def test_cluster_bootstrap_uses_week_sums_over_trade_counts():
    rows = [_r("A", "2024-W01", 0.10), _r("B", "2024-W01", 0.20), _r("A", "2024-W02", -0.05)]
    b = st.cluster_bootstrap(rows, nboot=200)
    assert b["weeks"] == 2 and b["n"] == 3 and abs(b["mean"] - 0.25 / 3) < 1e-12
    assert b["ci_low"] >= -0.05 - 1e-12 and b["ci_high"] <= 0.15 + 1e-12


def test_basket_baseline_excludes_delist_and_averages_per_monday():
    pool = [dict(split="VAL", delist=False, entry_ts=1, net=0.10), dict(split="VAL", delist=False, entry_ts=1, net=0.00),
            dict(split="VAL", delist=True, entry_ts=1, net=-0.9), dict(split="VAL", delist=False, entry_ts=2, net=0.01),
            dict(split="DEV", delist=False, entry_ts=3, net=0.5)]
    b = st.basket_baseline(pool, "VAL")
    assert b["mondays"] == 2 and abs(b["mean"] - (0.05 + 0.01) / 2) < 1e-12
