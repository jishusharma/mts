"""phase3_dev.py pure parts: the Krown structural lower-high finder (operator's six 2026-10-30/31 lines, PHASE1_RANGE.md Q4),
the single-short book (stop / L1 / time / one-bar shift / F3 exit), the DEV guard. No network, no bars outside the fixture.
Fixture = public Binance spot BTCUSDT 15m klines 2026-10-28 00:00 .. 10-31 11:45 UTC, [open_ms, o, h, l, c]."""
import importlib.util, json, os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("phase3_dev", os.path.join(HERE, "phase3_dev.py"))
P3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P3)


def ms(s):
    return int(datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).timestamp() * 1000)


def fixture():
    b = json.load(open(os.path.join(HERE, "fixture_btc15m_2026-10-28_31.json")))
    return [x[0] for x in b], [x[2] for x in b], [x[3] for x in b]


def test_import_has_no_side_effects():
    assert P3.DEV_END_MS == ms("2024-07-01 00:00")  # DEV is half-open: nothing at or after 2024-07-01 is ever loaded


def test_krown_keeps_the_four_lines_and_drops_the_other_two():
    # operator's lines (Bitstamp) -> Binance swing highs (Q4 table): 81,888 -> 81,971 10-29 16:00; 80,842 -> 80,946 18:15;
    # 79,688 -> 79,811 21:15; 79,131 -> 79,272 22:15 (1-bar retest high, DROP); 78,644 -> 78,804 10-30 06:30 (DROP); 77,937 -> 78,110 15:15
    T, H, L = fixture()
    dom = {T[h]: H[h] for h, _, _ in P3.krown_dominant(H, L)}
    for t, px in (("2026-10-29 16:00", 81971.0), ("2026-10-29 18:15", 80946.01), ("2026-10-29 21:15", 79811.23), ("2026-10-30 15:15", 78110.0)):
        assert dom.get(ms(t)) == px, t
    for t in ("2026-10-29 22:15", "2026-10-30 06:30"):
        assert ms(t) not in dom, t


def test_krown_is_known_at_the_time():
    # each dominant high must already be found on the series cut at its own known-bar, and not one bar earlier
    T, H, L = fixture()
    full = P3.krown_dominant(H, L)
    assert len(full) >= 4
    for h, known, brk in full:
        assert known >= h + P3.KR_K and known >= brk
        cut = P3.krown_dominant(H[:known + 1], L[:known + 1])
        assert (h, known, brk) in cut
        if known > 0:
            assert all(c[0] != h for c in P3.krown_dominant(H[:known], L[:known]))


def test_krown_high_exceeded_before_the_break_is_not_a_lower_high():
    # swing high 9.5 (idx 3) is taken out by 20 (idx 5) before the first lower low (idx 7): only 20 is a dominant high
    H = [5, 9, 5, 9.5, 6, 20, 6, 4, 3, 2, 1]
    L = [4, 8, 4, 8.5, 5, 19, 5, 3.5, 2.5, 1.5, 0.5]
    got = [h for h, _, _ in P3.krown_dominant(H, L, K=1, M=2)]
    assert 3 not in got and 5 in got


def bars(n=40, px=100.0):
    return [px] * n


def test_fee_comes_from_fees_py():
    import importlib
    spec = importlib.util.spec_from_file_location("mts_fees", os.path.join(P3.REPO, "MyTradingSys", "backtest", "fees.py"))
    f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
    assert abs(P3.FEE_PCT - f.BINANCE_TAKER * 2 * 100) < 1e-12


def make_market(n=130):
    O = [100.0] * n; H = [100.0] * n; L = [100.0] * n; C = [100.0] * n
    return dict(O=O, H=H, L=L, C=C, N=n)


def test_single_short_target_stop_time_and_shift():
    m = make_market()
    lvl, l1, take = 100.0, 98.0, 5
    # take-out bar 5 spikes over the level, bar 6 closes back under (signal bar s=6), bar 7 touches L1
    m["H"][5] = 100.5; m["C"][5] = 100.2
    m["C"][6] = 99.5; m["O"][6] = 100.1; m["H"][6] = 100.3; m["L"][6] = 99.4
    m["O"][7] = 99.4; m["C"][7] = 98.5; m["H"][7] = 99.5; m["L"][7] = 97.9
    ev = dict(lvl=lvl, l1=l1, take=take)
    r0 = P3.simulate(m, ev, shift=False, imp=None, f3=False)
    assert r0["why"] == "L1" and r0["entry"] == 99.5 and r0["bar_in"] == 6
    assert abs(r0["net"] - ((99.5 - 98.0) / 99.5 * 100 - P3.FEE_PCT)) < 1e-9
    r1 = P3.simulate(m, ev, shift=True, imp=None, f3=False)  # enters at the open of bar 7 (99.4), L1 touched on the same bar
    assert r1["why"] == "L1" and r1["entry"] == 99.4 and r1["bar_in"] == 7
    assert abs(r1["net"] - ((99.4 - 98.0) / 99.4 * 100 - P3.FEE_PCT)) < 1e-9


def test_single_short_stop_wins_same_bar_tie_and_time_exit():
    m = make_market()
    m["H"][5] = 100.5; m["C"][6] = 99.5
    m["H"][7] = 101.2; m["L"][7] = 97.0; m["C"][7] = 99.0  # stop 101.0 and L1 98.0 in one bar -> stop
    ev = dict(lvl=100.0, l1=98.0, take=5)
    r = P3.simulate(m, ev, shift=False, imp=None, f3=False)
    assert r["why"] == "stop" and abs(r["net"] - ((99.5 - 101.0) / 99.5 * 100 - P3.FEE_PCT)) < 1e-9
    m2 = make_market(120); m2["H"][5] = 100.5; m2["C"][6] = 99.5
    r2 = P3.simulate(m2, dict(lvl=100.0, l1=98.0, take=5), shift=False, imp=None, f3=False)
    assert r2["why"] == "24h" and r2["bar_out"] == 5 + P3.HOLD
    assert P3.simulate(make_market(40), dict(lvl=100.0, l1=98.0, take=5), shift=False, imp=None, f3=False) is None  # hold runs past the data


def test_f3_exits_at_the_close_of_the_first_up_impulse_within_8_bars():
    m = make_market(130)
    m["H"][5] = 100.5; m["C"][6] = 99.5
    for k in range(7, 130):
        m["C"][k] = 99.0
    imp = [0] * 130
    imp[9] = 1; imp[20] = 1
    ev = dict(lvl=100.0, l1=90.0, take=5)
    r = P3.simulate(m, ev, shift=False, imp=imp, f3=True)
    assert r["why"] == "F3" and r["bar_out"] == 9 and abs(r["net"] - ((99.5 - 99.0) / 99.5 * 100 - P3.FEE_PCT)) < 1e-9
    imp2 = [0] * 130; imp2[16] = 1  # first checked bar is 7, window 7..14: bar 16 is outside
    assert P3.simulate(m, ev, shift=False, imp=imp2, f3=True)["why"] == "24h"


def test_loader_refuses_bars_from_the_sealed_split():
    import pytest
    with pytest.raises(ValueError):
        P3.guard_dev([ms("2024-06-30 23:45"), ms("2024-07-01 00:00")])
    P3.guard_dev([ms("2024-06-30 23:45")])


def test_c26_events_on_a_hand_built_tent():
    # peak 105 at bar 20 (the only +-16 pivot high before bar 60), pull-back far below 0.8 %, retest bar 50 at 104.7 (>= 105 x 0.996, < 105)
    # held 4 bars, then bar 60 takes the level out
    n = 120
    H = [100 - 0.01 * abs(k - 20) for k in range(n)]
    H[20] = 105.0; H[50] = 104.7; H[60] = 105.5
    L = [h - 0.5 for h in H]
    C = [h - 0.2 for h in H]
    ev = [e for e in P3.c26_events(H, L, C, 0) if e["h"] == 20]
    assert len(ev) == 1 and ev[0]["lvl"] == 105.0 and ev[0]["i"] == 50 and ev[0]["j"] == 54
    assert ev[0]["l1"] == min(L[20:51])
    assert P3.take_out(H, 54, 105.0) == 60
    assert P3.take_out(H, 54, 106.0) is None
    H2 = list(H); H2[52] = 105.2  # the level is exceeded inside the 4 held bars: no event
    assert not [e for e in P3.c26_events(H2, [h - 0.5 for h in H2], [h - 0.2 for h in H2], 0) if e["h"] == 20]


def test_sma_impulse_and_power_arithmetic_against_hand_values():
    assert P3.sma([1.0, 2.0, 3.0, 4.0], 2) == [None, 1.5, 2.5, 3.5]
    D = [1.0, -1.0] * (P3.IMP_W // 2) + [10.0, -10.0, 0.5]  # prior std 1: 10 > 1.5 x 1 up, -10 down, 0.5 none
    imp = P3.impulses(D)
    assert imp[P3.IMP_W] == 1 and imp[P3.IMP_W + 1] == -1 and imp[P3.IMP_W + 2] == 0
    from statistics import NormalDist
    d = [0.2 + (0.5 if i % 2 else -0.5) for i in range(100)]  # mean 0.2, sd 0.5025.. over n = 100
    pr = P3.paired(d)
    import math
    sd = math.sqrt(sum((x - 0.2) ** 2 for x in d) / 99)
    se = sd / 10
    z = NormalDist().inv_cdf(1 - 0.05 / 24)
    assert abs(pr["se"] - se) < 1e-12 and abs(pr["power"] - NormalDist().cdf(0.2 / se - z)) < 1e-12
    assert abs(pr["mde"] - 2.8 * se) < 1e-12
