"""Declutter: page.html drops the Questions panel and draws every breakdown group the run returns, mockup/ is gone,
and SIM_DESIGN_RESEARCH.md keeps only the OPERATOR OVERRIDE block and sections 1, 6, 7 (sections 2-5 become one pointer
line). questions.json, /api/questions and the answers endpoint are untouched (desk.load_questions() below)."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402

PAGE = (HERE / 'page.html').read_text(encoding='utf-8')
DESIGN_DOC = (HERE / 'SIM_DESIGN_RESEARCH.md').read_text(encoding='utf-8')


def test_page_has_no_questions_panel():
    assert 'id="qs"' not in PAGE
    assert 'loadQuestions' not in PAGE


def test_server_side_questions_endpoints_untouched():
    # questions.json, /api/questions and the answer endpoint stay wired on the desk server (desk.py); only the page's
    # panel and its one caller (loadQuestions) go, so the page script should keep no reference to the endpoint either.
    desk_py = (HERE / 'desk.py').read_text(encoding='utf-8')
    assert "'/api/questions'" in desk_py and "'/api/answer'" in desk_py
    assert (HERE / 'questions.json').exists()
    assert '/api/questions' not in PAGE.split('<script>', 1)[1]


def test_breakdown_loops_over_every_group_key():
    m = re.search(r'function breakdown\(B\) \{.*?\n\}', PAGE, re.S)
    assert m, 'breakdown() not found in page.html'
    body = m.group(0)
    # old code: a fixed [year, side, hour] list of tuples driving the loop
    assert "[['year', 'Year'], ['side', 'Side'], ['hour', 'Hour of day']]" not in body
    # new code: drives the loop from the run's own keys
    assert 'Object.keys(B)' in body
    # a title map for known keys (year/side/hour at least), with an unknown key falling back to its own name
    maps_before = list(re.finditer(r'(const|var|let)\s+\w+\s*=\s*\{[^}]*\}', PAGE[:m.start()], re.S))
    assert maps_before, 'no title-map object literal found before breakdown()'
    title_map = maps_before[-1].group(0)   # the one closest to breakdown(): BD_TITLES, not an unrelated earlier map
    assert {'year', 'side', 'hour'} <= set(re.findall(r'(\w+)\s*:', title_map))
    assert re.search(r'\|\|\s*g\b', body)  # unknown key name used as its own fallback label


def test_mockup_not_tracked():
    out = subprocess.run(['git', '-C', str(HERE), 'ls-files', 'mockup/'], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ''


def test_design_doc_sections_2_to_5_collapsed_to_one_pointer():
    headings = re.findall(r'^## (\d+)\.', DESIGN_DOC, re.M)
    assert headings == ['1', '6', '7'], f'expected only sections 1, 6, 7; found {headings}'
    assert '# OPERATOR OVERRIDE' in DESIGN_DOC


def test_load_questions_still_returns_seeded_questions():
    qs = {q['id']: q for q in desk.load_questions()}
    assert {'first-layers', 'levels-park'} <= set(qs)
