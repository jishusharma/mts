"""Acceptance check for news_events.csv (cards news-effect-event-catalogue-1108, news-effect-catalogue-v2-gaps-1108).

Run: python MyTradingSys/research/news_effects_2026-11/check_catalogue.py
Exit 0 = all checks pass, 1 = at least one FAIL. Observation only; no trade gate.

Checks: schema, minimum counts (total / before / after 2025-01-20), timestamp sanity
(parse, range, weekday, UTC clock vs US DST for scheduled releases, volume spike at
scheduled CPI/NFP), privacy (short title + https URL only), 20-row independent
re-derivation of the reaction columns from public Binance 1m klines, and that REPORT.md
lists every class with fewer than MIN_CLASS events under Gaps.
v2 adds: verified/verify_source/verify_note/overlap and surprise columns (actual, consensus, prior, surprise_sign, surprise_url),
the Opus data fixes (phantom PPI rows, 2025-11-25 PPI, tariff 2025-10-10 unverified), same-clock control windows,
z15d (24 h baseline), analyst_events.md (30+ mention blocks, quotes verified by scripts/dev/verify_extract_quotes.py) and report sections.
"""
import csv
import datetime as dt
import json
import os
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, 'news_events.csv')
REPORT_PATH = os.path.join(HERE, 'REPORT.md')
CONTROL_PATH = os.path.join(HERE, 'control_windows.csv')
ANALYST_PATH = os.path.join(HERE, 'analyst_events.md')
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CBP_INBOX = 'F:/CryptoScrapper/cbp_v2/inbox'
TRUMP_TAKES_OFFICE = dt.datetime(2025, 1, 20, 17, 0, tzinfo=dt.timezone.utc)
MIN_TOTAL, MIN_PRE, MIN_POST, MIN_CLASS = 150, 40, 80, 8
RANGE_LO = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)
RANGE_HI = dt.datetime(2026, 11, 8, tzinfo=dt.timezone.utc)
TS_QUALITY = {'SCHEDULED', 'EXACT_REPORTED', 'APPROX_INTRADAY', 'DAY_ONLY'}
SOURCE_KIND = {'PUBLIC_CALENDAR', 'PUBLIC_WEB_RECALL', 'CBP_EXTRACT', 'REGISTRY_REPORT'}
CLASS_LABEL = {'SOURCED', 'OURS'}
SYMS = ('btc', 'eth')
NUM = ['p0', 'r1', 'r5', 'r15', 'r60', 'r240', 'up60', 'dn60', 'vr5', 'rv60', 'z15', 'z15d', 'tpk60', 'retr60', 'day_ret']
SURPRISE_CLASSES = ('MACRO_CPI', 'MACRO_PPI', 'MACRO_NFP', 'FOMC')
SURPRISE_SIGNS = ('hot', 'cool', 'in line', 'none')
MIN_ANALYST = 30
COLS = (['event_id', 't0_utc', 'era', 'class', 'class_label', 'subtype', 'title', 'url', 'source_kind',
         'analyst_named', 'ts_quality', 'measured_ok', 'class_seq', 'class_n',
         'verified', 'verify_source', 'verify_note', 'overlap', 'actual', 'consensus', 'prior', 'surprise_sign', 'surprise_url']
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


def check_v2(rows, ok_rows):
    """Checks added by card news-effect-catalogue-v2-gaps-1108."""
    by = {r['event_id']: r for r in rows}
    check('verified is Y or N', all(r['verified'] in ('Y', 'N') for r in rows))
    check('verified=Y has an https verify_source and a SCHEDULED or EXACT_REPORTED time',
          all(r['verify_source'].startswith('https://') and r['ts_quality'] in ('SCHEDULED', 'EXACT_REPORTED') for r in rows if r['verified'] == 'Y'))
    check('verified=N carries a verify_note', all(r['verify_note'] for r in rows if r['verified'] == 'N'))
    check('every SCHEDULED calendar row is verified (BLS schedule / Fed press release)',
          all(r['verified'] == 'Y' for r in rows if r['ts_quality'] == 'SCHEDULED' and r['source_kind'] == 'PUBLIC_CALENDAR'))
    check('no recalled (PUBLIC_WEB_RECALL) row is verified without a checked page',
          all(r['verified'] == 'N' for r in rows if r['source_kind'] == 'PUBLIC_WEB_RECALL'))
    cnt = {}
    for r in rows:
        c = cnt.setdefault(r['class'], [0, 0])
        c[r['verified'] == 'Y'] += 1
    check('verified counts per class', True, ', '.join('%s %d/%d' % (k, v[1], v[0] + v[1]) for k, v in sorted(cnt.items())))
    # surprise columns
    bad = []
    for r in rows:
        if r['class'] in SURPRISE_CLASSES:
            if r['surprise_sign'] not in SURPRISE_SIGNS or not (r['actual'] and r['consensus'] and r['prior']):
                bad.append(r['event_id'])
            elif r['surprise_sign'] == 'none':
                if r['consensus'] != 'none' or r['surprise_url']:
                    bad.append(r['event_id'])
            else:
                try:
                    float(r['actual'].rstrip('%')), float(r['consensus'].rstrip('%')), float(r['prior'].rstrip('%'))
                except ValueError:
                    bad.append(r['event_id'])
                if not r['surprise_url'].startswith('https://'):
                    bad.append(r['event_id'])
        elif any(r[k] for k in ('actual', 'consensus', 'prior', 'surprise_sign', 'surprise_url')):
            bad.append(r['event_id'])
    check('surprise columns: every CPI/PPI/NFP/FOMC row has actual, consensus, prior and sign; sign none only with consensus none; real sign needs numbers + URL',
          not bad, str(bad[:5]))
    ns = {k: sum(1 for r in rows if r['class'] in SURPRISE_CLASSES and r['surprise_sign'] == k) for k in SURPRISE_SIGNS}
    check('surprise counts', True, str(ns))
    # opus data fixes
    check('phantom PPI rows removed', 'ppi-2025-10-16' not in by and 'ppi-2025-11-14' not in by)
    p = by.get('ppi-2025-11-25')
    check('real PPI 2025-11-25 13:30Z present', bool(p) and p['t0_utc'] == '2025-11-25T13:30:00Z')
    check('tar-20251010 marked unverified', 'tar-20251010' in by and by['tar-20251010']['verified'] == 'N')
    check('CPI + FOMC same-day pair flagged overlapping',
          'fomc-2024-06-12' in by['cpi-2024-06-12']['overlap'] and 'cpi-2024-06-12' in by['fomc-2024-06-12']['overlap'])
    sched = [r for r in rows if r['ts_quality'] == 'SCHEDULED' and r['source_kind'] == 'PUBLIC_CALENDAR']
    check('z15d (24 h baseline) present for >= 95% of scheduled rows',
          sum(1 for r in sched if r['btc_z15d'] != '') >= 0.95 * len(sched))
    # same-clock controls
    if not os.path.exists(CONTROL_PATH):
        check('control_windows.csv exists', False)
    else:
        ctl = list(csv.DictReader(open(CONTROL_PATH, encoding='utf8', newline='')))
        days = {r['t0_utc'][:10] for r in rows}
        per = {}
        bad = []
        for c in ctl:
            ev = by.get(c['event_id'])
            t = parse_t(c['ctl_t0_utc'])
            if not ev or t.weekday() > 4 or ctl and c['ctl_t0_utc'][:10] in days or c['ctl_t0_utc'][11:] != ev['t0_utc'][11:] or c['ctl_t0_utc'] >= ev['t0_utc']:
                bad.append(c['event_id'])
            per[c['event_id']] = per.get(c['event_id'], 0) + 1
        check('control windows: weekday, same UTC minute, before the event, not a catalogue day', not bad, str(bad[:4]))
        check('control windows: at most 3 per event, >= 90% of scheduled events have 3',
              all(v <= 3 for v in per.values()) and sum(1 for r in sched if per.get(r['event_id']) == 3) >= 0.9 * len(sched),
              '%d windows, %d events' % (len(ctl), len(per)))
    # analyst events
    if not os.path.exists(ANALYST_PATH):
        check('analyst_events.md exists', False)
    else:
        txt = open(ANALYST_PATH, encoding='utf8').read()
        n_ev = txt.count('\nevidence: "')
        refs = [l.split(':', 1)[1].strip() for l in txt.split('\n') if l.startswith('event:')]
        check('analyst_events.md has >= %d mention blocks with a quote' % MIN_ANALYST, n_ev >= MIN_ANALYST, str(n_ev))
        check('every analyst block names a catalogue event_id', len(refs) == n_ev and all(x in by for x in refs))
        named = {r['event_id'] for r in rows if r['analyst_named'] == 'Y'}
        check('analyst_named=Y exactly for the events the analyst file names', named == set(refs), '%d vs %d' % (len(named), len(set(refs))))
        if os.path.isdir(CBP_INBOX):
            tmp = tempfile.mkdtemp(prefix='newseff_')
            try:
                os.makedirs(os.path.join(tmp, 'inbox'))
                for f in os.listdir(CBP_INBOX):
                    shutil.copy(os.path.join(CBP_INBOX, f), os.path.join(tmp, 'inbox', f))
                shutil.copy(ANALYST_PATH, os.path.join(tmp, 'analyst_events.md'))
                pr = subprocess.run([sys.executable, os.path.join(REPO, 'scripts', 'dev', 'verify_extract_quotes.py'),
                                     os.path.join(tmp, 'analyst_events.md')], capture_output=True, text=True)
                check('verify_extract_quotes.py accepts every analyst quote', pr.returncode == 0,
                      (pr.stdout.strip().split('\n') or [''])[-1])
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        else:
            check('verify_extract_quotes.py accepts every analyst quote', True, 'SKIP: %s not on this machine' % CBP_INBOX)
    if os.path.exists(REPORT_PATH):
        rep = open(REPORT_PATH, encoding='utf8').read()
        for h in ('Reaction by surprise sign', 'Same-clock control', 'Verified vs unverified', 'Analyst-named', 'Before and after 2025-01-20',
                  'P(abs r60 > abs r15)'):
            check('REPORT.md section: %s' % h, h in rep)
        vtxt = rep.split('Verified vs unverified', 1)[1][:6000] if 'Verified vs unverified' in rep else ''
        check('report counts verified vs unverified for every class', all(c in vtxt for c in {r['class'] for r in rows}))
        check('report states surprise stats exclude rows with no consensus', 'excluded from surprise stats' in rep)


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

    if rows and 'verified' in rows[0] and 'btc_z15d' in rows[0]:
        check_v2(rows, ok_rows)
    else:
        check('v2 columns present (run build_events.py)', False)
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
