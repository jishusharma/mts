"""Tests for the T4 core and stats. SYNTHETIC bars only: nothing here reads the data cache or any path outside the repo.
Expected numbers come from FORMULAS.md worked examples or hand arithmetic, not from t4_core.py. Each test is meant to fail on a
deliberately broken version of the code (see mutation_check.txt)."""
import os
import sys
import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t4_core as C  # noqa: E402
import t4_stats as T  # noqa: E402
from MyTradingSys.backtest import fees  # noqa: E402

DAY, STEP = C.DAY, C.STEP


def ms(y, m, d, h=0):
    return (C.day_num(y, m, d) * 86400 + h * 3600) * 1000


# ---------------------------------------------------------------- indicators (hand numbers)
def test_atr_plain_sma_s12():
    atr = C.atr_sma([10, 11, 12, 11], [9, 9, 10, 9], [9.5, 10.5, 11.5, 10], 3)
    assert abs(atr[3] - 2.1666667) < 1e-6 and np.isnan(atr[2])


def test_pct_rank_excludes_current_and_needs_full_window():
    out = C.pct_rank([1, 2, 3, 2.5, 0.5], 3)
    assert np.isnan(out[2]) and abs(out[3] - 2 / 3) < 1e-12 and out[4] == 0.0
    out2 = C.pct_rank([1, 2, 3, np.nan, 5, 0.1], 3)      # strict: any NaN in the prior window gives NaN
    assert np.isnan(out2[3]) and np.isnan(out2[4]) and np.isnan(out2[5])
    out3 = C.pct_rank([np.nan, 1, 2, 3, 4, 0.5], 3)
    assert np.isnan(out3[3]) and abs(out3[4] - 1.0) < 1e-12 and out3[5] == 0.0


def _flat_bars(n, t0=ms(2021, 1, 1)):
    ts = t0 + STEP * np.arange(n)
    one = np.full(n, 100.0)
    return dict(ts=ts, o=one.copy(), h=one + 0.2, l=one - 0.2, c=one.copy(), v=np.full(n, 1000.0), tbv=np.full(n, 500.0))


def _all_days(D, val=True):
    days = np.arange(D["ts"][0] // DAY - 2, D["ts"][-1] // DAY + 2)
    return days, np.full(len(days), val)


def test_brk5_uses_prior_bars_only():
    D = _flat_bars(80)
    D["h"][:] = 10.0
    D["c"][:] = 9.5
    D["c"][50], D["h"][50] = 10.5, 10.6          # closes above the prior 30-bar high (10)
    D["c"][51], D["h"][51] = 10.4, 10.45         # prior high is now 10.6: no break
    brk5, _, _, _ = C.bar_features(D, _all_days(D))
    assert brk5[50] and not brk5[51] and not brk5[49]


def test_nb_abs_threshold_hand_number():
    D = _flat_bars(300)
    D["tbv"][:] = 500.0                           # net taker ratio 0 everywhere, bias 0
    D["tbv"][250:253] = 600.0                     # delta = +0.2 v on three bars
    _, nb, _, _ = C.bar_features(D, _all_days(D))
    # a3: first burst bar (0+0+0.2)/3 = 0.0667 < 0.08 ; second (0+0.2+0.2)/3 = 0.133 ; third 0.2 (bias ~ 0.001, negligible)
    assert not nb[250] and nb[251] and nb[252] and not nb[249]


def test_nb_abs_bias_is_shifted_one_bar_hand_number():
    D = _flat_bars(300)
    x = 0.2412                                    # a lone bar with net taker ratio x: a3 = x / 3 = 0.0804 >= 0.08
    D["tbv"][250] = 1000.0 * (1 + x) / 2          # bias is the mean of the PRIOR 180 bars (0), not including this bar
    _, nb, _, _ = C.bar_features(D, _all_days(D))
    assert nb[250]                                # including the bar itself in the bias would give 0.0804 * 179/180 = 0.07995


def test_onset_only_first_true_bar_and_first_bar_never():
    out = C.onset_mask([True, True, False, True, True, True, False, True])
    assert out.tolist() == [False, False, False, True, False, False, False, True]


def test_fund_lo_hand_example_and_missing():
    days = np.arange(C.day_num(2021, 1, 1), C.day_num(2021, 1, 1) + 200)
    rate = np.full(200, 0.001)
    rate[130:132] = -0.001                         # fd3 on day 132 = -0.001, below every one of the prior 90 values
    fts = days * DAY + 3600_000
    fd, lo = C.fund_lo_daily(days * DAY, fts, rate)
    assert not lo[129] and lo[130] and lo[131] and lo[132]   # each is the lowest 3-day mean of the prior 90
    assert not lo[120] and not lo[50]
    _, none = C.fund_lo_daily(days * DAY, np.array([], np.int64), np.array([]))
    assert not none.any()
    short = C.fund_lo_daily(days[:60] * DAY, fts[:60], rate[:60])[1]
    assert not short.any()                         # fewer than 90 prior values


def test_fund_lo_false_until_90_full_prior_values():
    """Regression (checker blocker): a coin with a thin funding history used to pass FUND_LO because NaN counted as 'not <=' but
    the share was still divided by 90. Constant-high funding then a deep negative dip at day 40: the dip must NOT fire (only 37
    prior fd3 values), and the same dip after a full window must fire."""
    d0 = C.day_num(2021, 1, 1)
    days = np.arange(d0, d0 + 200)
    rate = np.full(200, 0.001)
    rate[40:42] = -0.001
    rate[150:152] = -0.001
    fts = days * DAY + 3600_000
    _, lo = C.fund_lo_daily(days * DAY, fts, rate)
    assert not lo[:92].any()                      # window of 90 prior fd3 values needs ~92 days of funding
    assert lo[150] and lo[151] and lo[152]
    # a gap inside the window (missing funding days) also blocks the flag
    keep = np.ones(200, bool)
    keep[100:103] = False
    _, lo2 = C.fund_lo_daily(days * DAY, fts[keep], rate[keep])
    assert not lo2[150:153].any()


def test_funding_print_jitter_does_not_move_a_print_across_a_bar_open():
    """Regression (checker major): +1 ms stamps vs exact stamps at the entry and exit opens must charge the same funding."""
    t0 = 1_000_000_020_000 - (1_000_000_020_000 % STEP)
    ts = t0 + STEP * np.arange(8)
    exact = np.array([ts[1], ts[2], ts[3]])
    rate = np.array([0.5, 0.001, 0.002])
    pay = []
    for jit in (0, 1, 3, 17):
        fts = C.snap_ts(exact + jit)
        _, cf = C.cum_funding(ts, STEP, fts, rate)
        pay.append(C.funding_paid(cf, 1, 3))
    assert max(pay) - min(pay) < 1e-15 and abs(pay[0] - 0.003) < 1e-12   # entry-open print excluded, exit-open included
    assert C.snap_ts([ts[1] + 1])[0] == ts[1] and C.snap_ts([ts[1] + 4 * 3600000 + 2])[0] == ts[1] + 4 * 3600000


# ---------------------------------------------------------------- synthetic world
class World:
    """Random-walk coins on a 4h grid (2020-06-01 .. 2025-06-01), a BTC daily series that trends up (non-bear), 8h funding."""
    N = 10950

    def __init__(self, seed, n_coins=6):
        rng = np.random.default_rng(seed)
        self.t0 = ms(2020, 6, 1)
        self.ts = self.t0 + STEP * np.arange(self.N)
        self.lr = [rng.normal(0.0, 0.008, self.N) for _ in range(n_coins)]
        self.noise = [dict(hi=np.abs(rng.normal(0, 0.003, self.N)), lo=np.abs(rng.normal(0, 0.003, self.N)),
                           v=1000 * (1 + rng.random(self.N)), tb=np.clip(0.5 + 0.08 * rng.normal(size=self.N), 0, 1))
                      for _ in range(n_coins)]
        fts = np.arange(ms(2020, 12, 1), self.ts[-1] + STEP, 8 * 3600_000)
        self.fund = [(fts, 1e-4 + 5e-5 * rng.normal(size=len(fts))) for _ in range(n_coins)]
        bd = np.arange(C.day_num(2018, 1, 1), C.day_num(2025, 12, 31))
        self.btc_ts = bd * DAY
        self.btc_c = 100 * np.exp(np.cumsum(0.0015 + 0.01 * rng.normal(size=len(bd))))
        self.table = C.phase_table(self.btc_ts, self.btc_c)
        d0 = self.ts[0] // DAY
        self.d1 = dict(ts=np.arange(d0, self.ts[-1] // DAY + 1) * DAY)

    def bars(self, i, lr=None):
        lr = self.lr[i] if lr is None else lr
        nz = self.noise[i]
        c = 100.0 * np.exp(np.cumsum(lr))
        o = np.empty(self.N)
        o[0] = 100.0
        o[1:] = c[:-1]
        return dict(ts=self.ts.copy(), o=o, h=np.maximum(o, c) * (1 + nz["hi"]), l=np.minimum(o, c) * (1 - nz["lo"]), c=c,
                    v=nz["v"].copy(), tbv=nz["v"] * nz["tb"])

    def coin(self, i, lr=None, fund=None):
        return C.build_coin(f"S{i}", self.bars(i, lr), self.d1, self.fund[i] if fund is None else fund, self.table)


@pytest.fixture(scope="module")
def world():
    return World(7)


@pytest.fixture(scope="module")
def coins(world):
    return [world.coin(i) for i in range(len(world.lr))]


def test_world_has_natural_onsets(coins):
    assert sum(int(c.onset.sum()) for c in coins) >= 8      # the causality tests below are not vacuous
    assert sum(int((c.onset & c.elig).sum()) for c in coins) >= 5


def test_world_is_mostly_nonbear(coins):
    ph = coins[0].phase[coins[0].elig]
    assert np.isin(ph, list(C.NONBEAR)).mean() > 0.9


# ---------------------------------------------------------------- look-ahead
def _same(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return np.array_equal(a, b, equal_nan=True)


def test_future_bars_do_not_change_signal_or_phase_flag(world, coins):
    rng = np.random.default_rng(3)
    checked = 0
    for i in range(3):
        base = coins[i]
        on = np.flatnonzero(base.onset & base.elig)
        picks = list(on[:3]) + [int(x) for x in rng.integers(2000, world.N - 200, 3)]
        for s in picks:
            D = world.bars(i)
            later = np.arange(world.N) > s                   # every bar after the signal bar is replaced
            nl = int(later.sum())
            for k in ("o", "h", "l", "c"):
                D[k][later] = D[k][later] * rng.uniform(0.5, 1.5, nl)
            D["v"][later] = rng.uniform(10, 5000, nl)
            D["tbv"][later] = D["v"][later] * rng.random(nl)
            fts, fr = world.fund[i]
            cut = D["ts"][s] // DAY * DAY                    # day of the signal bar: its prints reach bars of the NEXT day only
            fr2 = np.where(fts >= cut, rng.normal(-0.01, 0.01, len(fr)), fr)
            alt = C.build_coin("x", D, world.d1, (fts, fr2), world.table)
            for name in ("onset", "brk5", "nb_abs", "fund_lo", "atr", "phase", "elig"):
                assert _same(getattr(base, name)[:s + 1], getattr(alt, name)[:s + 1]), (name, i, s)
            checked += 1
    assert checked >= 12


def _day_label(table, d):
    return C.phase_for_days(table, np.array([d]))[0]


def test_phase_flag_reads_only_closes_before_the_entry_day(world):
    d = C.day_num(2022, 3, 15)
    keep = np.arange(len(world.btc_ts))
    cut = np.flatnonzero(world.btc_ts // DAY >= d)[0]
    c2 = world.btc_c.copy()
    c2[cut:] = c2[cut:] * 1e-3                               # crash from day d on
    t2 = C.phase_table(world.btc_ts, c2)
    assert _day_label(world.table, d) == _day_label(t2, d)   # entry day d reads closes <= d-1
    assert _day_label(world.table, d + 2) != _day_label(t2, d + 2) or _day_label(world.table, d + 1) != _day_label(t2, d + 1)
    assert len(keep) > 0


def test_same_day_phase_read_is_caught(world):
    """The detector used above must bite: a same-day-keyed table (bug) changes its label when the day's own close changes."""
    d = C.day_num(2022, 3, 15)
    cut = np.flatnonzero(world.btc_ts // DAY >= d)[0]
    c2 = world.btc_c.copy()
    c2[cut:] = c2[cut:] * 1e-3
    leak = _day_label(C.phase_table(world.btc_ts, world.btc_c, bug=True), d) != _day_label(C.phase_table(world.btc_ts, c2, bug=True), d)
    assert leak


def test_funding_feature_lags_one_day_and_same_day_read_is_caught(world):
    i = 1
    D = world.bars(i)
    fts, fr = world.fund[i]
    fl_days, fl = C.fund_lo_daily(world.d1["ts"], fts, fr)
    d = int(fl_days[(fl_days >= C.day_num(2022, 6, 1)) & ~fl][0])     # a day whose own FUND_LO is False
    fr2 = np.where(fts // DAY == d, -0.5, fr)                # one extreme day makes it True
    base = C.bar_features(D, C.fund_lo_daily(world.d1["ts"], fts, fr))[2]
    alt = C.bar_features(D, C.fund_lo_daily(world.d1["ts"], fts, fr2))[2]
    on_day = (D["ts"] // DAY) <= d
    assert _same(base[on_day], alt[on_day])                   # nothing on day d or before changes
    assert not _same(base[D["ts"] // DAY == d + 1], alt[D["ts"] // DAY == d + 1])   # day d+1 legitimately sees it
    bug_a = C.bar_features(D, C.fund_lo_daily(world.d1["ts"], fts, fr), bug=True)[2]
    bug_b = C.bar_features(D, C.fund_lo_daily(world.d1["ts"], fts, fr2), bug=True)[2]
    assert not _same(bug_a[D["ts"] // DAY == d], bug_b[D["ts"] // DAY == d])        # the detector bites on the buggy read


# ---------------------------------------------------------------- simulator: stop wins ties, gap fills
def _path(n=400, base=100.0):
    return [np.full(n, base) for _ in range(4)]   # o, h, l, c


def test_stop_wins_same_bar_tie_with_target():
    o, h, l, c = _path()
    h = h + 0.1
    l = l - 0.1
    l[1], h[1] = 97.0, 107.0                       # entry bar touches both stop 98 and target 106 (S = 2)
    for kind in ("T3R", "RIDE"):
        r = C.simulate(o, h, l, c, [0], [2.0], kind, C.prior_low(l, 10))
        assert r["why"][0] == 1 and abs(r["ret"][0] - (-0.02)) < 1e-12 and r["xi"][0] == 1 and r["xt"][0] == 2


def test_stop_gap_fills_at_the_worse_open_and_target_at_target():
    o, h, l, c = _path()
    h = h + 0.1
    l = l - 0.1
    o[2], l[2], h[2] = 95.0, 94.0, 96.0            # bar 2 gaps below the stop (98): fills at the open, worse than the stop
    r = C.simulate(o, h, l, c, [0], [2.0], "T3R", None)
    assert abs(r["ret"][0] - (-0.05)) < 1e-12 and r["why"][0] == 1 and r["xi"][0] == 2
    o, h, l, c = _path()
    h = h + 0.1
    l = l - 0.1
    o[2], h[2] = 108.0, 109.0                      # bar 2 gaps above the target (106): filled AT the target
    r = C.simulate(o, h, l, c, [0], [2.0], "T3R", None)
    assert abs(r["ret"][0] - 0.06) < 1e-12 and r["why"][0] == 2


def test_stop_touch_exactly_counts_and_is_checked_from_the_entry_bar():
    o, h, l, c = _path()
    h = h + 0.1
    l = l - 0.1
    l[1] = 98.0                                    # low == stop on the ENTRY bar
    r = C.simulate(o, h, l, c, [0], [2.0], "T3R", None)
    assert r["why"][0] == 1 and r["xi"][0] == 1 and abs(r["ret"][0] + 0.02) < 1e-12


def test_ride_exit_at_next_open_after_close_at_or_below_prior_10d_low():
    o, h, l, c = _path()
    h = h + 0.1
    l = l - 0.1                                    # every low 99.9 -> prior 60-bar low 99.9
    c[100], l[100] = 99.9, 99.85                   # close equal to the prior low: exits (<=)
    o[101] = 99.95
    exit_lvl = C.prior_low(l, 10)
    r = C.simulate(o, h, l, c, [60], [2.0], "RIDE", exit_lvl)
    assert r["why"][0] == 3 and r["xi"][0] == 100 and r["xt"][0] == 101 and abs(r["ret"][0] - (99.95 - 100.0) / 100.0) < 1e-12
    c[100] = 99.91                                 # just above: no exit there
    r = C.simulate(o, h, l, c, [60], [2.0], "RIDE", exit_lvl)
    assert r["xi"][0] != 100


def test_time_exits_at_close_of_last_hold_bar_and_unresolved_at_data_end():
    o, h, l, c = _path()
    h = h + 0.1
    l = l - 0.1
    c[240] = 100.5
    r = C.simulate(o, h, l, c, [60], [2.0], "T3R", None)           # entry bar 61, 180 bars: last hold bar 240
    assert r["why"][0] == 4 and r["xi"][0] == 240 and abs(r["ret"][0] - 0.005) < 1e-12
    r = C.simulate(o[:200], h[:200], l[:200], c[:200], [60], [2.0], "T3R", None)   # data ends before day 30
    assert r["xi"][0] == -1 and np.isnan(r["ret"][0])


# ---------------------------------------------------------------- fees and funding arithmetic
def test_cost_is_twelve_basis_points_from_fees_py():
    assert abs(C.ROUND_TRIP - 0.0012) < 1e-12
    assert C.ROUND_TRIP == 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13


def test_net_r_hand_numbers():
    assert abs(C.net_r(0.10, 0.001, 0.04) - 2.445) < 1e-9        # (0.10 - 0.0012 - 0.001) / 0.04
    assert abs(C.net_r(0.10, -0.001, 0.04) - 2.495) < 1e-9       # a long RECEIVES negative funding
    assert abs(C.net_r(-0.02, 0.0, 0.02) - (-0.02 - 0.0012) / 0.02) < 1e-9


def test_funding_window_after_entry_open_up_to_and_including_exit_open():
    ts = 1_000_000_000_000 + STEP * np.arange(8)
    fts = np.array([ts[1], ts[2] + 5, ts[3], ts[4] + 1])
    frate = np.array([0.5, 0.001, 0.002, 0.5])
    grid, cf = C.cum_funding(ts, STEP, fts, frate)
    # entry open = ts[1] (print AT the entry open excluded), exit open = ts[3] (print AT the exit open included)
    assert abs(C.funding_paid(cf, 1, 3) - 0.003) < 1e-12
    assert abs(C.funding_paid(cf, 1, 4) - 0.003) < 1e-12          # the print at ts[4]+1 is after the exit open
    assert grid[-1] == ts[-1] + STEP


def _hand_coin(n=400, t0=ms(2021, 3, 1), phase=0.0, fund=(np.array([], np.int64), np.array([]))):
    """A hand-built Coin: flat 100, every low 99.9, constant ATR 0.4 (S = max(1.0, 2.0) = 2.0, risk 2%), eligible, single phase."""
    c = C.Coin()
    c.sym = "H"
    c.ts = t0 + STEP * np.arange(n)
    c.o, c.h, c.l, c.c = (np.full(n, 100.0), np.full(n, 100.2), np.full(n, 99.9), np.full(n, 100.0))
    c.atr = np.full(n, 0.4)
    c.onset = np.zeros(n, bool)
    c.entry_ts = np.append(c.ts[1:], c.ts[-1] + STEP)
    c.entry_day = c.entry_ts // DAY
    c.phase = np.full(n, phase)
    c.elig = np.ones(n, bool)
    c.first_fund = fund[0][0] if len(fund[0]) else np.inf
    c.fund_last = fund[0][-1] if len(fund[0]) else -1
    c.grid, c.cf = C.cum_funding(c.ts, STEP, fund[0], fund[1])
    c.exit_lvl = C.prior_low(c.l, 10)
    c.n = n
    return c


def test_trade_row_net_r_against_a_hand_number():
    t0 = ms(2021, 3, 1)
    ts = t0 + STEP * np.arange(400)
    fund = (np.array([ts[101], ts[103], ts[106], ts[107]]), np.array([0.5, 0.001, 0.001, 0.5]))
    c = _hand_coin(fund=fund)
    c.onset[100] = True
    c.c[105], c.l[105] = 99.9, 99.85               # close <= prior 60-bar low -> exit at the next open
    c.o[106] = 99.95
    rows = C.make_trades(c, "RIDE", C.NONBEAR, "nonbear")
    assert len(rows) == 1
    r = rows[0]
    assert r["entry_price"] == 100.0 and abs(r["stop"] - 98.0) < 1e-9 and abs(r["risk"] - 0.02) < 1e-12
    assert r["exit_reason"] == "SIGNAL" and r["exit_price"] == 99.95 and r["hold_bars"] == 5
    assert abs(r["gross"] - (-0.0005)) < 1e-12
    assert abs(r["funding"] - 0.002) < 1e-12          # prints at ts[103] and ts[106]; not ts[101] (entry open) nor ts[107]
    assert abs(r["net_ret"] - (-0.0005 - 0.0012 - 0.002)) < 1e-12
    assert abs(r["R"] - (-0.0037 / 0.02)) < 1e-9
    assert abs(r["R6"] - (-0.0005 - 0.0006 - 0.002) / 0.02) < 1e-9


def test_target_trade_hand_number_t3r():
    c = _hand_coin()
    c.onset[100] = True
    c.h[103] = 107.0                                # 3R target 106 touched, stop (98) not
    rows = C.make_trades(c, "T3R", C.NONBEAR, "nonbear")
    r = rows[0]
    assert r["exit_reason"] == "TARGET" and abs(r["gross"] - 0.06) < 1e-12 and abs(r["R"] - (0.06 - 0.0012) / 0.02) < 1e-9


# ---------------------------------------------------------------- lockout / overlap / gates / split
def test_greedy_overlap_hand_example():
    idx = np.array([10, 15, 50, 60, 100])
    xg = np.array([50, 20, 70, 65, 130])            # the trade from 10 occupies bars up to 50
    assert C.greedy(idx, xg).tolist() == [10, 50, 100]   # 15 skipped; 50 may start AT the exit bar; 60 is inside the trade from 50


def test_overlapping_signals_on_one_coin_are_skipped_and_later_one_taken():
    c = _hand_coin()
    c.onset[[100, 101, 150]] = True
    c.l[103] = 97.0                                 # trade 100 stops out on bar 103
    c.l[160] = 97.0                                 # trade 150 stops out on bar 160
    rows = C.make_trades(c, "T3R", C.NONBEAR, "nonbear")
    assert [r["signal_ts"] for r in rows] == [int(c.ts[100]), int(c.ts[150])]


def test_phase_gate_and_warmup():
    c = _hand_coin(phase=4.0)
    c.onset[[100, 200]] = True
    c.l[[110, 210]] = 97.0
    assert C.make_trades(c, "T3R", C.NONBEAR, "nonbear") == []
    assert len(C.make_trades(c, "T3R", C.BEAR, "bear")) == 2     # control row
    c2 = _hand_coin(phase=1.0)
    c2.onset[[5, 100]] = True
    c2.atr[:14] = np.nan                                        # warm-up: ATR undefined
    c2.l[110] = 97.0
    assert [r["signal_ts"] for r in C.make_trades(c2, "T3R", C.NONBEAR, "nonbear")] == [int(c2.ts[100])]
    c3 = _hand_coin(phase=1.0)
    c3.onset[100] = True
    c3.elig[:] = False                                           # before 2020 or before the first funding print
    assert C.make_trades(c3, "T3R", C.NONBEAR, "nonbear") == []


def test_eligibility_before_first_funding_print_and_before_2020(coins, world):
    c = coins[0]
    first = world.fund[0][0][0]
    assert not c.elig[c.entry_ts < first].any()
    assert c.elig[(c.entry_ts >= first + 30 * DAY)].mean() > 0.9


def test_split_by_signal_bar_not_entry_day():
    last_dev = ms(2023, 12, 31, 20)                 # entry is 2024-01-01 00:00 (a VAL day) but the SIGNAL bar is DEV
    assert C.split_of_signal([last_dev, last_dev + STEP]).tolist() == ["DEV", "VAL"]
    c = _hand_coin(n=500, t0=last_dev - STEP * 100)
    c.onset[100] = True
    c.l[110] = 97.0
    rows = C.make_trades(c, "T3R", C.NONBEAR, "nonbear")
    assert rows[0]["split"] == "DEV" and rows[0]["entry_utc"].startswith("2024-01-01 00:00")


# ---------------------------------------------------------------- stats code: hand numbers
def test_week_bootstrap_p_formula_and_sign():
    r = np.array([1.0, 2.0, 1.5, 0.5] * 10)
    wk = np.repeat([f"w{i}" for i in range(20)], 2)
    b = T.week_bootstrap(r, wk, n_boot=400, seed=1)
    assert b["lo"] > 0 and abs(b["p"] - 1 / 401) < 1e-12 and b["weeks"] == 20 and abs(b["mean"] - 1.25) < 1e-12


def test_week_bootstrap_resamples_weeks_not_trades():
    r = np.array([5.0, 5.0, 5.0, 5.0, -1.0, -1.0, -1.0, -1.0])
    wk = np.array(["a"] * 4 + ["b"] * 4)                       # two weeks: a resample mean is one of 5, -1 or their mix
    b = T.week_bootstrap(r, wk, n_boot=300, seed=2)
    assert b["lo"] == -1.0 and b["hi"] == 5.0


def test_ex_best_weeks_hand_number():
    r = np.array([10.0, 2.0, 5.0, 1.0, -1.0, -1.0, -3.0])
    wk = np.array(["A", "A", "B", "C", "D", "D", "E"])        # sums A 12, B 5, C 1, D -2, E -3
    e = T.ex_best_weeks(r, wk, k=2)
    assert e["weeks_dropped"] == ["A", "B"] and abs(e["mean"] - (1.0 - 1.0 - 1.0 - 3.0) / 4) < 1e-12 and e["n_left"] == 4


def test_top_coin_removal_and_daily_baselines_hand_numbers():
    df = pd.DataFrame(dict(coin=["a", "a", "b", "c"], R=[4.0, 2.0, -1.0, 1.0]))
    t = T.top_coin_removal(df)
    assert abs(t["by_coin"]["a"] - 0.0) < 1e-12 and t["worst_coin"] == "a" and t["all_positive"] is False
    tr = pd.DataFrame(dict(net_ret=[0.06, -0.02], hold_days=[3.0, 1.0]))
    assert abs(T.strategy_daily(tr)["mean"] - 0.01) < 1e-12
    d0 = 20000
    table = (np.arange(d0 - 5, d0 + 10), np.zeros(15))        # label 0 (UP_E) keyed to those days
    closes = {"A": (np.array([d0, d0 + 1]), np.array([100.0, 110.0])), "B": (np.array([d0, d0 + 1]), np.array([100.0, 100.0]))}
    b = T.basket_daily(closes, {"A": 0, "B": 0}, table, d0, d0 + 1)
    assert abs(b["mean"] - 0.05) < 1e-12 and b["days"] == 1
    bear = (np.arange(d0 - 5, d0 + 10), np.full(15, 4.0))
    assert T.basket_daily(closes, {"A": 0, "B": 0}, bear, d0, d0 + 1)["days"] == 0


# ---------------------------------------------------------------- planted edge
def _signal_bars(world, coin_ix, rng, gap=130):
    base = world.coin(coin_ix)
    ok = np.flatnonzero(base.elig & np.isfinite(base.atr))
    ok = ok[ok < world.N - 500]
    picks, last = [], -10 ** 9
    for s in rng.permutation(ok)[:400]:
        picks.append(int(s))
    picks = sorted(picks)
    out = []
    for s in picks:
        if s - last >= gap:
            out.append(s)
            last = s
    return np.array(out)


def _world_trades(world, planted, seed=11, n_coins=6):
    rng = np.random.default_rng(seed)
    rows, cs = [], {}
    for i in range(n_coins):
        sigs = _signal_bars(world, i, rng)
        lr = world.lr[i].copy()
        pos = np.arange(len(lr))
        if planted:
            for s in sigs:
                lr[(pos > s) & (pos <= s + 24)] += 0.004   # +9.6% over four days after every signal
        c = world.coin(i, lr=lr)
        c.onset = np.zeros(c.n, bool)
        c.onset[sigs] = True
        cs[c.sym] = c
        rows += C.make_trades(c, "RIDE", C.NONBEAR, "nonbear")
    return pd.DataFrame(rows), cs


@pytest.fixture(scope="module")
def planted(world):
    return _world_trades(world, True)


@pytest.fixture(scope="module")
def null(world):
    return _world_trades(world, False)


def test_planted_edge_is_found_by_the_stats_code(planted):
    df, cs = planted
    val = df[df.split == "VAL"]
    assert len(val) >= 30 and val.entry_week.nunique() >= 20
    b = T.week_bootstrap(val.R, val.entry_week, n_boot=500)
    assert b["mean"] > 1.0 and b["lo"] > 0 and b["p"] < 0.01
    pl = T.placebo_draws(cs, val[["coin", "risk"]], n_draw=120)
    v = T.placebo_verdict(val.R.mean(), pl["means"])
    assert v["beats"] and v["percentile"] >= 0.975 and v["excess"] > 0.5


def test_no_drift_world_reads_about_zero(null):
    df, cs = null
    val = df[df.split == "VAL"]
    assert len(val) >= 30
    b = T.week_bootstrap(val.R, val.entry_week, n_boot=500)
    assert abs(b["mean"]) < 0.6 and b["lo"] <= 0 <= b["hi"]
    pl = T.placebo_draws(cs, val[["coin", "risk"]], n_draw=120)
    v = T.placebo_verdict(val.R.mean(), pl["means"])
    assert not v["beats"] and abs(v["excess"]) < 0.6


def test_trades_respect_phase_split_and_entry_window(planted, world):
    df, _ = planted
    assert len(df) > 50
    assert set(df.phase) <= set(C.PHASES[i] for i in C.NONBEAR)
    assert (df.entry_ts >= ms(2020, 12, 1)).all()
    assert (df[df.split == "DEV"].signal_ts // DAY <= C.DEV_END_DAY).all() and (df[df.split == "VAL"].signal_ts // DAY >= C.VAL_START_DAY).all()
    per_coin = df.sort_values(["coin", "signal_ts"])
    for _, g in per_coin.groupby(["coin", "split"]):
        assert (g.signal_ts.to_numpy()[1:] >= g.exit_bar_ts.to_numpy()[:-1]).all()      # no overlap per coin and window
