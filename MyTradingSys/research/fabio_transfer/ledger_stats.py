"""Fabio ledger inventory (audit H4): parent trade vs fill vs management vs teaching example, and stop-width stats.

The membership below is a definition, not a measurement: it says which CSV rows each count uses. Widths are read from the
CSV cells (first number of the entry and stop cell), so the stats follow the corrected prices (H1) and fail loudly if a row changes.
Run: python ledger_stats.py  -> prints the inventory section that FABIO_TRADE_LEDGER.md carries.
"""
import csv
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE / 'FABIO_TRADE_LEDGER.csv'

# parent -> (market, member entry rows, row whose entry/stop cells give the initial stop width or None, status)
PARENTS = [
    ('P1', 'NQ', ['F1'], 'F1', 'frame-read entry/stop/TP'),
    ('P2', 'NQ', ['F2'], None, 'PARTIAL: teaching example, levels approximate; transcript says 3 positions closed (0jM5Y31YJak.en.vtt:1026-1058) and 5+ more with another later (:1234-1258): one row cannot represent them'),
    ('P3', 'NQ', ['F3a', 'F3b'], 'F3b', 'F3b scales F3a (no flat frame between); stop read only on F3b'),
    ('P4', 'NQ', ['F3c'], 'F3c', 're-entry after the first leg closed (flat frame at t=180 per note)'),
    ('P5', 'ES', ['F4a', 'F4b'], None, 'UNRESOLVED grouping: two screenshot fills, order -1@6977.5 is left of -1@6986.75, continuity not shown; counts as 1 or 2 parents; no stop'),
    ('P6', 'NQ', ['F5'], 'F5', 'frame-read; scaled 15 -> 18 within the position'),
    ('P7', 'NQ', ['F6'], 'F6', 'frame-read; scaled 4 -> 6 within the position'),
    ('P8', 'NQ', ['F7'], 'F7', 'entry derived from risk (approximate)'),
    ('P9', 'NQ', ['F8'], 'F8', 'frame-read average'),
    ('P10', 'NQ', ['F9'], 'F9', 'frame-read average ~'),
    ('P11', 'NQ', ['F10'], 'F10', 'frame-read average ~'),
    ('P12', 'NQ', ['F11'], 'F11', 'entry and stop both approximate (~)'),
    ('P13', 'NQ', ['F12'], 'F12', 'frame-read average and stop at t=3100'),
    ('P14', 'NQ', ['F13'], 'F13', 'frame-read average'),
    ('P15', 'NQ', ['F14'], 'F14', 'frame-read'),
]
EXCLUDED = [('F15-draft-6975-7025', 'drawing (DyS79Eb92Ug.txt:2854-2855), not a submitted order, no fill')]


def rows():
    with open(CSV, encoding='utf-8', newline='') as f:
        return {r['id']: r for r in csv.DictReader(f)}


def first_num(cell):
    m = re.search(r'[0-9]+(?:\.[0-9]+)?', cell or '')
    return float(m.group()) if m else None


def row_class(rid):
    if rid.startswith('F-noTrade'):
        return 'no-trade window (sampled frames only)'
    if rid.startswith('F15-draft'):
        return 'drawing'
    if rid.endswith('-z'):
        return 'no-trade window (sampled frames only)'
    if re.fullmatch(r'F[0-9]+[abc]?', rid):
        return 'fill (entry row)'
    if re.fullmatch(r'F[0-9]+[abc]?-m[0-9]+', rid):
        return 'management observation'
    if re.fullmatch(r'F[0-9]+[abc]?-x', rid):
        return 'flat-state observation (exit)'
    return 'other'


def class_counts():
    out = {}
    for rid in rows():
        c = row_class(rid)
        out[c] = out.get(c, 0) + 1
    return out


def widths():
    """[(parent, width_pt, pct)] for parents with a read initial stop."""
    r = rows()
    out = []
    for p, mkt, members, wrow, _ in PARENTS:
        if wrow is None:
            continue
        e, s = first_num(r[wrow]['entry']), first_num(r[wrow]['stop'])
        out.append((p, wrow, round(abs(e - s), 2), round(abs(e - s) / e * 100, 3)))
    return out


def stats():
    w = [x[2] for x in widths()]
    return dict(n=len(w), median=round(statistics.median(w), 2), mean=round(statistics.mean(w), 2), min=min(w), max=max(w))


def render():
    r = rows()
    cc = class_counts()
    s = stats()
    lines = ['## Audit correction H4 - inventory (card fabio-audit-20261013-counts, 2026-10-17)',
             'Definitions. PARENT TRADE = one position from flat to flat (scale-ins and re-sizing inside it are fills/management of the same parent). FILL = an entry row (a label with a quantity and price). MANAGEMENT = a `-m` row (stop/TP/size change on an open parent). FLAT-STATE OBSERVATION = an `-x` row (position 0 and Daily P/L, not an exit fill, see H2). TEACHING EXAMPLE = a row from a commentary video with approximate levels (F2). A drawing is none of these.',
             '',
             '| Parent | Market | Member entry rows | Initial stop width used | Status |', '|---|---|---|---|---|']
    wd = {x[0]: x for x in widths()}
    for p, mkt, members, wrow, status in PARENTS:
        w = wd.get(p)
        ws = '%.2f pt = %.3f%% (row %s)' % (w[2], w[3], w[1]) if w else 'none read'
        lines.append('| %s | %s | %s | %s | %s |' % (p, mkt, ', '.join(members), ws, status))
    lines += ['', 'Excluded from every count: ' + '; '.join('%s: %s' % x for x in EXCLUDED) + '.',
              '',
              'Counts (replace the earlier "14 filled trades, 13 NQ / 1 ES" and "all available"): %d parent rows listed = %d with a frame-read initial stop (NQ), 1 partial teaching example (P2, NQ), 1 unresolved ES grouping (P5: 1 or 2 parents). So NQ frame-read parent trades = %d; ES = 1-2 parents with no stop; total %d to %d parents.' % (
                  len(PARENTS), s['n'], s['n'], len(PARENTS) - 1, len(PARENTS)),
              'Row classes in the CSV (%d rows): ' % len(r) + '; '.join('%s %d' % (k, v) for k, v in sorted(cc.items())) + '.',
              '',
              'Stop-width statistic (initial stop, %d NQ parents with a read stop; entry/stop = first number of the CSV cells, so F7 and F11 are approximate): median %.2f pt, mean %.2f pt, min %.2f pt, max %.2f pt.' % (s['n'], s['median'], s['mean'], s['min'], s['max']),
              'The old "min 1.5pt (0.006%)" came from the F12 initial stop read (~25105.50 vs ~25107) that the audit rejects (F12 stop is 25089.75 at t=3100); tightened management stops (F5 2.07 pt after the tighten, F12-m1 8.83 pt) are management rows, not initial stops, and are not in this statistic. Members of the statistic: ' + ', '.join('%s=%s' % (x[1], x[2]) for x in widths()) + '.',
              '',
              'Coverage is PARTIAL, not "all available": 8CWKfoSJu3c, fZlNGWvd2Ko, jasv3L-d8ZE, Jpd96fLqr5M sheets read; 0jM5Y31YJak sheets 00/03/04 were unread in the first pass; 9IliXww64uM has no stop/TP labels; DyS79Eb92Ug read in 250 s windows where each no-trade window cites only 2-4 sampled frames, so "no trade" holds for the sampled frames only; Is1HvdfQm5c has frames to t=500 and an ASR extract with no confirmed live position; xUyqIjCfZzg (3.8 h) is unread in this ledger and 9I5vTvwsMBk was never downloaded. F2 omits at least the positions named in 0jM5Y31YJak.en.vtt:1026-1058 and 1234-1258.',
              'UNRESOLVED (H4): the P3/P5 grouping rule for F3b/F4 (no flat frame between fills), the F2 position count and prices, and the unread videos; counts above are a definition applied to the current rows, not ground truth.']
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    print(render())
