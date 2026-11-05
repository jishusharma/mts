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


def test_all_337_rows_present():
    assert len(FILES) == 337
    late = [os.path.basename(f)[:-5] for f in ALL if f not in FILES]
    assert all(i[-10:] >= '2026-11-04' for i in late), late
    assert len(late) == 20, late   # 2026-11-05 pz-4-backtest, oi-pivot-1h-4h-long-oi-followup, wt-extreme-cross-volmatch, level-approach-eth-replicate; 2026-11-04 context re-run rows: rsi-div x2, wavetrend-c30 x2, bb x4 (incl. eth-pool), fabio-l1-strict, bear-proxy-context-tuning, rsi-40-60-line-behaviour; desk-trades x5 (fabio_v3 a-d/b/c, tom_vp-fade, tom_spike_level)


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
