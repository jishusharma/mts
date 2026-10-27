"""LC3 ladder simulator: hand-derived paths (red before ladder.py existed)."""
import importlib.util
import math
from pathlib import Path

P = Path(__file__).with_name('ladder.py')
S = importlib.util.spec_from_file_location('lc_ladder', P); m = importlib.util.module_from_spec(S); S.loader.exec_module(m)
PE = Path(__file__).with_name('event_table.py')
SE = importlib.util.spec_from_file_location('lc_event_table', PE); et = importlib.util.module_from_spec(SE); SE.loader.exec_module(et)

DAY = 86400000
MAKER, TAKER = 0.0002, 0.0005


def _bar(k, o, h, l, c, v=10., tbv=5.):
    return {'t': DAY + k * 60000, 'o': o, 'h': h, 'l': l, 'c': c, 'v': v, 'tbv': tbv}


def _flat_prefix(n=100, tbv=5.):
    return [_bar(k, 100., 100., 100., 100., 10., tbv) for k in range(n)]


IDEA = {'side': 1, 'L1': 99., 'L2': 98., 'T1': 101., 'T2': 103., 'atr1h': 1.0}


def test_ladder_support_long_half_at_resistance_quarter_on_flat_cvd_rest_on_band():
    bars = []
    for k in range(100):  # 20 closed 5m buckets, closes alternate 100/101, delta +2 a bar (+10 a bucket)
        px = 100. + ((k // 5) % 2)
        bars.append(_bar(k, px, px, px, px, 10., 6.))
    bars.append(_bar(100, 100., 100., 99., 99.5, 10., 8.))        # first touch of L1 = 99, previous close 101: long
    bars.append(_bar(101, 99.5, 101., 99.5, 100.5, 10., 8.))      # first resistance 101 reached: half out
    bars += [_bar(k, 100.5, 100.5, 100.5, 100.5, 10., 8.) for k in range(102, 105)]   # bucket 100-104: delta +30, agrees
    bars += [_bar(k, 100.5, 100.5, 100.5, 100.5, 10., 5.) for k in range(105, 110)]   # bucket 105-109: delta 0, flat: quarter out
    bars += [_bar(k, 100.5, 100.5, 100.5, 100.5, 10., 8.) for k in range(110, 114)]
    bars.append(_bar(114, 100.5, 110., 100.5, 110., 10., 8.))     # bucket 110-114 closes 110: above the upper band: rest out
    bars += [_bar(k, 110., 110., 110., 110., 10., 8.) for k in range(115, 120)]
    r = m.simulate(bars, 100, IDEA, 'S0', 'K1', 'X2', fees=m.FEES_MAIN)
    assert [(e[0], e[1], e[2]) for e in r['exits']] == [(101.0, 0.5, 'T1'), (100.5, 0.25, 'CVD_FLAT'), (110.0, 0.25, 'BAND')]
    stop = 99. * (1 - 0.002)                     # K1 with maker entries: 0.20 % beyond the entry level
    R = 99. - stop                               # 0.198
    gross = 0.5 * (101 - 99) + 0.25 * (100.5 - 99) + 0.25 * (110 - 99)      # 4.125
    fees = MAKER * 99 * 1.0 + MAKER * 101 * 0.5 + TAKER * 100.5 * 0.25 + TAKER * 110 * 0.25
    assert abs(r['R_price'] - R) < 1e-12
    assert abs(r['gross_r'] - gross / R) < 1e-9
    assert abs(r['fees_r'] - fees / R) < 1e-9
    assert abs(r['net_r'] - (gross - fees) / R) < 1e-9
    assert r['stop_status'] == 'NOT_STOPPED'


def test_scale_in_two_fills_hand_average_one_stop_then_target():
    bars = _flat_prefix()
    bars.append(_bar(100, 100., 100., 99., 99.5))                 # L1 fill at 99
    bars.append(_bar(101, 99.5, 99.5, 98., 98.5))                 # L2 fill at 98
    bars.append(_bar(102, 98.5, 101., 98.5, 100.))                # first resistance: all out at 101
    bars += [_bar(k, 100., 100., 100., 100.) for k in range(103, 110)]
    r = m.simulate(bars, 100, IDEA, 'S1', 'K2', 'X1')
    assert [(f[0], f[1]) for f in r['fills']] == [(99.0, 0.5), (98.0, 0.5)]
    stop = 98. * (1 - 0.001)                                     # K2: 0.10 % beyond L2
    R = 98.5 - stop                                              # planned average 98.5, one stop for the set
    gross = 0.5 * (101 - 99) + 0.5 * (101 - 98)                  # 2.5
    fees = MAKER * (99 * 0.5 + 98 * 0.5) + MAKER * 101 * 1.0
    assert abs(r['avg_entry'] - 98.5) < 1e-12 and abs(r['R_price'] - R) < 1e-12
    assert abs(r['net_r'] - (gross - fees) / R) < 1e-9


def test_unfilled_half_counts_zero_and_l2_only_arm_can_miss():
    bars = _flat_prefix()
    bars.append(_bar(100, 100., 100., 99., 99.5))
    bars.append(_bar(101, 99.5, 101., 99.5, 100.))                # straight to the target, L2 never touched
    bars += [_bar(k, 100., 100., 100., 100.) for k in range(102, 110)]
    r = m.simulate(bars, 100, IDEA, 'S1', 'K2', 'X1')
    R = 98.5 - 98. * (1 - 0.001)
    fees = MAKER * 99 * 0.5 + MAKER * 101 * 0.5
    assert [(f[0], f[1]) for f in r['fills']] == [(99.0, 0.5)]
    assert abs(r['net_r'] - (0.5 * 2 - fees) / R) < 1e-9
    r2 = m.simulate(bars, 100, IDEA, 'S2', 'K2', 'X1')
    assert r2['fills'] == [] and r2['net_r'] == 0.0 and r2['stop_status'] == 'NO_FILL'


def test_stop_costs_one_r_plus_fees_and_is_bad_when_target_follows():
    bars = _flat_prefix()
    bars.append(_bar(100, 100., 100., 99., 99.5))
    bars.append(_bar(101, 99., 99., 98.7, 98.8))                  # through the K1 stop 98.802
    bars.append(_bar(102, 98.8, 101.5, 98.8, 101.))               # then the target: the stop was bad
    bars += [_bar(k, 101., 101., 101., 101.) for k in range(103, 110)]
    r = m.simulate(bars, 100, IDEA, 'S0', 'K1', 'X1')
    stop = 99. * (1 - 0.002); R = 99. - stop
    fees = MAKER * 99 + TAKER * stop
    assert r['exits'][0][2] == 'STOP' and abs(r['exits'][0][0] - stop) < 1e-12
    assert abs(r['net_r'] - (-R - fees) / R) < 1e-9
    assert abs(r['net_r'] - (-1.0 - r['fees_r'])) < 1e-9
    assert r['stop_status'] == 'BAD'


def test_k1_floor_is_0_4_pct_with_taker_entries():
    bars = _flat_prefix() + [_bar(100, 100., 100., 99., 99.5)] + [_bar(k, 99.5, 99.5, 99.5, 99.5) for k in range(101, 110)]
    r = m.simulate(bars, 100, IDEA, 'S0', 'K1', 'X1', fees=m.FEES_TAKER)
    assert abs(r['R_price'] - 99. * 0.004) < 1e-12


def _arm_p_bars():
    bars = _flat_prefix()
    bars.append(_bar(100, 100., 100., 99., 99.5))                 # L1 = 99 filled (limit, maker)
    bars.append(_bar(101, 99.2, 99.2, 98.9, 99.0))                # low 98.9 <= 98.901: add 2 triggers
    bars.append(_bar(102, 98.9, 98.9, 98.8, 98.85))               # add 2 fills at the open 98.9; low 98.8 <= 98.802: add 3 triggers
    bars.append(_bar(103, 98.8, 98.8, 98.75, 98.78))              # add 3 fills at the open 98.8
    bars.append(_bar(104, 98.78, 98.78, 98.5, 98.6))              # low 98.5 <= stop 98.604: all out at the stop
    bars += [_bar(k, 98.6, 98.6, 98.6, 98.6) for k in range(105, 110)]
    return bars


def test_arm_p_capped_1_2_3_loss_at_stop_equals_budget():
    bars = _arm_p_bars()
    r = m.arm_p(bars, 100, IDEA, equity=10000., budget=50.)
    D = 0.004 * 99.; stop = 99. - D
    planned = [(99., 1), (99. - 0.25 * D, 2), (99. - 0.5 * D, 3)]
    gross_planned = sum(q * (p - stop) for p, q in planned)                      # 1.584 a unit
    fee_planned = MAKER * 99 * 1 + TAKER * (2 * planned[1][0] + 3 * planned[2][0]) + TAKER * 6 * stop
    unit = 50. / (gross_planned + fee_planned)
    assert abs(r['unit_qty'] - unit) < 1e-9
    assert abs(r['planned_loss_usd'] - 50.) < 1e-9
    assert [(f[0], f[1]) for f in r['fills']] == [(99.0, 1), (98.9, 2), (98.8, 3)]
    gross = unit * (1 * (stop - 99.) + 2 * (stop - 98.9) + 3 * (stop - 98.8))
    fees = unit * (MAKER * 99 + TAKER * (2 * 98.9 + 3 * 98.8) + TAKER * 6 * stop)
    assert abs(r['net_usd'] - (gross - fees)) < 1e-9
    assert r['status'] == 'STOP' and r['liquidated'] is False


def test_arm_p_liquidation_fixture_counted_liquidated():
    bars = _arm_p_bars()
    r = m.arm_p(bars, 100, IDEA, equity=100., budget=50., mmr=0.005)
    assert r['leverage_max'] > 50
    assert r['liquidated'] is True and r['status'] == 'LIQUIDATED'
    assert r['liq_price'] > 99. - 0.004 * 99.                    # liquidation sits above the stop


def test_bias_fast_equals_event_table_bias():
    bars = [{'t': i * 60000, 'o': 100., 'h': 100. + (i * 7 % 5), 'l': 100. - (i * 3 % 4), 'c': 100. + math.sin(i / 37.) * 3 + (i % 11) * .2, 'v': 1., 'tbv': .5} for i in range(9000)]
    fast = m.BiasIndex(bars)
    pd = {'vah': 101.0, 'val': 99.0}
    for i in (1500, 3000, 4321, 7777, 8999):
        t = bars[i]['t']; ref = bars[i - 1]['c']
        assert fast.at(t, pd, ref) == et._bias_at(bars, t, pd, None, ref)


def test_atr14_1h_plain_sma_of_true_range():
    bars = []
    for h in range(20):
        for k in range(60):
            bars.append({'t': (h * 60 + k) * 60000, 'o': 100., 'h': 100. + h, 'l': 100. - h, 'c': 100., 'v': 1., 'tbv': .5})
    # 1h bars h: high 100+h, low 100-h, close 100 (previous close 100): TR = 2h. Closed before bar 19*60: hours 0..18.
    atr = m.atr14_1h(bars, 19 * 60 * 60000)
    assert abs(atr - sum(2 * h for h in range(5, 19)) / 14) < 1e-9
