"""Acceptance check for news_events.csv (card news-effect-event-catalogue-1108).

Run: python MyTradingSys/research/news_effects_2026-11/check_catalogue.py
Exit 0 = all checks pass, 1 = at least one FAIL. Observation only; no trade gate.

Checks: schema, minimum counts (total / before / after 2025-01-20), timestamp sanity
(parse, range, weekday, UTC clock vs US DST for scheduled releases, volume spike at
scheduled CPI/NFP), privacy (short title + https URL only), 20-row independent
re-derivation of the reaction columns from public Binance 1m klines, and that REPORT.md
lists every class with fewer than MIN_CLASS events under Gaps.
"""
import csv
import datetime as dt
import json
import os
import random
import statistics
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, 'news_events.csv')
REPORT_PATH = os.path.join(HERE, 'REPORT.md')
TRUMP_TAKES_OFFICE = dt.datetime(2025, 1, 20, 17, 0, tzinfo=dt.timezone.utc)
MIN_TOTAL, MIN_PRE, MIN_POST, MIN_CLASS = 150, 40, 80, 8
RANGE_LO = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)
RANGE_HI = dt.datetime(2026, 11, 8, tzinfo=dt.timezone.utc)
TS_QUALITY = {'SCHEDULED', 'EXACT_REPORTED', 'APPROX_INTRADAY', 'DAY_ONLY'}
SOURCE_KIND = {'PUBLIC_CALENDAR', 'PUBLIC_WEB_RECALL', 'CBP_EXTRACT', 'REGISTRY_REPORT'}
CLASS_LABEL = {'SOURCED', 'OURS'}
SYMS = ('btc', 'eth')
NUM = ['p0', 'r1', 'r5', 'r15', 'r60', 'r240', 'up60', 'dn60', 'vr5', 'rv60', 'z15', 'tpk60', 'retr60', 'day_ret']
COLS = (['event_id', 't0_utc', 'era', 'class', 'class_label', 'subtype', 'title', 'url', 'source_kind',
         'analyst_named', 'ts_quality', 'measured_ok', 'class_seq', 'class_n']
        + ['%s_%s' % (s, n) for s in SYMS for n in NUM])
FAILS = []


def check(name, ok, detail=''):
    print('%s  %s %s' % ('PASS' if ok else 'FAIL', name, ('- ' + detail) if detail else ''))
    if not ok:
        FAILS.append(name)


def parse_t(s):
    return dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)


def us_dst(d):
    """True when US Eastern is on daylight time at UTC datetime d (second Sun Mar 07:00Z .. first Sun Nov 06:00Z approx)."""
    y = d.year
    mar = dt.datetime(y, 3, 8, 7, tzinfo=dt.timezone.utc)
    mar += dt.timedelta(days=(6 - mar.weekday()) % 7)
    nov = dt.datetime(y, 11, 1, 6, tzinfo=dt.timezone.utc)
    nov += dt.timedelta(days=(6 - nov.weekday()) % 7)
    return mar <= d < nov


def klines(sym, start_ms, end_ms):
    out = []
    cur = start_ms
    while cur < end_ms:
        u = ('https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=1m&startTime=%d&endTime=%d&limit=1000'
             % (sym.upper(), cur, end_ms))
        rows = json.loads(urllib.request.urlopen(u, timeout=30).read())
        if not rows:
            break
        out += rows
        cur = rows[-1][0] + 60000
        if len(rows) < 1000:
            break
    return out


def rederive(row, sym):
    """Independent re-computation of r5, r60 (%) and vr5 for one row/symbol."""
    t0 = parse_t(row['t0_utc'])
    m = int(t0.timestamp() // 60) * 60 * 1000
    ks = {k[0]: k for k in klines(sym, m - 61 * 60000, m + 61 * 60000)}
    base = float(ks[m - 60000][4])
    r5 = (float(ks[m + 4 * 60000][4]) / base - 1) * 100
    r60 = (float(ks[m + 59 * 60000][4]) / base - 1) * 100
    prev = [float(ks[m - i * 60000][5]) for i in range(1, 61) if (m - i * 60000) in ks]
    first = [float(ks[m + i * 60000][5]) for i in range(5)]
    vr5 = (sum(first) / 5) / (sum(prev) / len(prev))
    return r5, r60, vr5


def main():
    if not os.path.exists(CSV_PATH):
        check('csv exists', False, 'missing %s (run build_events.py)' % CSV_PATH)
        check('report exists', os.path.exists(REPORT_PATH), 'REPORT.md')
        return finish()
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf8', newline='')))
    check('csv exists', True, '%d rows' % len(rows))
    check('schema columns', list(rows[0].keys()) == COLS if rows else False,
          'missing=%s extra=%s' % ([c for c in COLS if rows and c not in rows[0]], [c for c in (rows[0] if rows else {}) if c not in COLS]))
    ids = [r['event_id'] for r in rows]
    check('event_id unique', len(ids) == len(set(ids)))
    check('min total >= %d' % MIN_TOTAL, len(rows) >= MIN_TOTAL, str(len(rows)))
    try:
        ts = [parse_t(r['t0_utc']) for r in rows]
        check('t0 parse (UTC Z)', True)
    except Exception as e:
        check('t0 parse (UTC Z)', False, str(e))
        return finish()
    pre = sum(1 for t in ts if t < TRUMP_TAKES_OFFICE)
    check('min before 2025-01-20 >= %d' % MIN_PRE, pre >= MIN_PRE, str(pre))
    check('min after 2025-01-20 >= %d' % MIN_POST, len(ts) - pre >= MIN_POST, str(len(ts) - pre))
    check('t0 within range 2024-01-01..2026-11-08', all(RANGE_LO <= t < RANGE_HI for t in ts))
    check('era matches t0', all((r['era'] == 'PRE_TRUMP2') == (t < TRUMP_TAKES_OFFICE) and r['era'] in ('PRE_TRUMP2', 'POST_TRUMP2')
                                for r, t in zip(rows, ts)))
    check('enums valid', all(r['ts_quality'] in TS_QUALITY and r['source_kind'] in SOURCE_KIND and r['class_label'] in CLASS_LABEL
                             and r['analyst_named'] in ('Y', 'N') and r['measured_ok'] in ('Y', 'N') for r in rows))
    check('title short (<=90) and url https', all(0 < len(r['title']) <= 90 and r['url'].startswith('https://') for r in rows))
    classes = {}
    for r in rows:
        classes.setdefault(r['class'], []).append(r)
    check('class_label constant per class', all(len({r['class_label'] for r in v}) == 1 for v in classes.values()))
    check('class_n matches', all(int(r['class_n']) == len(classes[r['class']]) for r in rows))
    # sequence integrity: class_seq is 1..n in time order within class
    ok_seq = True
    for v in classes.values():
        v2 = sorted(v, key=lambda r: r['t0_utc'])
        ok_seq &= [int(r['class_seq']) for r in v2] == list(range(1, len(v2) + 1))
    check('class_seq 1..n in time order', ok_seq)
    # timestamp sanity for scheduled releases
    sched = [r for r in rows if r['ts_quality'] == 'SCHEDULED' and r['source_kind'] == 'PUBLIC_CALENDAR']
    check('scheduled rows exist (>=100)', len(sched) >= 100, str(len(sched)))
    bad_wd, bad_clock = [], []
    for r in sched:
        t = parse_t(r['t0_utc'])
        if t.weekday() > 4:
            bad_wd.append(r['event_id'])
        want = (18, 0) if r['subtype'] == 'FOMC_STATEMENT' else (12, 30)
        if r['subtype'] == 'FOMC_STATEMENT':
            want = (18, 0) if us_dst(t) else (19, 0)
        else:
            want = (12, 30) if us_dst(t) else (13, 30)
        if (t.hour, t.minute) != want:
            bad_clock.append(r['event_id'])
    check('scheduled releases on weekdays', not bad_wd, str(bad_wd[:5]))
    check('scheduled clock matches 08:30/14:00 ET in UTC (DST aware)', not bad_clock, str(bad_clock[:5]))
    ok_rows = [r for r in rows if r['measured_ok'] == 'Y']
    check('measured_ok >= 95%', len(ok_rows) >= 0.95 * len(rows), '%d/%d' % (len(ok_rows), len(rows)))
    for sub in ('CPI', 'NFP'):
        vr = [float(r['btc_vr5']) for r in ok_rows if r['subtype'] == sub and r['ts_quality'] == 'SCHEDULED' and r['btc_vr5']]
        med = statistics.median(vr) if vr else 0
        check('%s release minute shows volume spike (median vr5 >= 1.5)' % sub, med >= 1.5, 'median=%.2f n=%d' % (med, len(vr)))
    # 20-row re-derivation
    rnd = random.Random(1108)
    pick_pool = sorted(ok_rows, key=lambda r: r['event_id'])
    picked = rnd.sample(pick_pool, min(20, len(pick_pool)))
    check('20 rows available for re-derivation', len(picked) == 20, str(len(picked)))
    bad = []
    for r in picked:
        for s in SYMS:
            try:
                r5, r60, vr5 = rederive(r, s)
            except Exception as e:
                bad.append('%s/%s: %s' % (r['event_id'], s, str(e)[:40]))
                continue
            if abs(r5 - float(r[s + '_r5'])) > 0.006 or abs(r60 - float(r[s + '_r60'])) > 0.006 or abs(vr5 - float(r[s + '_vr5'])) > 0.02:
                bad.append('%s/%s r5 %.3f vs %s r60 %.3f vs %s' % (r['event_id'], s, r5, r[s + '_r5'], r60, r[s + '_r60']))
    check('20-row re-derivation (btc+eth r5, r60, vr5 match)', not bad, '; '.join(bad[:3]))
    # report gaps
    if not os.path.exists(REPORT_PATH):
        check('REPORT.md exists', False)
    else:
        rep = open(REPORT_PATH, encoding='utf8').read()
        check('REPORT.md exists', True)
        gi = rep.find('## Gaps')
        check('REPORT.md has Gaps section', gi >= 0)
        small = [c for c, v in classes.items() if len(v) < MIN_CLASS]
        gtxt = rep[gi:] if gi >= 0 else ''
        check('every class with < %d events named in Gaps' % MIN_CLASS, all(c in gtxt for c in small), 'small=%s' % small)
        check('Gaps names events with no reliable timestamp', 'no reliable timestamp' in gtxt)
        check('Gaps states what was inferred', 'inferred' in gtxt.lower())
    return finish()


def finish():
    print('RESULT: %s (%d fail)' % ('GREEN' if not FAILS else 'RED', len(FAILS)))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
