"""Example-trade charts: 3 typical winners + 3 typical losers, each a small inline SVG whose stop and exit equal
ladder.simulate() for that trade. The data test runs only when the local idea cache is built."""
import re
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import charts  # noqa: E402
import desk  # noqa: E402
from studies import levels as study_levels  # noqa: E402

FROZEN_P = {'entry': 'E1', 'scale': 'S2', 'stop': 'K5', 'exit': 'X0_2R'}


def _attr(svg, name):
    return float(re.search(rf'data-{name}="([^"]+)"', svg).group(1))


def _trade(n=600, exit_reason='STOP'):
    t0 = 1_700_000_000_000 - 1_700_000_000_000 % 86400000
    px = 30000 + np.cumsum(np.sin(np.arange(n) / 7.0) * 5)
    bars = [{'t': t0 + k * 60000, 'o': float(p), 'h': float(p) + 8, 'l': float(p) - 8, 'c': float(p) + 1} for k, p in enumerate(px)]
    return {'bars': bars, 'side': 1, 'level': 30010.0, 'entries': [(bars[100]['t'], 30010.0)], 'stop': 29950.5, 'target': 30130.25,
            'exits': [(bars[n - 1]['t'], 29950.5, exit_reason)], 'net_r': -1.12}


def test_pick_median_winners_and_losers():
    net = np.array([-1.0, -0.9, -1.1, -0.2, 2.0, 1.9, 0.1, 2.1, -1.05, 1.8, 3.0])
    w, l = charts.pick(net)
    assert len(w) == 3 and len(l) == 3
    assert all(net[k] > 0 for k in w) and all(net[k] < 0 for k in l)
    assert 10 not in w and 3 not in l     # extremes are not chosen: closest to the median of each side


def test_svg_small_and_carries_exact_levels():
    tr = _trade()
    svg = charts.svg(tr)
    assert svg.startswith('<svg') and len(svg.encode()) < 10240
    assert _attr(svg, 'stop') == tr['stop'] and _attr(svg, 'exit') == tr['exits'][-1][1]
    assert _attr(svg, 'target') == tr['target']
    assert '-1.12 R long' in svg and 'stopped' in svg
    assert '2023-11-14 ' in svg and 'UTC' in svg            # date and time of the first fill


def test_fill_level_drawn_when_not_the_touched_level():
    tr = _trade()
    tr['entries'] = [(tr['bars'][120]['t'], 29990.0)]
    svg = charts.svg(tr)
    assert _attr(svg, 'fill') == 29990.0 and 'filled' in svg


def test_long_trade_still_small():
    svg = charts.svg(_trade(n=1440, exit_reason='TIME'))
    assert len(svg.encode()) < 10240 and 'day end' in svg


needs_cache = pytest.mark.skipif(not study_levels.cache_ready(), reason='idea cache not built (desk.py --build)')


@needs_cache
def test_frozen_run_charts_match_simulate(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    out = desk.run_setting(study_levels, FROZEN_P, trials_path=trials, cache_dir=tmp_path / 'c', charts=True)
    cs = out['charts']
    assert len(cs) == 6
    q = study_levels.normalize(FROZEN_P)
    for c in cs:
        assert len(c['svg'].encode()) < 10240
        _, _, r = study_levels.trade_bars(c['ref'], q)
        assert _attr(c['svg'], 'stop') == r['stop']
        assert _attr(c['svg'], 'exit') == r['exits'][-1][0]
        assert (c['net_r'] > 0) == (r['net_r'] > 0)
        assert r['filled_qty'] > 0 and 'UTC' in c['svg']
