"""Acceptance check for NEWS_DESIGN.md (card news-design-synthesis-1108).

Usage: python check_design.py            (reads NEWS_DESIGN.md next to this file)

Checks the "done when" of the card, offline:
  1. layout: the first body line is one bold result line; no prose paragraph longer than 2 lines;
     no table cell longer than CELL_MAX characters (phone reader);
  2. class table: every class in news_events.csv has exactly one KEEP / CHANGE / DROP call with an
     evidence count (a number) in the row;
  3. rule tables (weight, flash, bias, repeat, strip): every rule row ends with an evidence cell that
     cites a count (a number) or says OURS; decimals cited must exist in REPORT.md or a review;
  4. bias section names LONG, SHORT and HOLD and says when to say HOLD;
  5. flash section answers when, how long and what stops it;
  6. a disagreements table with at least 3 rows;
  7. a one-screen text mock of the News tab: one fenced block, <= MOCK_LINES lines, <= MOCK_COLS wide.
Exit 0 = GREEN.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.join(HERE, 'NEWS_DESIGN.md')
CALLS = {'KEEP', 'CHANGE', 'DROP'}
CELL_MAX = 170
MOCK_LINES = 28
MOCK_COLS = 96
RULE_SECTIONS = r'(weight|flash|bias|repeat|strip)'


def section(text, title_re):
    m = re.search(r'^##\s+[^\n]*' + title_re + r'[^\n]*$', text, re.I | re.M)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r'^##\s', rest, re.M)
    return rest[:n.start()] if n else rest


def sections(text):
    """[(title, body)] for every ## section."""
    out = []
    for m in re.finditer(r'^##\s+([^\n]*)$', text, re.M):
        rest = text[m.end():]
        n = re.search(r'^##\s', rest, re.M)
        out.append((m.group(1), rest[:n.start()] if n else rest))
    return out


def table_rows(block):
    out = []
    for line in (block or '').splitlines():
        line = line.strip()
        if line.startswith('|') and not re.match(r'^\|[\s\-:|]+\|$', line):
            out.append([c.strip() for c in line.strip('|').split('|')])
    return out[1:] if out else []


def all_cells(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('|') and not re.match(r'^\|[\s\-:|]+\|$', line):
            for c in line.strip('|').split('|'):
                yield c.strip()


def main():
    results = []

    def check(name, ok, detail=''):
        results.append(ok)
        print('%s  %s %s' % ('PASS' if ok else 'FAIL', name, detail))

    if not os.path.exists(DESIGN):
        check('NEWS_DESIGN.md exists', False, DESIGN)
        print('RESULT: RED')
        return 1
    text = open(DESIGN, encoding='utf-8').read()
    check('NEWS_DESIGN.md exists', True, '%d chars' % len(text))
    rows = list(csv.DictReader(open(os.path.join(HERE, 'news_events.csv'), encoding='utf-8')))
    classes = {r['class'] for r in rows}
    evidence = ''
    for fn in ('REPORT.md', 'REVIEW_OPUS.md', 'REVIEW_MARKET.md'):
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            evidence += open(p, encoding='utf-8').read() + '\n'

    # 1. layout
    body = [l for l in text.splitlines()]
    first = next((l for l in body[1:] if l.strip()), '')
    check('first body line is one bold result line', first.startswith('**') and first.rstrip().endswith('**'), repr(first[:60]))
    # prose paragraphs: runs of plain lines (not table, heading, list, code) longer than 2 lines
    long_paras, run, in_code = [], 0, False
    for l in body:
        s = l.strip()
        if s.startswith('```'):
            in_code = not in_code
            run = 0
            continue
        plain = bool(s) and not in_code and not s.startswith(('|', '#', '-', '*', '>')) and not re.match(r'^\d+\.\s', s)
        run = run + 1 if plain else 0
        if run > 2:
            long_paras.append(s[:40])
    check('no prose paragraph over 2 lines', not long_paras, 'found=%s' % long_paras[:3])
    long_cells = [c[:40] for c in all_cells(text) if len(c) > CELL_MAX]
    check('no table cell over %d chars' % CELL_MAX, not long_cells, 'found=%s' % long_cells[:3])

    # 2. class table
    ct = table_rows(section(text, r'class'))
    got = {}
    for r in ct:
        if not r:
            continue
        name = r[0].strip('`*')
        if name in classes:
            call = next((c.strip('*').upper() for c in r[1:] if c.strip('*').upper() in CALLS), None)
            has_n = any(re.search(r'\d', c) for c in r[1:])
            got.setdefault(name, []).append((call, has_n))
    missing = sorted(classes - set(got))
    dup = sorted(k for k, v in got.items() if len(v) != 1)
    nocall = sorted(k for k, v in got.items() if v[0][0] is None)
    nocount = sorted(k for k, v in got.items() if not v[0][1])
    check('every class has one row in the class table', not missing and not dup, 'missing=%s dup=%s' % (missing, dup))
    check('every class row has a KEEP/CHANGE/DROP call', bool(got) and not nocall, 'nocall=%s' % nocall)
    check('every class row has an evidence count', bool(got) and not nocount, 'nocount=%s' % nocount)

    # 3. rule tables: last cell cites a count or OURS; decimals exist in the evidence files
    n_rules, bad_ev, bad_num = 0, [], []
    for title, blk in sections(text):
        if not re.search(RULE_SECTIONS, title, re.I):
            continue
        for r in table_rows(blk):
            if len(r) < 2:
                continue
            n_rules += 1
            ev = r[-1]
            if 'OURS' in ev:
                continue
            if not re.search(r'\d', ev):
                bad_ev.append('%s: %s' % (title[:20], r[0][:30]))
                continue
            for num in re.findall(r'\d+\.\d+', ev):
                if num not in evidence:
                    bad_num.append('%s: %s' % (r[0][:25], num))
    check('rule rows found in weight/flash/bias/repeat/strip sections (>= 12)', n_rules >= 12, 'n=%d' % n_rules)
    check('every rule row cites a count or says OURS', not bad_ev, 'bad=%s' % bad_ev[:4])
    check('every decimal cited in a rule exists in REPORT.md or a review', not bad_num, 'bad=%s' % bad_num[:4])

    # 4. bias
    bias = section(text, r'bias') or ''
    check('bias section names LONG, SHORT and HOLD', all(w in bias for w in ('LONG', 'SHORT', 'HOLD')))
    check('bias section says when to say HOLD', bool(re.search(r'HOLD\s+when', bias)) or 'say HOLD' in bias)

    # 5. flash
    flash = section(text, r'flash') or ''
    check('flash section answers when, how long, what stops it',
          all(re.search(w, flash, re.I) for w in (r'\bwhen\b', r'how long', r'stops?\b')))

    # 6. disagreements
    dis = table_rows(section(text, r'disagree'))
    check('disagreements table with >= 3 rows', len(dis) >= 3, 'n=%d' % len(dis))

    # 7. mock
    mocks = re.findall(r'```[^\n]*\n(.*?)```', section(text, r'mock') or '', re.S)
    ok = False
    if mocks:
        lines = mocks[0].rstrip('\n').splitlines()
        width = max(len(l) for l in lines) if lines else 0
        ok = len(lines) <= MOCK_LINES and width <= MOCK_COLS
        check('one-screen mock of the News tab (<= %d lines, <= %d cols)' % (MOCK_LINES, MOCK_COLS), ok,
              'lines=%d width=%d' % (len(lines), width))
    else:
        check('one-screen mock of the News tab', False, 'no fenced block in the mock section')

    print('RESULT: %s' % ('GREEN' if all(results) else 'RED'))
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
