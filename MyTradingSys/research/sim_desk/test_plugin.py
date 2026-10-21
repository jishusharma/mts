"""Plug-in seam and Questions panel. A new study is one file in a studies folder, no desk.py edit; questions and answers
live on the desk page and answers are saved to a gitignored local file the next session reads."""
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402

DUMMY = '''
import numpy as np
ID = 'dummy'
TITLE = 'Dummy study'


def params():
    return [{'name': 'x', 'label': 'X', 'number': True, 'min': 0, 'max': 9, 'step': 1}]


def normalize(p):
    return {'x': float((p or {}).get('x', 1)), 'start': '2022-04-01', 'end': '2024-06-30'}


def label(q):
    return f"x {q['x']:g}"


def describe(q):
    return 'a dummy study'


def run(q, progress=None):
    n = 40
    net = np.where(np.arange(n) % 2, 1.0, -0.5) * q['x']
    return {'day': np.arange(n) // 2, 'touch_t': np.arange(n), 'net': net, 'gross': net, 'fees': np.zeros(n),
            'filled': np.ones(n, bool), 'all_days': np.arange(n // 2), 'refs': [None] * n}
'''


def test_new_study_is_one_file_in_a_folder(tmp_path):
    folder = tmp_path / 'studies'
    folder.mkdir()
    (folder / 'dummy.py').write_text(DUMMY, encoding='utf-8')
    (folder / '_helper.py').write_text('ID = "hidden"', encoding='utf-8')
    (folder / 'notastudy.py').write_text('X = 1', encoding='utf-8')
    found = desk.load_studies(folder)
    assert set(found) == {'dummy'}
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    r = desk.run_setting(found['dummy'], {'x': 2}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert r['n'] == 40 and r['verdict'] in ('PASSED', 'FAILED', 'NOT ENOUGH DATA')
    assert '| sim-desk dummy x 2 |' in trials.read_text(encoding='utf-8')


def test_levels_study_found_in_default_folder():
    assert 'levels' in desk.load_studies()


def test_questions_seeded_in_plain_words():
    qs = {q['id']: q for q in desk.load_questions()}
    assert {'first-layers', 'levels-park'} <= set(qs)
    for q in qs.values():
        assert q['context'] and q['default'] and 2 <= len(q['options']) <= 3
    assert 'park' in qs['levels-park']['default'].lower()


def test_answer_saved_and_read_back(tmp_path):
    f = tmp_path / 'answers.jsonl'
    desk.save_answer('levels-park', 'Park it', 'no more tries on this one', path=f)
    desk.save_answer('levels-park', 'Iterate once', '', path=f)
    rows = [json.loads(ln) for ln in f.read_text(encoding='utf-8').splitlines()]
    assert len(rows) == 2 and rows[0]['text'] == 'no more tries on this one'
    qs = {q['id']: q for q in desk.load_questions(answers_path=f)}
    assert qs['levels-park']['answer']['choice'] == 'Iterate once'


def test_unknown_question_refused(tmp_path):
    with pytest.raises(ValueError):
        desk.save_answer('no-such-question', 'x', '', path=tmp_path / 'a.jsonl')


def test_answers_file_is_gitignored_local():
    assert desk.ANSWERS.resolve().is_relative_to((HERE / 'cache').resolve())
