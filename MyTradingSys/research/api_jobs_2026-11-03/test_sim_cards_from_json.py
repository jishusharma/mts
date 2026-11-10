"""Card Verdict/Keep must match results/*.json (banner.state, banner.n, kpis). Expected values are
derived here from the json directly, not from sim_cards_from_json.py."""
import glob, json, os, subprocess, sys, tempfile
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'sim_desk', 'results')
MD = os.path.join(HERE, '..', 'sim_desk', 'api_review', 'RESULTS_CARDS_2026-11-03.md')
ALL = sorted(f for f in glob.glob(os.path.join(RES, '*.json')) if not os.path.basename(f).startswith('_'))


def cards():
    out = {}
    for ln in open(MD, encoding='utf-8').read().split('\n'):
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        if ln.startswith('| ') and len(c) >= 5:
            out[c[0]] = c
    return out


CARDS = cards()
# the cards file is the 2026-11-03 set; results added later (id ends -2026-11-04 or newer) have no row here
FILES = [f for f in ALL if os.path.basename(f)[:-5] in CARDS]


# card rows that never had a results json (no result file, not a failure); the header row is 'id'
NO_JSON = {'id', 'rsi-deep-confluence-2026-11-04', 'rsi-deep-confirmations-2026-11-04',
           'rsi-deep-context-tables-2026-11-04', 'rsi-deep-divergence-context-2026-11-04'}


def rows_problems(card_ids, result_ids):
    """Set-based (arch review row 2): every card row has its result json, and every result without a card
    is a later one (id ends 2026-11-04 or newer). A new result landing never changes the outcome."""
    missing = sorted(set(card_ids) - set(result_ids) - NO_JSON)
    late = [i for i in result_ids if i not in set(card_ids)]
    old_uncarded = sorted(i for i in late if i[-10:] < '2026-11-04')
    return missing, old_uncarded


def test_all_card_rows_present():
    ids = [os.path.basename(f)[:-5] for f in ALL]
    missing, old_uncarded = rows_problems(CARDS, ids)
    assert not missing, missing
    assert not old_uncarded, old_uncarded
    assert len(FILES) >= 337   # floor, the 2026-11-03 set; never an exact count


def test_new_result_landing_does_not_break_rows_check():
    """The old exact asserts (len(late) == 21) failed the moment one more result json landed."""
    ids = [os.path.basename(f)[:-5] for f in ALL]
    assert rows_problems(CARDS, ids + ['some-new-study-2026-12-01']) == rows_problems(CARDS, ids)
    # a card row that lost its json, or an old uncarded result, is still caught
    assert rows_problems(CARDS, ids[1:])[0] == [ids[0]] if ids[0] in CARDS else True
    assert rows_problems(CARDS, ids + ['stray-2026-10-01'])[1] == ['stray-2026-10-01']


@pytest.mark.parametrize('f', FILES, ids=lambda f: os.path.basename(f)[:-5])
def test_card_matches_json(f):
    sid = os.path.basename(f)[:-5]
    d = json.load(open(f, encoding='utf-8'))
    b = d['banner']
    n = b['n']
    if b['state'] == 'FAIL':
        want = 'FAILED'
    elif b['state'] == 'TOO_FEW' or (isinstance(n, int) and n > 0):
        want = 'NOT ENOUGH DATA'
    else:
        want = 'EMPTY'
    c = CARDS[sid]
    assert c[1] == want, 'Verdict %s != json %s (state=%s n=%s)' % (c[1], want, b['state'], n)
    # a card must never say "no trades" when the file states n > 0
    if isinstance(n, int) and n > 0:
        assert 'n=%d' % n in c[2], 'Keep omits banner.n=%d: %s' % (n, c[2])
        assert 'no trade' not in c[2].lower() and '0 trade' not in c[2].lower()
    assert c[2].startswith('NO') or want == 'PASSED'


def test_totals_match():
    txt = open(MD, encoding='utf-8').read()
    for w in ('EMPTY', 'NOT ENOUGH DATA', 'FAILED'):
        k = sum(1 for c in CARDS.values() if c[1] == w)
        assert '| %s | %d |' % (w, k) in txt


def test_job_builder_uses_banner_n():
    src = json.load(open(os.path.join(RES, 'desk-cowen_bmsb-a0c48d6a.json'), encoding='utf-8'))
    assert src['banner']['n'] == 10
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, 'r'))
        for name in ('a-1', 'a-2'):
            json.dump(src, open(os.path.join(t, 'r', name + '.json'), 'w', encoding='utf-8'))
        out = os.path.join(t, 'o.jsonl')
        subprocess.run([sys.executable, os.path.join(HERE, 'build_sim_cards_jobs.py'), os.path.join(t, 'r'), out],
                       check=True, capture_output=True)
        rows = [json.loads(l) for l in open(out, encoding='utf-8')]
    assert '(banner.n): 10.' in rows[0]['prompt'] and 'Trade rows in file: 0' not in rows[0]['prompt']
    assert 'duplicate of a-1' in rows[1]['prompt'] and 'duplicate' not in rows[0]['prompt']
