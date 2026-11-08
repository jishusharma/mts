"""Fetch actual / forecast (consensus) / previous for the CPI, PPI, NFP and FOMC rows of news_events.csv.

Source: the public ForexFactory calendar page for the release day (https://www.forexfactory.com/calendar?day=jan5.2024).
The page is dated, public and free; it carries the forecast that stood at release time. It is a third-party aggregator,
not the statistics agency: actual and previous are cross-checked by check_catalogue.py against the sign rule only.
Run: python MyTradingSys/research/news_effects_2026-11/fetch_surprise.py   (needs internet; writes surprise_cache.json, numbers only)
Metric per class: CPI = "CPI m/m" (%), PPI = "PPI m/m" (%), NFP = "Non-Farm Employment Change" (thousand jobs), FOMC = "Federal Funds Rate" (%).
"""
import csv
import datetime as dt
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, 'news_events.csv')
CACHE = os.path.join(HERE, 'surprise_cache.json')
METRIC = {'MACRO_CPI': 'CPI m/m', 'MACRO_PPI': 'PPI m/m', 'MACRO_NFP': 'Non-Farm Employment Change', 'FOMC': 'Federal Funds Rate'}
MON = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
UA = {'User-Agent': 'Mozilla/5.0 (research; public pages, low rate)'}


def day_url(d):
    return 'https://www.forexfactory.com/calendar?day=%s%d.%d' % (MON[d.month - 1], d.day, d.year)


def get(u):
    for k in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode('utf8', 'replace')
        except Exception:
            time.sleep(3 * (k + 1))
    return ''


def events_on(page):
    out = []
    for m in re.finditer(r'\{"id":\d+,"ebaseId":\d+,"name":"([^"]+)".*?"dateline":(\d+),"country":"([A-Z]+)".*?"actual":"([^"]*)","previous":"([^"]*)","revision":"([^"]*)","forecast":"([^"]*)"', page):
        out.append(dict(name=m.group(1).replace(chr(92) + '/', '/'), dateline=int(m.group(2)), country=m.group(3), actual=m.group(4), previous=m.group(5), revision=m.group(6), forecast=m.group(7)))
    return out


def num(x):
    """'216K' -> '216', '0.4%' -> '0.4%', '' -> ''."""
    x = x.strip().replace('\\/', '/')
    if x.endswith('K'):
        return x[:-1]
    return x


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf8')))
    cache = json.load(open(CACHE, encoding='utf8')) if os.path.exists(CACHE) else {}
    pages = {}
    for r in rows:
        if r['class'] not in METRIC or r['event_id'] in cache:
            continue
        t0 = dt.datetime.strptime(r['t0_utc'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
        epoch = int(t0.timestamp())
        hit = None
        for off in (0, 1, -1):
            d = (t0 + dt.timedelta(days=off)).date()
            u = day_url(d)
            if u not in pages:
                txt = get(u)
                if not txt:
                    raise SystemExit('page fetch failed (blocked?) for %s; rerun later, cache kept' % u)
                pages[u] = events_on(txt)
                time.sleep(2.0)
            for e in pages[u]:
                if e['country'] == 'US' and e['name'] == METRIC[r['class']] and abs(e['dateline'] - epoch) <= 3600 * 2:
                    hit = (u, e)
                    break
            if hit:
                break
        if hit:
            u, e = hit
            cache[r['event_id']] = dict(url=u, actual=num(e['actual']), consensus=num(e['forecast']), prior=num(e['previous']), revision=num(e['revision']), metric=e['name'])
        else:
            cache[r['event_id']] = dict(url='', actual='', consensus='', prior='', revision='', metric=METRIC[r['class']], miss='not on the day page')
        print(r['event_id'], cache[r['event_id']])
        json.dump(cache, open(CACHE, 'w', encoding='utf8', newline='\n'), indent=1, sort_keys=True)
    print('cached', len(cache), 'filled', sum(1 for v in cache.values() if v['actual']))


if __name__ == '__main__':
    main()
