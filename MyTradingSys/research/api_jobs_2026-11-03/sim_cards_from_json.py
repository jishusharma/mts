"""Rewrite Verdict, Keep and Totals of RESULTS_CARDS_2026-11-03.md from results/*.json.

The json is the source of truth (banner.state, banner.n, kpis, what). Claim and Finding
columns (Haiku text) are kept as they are. Rules are OURS:
  banner.state FAIL    -> FAILED
  banner.state TOO_FEW -> NOT ENOUGH DATA
  banner.state UNCLEAR -> NOT ENOUGH DATA when banner.n > 0, else EMPTY (no trade count)
  PASSED is never assigned here (no result file carries a pass state); Keep is YES only for PASSED.
Duplicate = same Study + Settings + Condition text as an earlier id (not the absent params key).
Usage: python sim_cards_from_json.py <results_dir> <cards.md>
"""
import glob, json, os, sys

ORDER = ('EMPTY', 'NOT ENOUGH DATA', 'FAILED', 'PASSED')


def verdict_word(d):
    b = d.get('banner') or {}
    st, n = b.get('state'), b.get('n')
    if st == 'FAIL':
        return 'FAILED'
    if st == 'TOO_FEW':
        return 'NOT ENOUGH DATA'
    return 'NOT ENOUGH DATA' if isinstance(n, int) and n > 0 else 'EMPTY'


def dup_key(d):
    return json.dumps([w.get('value_plain') for w in d.get('what') or []], sort_keys=True)


def keep_line(d, word, dup):
    n = (d.get('banner') or {}).get('n')
    cnt = 'n=%d' % n if isinstance(n, int) and n > 0 else 'no trade count in file'
    s = '%s; verdict %s' % (cnt, word)
    if dup:
        s += '; duplicate of %s (same study and settings)' % dup
    return ('YES (%s)' if word == 'PASSED' else 'NO (%s)') % s


def load(results_dir):
    out = {}
    for f in sorted(glob.glob(os.path.join(results_dir, '*.json'))):
        sid = os.path.basename(f)[:-5]
        if not sid.startswith('_'):
            out[sid] = json.load(open(f, encoding='utf-8'))
    return out


def expected(results_dir):
    seen, res = {}, {}
    for sid, d in load(results_dir).items():
        k = dup_key(d)
        dup = seen.get(k) if d.get('what') else None  # no what = nothing to compare
        seen.setdefault(k, sid)
        w = verdict_word(d)
        res[sid] = (w, keep_line(d, w, dup), dup)
    return res


def main(results_dir, md_path):
    exp = expected(results_dir)
    lines = open(md_path, encoding='utf-8').read().split('\n')
    head, rows, tail, mode = [], [], [], 0
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        if mode == 0:
            head.append(ln)
            if ln.startswith('|---|---|---|---|---|'):
                mode = 1
        elif mode == 1 and ln.startswith('| ') and len(cells) >= 5 and cells[0] in exp:
            rows.append(cells)
        else:
            mode = 2
            tail.append(ln)
    assert {r[0] for r in rows} == set(exp), 'card rows and result files differ'
    for r in rows:
        r[1], r[2] = exp[r[0]][0], exp[r[0]][1]
    rows.sort(key=lambda r: (r[1], r[0]))
    cnt = {w: sum(1 for r in rows if r[1] == w) for w in ORDER}
    keep_no = sum(1 for r in rows if r[2].startswith('NO'))
    dups = sum(1 for v in exp.values() if v[2])
    new, skip = [], False
    for ln in head:
        if ln.startswith('| ') and ln.split(' | ')[0].strip('| ') in ORDER:
            if skip:
                continue
            skip = True
            for w in sorted(ORDER, key=lambda w: -cnt[w]):
                if cnt[w]:
                    new.append('| %s | %d |' % (w, cnt[w]))
            new.append('| Keep: NO | %d |' % keep_no)
            new.append('| flagged duplicate settings | %d |' % dups)
            continue
        if skip and (ln.startswith('| Keep:') or ln.startswith('| flagged')):
            continue
        new.append(ln)
    for r in rows:
        new.append('| ' + ' | '.join(r) + ' |')
    new.extend(tail)
    with open(md_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(new))
    print(len(rows), 'rows;', cnt, 'keep NO', keep_no, 'dups', dups)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
