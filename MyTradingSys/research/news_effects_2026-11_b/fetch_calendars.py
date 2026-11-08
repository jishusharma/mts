"""Fetch public release calendars (BLS via Internet Archive snapshots, Fed FOMC calendar). SOURCED. Writes raw/calendar_dates.csv."""
import csv, re, sys, urllib.request, datetime as dt
from pathlib import Path
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) Chrome/120 Safari/537.36'}
OUT = Path(__file__).parent / 'raw'
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}

def get(u):
    import time
    for k in range(5):
        try:
            time.sleep(3 * k)
            return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60).read().decode('utf8', 'ignore')
        except Exception:
            if k == 4: raise

def text(b):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', b))

def bls(name):
    rows = {}
    for snap in ('20240102', '20240701', '20250102', '20250701', '20260102', '20260601', '2026'):
        u = 'https://web.archive.org/web/%s/https://www.bls.gov/schedule/news_release/%s.htm' % (snap, name)
        try:
            t = text(get(u))
        except Exception as e:
            print('skip', u, e, file=sys.stderr); continue
        for m in re.finditer(r'([A-Z][a-z]+)\.? (\d\d), (20\d\d) (\d\d:\d\d) (AM|PM)', t):
            mo = MON.get(m.group(1)[:3]);
            if not mo: continue
            d = dt.date(int(m.group(3)), mo, int(m.group(2)))
            rows[d] = m.group(4) + ' ' + m.group(5)
    return rows

def fomc():
    rows = {}
    pages = ['https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'] + \
            ['https://www.federalreserve.gov/monetarypolicy/fomchistorical%d.htm' % y for y in (2019, 2020)]
    t = text(get(pages[0]))
    for y in re.finditer(r'(20\d\d) FOMC Meetings(.*?)(?=20\d\d FOMC Meetings|$)', t):
        yr = int(y.group(1))
        for m in re.finditer(r'(January|February|March|April|May|June|July|August|September|October|November|December) (\d\d?)-(\d\d?)(\*?)', y.group(2)):
            mo = MON[m.group(1)[:3]]
            rows[dt.date(yr, mo, int(m.group(3)))] = 'meeting day 2 (statement 14:00 ET)' + (' SEP' if m.group(4) else '')
    return rows

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    with open(OUT / 'calendar_dates.csv', 'w', newline='\n') as f:
        w = csv.writer(f); w.writerow(['class', 'date', 'time_et', 'source'])
        for cls, nm in (('CPI', 'cpi'), ('NFP', 'empsit'), ('PPI', 'ppi')):
            for d, tm in sorted(bls(nm).items()):
                if dt.date(2024, 1, 1) <= d <= dt.date(2026, 11, 7):
                    w.writerow([cls, d, tm, 'bls.gov/schedule/news_release/%s.htm (web.archive.org snapshots)' % nm])
        for d, tm in sorted(fomc().items()):
            if dt.date(2024, 1, 1) <= d <= dt.date(2026, 11, 7):
                w.writerow(['FOMC', d, tm, 'federalreserve.gov/monetarypolicy/fomccalendars.htm'])
