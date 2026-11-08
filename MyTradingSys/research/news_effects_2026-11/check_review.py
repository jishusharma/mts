"""Acceptance check for an independent review of the news-effect catalogue.

Usage: python check_review.py REVIEW_OPUS.md   (path relative to this folder or absolute)

Checks the review for the card news-effect-review-opus-1108 "done when":
  1. a verdict table that gives every catalogue class exactly one of SAFE / WEAK / UNKNOWN;
  2. a section with exactly 5 numbered ways the catalogue could mislead;
  3. at least 10 re-checked events, each an event_id that exists in news_events.csv,
     with an https primary source and a status (CONFIRMED / WRONG / UNVERIFIED);
  4. a section with the method changes required before any weight rule (at least 3 items);
  5. an independence statement (written without reading the other review).
Offline: reads only the review and news_events.csv. Exit 0 = GREEN.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = {'SAFE', 'WEAK', 'UNKNOWN'}
STATUSES = {'CONFIRMED', 'WRONG', 'UNVERIFIED'}


def section(text, title_re):
    m = re.search(r'^##\s+[^\n]*' + title_re + r'[^\n]*$', text, re.I | re.M)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r'^##\s', rest, re.M)
    return rest[:n.start()] if n else rest


def table_rows(block):
    out = []
    for line in (block or '').splitlines():
        line = line.strip()
        if line.startswith('|') and not re.match(r'^\|[\s\-:|]+\|$', line):
            out.append([c.strip() for c in line.strip('|').split('|')])
    return out[1:] if out else []  # drop header


def main(argv):
    if len(argv) < 2:
        print('usage: check_review.py REVIEW_OPUS.md')
        return 2
    path = argv[1] if os.path.isabs(argv[1]) else os.path.join(HERE, argv[1])
    results = []

    def check(name, ok, detail=''):
        results.append(ok)
        print('%s  %s %s' % ('PASS' if ok else 'FAIL', name, detail))

    if not os.path.exists(path):
        check('review exists', False, path)
        print('RESULT: RED')
        return 1
    text = open(path, encoding='utf-8').read()
    rows = list(csv.DictReader(open(os.path.join(HERE, 'news_events.csv'), encoding='utf-8')))
    ids = {r['event_id'] for r in rows}
    classes = {r['class'] for r in rows}
    check('review exists', True, '%d chars' % len(text))

    # 1. verdict per class
    vt = table_rows(section(text, r'verdict'))
    got = {}
    for r in vt:
        if len(r) >= 2 and r[0].strip('`*') in classes:
            got[r[0].strip('`*')] = r[1].strip('*').upper()
    missing = sorted(classes - set(got))
    bad = sorted(c for c, v in got.items() if v not in VERDICTS)
    check('verdict for every class', not missing, 'missing=%s' % missing)
    check('verdicts are SAFE/WEAK/UNKNOWN', bool(got) and not bad, 'bad=%s' % bad)

    # 2. five ways to mislead
    mb = section(text, r'mislead')
    items = re.findall(r'^\s*(\d+)\.\s+\S', mb or '', re.M)
    check('exactly 5 numbered ways to mislead', [int(i) for i in items] == [1, 2, 3, 4, 5], 'found=%s' % items)

    # 3. ten re-checked events
    rt = table_rows(section(text, r're-check'))
    good, probs = 0, []
    seen = set()
    for r in rt:
        eid = r[0].strip('`*') if r else ''
        line = ' | '.join(r)
        if eid not in ids:
            probs.append('unknown id %s' % eid)
            continue
        if eid in seen:
            probs.append('dup %s' % eid)
            continue
        if 'https://' not in line:
            probs.append('%s no https source' % eid)
            continue
        if not any(s in line.upper() for s in STATUSES):
            probs.append('%s no status' % eid)
            continue
        seen.add(eid)
        good += 1
    check('>= 10 re-checked events (id in csv, https source, status)', good >= 10, 'ok=%d problems=%s' % (good, probs[:5]))

    # 4. method changes
    mc = section(text, r'method change')
    n_mc = len(re.findall(r'^\s*(?:\d+\.|-)\s+\S', mc or '', re.M))
    check('method changes before any weight rule (>= 3 items)', n_mc >= 3, 'items=%d' % n_mc)

    # 5. independence
    check('independence statement', bool(re.search(r'without reading (the )?other review', text, re.I)))

    ok = all(results)
    print('RESULT: %s (%d fail)' % ('GREEN' if ok else 'RED', results.count(False)))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
