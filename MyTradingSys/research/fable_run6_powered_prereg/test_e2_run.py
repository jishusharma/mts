"""Fail-first tests for e2_run.py (PRE_REG.md section 2). Expected numbers are computed by hand from FORMULAS 18.5
(taker 0.05 % + slip 0.02 % on market and stop fills, maker 0.02 % on a target fill), never from e2_run.py."""
import datetime as dt
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import counts_only as co  # noqa: E402
import e2_run as e2  # noqa: E402

H4 = 4 * 3600 * 1000


def test_loader_refuses_sealed_bars_and_reads_only_ohlc(tmp_path, monkeypatch):
    """(1) a bar at/after 2024-07-01 never survives the load, and extra columns (volume, taker buy...) are not kept."""
    cut = co.CUT_MS
    for sym in co.SYMBOLS:
        for ym in co.months(co.WARMUP_FROM, co.LAST_MONTH):
            (tmp_path / f'{sym}-4h-{ym}.missing').write_text('404\n')
    f = tmp_path / 'BTCUSDT-4h-2024-06.csv'
    (tmp_path / 'BTCUSDT-4h-2024-06.missing').unlink()
    f.write_text('open_time,open,high,low,close,volume,quote_volume\n'
                 f'{cut - 2 * H4},1,2,0.5,1.5,999,999\n{cut - H4},1.5,2,1,1.8,999,999\n'
                 f'{cut},1.8,3,1,2,999,999\n{cut + H4},2,3,1,2,999,999\n', encoding='utf-8')
    monkeypatch.setattr(co, 'DATA', tmp_path)
    rows = e2.load_bars('BTCUSDT')
    assert len(rows) == 2 and max(r[0] for r in rows) < cut
    assert all(len(r) == 5 for r in rows)
    with pytest.raises(ValueError):
        e2.assert_no_sealed([(cut, 1, 1, 1, 1)], 'x')


def _bars(first):
    return [(i * H4, *b) for i, b in enumerate(first)]


def test_long_stop_wins_same_bar_net_r_by_hand():
    """(2a) long, entry open 100 -> fill 100.02, stop 95 -> R 5.02; bar holds target (>=110.06) and stop: stop wins, filled 95*(1-0.0002)=94.981.
    pnl -5.039; fees 0.0005*100.02 + 0.0005*94.981 = 0.0975005; net R = -5.1365005/5.02; gross R = (95-100)/5.02."""
    bars = _bars([(100, 111, 94, 100)])
    t = e2.run_trade(+1, bars, 0, 95.0)
    assert t['kind'] == 'stop'
    assert t['net_r'] == pytest.approx(-5.1365005 / 5.02, abs=1e-6)
    assert t['gross_r'] == pytest.approx(-5.0 / 5.02, abs=1e-6)


def test_short_target_maker_net_r_by_hand():
    """(2b) short, open 200 -> fill 199.96, stop 210 -> R 10.04, target 199.96-20.08 = 179.88 (maker). pnl 20.08; fees 0.0005*199.96 + 0.0002*179.88 = 0.135956."""
    bars = _bars([(200, 205, 179, 190)])
    t = e2.run_trade(-1, bars, 0, 210.0)
    assert t['kind'] == 'target'
    assert t['net_r'] == pytest.approx((20.08 - 0.135956) / 10.04, abs=1e-6)
    assert t['gross_r'] == pytest.approx(20.12 / 10.04, abs=1e-6)


def test_time_stop_and_floor():
    """100 bars held (entry bar + 99), exit at that close with taker + slip; a stop closer than 0.56 % of the fill is skipped."""
    bars = _bars([(100, 101, 99.5, 100)] * 150)
    t = e2.run_trade(+1, bars, 0, 95.0)
    assert t['kind'] == 'time' and t['exit_i'] == 99
    # long, fill 100.02, exit 100*(1-0.0002)=99.98: pnl -0.04, fees 0.0005*(100.02+99.98)=0.1 -> net (-0.14)/5.02
    assert t['net_r'] == pytest.approx(-0.14 / 5.02, abs=1e-6)
    assert e2.run_trade(+1, bars, 0, 99.6) is None            # 0.42 % < 0.56 % floor


@pytest.mark.skipif(not (co.DATA / 'BTCUSDT-4h-2024-06.csv').exists(), reason='cached klines not on this machine')
def test_event_count_matches_counts_only_within_one_percent():
    """(3) the event set is the counts_only set: 807 events / 539 days (+-1 %)."""
    n_ev, days = 0, set()
    for sym in co.SYMBOLS:
        bars = e2.load_bars(sym)
        mine = [(bars[i][0], s) for i, s in e2.signals(bars)]
        theirs = [t for t, _ in co.krown_events(bars, 'S8') if e2.LO_MS <= t < e2.HI_MS]
        assert [t for t, _ in mine if e2.LO_MS <= t < e2.HI_MS] == theirs
        n_ev += len(theirs)
        days |= {t // co.DAY for t in theirs}
    assert abs(n_ev - 807) <= 8 and abs(len(days) - 539) <= 5
