import csv
import json
import pathlib
import re

MTS = pathlib.Path(__file__).resolve().parents[1]
ART = MTS / 'system' / 'artifacts'
HTML = ART / 'LIVE_ONEPAGE_MOCK_2026-11-04.html'
MD = ART / 'LIVE_ONEPAGE_MOCK_2026-11-04.md'
TABS = ['market', 'signals', 'positions', 'news', 'layers', 'health']


def _html():
    return HTML.read_text(encoding='utf-8')


def _panels(h):
    parts = re.split(r'<section id="panel-', h)[1:]
    return {p.split('"', 1)[0]: p.split('</section>', 1)[0] for p in parts}


def test_six_tab_ids():
    h = _html()
    for t in TABS:
        assert f'id="tab-{t}"' in h and f'id="panel-{t}"' in h


def test_no_fixed_width_over_viewport():
    h = _html()
    css = re.search(r'<style>(.*?)</style>', h, re.S).group(1)
    assert 'overflow:hidden' in css and 'viewport' in h
    for m in re.finditer(r'(?<![-\w])(?:min-)?width:\s*(\d+(?:\.\d+)?)(px|vw|%|rem)', css):
        v, unit = float(m.group(1)), m.group(2)
        assert not (unit == 'px' and v > 320) and not (unit == 'rem' and v > 20) \
            and not (unit in ('vw', '%') and v > 100), m.group(0)


def test_every_sample_badge_in_md():
    h = _html()
    md = MD.read_text(encoding='utf-8')
    ids = re.findall(r'data-sample="([^"]+)"', h)
    assert ids
    for i in ids:
        assert i in md
    assert len(md.strip().splitlines()) <= 10 + 1


# operator style (memory mts-artifact-design-dense-symbols), added in v2
def test_base_font_at_least_16px():
    css = re.search(r'<style>(.*?)</style>', _html(), re.S).group(1)
    body = re.search(r'(?:^|[}\s])body\{([^}]*)\}', css).group(1)
    size = int(re.search(r'font:\s*(\d+)px', body).group(1))
    assert size >= 16


def test_every_tab_has_kpi_row_and_delta_box():
    panels = _panels(_html())
    assert sorted(panels) == sorted(TABS)
    for pid, body in panels.items():
        n = body.count('class="kpi"')
        assert 3 <= n <= 4, (pid, n)
        assert 'class="box delta"' in body and '<h3>Δ ' in body, pid


def test_trailing_1m_5m_legend_and_data_age():
    h = _html()
    foot = re.search(r'<footer>(.*?)</footer>', h, re.S).group(1)
    assert '<b>1m</b>' in foot and '<b>5m</b>' in foot
    assert re.search(r'class="age"[^>]*>data \d{4}-\d\d-\d\d \d\d:\d\dZ · \d+ d old<', h)


def test_tabs_use_symbols_not_emoji():
    nav = re.search(r'<nav class="tabs".*?</nav>', _html(), re.S).group(0)
    assert not [c for c in nav if ord(c) >= 0x1F000]


def test_numbers_come_from_repo_files():
    h = _html()
    days = sorted((MTS / 'runtime' / 'orderflow_live').glob('20*.csv'))
    last = list(csv.DictReader(open(days[-1])))[-1]
    assert f'<span class="val ">{float(last["c"]):,.0f}</span>' in h
    c30 = json.load(open(MTS / 'research' / 'eagle_eyes_picture_2026-10-28' / 'c30_validation_verdict.json'))
    assert f'<span class="lab">H1 trades</span><span class="val ">{c30["H1"]["n"]}</span>' in h
