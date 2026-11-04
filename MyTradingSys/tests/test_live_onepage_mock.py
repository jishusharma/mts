import pathlib
import re

ART = pathlib.Path(__file__).resolve().parents[1] / 'system' / 'artifacts'
HTML = ART / 'LIVE_ONEPAGE_MOCK_2026-11-04.html'
MD = ART / 'LIVE_ONEPAGE_MOCK_2026-11-04.md'
TABS = ['market', 'signals', 'positions', 'news', 'layers', 'health']


def test_six_tab_ids():
    h = HTML.read_text(encoding='utf-8')
    for t in TABS:
        assert f'id="tab-{t}"' in h and f'id="panel-{t}"' in h


def test_no_fixed_width_over_viewport():
    h = HTML.read_text(encoding='utf-8')
    css = re.search(r'<style>(.*?)</style>', h, re.S).group(1)
    assert 'overflow:hidden' in css and 'viewport' in h
    for m in re.finditer(r'(?<![-\w])(?:min-)?width:\s*(\d+(?:\.\d+)?)(px|vw|%)', css):
        v, unit = float(m.group(1)), m.group(2)
        assert not (unit == 'px' and v > 320) and not (unit in ('vw', '%') and v > 100), m.group(0)


def test_every_sample_badge_in_md():
    h = HTML.read_text(encoding='utf-8')
    md = MD.read_text(encoding='utf-8')
    ids = re.findall(r'data-sample="([^"]+)"', h)
    assert ids
    for i in ids:
        assert i in md
    assert len(md.strip().splitlines()) <= 10 + 1
