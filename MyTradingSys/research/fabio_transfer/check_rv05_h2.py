"""RV05 H2 check: five Fabio ledger rows x {entry, stop} are adjudicated against full-res position-line reads.

Usage: python check_rv05_h2.py [--git-ref REF]   (exit 0 = consistent; --git-ref also compares the CSV cells to REF, default off)
Directory override for tests: env FABIO_LEDGER_DIR.

Status is recomputed here from RV05_H2_READS.csv, the earlier reads below and the CSV value before the card (column "CSV before"
of the table in FABIO_TRADE_LEDGER.md), never taken on trust from the table.
"""
import csv
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(os.environ.get('FABIO_LEDGER_DIR') or Path(__file__).resolve().parent)
TOL = 0.25  # one NQ tick pair, card step 2
ROWS = ['F8', 'F12', 'F12-m2', 'F13', 'F13-m1']
FIELDS = ['entry', 'stop']
STATUSES = {'KEPT', 'CHANGED', 'CONTESTED', 'NOT_IN_DATA'}
# Earlier reads (AUDIT H1 report, RV05 report) of each field; typed from those reports, not from the CSV.
EARLIER = {
    ('F8', 'entry'): [25034.53, 25034.53], ('F8', 'stop'): [25021.75],
    ('F12', 'entry'): [25105.78, 25105.18], ('F12', 'stop'): [25089.75],
    ('F12-m2', 'entry'): [25108.50, 25108.50], ('F12-m2', 'stop'): [25098.75, 25098.75],
    ('F13', 'entry'): [25108.90, 25108.90], ('F13', 'stop'): [25097.00],
    ('F13-m1', 'entry'): [25108.05, 25108.05], ('F13-m1', 'stop'): [25097.00],
}
FIRST_NUM = re.compile(r'^~?\s*(-?\d+(?:\.\d+)?)')


def num(text):
    m = FIRST_NUM.match(text.strip().strip('"'))
    return float(m.group(1)) if m else None


def load_csv(path_or_text):
    return {r['id']: r for r in csv.DictReader(path_or_text)}


def parse_table(md):
    """{(row, field): dict(status, frame, before)} from the RV05 H2 adjudication section."""
    sec = md.split('## RV05 H2 adjudication', 1)
    if len(sec) < 2:
        return None
    out = {}
    for line in sec[1].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 6 and cells[0] in ROWS and cells[1] in FIELDS:
            out[(cells[0], cells[1])] = {'status': cells[2], 'frame': cells[3], 'before': cells[4]}
    return out


def compute_status(read, before, earlier):
    if read is None:
        return 'NOT_IN_DATA'
    if before is not None and abs(read - before) <= TOL:
        return 'KEPT'
    if any(abs(read - e) <= TOL for e in earlier):
        return 'CHANGED'
    return 'CONTESTED'


def git_csv(ref):
    rel = (HERE / 'FABIO_TRADE_LEDGER.csv').resolve().relative_to(Path(subprocess.run(
        ['git', '-C', str(HERE), 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()).resolve())
    out = subprocess.run(['git', '-C', str(HERE), 'show', f'{ref}:{rel.as_posix()}'], capture_output=True, text=True, check=True).stdout
    return load_csv(out.splitlines())


def check(git_ref=None):
    errs = []
    reads_path, csv_path, md_path = HERE / 'RV05_H2_READS.csv', HERE / 'FABIO_TRADE_LEDGER.csv', HERE / 'FABIO_TRADE_LEDGER.md'
    if not reads_path.exists():
        return ['RV05_H2_READS.csv missing']
    with open(reads_path, encoding='utf-8', newline='') as f:
        reads = {(r['row'], r['field']): r for r in csv.DictReader(f)}
    with open(csv_path, encoding='utf-8', newline='') as f:
        cur = load_csv(f)
    table = parse_table(md_path.read_text(encoding='utf-8'))
    if table is None:
        return ['ledger .md has no "RV05 H2 adjudication" section']
    changed = 0
    for row in ROWS:
        for fld in FIELDS:
            k = (row, fld)
            if k not in reads:
                errs.append(f'{k}: no reading in RV05_H2_READS.csv (NULL allowed, a line is required)')
                continue
            if k not in table:
                errs.append(f'{k}: no status in the .md table')
                continue
            t = table[k]
            rv = reads[k]['value'].strip()
            read = None if rv.upper() in ('', 'NULL') else float(rv)
            before = num(t['before'])
            want = compute_status(read, before, EARLIER[k])
            if t['status'] not in STATUSES:
                errs.append(f'{k}: status {t["status"]!r} not in {sorted(STATUSES)}')
            elif t['status'] != want:
                errs.append(f'{k}: table says {t["status"]}, code computes {want} (read {read}, CSV before {before})')
            if want != 'NOT_IN_DATA' and not re.search(r't=\d+', t['frame']):
                errs.append(f'{k}: no frame time in the .md table')
            cell = cur[row][fld]
            cur_num = num(cell)
            if want == 'CHANGED':
                changed += 1
                if cur_num is None or abs(cur_num - read) > 0.005:
                    errs.append(f'{k}: CHANGED but CSV cell starts {cur_num}, read is {read}')
                if not re.search(r't=%s\b' % re.escape(reads[k]['frame_t']), cell):
                    errs.append(f'{k}: CHANGED cell has no frame time t={reads[k]["frame_t"]} and is not NOT_IN_DATA')
            elif cur_num != before:
                errs.append(f'{k}: status {want} but CSV cell starts {cur_num}, expected unchanged {before}')
    if git_ref:
        base = git_csv(git_ref)
        diff = sum(1 for row in ROWS for fld in FIELDS if cur[row][fld] != base[row][fld])
        if diff != changed:
            errs.append(f'CHANGED count {changed} != CSV cells differing from {git_ref} ({diff})')
    return errs


def main(argv):
    ref = argv[argv.index('--git-ref') + 1] if '--git-ref' in argv else None
    errs = check(ref)
    for e in errs:
        print('FAIL', e)
    if not errs:
        print('check_rv05_h2: OK (10 fields adjudicated)')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
