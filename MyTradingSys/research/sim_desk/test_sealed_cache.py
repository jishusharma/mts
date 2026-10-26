"""Sealed-window content guard (astra_sealed_guard.md L1-L7). All data is synthetic and lives in temp folders.
Desired safety: no cached or fetched bar/trade timestamp at or after the cut (2024-07-01 UTC) reaches a study, replay or chart;
a bad payload is refused with ValueError, never silently sanitised."""
import hashlib
import io
import json
import pickle
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'studies'))
import desk  # noqa: E402
import fetch_klines as fetch  # noqa: E402
from studies import _bars as bars  # noqa: E402
from studies import levels  # noqa: E402

CUT = 1719792000000
HOLD = 1751328000000
DAY = 86400000
SYN = np.array([[CUT - 60000, 100, 101, 99, 100], [CUT, 100, 102, 98, 101]], float)


def _idea_cache(tmp_path):
    day = CUT // DAY - 1
    idea = dict(day=day, touch_t=CUT, touch_i=0, side=1, E1=True)
    blob = dict(ideas=[idea], bars={day: np.array([[CUT, 100, 101, 99, 100, 1, 1]], float)})
    p = tmp_path / 'month.pkl'
    p.write_bytes(pickle.dumps(blob))
    return p


def test_l1_month_loader_refuses_sealed_row(tmp_path):
    (tmp_path / 'bars').mkdir()
    np.save(tmp_path / 'bars/BTCUSDT-1m-2024-06.npy', SYN)
    with patch.object(bars, 'BAR_CACHE', tmp_path / 'bars'):
        with pytest.raises(ValueError):
            bars._month('2024-06')


def test_l2_hot_memory_is_revalidated():
    with patch.object(bars, '_ALL', {'BTCUSDT': SYN}):
        with pytest.raises(ValueError):
            bars.load_1m()


def _poisoned_rsi(tmp_path):
    s = desk.STUDIES['rsi']
    q = s.normalize({})
    c = tmp_path / 'results'
    c.mkdir()
    day = CUT // DAY
    payload = dict(day=[day, day], touch_t=[CUT, HOLD], side=[1, 1], net=[.1, -.2], gross=[.2, -.1], fees=[.1, .1],
                   filled=[True, True], refs=[None, None], all_days=[day])
    (c / f'{s.ID}_{desk._key(s, q)}.json').write_text(json.dumps(payload))
    return s, c


def test_l3_result_cache_refused(tmp_path):
    s, c = _poisoned_rsi(tmp_path)
    with pytest.raises(ValueError):
        desk.run_setting(s, {}, trials_path=tmp_path / 't.md', cache_dir=c, progress=lambda _: None)


def test_l4_result_cache_refused_under_condition(tmp_path):
    s, c = _poisoned_rsi(tmp_path)
    with pytest.raises(ValueError):
        desk.run_setting(s, {}, trials_path=tmp_path / 't.md', cache_dir=c, progress=lambda _: None, cond={'side': 'long'})


def test_l5_levels_run_month_refuses_sealed_bars(tmp_path):
    p = _idea_cache(tmp_path)
    seen = []
    with patch.object(levels, '_month_file', lambda _: p), patch.object(levels, 'simulate_one', lambda db, *a, **k: seen.extend(b['t'] for b in db)):
        with pytest.raises(ValueError):
            levels._run_month((CUT - 30 * DAY, levels.normalize({})))
    assert not seen


def test_l6_levels_trade_bars_refuses_sealed_bars(tmp_path):
    p = _idea_cache(tmp_path)
    with patch.object(levels, '_month_file', lambda _: p), patch.object(levels, 'simulate_one', lambda *a, **k: None):
        with pytest.raises(ValueError):
            levels.trade_bars([CUT - 30 * DAY, 0], levels.normalize({}))


def test_l7_fetch_refuses_sealed_row(tmp_path):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as z:
        z.writestr('BTCUSDT-1m-2024-06.csv', f'{CUT},100,101,99,100\n')
    zdata = b.getvalue()
    get = lambda url: hashlib.sha256(zdata).hexdigest().encode() + b' f.zip' if url.endswith('.CHECKSUM') else zdata  # noqa: E731
    with patch.object(fetch, 'months', lambda: iter(['2024-06'])), patch.object(fetch, 'get', get):
        with pytest.raises(ValueError):
            fetch.fetch('BTCUSDT', root=tmp_path)
    assert not list(tmp_path.glob('*.csv'))


def test_guard_passes_last_dev_minute():
    bars.guard_ms([CUT - 60000], 'control')
