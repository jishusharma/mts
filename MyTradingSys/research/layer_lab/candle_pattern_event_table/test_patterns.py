from patterns import engulfing, pin_bar, inside_bar, doji
from event_table import build_event_table


def b(o,h,l,c,t): return {'o':o,'h':h,'l':l,'c':c,'t':t}


def test_engulf_and_nearmiss():
    bars=[b(10,11,8,9,0),b(8.5,11,8,10.5,1)]
    assert engulfing(bars,1)==1
    assert engulfing([bars[0],b(8.5,10,8,9.5,1)],1)==0


def test_pin_bar_and_nearmiss():
    assert pin_bar([b(9,10,5,9.5,0)],0)==1
    assert pin_bar([b(9,10,8.5,9.5,0)],0)==0


def test_inside_bar_and_nearmiss():
    bars=[b(5,10,2,6,0),b(5,9,3,7,1)]
    assert inside_bar(bars,1)==1
    assert inside_bar([bars[0],b(5,11,3,7,1)],1)==0


def test_doji_and_nearmiss():
    assert doji([b(5,10,0,5.5,0)],0)==1
    assert doji([b(5,10,0,7,0)],0)==0


def test_event_stamped_close_forward_begins_next_bar():
    bars=[b(1,2,0,1,10),b(1,3,0.5,2,20),b(2,5,1,4,30)]
    event={'pattern':'doji','index':0,'side':1}
    row=build_event_table([event],bars,horizon=2)[0]
    assert row['event_time']==10
    assert row['mfe_R']==2.0
    assert row['bars_forward']==2


def test_short_event_excursions_use_favorable_low_and_adverse_high():
    bars=[b(10,12,8,10,10),b(10,11,7,8,20)]
    row=build_event_table([{'pattern':'bear','index':0,'side':-1}],bars,horizon=1)[0]
    assert row['event_time']==10
    assert row['mfe_R']==0.75
    assert row['mae_R']==0.25
    assert row['bars_forward']==1


H = 3_600_000
DEV_END = 1719792000000


def _npz(tmp_path, times):
    import numpy as np
    n = len(times)
    p = tmp_path / "k.npz"
    np.savez(p, t=np.array(times, dtype=np.int64), o=np.full(n, 10.0), h=np.full(n, 11.0),
             l=np.full(n, 9.0), c=np.full(n, 10.5), v=np.ones(n))
    return p


def test_loader_drops_bars_on_or_after_dev_end(tmp_path):
    from event_table import load_dev_npz
    p = _npz(tmp_path, [DEV_END - 2 * H, DEV_END - H, DEV_END, DEV_END + H])
    bars = load_dev_npz(p, "1h")
    assert [x['t'] for x in bars] == [DEV_END - 2 * H, DEV_END - H]


def test_4h_bucket_with_missing_1h_bar_is_skipped(tmp_path):
    from event_table import load_dev_npz
    start = 1640995200000  # 2022-01-01 00:00 UTC
    times = [start + k * H for k in range(4)] + [start + (4 + k) * H for k in range(4) if k != 2]
    bars = load_dev_npz(_npz(tmp_path, times), "4h")
    assert [x['t'] for x in bars] == [start]
    assert bars[0]['close_t'] == start + 4 * H


def test_event_time_is_close_time_when_given():
    bars = [dict(b(1, 2, 0, 1, 10), close_t=15), b(1, 3, 0.5, 2, 20)]
    row = build_event_table([{'pattern': 'doji', 'index': 0, 'side': 1}], bars, horizon=1)[0]
    assert row['event_time'] == 15


def test_gap_in_forward_window_is_not_in_data():
    bars = [b(1, 2, 0, 1, 0), b(1, 3, 0.5, 2, 10), b(2, 5, 1, 4, 30)]
    ev = [{'pattern': 'doji', 'index': 0, 'side': 1}]
    assert build_event_table(ev, bars, horizon=2, step=10)[0]['status'] == 'NOT_IN_DATA'
    assert build_event_table(ev, bars[:2], horizon=1, step=10)[0]['status'] == 'OK'
    assert build_event_table(ev, bars[:2], horizon=2, step=10)[0]['status'] == 'NOT_IN_DATA'


def test_run_counts_patterns_per_timeframe(tmp_path):
    import numpy as np
    from event_table import run
    start = 1640995200000
    n = 48
    t = np.array([start + k * H for k in range(n)], dtype=np.int64)
    o = np.full(n, 10.0); c = np.full(n, 10.1); h = np.full(n, 11.0); l = np.full(n, 9.0)
    p = tmp_path / "k.npz"
    np.savez(p, t=t, o=o, h=h, l=l, c=c, v=np.ones(n))
    rows = run(p, "1h", horizon=2)
    doji_rows = [r for r in rows if r['pattern'] == 'doji']
    assert len(doji_rows) == n and sum(r['status'] == 'OK' for r in doji_rows) == n - 2
