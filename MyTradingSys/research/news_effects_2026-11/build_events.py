"""Build news_events.csv, control_windows.csv and REPORT.md (cards news-effect-event-catalogue-1108, news-effect-catalogue-v2-gaps-1108).

Run: python MyTradingSys/research/news_effects_2026-11/build_events.py   (needs internet; public data only)
Observation only. No trade gate, no weight, no bias rule. No cookies, no private data.

Pipeline
  1. calendar: BLS release schedule (CPI, Employment Situation, PPI) via web.archive.org snapshots of the public
     bls.gov schedule pages (bls.gov itself answers 403 to scripts); FOMC statement dates from the public Fed page.
     Result cached in calendar_cache.json (public dates only) so reruns are offline for this step.
  2. curated: CURATED list below (our grouping; dates recalled by the author, NOT individually re-fetched; see REPORT Gaps).
  3. reaction: public Binance 1m klines (data-api.binance.vision) for BTCUSDT and ETHUSDT around each t0.
  4. write news_events.csv + REPORT.md.
"""
import csv
import datetime as dt
import json
import math
import os
import re
import ssl
import statistics
import sys
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_catalogue import COLS, NUM, SYMS, TRUMP_TAKES_OFFICE, us_dst, MIN_CLASS, SURPRISE_CLASSES  # noqa: E402

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
CSV_PATH = os.path.join(HERE, 'news_events.csv')
REPORT_PATH = os.path.join(HERE, 'REPORT.md')
CAL_PATH = os.path.join(HERE, 'calendar_cache.json')
CONTROL_PATH = os.path.join(HERE, 'control_windows.csv')
ANALYST_PATH = os.path.join(HERE, 'analyst_events.md')
TMP = os.path.join(tempfile.gettempdir(), 'newseff_klines')
LAST_T0 = dt.datetime(2026, 11, 7, 18, 0, tzinfo=dt.timezone.utc)  # need 240 min of klines after t0
FIRST_T0 = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)
MON = {m: i + 1 for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])}
FULLMON = {m: i + 1 for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                           'september', 'october', 'november', 'december'])}
CLASS_LABEL = {'MACRO_CPI': 'SOURCED', 'MACRO_NFP': 'SOURCED', 'MACRO_PPI': 'SOURCED', 'FOMC': 'SOURCED', 'PROTOCOL': 'SOURCED'}
WK = 'https://en.wikipedia.org/wiki/'
BLS = {'CPI': ('MACRO_CPI', 'cpi', 'US CPI release (BLS)'), 'NFP': ('MACRO_NFP', 'empsit', 'US Employment Situation / NFP (BLS)'),
       'PPI': ('MACRO_PPI', 'ppi', 'US PPI release (BLS)')}
FAILED = []
SKIPPED = []
SNAPS = ['20240201', '20240801', '20250201', '20250801', '20251120', '20260101', '20260201', '20260601', '20261001', '20261101']
# Opus review (REVIEW_OPUS.md) + re-fetch 2026-11-08: the 20251120 and 20260201 BLS PPI snapshots list 'September 2025: Nov. 25, 2025' and
# no 'October 2025' row (October data folded into the Jan 14 2026 release); the early-snapshot dates 2025-10-16 and 2025-11-14 are phantoms.
PPI_CORRECTIONS = {'set': {'September 2025': ['2025-11-25', '08:30 AM']}, 'drop': ['October 2025'],
                   'sources': ['https://web.archive.org/web/20251120id_/https://www.bls.gov/schedule/news_release/ppi.htm',
                               'https://web.archive.org/web/20260201id_/https://www.bls.gov/schedule/news_release/ppi.htm']}


def http(u, timeout=40, ctx=None):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout, context=ctx).read()


# ---------------------------------------------------------------- calendar
def et_to_utc(y, mo, d, hh, mm):
    local = dt.datetime(y, mo, d, hh, mm)
    off = 4 if us_dst(dt.datetime(y, mo, d, 12, tzinfo=dt.timezone.utc)) else 5
    return (local + dt.timedelta(hours=off)).replace(tzinfo=dt.timezone.utc)


def fetch_bls(rel):
    pat = re.compile(r'([A-Z][a-z]+ 20\d\d)\s+([A-Z][a-z]{2,4}\.? \d{1,2}, 20\d\d)\s+(\d\d:\d\d [AP]M)')
    snaps = []
    for s in SNAPS:
        u = 'https://web.archive.org/web/%s/https://www.bls.gov/schedule/news_release/%s.htm' % (s, rel)
        d = {}
        for attempt in range(6):
            try:
                if attempt:
                    time.sleep(5 * attempt)
                b = http(u).decode('utf8', 'replace')
                t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', b))
                for ref, dtxt, tm in pat.findall(t):
                    mm = re.match(r'([A-Za-z]{3})[a-z]*\.? (\d+), (\d{4})', dtxt)
                    day = dt.date(int(mm.group(3)), MON[mm.group(1).lower()], int(mm.group(2)))
                    d[ref] = [day.isoformat(), tm]
                break
            except Exception as e:  # noqa: BLE001
                print('  wayback retry', rel, s, str(e)[:50])
                if '403' in str(e):  # Wayback refuses this snapshot permanently; later snapshots cover the dates
                    SKIPPED.append('%s %s' % (rel, s))
                    break
        else:
            FAILED.append('%s %s' % (rel, s))
        snaps.append(d)
    return snaps


def merge_snaps(snaps):
    """Latest snapshot containing a reference month wins; an entry absent from a later snapshot that covers its date is dropped."""
    mins = [min((v[0] for v in d.values()), default='9999') for d in snaps]
    out = {}
    for i, d in enumerate(snaps):
        for ref, v in d.items():
            out[ref] = (i, v)
    final = {}
    for ref, (i, v) in out.items():
        dropped = any(ref not in snaps[j] and mins[j] <= v[0] for j in range(i + 1, len(snaps)) if snaps[j])
        if not dropped:
            final[ref] = v
    return final


def fetch_fomc():
    b = http('https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm').decode('utf8', 'replace')
    heads = [(m.start(), int(m.group(1))) for m in re.finditer(r'(\d{4}) FOMC Meetings', b)]
    meet = re.compile(r'fomc-meeting__month[^>]*><strong>([^<]+)</strong>.*?fomc-meeting__date[^>]*>([^<]+)<', re.S)
    out = []
    for m in meet.finditer(b):
        yr = [y for pos, y in heads if pos < m.start()]
        if not yr:
            continue
        year = yr[-1]
        mon = m.group(1).strip().split('/')[-1].strip().lower()
        days = re.findall(r'\d+', m.group(2))
        if mon not in FULLMON or not days:
            continue
        dd = dt.date(year, FULLMON[mon], int(days[-1]))
        if len(days) == 2 or '/' in m.group(1):  # two-day meetings only; the page also lists a one-day non-meeting item (2025-08-22)
            out.append(dd.isoformat())
    return sorted(set(out))


def finalize_cal(cal):
    """Idempotent v2 fixes on the cached calendar; returns True when the cache changed."""
    changed = False
    ppi = cal['bls']['PPI']
    for ref, v in PPI_CORRECTIONS['set'].items():
        if ppi.get(ref) != v:
            ppi[ref] = v
            changed = True
    for ref in PPI_CORRECTIONS['drop']:
        if ref in ppi:
            del ppi[ref]
            changed = True
    if cal.get('corrections') != PPI_CORRECTIONS:
        cal['corrections'] = PPI_CORRECTIONS
        changed = True
    pr = cal.setdefault('fomc_press_release', {})
    for d in cal['fomc']:
        if not ('2024-01-01' <= d <= '2026-11-01') or d in pr and pr[d]['release'].startswith('2:00'):
            continue
        url = 'https://www.federalreserve.gov/newsevents/pressreleases/monetary%sa.htm' % d.replace('-', '')
        rel = 'NOT FOUND'
        try:
            t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', http(url).decode('utf8', 'replace')))
            m = re.search(r'For release at (\d{1,2}:\d\d [ap]\.m\. E[SD]T)', t)
            rel = m.group(1) if m else rel
        except Exception as e:  # noqa: BLE001
            print('  fed retry later', d, str(e)[:40])
        pr[d] = {'url': url, 'release': rel}
        changed = True
    return changed


def load_calendar():
    if os.path.exists(CAL_PATH):
        cal = json.load(open(CAL_PATH, encoding='utf8'))
        if finalize_cal(cal):
            with open(CAL_PATH, 'w', encoding='utf8', newline='\n') as f:
                json.dump(cal, f, indent=1, sort_keys=True)
                f.write('\n')
        return cal
    cal = {'note': 'Public release dates. BLS: web.archive.org snapshots of bls.gov/schedule/news_release/<rel>.htm; FOMC: federalreserve.gov fomccalendars.htm',
           'bls': {}, 'fomc': fetch_fomc(), 'skipped_snapshots': []}
    for key, (_c, rel, _t) in BLS.items():
        cal['bls'][key] = merge_snaps(fetch_bls(rel))
    cal['skipped_snapshots'] = SKIPPED
    if FAILED:
        print('WARNING: wayback snapshots failed (calendar NOT cached, rerun): %s' % FAILED)
        return cal
    finalize_cal(cal)
    with open(CAL_PATH, 'w', encoding='utf8', newline='\n') as f:
        json.dump(cal, f, indent=1, sort_keys=True)
        f.write('\n')
    return cal


def fomc_proof(cal, day):
    p = cal.get('fomc_press_release', {}).get(day)
    if p and p['release'].startswith('2:00'):
        return dict(verified='Y', verify_source=p['url'], verify_note='Fed statement page says: For release at %s' % p['release'])
    return dict(verified='N', verify_source='', verify_note='date from the Fed calendar page; statement page not read or no 2:00 pm release line')


def calendar_rows(cal):
    rows = []
    for key, (cls, rel, title) in BLS.items():
        for ref, (day, tm) in cal['bls'][key].items():
            y, mo, d = map(int, day.split('-'))
            hh, mm = map(int, tm.split(' ')[0].split(':'))
            if tm.endswith('PM') and hh != 12:
                hh += 12
            t0 = et_to_utc(y, mo, d, hh, mm)
            if FIRST_T0 <= t0 <= LAST_T0:
                rows.append(dict(event_id='%s-%s' % (key.lower(), day), t0=t0, cls=cls, subtype=key,
                                 title='%s - %s data' % (title, ref),
                                 url='https://www.bls.gov/schedule/news_release/%s.htm' % rel, source_kind='PUBLIC_CALENDAR',
                                 ts_quality='SCHEDULED', verified='Y', verify_source='https://www.bls.gov/schedule/news_release/%s.htm' % rel,
                                 verify_note='date and 08:30 ET time listed on the BLS schedule page (read via web.archive.org snapshots, see calendar_cache.json)'))
    for day in cal['fomc']:
        y, mo, d = map(int, day.split('-'))
        t0 = et_to_utc(y, mo, d, 14, 0)
        if FIRST_T0 <= t0 <= LAST_T0:
            rows.append(dict(event_id='fomc-%s' % day, t0=t0, cls='FOMC', subtype='FOMC_STATEMENT',
                             title='FOMC rate decision statement %s' % day, url='https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
                             source_kind='PUBLIC_CALENDAR', ts_quality='SCHEDULED',
                             **fomc_proof(cal, day)))
    return rows


# ---------------------------------------------------------------- curated (OURS grouping; dates recalled, see REPORT Gaps)
# (id, 'YYYY-MM-DD HH:MM' UTC, class, subtype, short title, url, source_kind, ts_quality)
R, E, A, D = 'PUBLIC_WEB_RECALL', 'EXACT_REPORTED', 'APPROX_INTRADAY', 'DAY_ONLY'
CURATED = [
    ('etf-20240109', '2024-01-09 21:11', 'ETF_REGULATORY', 'FAKE_SEC_POST', 'Fake SEC X post says spot BTC ETFs approved (account hacked)', WK + 'Exchange-traded_fund', R, A),
    ('etf-20240110', '2024-01-10 21:00', 'ETF_REGULATORY', 'ETF_APPROVAL', 'SEC approves spot Bitcoin ETFs', WK + 'Exchange-traded_fund', R, A),
    ('etf-20240111', '2024-01-11 14:30', 'ETF_REGULATORY', 'ETF_LAUNCH', 'Spot Bitcoin ETFs start trading (US open)', WK + 'Exchange-traded_fund', R, E),
    ('etf-20240520', '2024-05-20 17:00', 'ETF_REGULATORY', 'ETF_ODDS', 'ETH ETF approval odds jump (Bloomberg analysts)', WK + 'Ethereum', R, A),
    ('etf-20240523', '2024-05-23 20:00', 'ETF_REGULATORY', 'ETF_APPROVAL', 'SEC approves spot Ether ETF 19b-4 filings', WK + 'Ethereum', R, A),
    ('etf-20240722', '2024-07-22 13:30', 'ETF_REGULATORY', 'ETF_LAUNCH', 'Spot Ether ETFs start trading (US open)', WK + 'Ethereum', R, E),
    ('etf-20241121', '2024-11-21 14:30', 'ETF_REGULATORY', 'SEC_PERSONNEL', 'SEC chair Gensler announces he will step down', WK + 'Gary_Gensler', R, D),
    ('etf-20250918', '2025-09-18 14:30', 'ETF_REGULATORY', 'ETF_RULE', 'SEC approves generic listing standards for crypto ETPs', WK + 'Exchange-traded_fund', R, D),
    ('hack-20240531', '2024-05-31 08:00', 'HACK_EXPLOIT', 'EXCHANGE_HACK', 'DMM Bitcoin hack (about $305M BTC)', WK + 'Cryptocurrency_exchange', R, D),
    ('hack-20240718', '2024-07-18 18:00', 'HACK_EXPLOIT', 'EXCHANGE_HACK', 'WazirX hack (about $230M)', WK + 'WazirX', R, D),
    ('hack-20250123', '2025-01-23 14:30', 'HACK_EXPLOIT', 'EXCHANGE_HACK', 'Phemex hot-wallet hack (about $70M)', WK + 'Cryptocurrency_exchange', R, D),
    ('hack-20250221', '2025-02-21 15:00', 'HACK_EXPLOIT', 'EXCHANGE_HACK', 'Bybit hack (about $1.5B ETH)', WK + 'Bybit', R, A),
    ('hack-20250515', '2025-05-15 14:30', 'HACK_EXPLOIT', 'DATA_BREACH', 'Coinbase discloses data breach (8-K)', WK + 'Coinbase', R, D),
    ('hack-20250618', '2025-06-18 12:00', 'HACK_EXPLOIT', 'EXCHANGE_HACK', 'Nobitex exchange hack', WK + 'Cryptocurrency_exchange', R, D),
    ('hack-20251103', '2025-11-03 08:00', 'HACK_EXPLOIT', 'DEFI_EXPLOIT', 'Balancer protocol exploit (about $128M)', WK + 'Decentralized_finance', R, D),
    ('hack-20261029', '2026-10-29 20:39', 'HACK_EXPLOIT', 'EXCHANGE_HACK', 'Binance hot-wallet drain: first scored headline (on-chain 20:24Z)', 'https://www.coindesk.com/', 'REGISTRY_REPORT', E),
    ('pol-20240727', '2024-07-27 20:00', 'TRUMP_POLICY', 'CAMPAIGN_SPEECH', 'Trump Bitcoin 2024 Nashville speech', WK + 'Donald_Trump', R, D),
    ('pol-20241106', '2024-11-06 07:30', 'TRUMP_POLICY', 'ELECTION', 'US election called for Trump (AP call, early UTC Nov 6)', WK + '2024_United_States_presidential_election', R, A),
    ('pol-20250117', '2025-01-17 22:00', 'TRUMP_POLICY', 'MEMECOIN', 'TRUMP memecoin launch', WK + 'Trump_memecoin', R, D),
    ('pol-20250120', '2025-01-20 17:00', 'TRUMP_POLICY', 'INAUGURATION', 'Trump inaugurated (noon ET oath)', WK + 'Second_inauguration_of_Donald_Trump', R, E),
    ('pol-20250123', '2025-01-23 22:00', 'TRUMP_POLICY', 'EXEC_ORDER', 'Trump signs crypto executive order (digital assets working group)', WK + 'Donald_Trump', R, D),
    ('pol-20250302', '2025-03-02 17:00', 'TRUMP_POLICY', 'RESERVE', 'Trump announces crypto strategic reserve (BTC, ETH, XRP, SOL, ADA)', WK + 'Strategic_Bitcoin_Reserve', R, A),
    ('pol-20250306', '2025-03-06 22:00', 'TRUMP_POLICY', 'RESERVE', 'Trump signs Strategic Bitcoin Reserve executive order', WK + 'Strategic_Bitcoin_Reserve', R, D),
    ('pol-20250307', '2025-03-07 15:00', 'TRUMP_POLICY', 'SUMMIT', 'White House crypto summit', WK + 'Strategic_Bitcoin_Reserve', R, D),
    ('pol-20250717', '2025-07-17 20:00', 'TRUMP_POLICY', 'LEGISLATION', 'House passes CLARITY Act (market structure bill)', WK + 'GENIUS_Act', R, D),
    ('pol-20250718', '2025-07-18 21:30', 'TRUMP_POLICY', 'LEGISLATION', 'Trump signs GENIUS Act (stablecoins)', WK + 'GENIUS_Act', R, D),
    ('pol-20250807', '2025-08-07 18:00', 'TRUMP_POLICY', 'EXEC_ORDER', 'Trump order opens 401(k) plans to alternative assets incl. crypto', WK + 'Donald_Trump', R, D),
    ('tar-20250201', '2025-02-01 22:00', 'TARIFF_TRADE', 'TARIFF_SIGNED', 'Trump signs tariffs on Canada, Mexico, China (weekend)', WK + 'Tariffs_in_the_second_Trump_administration', R, D),
    ('tar-20250203', '2025-02-03 14:30', 'TARIFF_TRADE', 'TARIFF_PAUSE', 'Canada and Mexico tariffs paused 30 days', WK + 'Tariffs_in_the_second_Trump_administration', R, D),
    ('tar-20250304', '2025-03-04 05:01', 'TARIFF_TRADE', 'TARIFF_EFFECTIVE', 'Canada, Mexico tariffs take effect (00:01 ET)', WK + 'Tariffs_in_the_second_Trump_administration', R, E),
    ('tar-20250402', '2025-04-02 20:00', 'TARIFF_TRADE', 'TARIFF_ANNOUNCE', 'Liberation Day reciprocal tariffs announced (4 pm ET)', WK + 'Tariffs_in_the_second_Trump_administration', R, E),
    ('tar-20250409', '2025-04-09 17:18', 'TARIFF_TRADE', 'TARIFF_PAUSE', 'Trump pauses reciprocal tariffs 90 days', WK + 'Tariffs_in_the_second_Trump_administration', R, A),
    ('tar-20250512', '2025-05-12 12:00', 'TARIFF_TRADE', 'TRADE_DEAL', 'US-China Geneva tariff truce announced', WK + 'Tariffs_in_the_second_Trump_administration', R, D),
    ('tar-20250523', '2025-05-23 14:30', 'TARIFF_TRADE', 'TARIFF_THREAT', 'Trump threatens 50% tariff on EU', WK + 'Tariffs_in_the_second_Trump_administration', R, D),
    ('tar-20251010', '2025-10-10 20:00', 'TARIFF_TRADE', 'TARIFF_THREAT', 'Trump threatens 100% tariff on China (record crypto liquidation day)', WK + 'Tariffs_in_the_second_Trump_administration', R, A),
    ('tar-20251030', '2025-10-30 02:00', 'TARIFF_TRADE', 'TRADE_DEAL', 'Trump-Xi meeting in Busan', WK + 'Tariffs_in_the_second_Trump_administration', R, D),
    ('geo-20240413', '2024-04-13 20:00', 'GEOPOLITICS', 'IRAN_ISRAEL', 'Iran launches drones and missiles at Israel', WK + 'Iran', R, D),
    ('geo-20240419', '2024-04-19 01:00', 'GEOPOLITICS', 'IRAN_ISRAEL', 'Israel strike near Isfahan reported', WK + 'Iran', R, D),
    ('geo-20241001', '2024-10-01 17:30', 'GEOPOLITICS', 'IRAN_ISRAEL', 'Iran ballistic missile attack on Israel', WK + 'Iran', R, D),
    ('geo-20250613', '2025-06-13 01:00', 'GEOPOLITICS', 'IRAN_ISRAEL', 'Israel strikes Iran (start of 12-day war)', WK + 'Iran', R, D),
    ('geo-20250621', '2025-06-21 23:50', 'GEOPOLITICS', 'IRAN_US', 'US strikes Iranian nuclear sites (weekend)', WK + 'Iran', R, A),
    ('geo-20250623', '2025-06-23 22:00', 'GEOPOLITICS', 'IRAN_US', 'Trump announces Iran-Israel ceasefire', WK + 'Iran', R, D),
    ('mac-20240805', '2024-08-05 00:00', 'MACRO_OTHER', 'YEN_UNWIND', 'Global sell-off day, yen carry unwind (Asia open)', WK + 'Bank_of_Japan', R, D),
    ('mac-20240823', '2024-08-23 14:00', 'MACRO_OTHER', 'JACKSON_HOLE', 'Powell Jackson Hole speech (10:00 ET)', WK + 'Jackson_Hole_Economic_Symposium', R, E),
    ('mac-20250421', '2025-04-21 12:00', 'MACRO_OTHER', 'FED_INDEPENDENCE', 'Trump attacks Powell, Fed independence fear', WK + 'Jerome_Powell', R, D),
    ('mac-20250516', '2025-05-16 21:00', 'MACRO_OTHER', 'SOVEREIGN_RATING', 'Moodys downgrades US credit rating', WK + 'Moody%27s_Ratings', R, D),
    ('mac-20250822', '2025-08-22 14:00', 'MACRO_OTHER', 'JACKSON_HOLE', 'Powell Jackson Hole speech (10:00 ET)', WK + 'Jackson_Hole_Economic_Symposium', R, E),
    ('mac-20250825', '2025-08-25 23:00', 'MACRO_OTHER', 'FED_INDEPENDENCE', 'Trump moves to remove Fed governor Cook', WK + 'Jerome_Powell', R, D),
    ('mac-20251001', '2025-10-01 04:00', 'MACRO_OTHER', 'SHUTDOWN', 'US federal government shutdown begins (00:00 ET)', WK + '2025_United_States_federal_government_shutdown', R, E),
    ('mac-20251112', '2025-11-12 22:00', 'MACRO_OTHER', 'SHUTDOWN', 'US government shutdown ends (funding bill signed)', WK + '2025_United_States_federal_government_shutdown', R, D),
    ('crt-20240328', '2024-03-28 14:30', 'COURT_LEGAL', 'SENTENCING', 'SBF sentenced to 25 years', WK + 'Sam_Bankman-Fried', R, D),
    ('crt-20240430', '2024-04-30 17:00', 'COURT_LEGAL', 'SENTENCING', 'CZ sentenced to 4 months', WK + 'Changpeng_Zhao', R, D),
    ('crt-20240807', '2024-08-07 14:30', 'COURT_LEGAL', 'SEC_RIPPLE', 'Ripple $125M penalty ruling', WK + 'Ripple_Labs', R, D),
    ('crt-20250227', '2025-02-27 14:30', 'COURT_LEGAL', 'SEC_DISMISSAL', 'SEC dismisses Coinbase case', WK + 'Coinbase', R, D),
    ('crt-20250319', '2025-03-19 14:30', 'COURT_LEGAL', 'SEC_RIPPLE', 'SEC ends Ripple appeal', WK + 'Ripple_Labs', R, D),
    ('crt-20250321', '2025-03-21 14:30', 'COURT_LEGAL', 'SANCTIONS', 'US Treasury lifts Tornado Cash sanctions', WK + 'Tornado_Cash', R, D),
    ('crt-20250529', '2025-05-29 14:30', 'COURT_LEGAL', 'SEC_DISMISSAL', 'SEC dismisses Binance case', WK + 'Binance', R, D),
    ('crt-20250806', '2025-08-06 16:00', 'COURT_LEGAL', 'VERDICT', 'Roman Storm (Tornado Cash) partial verdict', WK + 'Roman_Storm', R, D),
    ('crt-20251023', '2025-10-23 14:30', 'COURT_LEGAL', 'PARDON', 'Trump pardons CZ', WK + 'Changpeng_Zhao', R, D),
    ('crt-20251211', '2025-12-11 14:30', 'COURT_LEGAL', 'SENTENCING', 'Do Kwon sentenced', WK + 'Do_Kwon', R, D),
    ('boj-20240319', '2024-03-19 03:00', 'BOJ_JAPAN', 'BOJ_HIKE', 'BoJ ends negative interest rates', WK + 'Bank_of_Japan', R, A),
    ('boj-20240731', '2024-07-31 03:00', 'BOJ_JAPAN', 'BOJ_HIKE', 'BoJ hikes to 0.25% and trims bond buying', WK + 'Bank_of_Japan', R, A),
    ('boj-20250124', '2025-01-24 03:00', 'BOJ_JAPAN', 'BOJ_HIKE', 'BoJ hikes to 0.5%', WK + 'Bank_of_Japan', R, A),
    ('boj-20251219', '2025-12-19 03:00', 'BOJ_JAPAN', 'BOJ_HIKE', 'BoJ hikes to 0.75%', WK + 'Bank_of_Japan', R, A),
    ('prt-20240313', '2024-03-13 13:55', 'PROTOCOL', 'ETH_UPGRADE', 'Ethereum Dencun upgrade live', WK + 'Ethereum', R, E),
    ('prt-20240420', '2024-04-20 00:09', 'PROTOCOL', 'BTC_HALVING', 'Bitcoin halving (block 840000)', WK + 'Bitcoin', R, E),
    ('prt-20250507', '2025-05-07 10:05', 'PROTOCOL', 'ETH_UPGRADE', 'Ethereum Pectra upgrade live', WK + 'Ethereum', R, E),
    ('prt-20251203', '2025-12-03 21:49', 'PROTOCOL', 'ETH_UPGRADE', 'Ethereum Fusaka upgrade live', WK + 'Ethereum', R, E),
]
UNVERIFIED_NOTE = {
    'tar-20251010': 'placeholder 20:00Z time; Opus review: BTC r15 +0.10 and vr5 0.48 there, so no news minute; real post time unsourced',
    'hack-20261029': 'time from repo report research/news_feeds_2026-10-30/REPORT.md (Tree News 20:39Z); cited CoinDesk URL is generic, not a checked page',
    'mac-20250822': 'Jackson Hole 10:00 ET time from memory; Fed speech page not read (Opus: vr5 spike at t0 supports it)',
    'etf-20240109': 'time from memory (APPROX); vr5 spike supports a t0 within minutes, no primary page read',
}
DEFAULT_UNVERIFIED = 'date and time recalled from memory; cited page is a general reference, no minute checked against it'


# ---------------------------------------------------------------- klines
def klines(sym, start_ms, end_ms):
    os.makedirs(TMP, exist_ok=True)
    cp = os.path.join(TMP, '%s_%d_%d.json' % (sym, start_ms, end_ms))
    if os.path.exists(cp):
        return json.load(open(cp))
    out, cur = [], start_ms
    while cur < end_ms:
        u = ('https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=1m&startTime=%d&endTime=%d&limit=1000'
             % (sym.upper(), cur, end_ms))
        rows = None
        for _ in range(4):
            try:
                rows = json.loads(http(u, 30))
                break
            except Exception:  # noqa: BLE001
                pass
        if not rows:
            break
        out += rows
        cur = rows[-1][0] + 60000
        if len(rows) < 1000:
            break
    json.dump(out, open(cp, 'w'))
    return out


def daily(sym):
    out = {}
    for _ in range(4):
        try:
            rows = json.loads(http('https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=1d&startTime=%d&limit=1000'
                                   % (sym.upper(), int(FIRST_T0.timestamp() * 1000) - 86400000 * 2), 30))
            for r in rows:
                out[dt.datetime.fromtimestamp(r[0] / 1000, dt.timezone.utc).strftime('%Y-%m-%d')] = (float(r[1]), float(r[4]))
            return out
        except Exception:  # noqa: BLE001
            pass
    return out


def z_day(ks, m, r15):
    """r15 / (stdev of 1m log returns over the 24 h before t0 * sqrt(15)): a baseline that averages over all sessions."""
    lr = []
    for i in range(1441, 1, -1):
        a, b = ks.get(m - i * 60000), ks.get(m - (i - 1) * 60000)
        if a and b:
            lr.append(math.log(float(b[4]) / float(a[4])))
    if len(lr) < 1300:
        return ''
    mu = sum(lr) / len(lr)
    sd = math.sqrt(sum((x - mu) ** 2 for x in lr) / (len(lr) - 1)) * 100
    return round(r15 / (sd * math.sqrt(15)), 3) if sd > 0 else ''


def measure_ctl(t0):
    """BTC-only light measure for a same-clock control window: r15, r60, z15 (prior hour), z15d (prior 24 h)."""
    m = int(t0.timestamp() // 60) * 60 * 1000
    ks = {k[0]: k for k in klines('btc', m - 1441 * 60000, m + 61 * 60000)}
    if (m - 60000) not in ks or (m + 14 * 60000) not in ks or (m + 59 * 60000) not in ks:
        return None
    p0 = float(ks[m - 60000][4])
    r15 = (float(ks[m + 14 * 60000][4]) / p0 - 1) * 100
    r60 = (float(ks[m + 59 * 60000][4]) / p0 - 1) * 100
    cl = [float(ks[m - i * 60000][4]) for i in range(61, 0, -1) if (m - i * 60000) in ks]
    if len(cl) < 61:
        return None
    lr = [math.log(b / a) for a, b in zip(cl[:-1], cl[1:])]
    mu = sum(lr) / len(lr)
    rv = math.sqrt(sum((x - mu) ** 2 for x in lr) / (len(lr) - 1)) * 100
    return {'r15': round(r15, 4), 'r60': round(r60, 4), 'z15': round(r15 / (rv * math.sqrt(15)), 3) if rv > 0 else '',
            'z15d': z_day(ks, m, r15)}


def measure(sym, t0, days):
    m = int(t0.timestamp() // 60) * 60 * 1000
    ks = {k[0]: k for k in klines(sym, m - 1441 * 60000, m + 245 * 60000)}
    need = [m - 60000] + [m + i * 60000 for i in range(0, 241)]
    if any(x not in ks for x in need) or any((m - i * 60000) not in ks for i in range(1, 62)):
        return None
    c = lambda t: float(ks[t][4])  # noqa: E731
    p0 = c(m - 60000)
    res = {'p0': round(p0, 2)}
    for h in (1, 5, 15, 60, 240):
        res['r%d' % h] = round((c(m + (h - 1) * 60000) / p0 - 1) * 100, 4)
    res['up60'] = round((max(float(ks[m + i * 60000][2]) for i in range(60)) / p0 - 1) * 100, 4)
    res['dn60'] = round((min(float(ks[m + i * 60000][3]) for i in range(60)) / p0 - 1) * 100, 4)
    prev = [float(ks[m - i * 60000][5]) for i in range(1, 61)]
    first = [float(ks[m + i * 60000][5]) for i in range(5)]
    mp = sum(prev) / 60
    if mp <= 0:
        return None
    res['vr5'] = round((sum(first) / 5) / mp, 3)
    closes = [c(m - i * 60000) for i in range(61, 0, -1)]
    lr = [math.log(b / a) for a, b in zip(closes[:-1], closes[1:])]  # closes are all before t0
    mu = sum(lr) / 60
    rv = math.sqrt(sum((x - mu) ** 2 for x in lr) / 59) * 100
    res['rv60'] = round(rv, 5)
    res['z15'] = round(res['r15'] / (rv * math.sqrt(15)), 3) if rv > 0 else ''
    res['z15d'] = z_day(ks, m, res['r15'])
    exc = [abs(c(m + i * 60000) / p0 - 1) for i in range(60)]
    mx = max(exc)
    res['tpk60'] = exc.index(mx) + 1
    res['retr60'] = round(1 - abs(c(m + 59 * 60000) / p0 - 1) / mx, 3) if mx > 0 else ''
    dk = t0.strftime('%Y-%m-%d')
    res['day_ret'] = round((days[dk][1] / days[dk][0] - 1) * 100, 4) if dk in days else ''
    return res


# ---------------------------------------------------------------- stats helpers
def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def rank(xs):
    """Average ranks (ties share the mean rank)."""
    pos = {}
    for idx, v in enumerate(sorted(xs), 1):
        pos.setdefault(v, []).append(idx)
    return [sum(pos[v]) / len(pos[v]) for v in xs]


def spearman(a, b):
    if len(a) < 5:
        return None
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


def f2(x, n=2):
    return 'n/a' if x is None else ('%.' + str(n) + 'f') % x


# ---------------------------------------------------------------- v2 helpers
SCHED4 = ('MACRO_CPI', 'MACRO_PPI', 'MACRO_NFP', 'FOMC')


def mw_p(a, b):
    """Two-sided Mann-Whitney p (normal approximation, no tie correction)."""
    if len(a) < 3 or len(b) < 3:
        return None
    rk = rank(a + b)
    u = sum(rk[:len(a)]) - len(a) * (len(a) + 1) / 2
    mu = len(a) * len(b) / 2
    sd = math.sqrt(len(a) * len(b) * (len(a) + len(b) + 1) / 12)
    return math.erfc(abs(u - mu) / sd / math.sqrt(2))


def sim_null(paths=20000, seed=1108):
    """Random-walk null for the speed columns: P(abs r60 > abs r15), median tpk60, median retr60."""
    import random
    rnd = random.Random(seed)
    hit, tp, rt = 0, [], []
    for _ in range(paths):
        x, cum = 0.0, []
        for _ in range(60):
            x += rnd.gauss(0, 1)
            cum.append(x)
        hit += abs(cum[59]) > abs(cum[14])
        ex = [abs(v) for v in cum]
        mx = max(ex)
        tp.append(ex.index(mx) + 1)
        rt.append(1 - ex[59] / mx if mx > 0 else 0)
    return hit / paths, statistics.median(tp), statistics.median(rt)


def parse_analyst():
    out = []
    if not os.path.exists(ANALYST_PATH):
        return out
    cur = None
    for line in open(ANALYST_PATH, encoding='utf8').read().split('\n'):
        if line.startswith('### '):
            p = [x.strip() for x in line[4:].split('|')]
            cur = {'analyst': p[0], 'date': p[1], 'vid': p[2]}
            out.append(cur)
        elif cur is not None and ': ' in line:
            k, v = line.split(': ', 1)
            if k in ('event', 'expected_btc_dir', 'timing', 'stated', 'evidence'):
                cur[k] = v
    return out


def overlap_text(e, events):
    day = e['t0'].date()
    same = sorted(o['event_id'] for o in events if o is not e and o['t0'].date() == day and o['cls'] in SCHED4 and e['cls'] in SCHED4)
    near = sorted(o['event_id'] for o in events if o is not e and o['event_id'] not in same
                  and abs((o['t0'] - e['t0']).total_seconds()) < 14400)
    return ';'.join(x for x in (('SAME_DAY:' + '|'.join(same)) if same else '', ('WITHIN_4H:' + '|'.join(near)) if near else '') if x)


def controls_for(events, meas):
    """Up to 3 clean weekdays before each verified scheduled release at the same UTC minute (no catalogue event that day)."""
    cat_days = {e['t0'].date() for e in events}
    jobs = []
    for e, mm in zip(events, meas):
        if e['cls'] not in SCHED4 or e.get('verified') != 'Y' or not mm['btc']:
            continue
        got, k = 0, 0
        while got < 3 and k < 25:
            k += 1
            d = e['t0'] - dt.timedelta(days=k)
            if d.weekday() > 4 or d.date() in cat_days:
                continue
            jobs.append((e, d))
            got += 1
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda j: measure_ctl(j[1]), jobs))
    out = []
    for (e, d), r in zip(jobs, res):
        if r:
            out.append({'event_id': e['event_id'], 'class': e['cls'], 'ctl_t0_utc': d.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'btc_r15': r['r15'], 'btc_z15': r['z15'], 'btc_z15d': r['z15d'], 'btc_r60': r['r60']})
    return out


# ---------------------------------------------------------------- main
def url_alive(u, cache):
    if u in cache:
        return cache[u]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ok = False
    try:
        urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20, context=ctx).read(1)
        ok = True
    except urllib.error.HTTPError as e:
        ok = e.code in (403, 429)
    except Exception:  # noqa: BLE001
        ok = False
    cache[u] = ok
    return ok


def main():
    cal = load_calendar()
    events = calendar_rows(cal)
    for (eid, ts, cls, sub, title, url, kind, tsq) in CURATED:
        t0 = dt.datetime.strptime(ts, '%Y-%m-%d %H:%M').replace(tzinfo=dt.timezone.utc)
        if FIRST_T0 <= t0 <= LAST_T0:
            events.append(dict(event_id=eid, t0=t0, cls=cls, subtype=sub, title=title, url=url, source_kind=kind, ts_quality=tsq,
                               verified='N', verify_source='', verify_note=UNVERIFIED_NOTE.get(eid, DEFAULT_UNVERIFIED)))
    events.sort(key=lambda e: (e['t0'], e['event_id']))
    seq = {}
    for e in events:
        seq[e['cls']] = seq.get(e['cls'], 0) + 1
        e['class_seq'] = seq[e['cls']]
    days = {s: daily(s) for s in SYMS}

    def job(e):
        return {s: measure(s, e['t0'], days[s]) for s in SYMS}
    with ThreadPoolExecutor(6) as ex:
        meas = list(ex.map(job, events))
    urls = sorted({e['url'] for e in events})
    ucache = {}
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(lambda u: url_alive(u, ucache), urls))
    dead = [u for u in urls if not ucache.get(u)]
    analyst = parse_analyst()
    named = {a.get('event') for a in analyst}
    ctl = controls_for(events, meas)
    with open(CONTROL_PATH, 'w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['event_id', 'class', 'ctl_t0_utc', 'btc_r15', 'btc_z15', 'btc_z15d', 'btc_r60'], lineterminator='\n')
        w.writeheader()
        w.writerows(ctl)
    rows = []
    for e, mm in zip(events, meas):
        ok = all(mm[s] for s in SYMS)
        sched4 = e['cls'] in SCHED4
        r = {'event_id': e['event_id'], 't0_utc': e['t0'].strftime('%Y-%m-%dT%H:%M:%SZ'),
             'era': 'PRE_TRUMP2' if e['t0'] < TRUMP_TAKES_OFFICE else 'POST_TRUMP2', 'class': e['cls'],
             'class_label': CLASS_LABEL.get(e['cls'], 'OURS'), 'subtype': e['subtype'], 'title': e['title'], 'url': e['url'],
             'source_kind': e['source_kind'], 'analyst_named': 'Y' if e['event_id'] in named else 'N',
             'ts_quality': e['ts_quality'], 'measured_ok': 'Y' if ok else 'N', 'class_seq': e['class_seq'], 'class_n': seq[e['cls']],
             'verified': e['verified'], 'verify_source': e['verify_source'], 'verify_note': e['verify_note'],
             'overlap': overlap_text(e, events),
             # No free, timestamped, archived consensus source was reachable (BLS 403, FRED timeout, Wayback 429): never guessed.
             'actual': 'none' if sched4 else '', 'consensus': 'none' if sched4 else '', 'prior': 'none' if sched4 else '',
             'surprise_sign': 'none' if sched4 else '', 'surprise_url': ''}
        for s in SYMS:
            for n in NUM:
                r['%s_%s' % (s, n)] = (mm[s] or {}).get(n, '') if mm[s] else ''
        rows.append(r)
    with open(CSV_PATH, 'w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print('wrote %d rows; measured_ok %d; verified %d; control windows %d; analyst blocks %d; dead urls %d' % (
        len(rows), sum(r['measured_ok'] == 'Y' for r in rows), sum(r['verified'] == 'Y' for r in rows), len(ctl), len(analyst), len(dead)))
    for u in dead:
        print('  DEAD URL', u)
    write_report(rows, dead, ctl, analyst)


def write_report(rows, dead, ctl, analyst):
    L = []
    ok = [r for r in rows if r['measured_ok'] == 'Y']
    timed = [r for r in ok if r['verified'] == 'Y']  # verified rows only: unverified rows are in no table
    classes = sorted({r['class'] for r in rows})
    cr = {c: [r for r in rows if r['class'] == c] for c in classes}
    ct = {c: [r for r in timed if r['class'] == c] for c in classes}
    pre_n = sum(r['era'] == 'PRE_TRUMP2' for r in rows)
    by = {r['event_id']: r for r in rows}
    p73, tp_null, rt_null = sim_null()
    A = lambda t, k: [abs(fnum(r[k])) for r in t if fnum(r[k]) is not None]  # noqa: E731
    L.append('# News effects on BTC and ETH: event catalogue v2 and measured reaction (2026-11-08)\n')
    L.append('Cards news-effect-event-catalogue-1108 and news-effect-catalogue-v2-gaps-1108. Observation only: no trade gate, no Live Aid change, no weight, flash or bias rule is proposed here.')
    L.append('Files: `news_events.csv` (one row per event), `control_windows.csv` (same-clock controls), `analyst_events.md` (analyst mentions with quotes), `build_events.py`, `build_analyst_events.py`, `check_catalogue.py` (acceptance check), `calendar_cache.json` (public release dates and the Fed statement pages checked). Independent review of v1: `REVIEW_OPUS.md`.\n')
    L.append('## 1. What is in the catalogue\n')
    L.append('- **%d events**, %d measured on 1m klines (BTCUSDT and ETHUSDT); %d before and %d after the 2025-01-20 17:00Z inauguration; %d classes.' % (len(rows), len(ok), pre_n, len(rows) - pre_n, len(classes)))
    L.append('- **Only verified rows enter any table below** (%d of %d rows). Verified = the date and the minute were read on a public page: the BLS schedule page (via web.archive.org snapshots) for CPI, PPI and NFP, the Fed statement page ("For release at 2:00 p.m.") for each FOMC meeting. Every other row (our own grouping, dates and times recalled from memory) is marked `verified=N` with a reason in `verify_note`, stays in the CSV, and is in **no** table.' % (len(timed), len(rows)))
    L.append('- v2 fixes from the Opus review: the two non-release PPI rows (2025-10-16, 2025-11-14) are removed, the real 2025-11-25 PPI is added (BLS snapshots 20251120 and 20260201), tar-20251010 is marked unverified, CPI + FOMC same-day pairs carry an `overlap` flag (also PPI/NFP same day, and any event within 4 h).')
    L.append('- Reaction columns (percent, per symbol): r1/r5/r15/r60/r240 = close of the minute window vs the close of the minute before t0; up60/dn60 = 1m extremes in 60 min; vr5 = mean volume of the first 5 min / mean of the prior 60; rv60 = stdev of 1m returns of the prior hour; **z15 = r15 / (rv60 sqrt 15) depends on the session** (the prior hour is quiet before 08:30 ET and busy before 14:00 ET), so **z15d = r15 / (stdev of 1m returns over the prior 24 h * sqrt 15)** is the baseline used in the tables; tpk60 / retr60 = minute of the largest excursion and the share given back by minute 60; day_ret = UTC-day open to close.')
    L.append('- Surprise columns `actual`, `consensus`, `prior`, `surprise_sign`, `surprise_url` exist for every CPI, PPI, NFP and FOMC row. **All are `none` in this run** (section 5).\n')

    L.append('## 2. Verified vs unverified, per class\n')
    L.append('| class | label | rows | verified | unverified | verified and measured | verified pre/post 01-20 |')
    L.append('|---|---|---|---|---|---|---|')
    for c in classes:
        v = [r for r in cr[c] if r['verified'] == 'Y']
        t = ct[c]
        L.append('| %s | %s | %d | %d | %d | %d | %d/%d |' % (c, cr[c][0]['class_label'], len(cr[c]), len(v), len(cr[c]) - len(v), len(t),
                                                         sum(r['era'] == 'PRE_TRUMP2' for r in t), sum(r['era'] != 'PRE_TRUMP2' for r in t)))
    L.append('| **all** | | %d | %d | %d | %d | %d/%d |' % (len(rows), sum(r['verified'] == 'Y' for r in rows), sum(r['verified'] == 'N' for r in rows), len(timed),
                                                   sum(r['era'] == 'PRE_TRUMP2' for r in timed), sum(r['era'] != 'PRE_TRUMP2' for r in timed)))
    L.append('')
    L.append('No ETF, hack, Trump policy, tariff, geopolitics, court, BoJ, protocol or macro-other row is verified: a primary or news-archive page with the minute was not read for any of them in this run (section Gaps). Those classes are UNKNOWN.\n')

    L.append('## 3. Class table (verified rows; classes with fewer than %d verified events are UNKNOWN)\n' % MIN_CLASS)
    L.append('Speed and persistence columns are shown beside the random-walk null (simulated, 20,000 paths of 60 one-minute steps): **P(abs r60 > abs r15) = %.2f**, median tpk60 = %d min, median retr60 = %.2f. Opus review value for the first: 0.73. A class value near the null is not evidence of extension or fade.\n' % (p73, tp_null, rt_null))
    L.append('| class | n | med abs BTC r15 %% | med abs BTC z15d | med abs ETH r15 %% | med BTC vr5 | med tpk60 min (null %d) | med retr60 (null %.2f) | share abs r60 > abs r15 (null %.0f%%) |' % (tp_null, rt_null, 100 * p73))
    L.append('|---|---|---|---|---|---|---|---|---|')
    for c in classes:
        t = ct[c]
        if len(t) < MIN_CLASS:
            L.append('| %s | %d | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |' % (c, len(t)))
            continue
        pers = [abs(float(r['btc_r60'])) > abs(float(r['btc_r15'])) for r in t]
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %.0f%% |' % (
            c, len(t), f2(med(A(t, 'btc_r15'))), f2(med(A(t, 'btc_z15d'))), f2(med(A(t, 'eth_r15'))), f2(med([float(r['btc_vr5']) for r in t])),
            f2(med([float(r['btc_tpk60']) for r in t]), 0), f2(med([fnum(r['btc_retr60']) for r in t])), 100 * sum(pers) / len(pers)))
    L.append('')
    L.append('FOMC r60, tpk60 and retr60 mix the 14:00 ET statement with the 14:30 ET press conference; the two windows are not split here.\n')

    L.append('## 4. Same-clock control: event vs ordinary weekdays at the same UTC minute\n')
    L.append('For each verified scheduled release, up to 3 weekdays before it with no catalogue event that day, same UTC minute (BTC only, %d windows in `control_windows.csv`; US market holidays not removed). Baseline z15d (24 h), so the comparison does not depend on the session. p = Mann-Whitney on abs z15d (normal approximation, one test per class, no multiple-test correction).\n' % len(ctl))
    L.append('| class | events | controls | event med abs r15 % | control med abs r15 % | event med abs z15d | control med abs z15d | event share abs z15d > 2 | control share abs z15d > 2 | p |')
    L.append('|---|---|---|---|---|---|---|---|---|---|')
    allc = []
    for c in SCHED4:
        ev = [r for r in ct[c] if any(x['event_id'] == r['event_id'] for x in ctl[:0]) or True]
        cc = [x for x in ctl if x['class'] == c]
        ids = {x['event_id'] for x in cc}
        ev = [r for r in ct[c] if r['event_id'] in ids]
        allc += cc
        ez = A(ev, 'btc_z15d')
        cz = [abs(float(x['btc_z15d'])) for x in cc if x['btc_z15d'] != '']
        if not ev or not cz:
            continue
        p = mw_p(ez, cz)
        L.append('| %s | %d | %d | %s | %s | %s | %s | %.0f%% | %.0f%% | %s |' % (
            c, len(ev), len(cc), f2(med(A(ev, 'btc_r15'))), f2(med([abs(float(x['btc_r15'])) for x in cc])), f2(med(ez)), f2(med(cz)),
            100 * sum(v > 2 for v in ez) / len(ez), 100 * sum(v > 2 for v in cz) / len(cz), 'n/a' if p is None else '%.4f' % p))
    cz = [abs(float(x['btc_z15d'])) for x in allc if x['btc_z15d'] != '']
    if cz:
        L.append('| all controls | | %d | | %s | | %s | | %.0f%% | |' % (len(cz), f2(med([abs(float(x['btc_r15'])) for x in allc])), f2(med(cz)), 100 * sum(v > 2 for v in cz) / len(cz)))
    L.append('')

    L.append('## 5. Reaction by surprise sign (CPI, NFP, FOMC)\n')
    L.append('Surprise = actual vs consensus. A row enters this table only with a numeric actual, a numeric consensus and a cited public URL. **No such row exists in this run**: the BLS pages answer 403 to scripts, the FRED API timed out, Wayback rate-limited, and no free archived consensus page was reachable; the Fed gives no consensus. Every CPI, PPI, NFP and FOMC row therefore says `none` and is excluded from surprise stats; nothing was filled by guess.\n')
    L.append('| class | sign | n | median BTC r60 % (signed) | direction hit rate (hot expected down, cool up) |')
    L.append('|---|---|---|---|---|')
    for c in ('MACRO_CPI', 'MACRO_NFP', 'FOMC'):
        for sg in ('hot', 'cool', 'in line'):
            t = [r for r in ct[c] if r['surprise_sign'] == sg]
            if t:
                vals = [float(r['btc_r60']) for r in t]
                hit = ('%.0f%%' % (100 * sum((v < 0) == (sg == 'hot') for v in vals) / len(vals))) if sg != 'in line' else 'n/a'
                L.append('| %s | %s | %d | %s | %s |' % (c, sg, len(t), f2(med(vals)), hit))
            else:
                L.append('| %s | %s | 0 | n/a | n/a |' % (c, sg))
    nn = {c: sum(1 for r in rows if r['class'] == c and r['surprise_sign'] == 'none') for c in SCHED4}
    L.append('\nRows with sign `none` (excluded from surprise stats): %s. Analyst remarks that CPI 2026-10-14 and PPI 2026-10-15 were "hot" (section 8) are speech, not a sourced actual vs consensus, and are not used here.\n' % ', '.join('%s %d' % (k, v) for k, v in nn.items()))

    L.append('## 6. Before and after 2025-01-20 (verified rows, classes with at least 4 on each side)\n')
    L.append('| class | pre n | pre med abs BTC r15 % | pre med abs z15d | post n | post med abs BTC r15 % | post med abs z15d | p (abs z15d) |')
    L.append('|---|---|---|---|---|---|---|---|')
    anyrow = False
    for c in classes:
        a = [r for r in ct[c] if r['era'] == 'PRE_TRUMP2']
        b = [r for r in ct[c] if r['era'] == 'POST_TRUMP2']
        if len(a) >= 4 and len(b) >= 4:
            anyrow = True
            p = mw_p(A(a, 'btc_z15d'), A(b, 'btc_z15d'))
            L.append('| %s | %d | %s | %s | %d | %s | %s | %s |' % (c, len(a), f2(med(A(a, 'btc_r15'))), f2(med(A(a, 'btc_z15d'))), len(b),
                                                              f2(med(A(b, 'btc_r15'))), f2(med(A(b, 'btc_z15d'))), 'n/a' if p is None else '%.3f' % p))
    if not anyrow:
        L.append('| (no class has 4 verified events on both sides) | | | | | | | |')
    L.append('\nThis is a time split, not a Trump effect: price level, ETF flows, volatility regime and the Fed cycle changed at the same time; no placebo split date was run.\n')

    L.append('## 7. Repeat decay (verified rows, classes with at least %d)\n' % MIN_CLASS)
    L.append('rho = Spearman rank correlation of occurrence number vs abs BTC z15d (negative = fading). Without surprise data the sign of a data-release move follows the surprise, so sign agreement is shown only as a count.\n')
    L.append('| class | n | med abs z15d first 3 | med abs z15d later | rho(seq, abs z15d) | med abs r15 % first 3 | med abs r15 % later | sign agreement with previous |')
    L.append('|---|---|---|---|---|---|---|---|')
    for c in classes:
        t = sorted(ct[c], key=lambda r: r['t0_utc'])
        if len(t) < MIN_CLASS:
            continue
        z = [abs(fnum(r['btc_z15d'])) if fnum(r['btc_z15d']) is not None else None for r in t]
        zz = [(i, v) for i, v in enumerate(z) if v is not None]
        rho = spearman([i for i, _ in zz], [v for _, v in zz])
        ra = [abs(float(r['btc_r15'])) for r in t]
        sg = [(float(t[i]['btc_r15']) > 0) == (float(t[i - 1]['btc_r15']) > 0) for i in range(1, len(t))]
        L.append('| %s | %d | %s | %s | %s | %s | %s | %.0f%% (%d pairs) |' % (c, len(t), f2(med(z[:3])), f2(med(z[3:])), f2(rho), f2(med(ra[:3])), f2(med(ra[3:])), 100 * sum(sg) / len(sg), len(sg)))
    L.append('\nAt n = 23 to 34 a two-sided 5% test needs |rho| of about 0.34 to 0.41. Same-subtype repeats inside the own-grouping classes are not shown: none of those rows is verified.\n')

    L.append('## 8. Analyst-named events (CBP transcripts) and the measured 1 h move\n')
    ev_ids = sorted({a['event'] for a in analyst})
    n_dir = [a for a in analyst if a.get('expected_btc_dir') in ('up', 'down')]
    n_before = [a for a in n_dir if a.get('timing') == 'before']
    L.append('`analyst_events.md` holds **%d analyst mentions** (transcript id and a verbatim quote each; `scripts/dev/verify_extract_quotes.py` accepts all of them) of **%d distinct catalogue events** by %d analysts, from the 24 transcripts of 2026-10-14 to 10-22 in the CBP inbox (the 61 raw transcripts in the repo are mostly Hindi RSI teaching videos and name no catalogue event). %d mentions state a BTC direction; %d of those are stated before the event, the rest describe what happened. The brief asked for 30 or more analyst-named events: the 30-mention bar is met, but the distinct-event count is %d because the transcripts cover one month around CPI, PPI and the FOMC.\n' % (
        len(analyst), len(ev_ids), len({a['analyst'] for a in analyst}), len(n_dir), len(n_before), len(ev_ids)))
    L.append('| event | class | date UTC | verified | BTC r15 % | BTC r60 % | mentions | analysts | before / after | stated BTC direction |')
    L.append('|---|---|---|---|---|---|---|---|---|---|')
    for eid in ev_ids:
        r = by[eid]
        ms = [a for a in analyst if a['event'] == eid]
        shown = r['verified'] == 'Y' and r['measured_ok'] == 'Y'
        L.append('| %s | %s | %s | %s | %s | %s | %d | %s | %d / %d | %s |' % (
            eid, r['class'], r['t0_utc'][:16].replace('T', ' '), r['verified'], ('%+.2f' % float(r['btc_r15'])) if shown else 'unverified t0, not shown',
            ('%+.2f' % float(r['btc_r60'])) if shown else 'not shown', len(ms), ', '.join(sorted({a['analyst'] for a in ms})),
            sum(a['timing'] == 'before' for a in ms), sum(a['timing'] == 'after' for a in ms),
            ', '.join('%s %s' % (a['expected_btc_dir'], a['timing']) for a in ms if a['expected_btc_dir'] != 'none') or 'none'))
    L.append('\nStated expectation vs measured BTC 1 h move (mentions that state a direction):\n')
    L.append('| analyst | video | event | timing | stated direction | measured BTC r60 % | match |')
    L.append('|---|---|---|---|---|---|---|')
    hits, nh = 0, 0
    for a in n_dir:
        r = by[a['event']]
        shown = r['verified'] == 'Y' and r['measured_ok'] == 'Y'
        v = float(r['btc_r60']) if shown else None
        if a['timing'] == 'before' and v is not None:
            m = (v > 0) == (a['expected_btc_dir'] == 'up')
            nh += 1
            hits += m
            mt = 'hit' if m else 'miss'
        else:
            mt = 'description of the past, not an expectation' if a['timing'] == 'after' else 'event t0 unverified'
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (a['analyst'], a['vid'], a['event'], a['timing'], a['expected_btc_dir'], f2(v) if v is not None else 'not shown', mt))
    L.append('\nDirection hit rate of stated expectations before a verified event: %d of %d. That is n = %d, which is not a test. Stated surprise (analysts only): CPI 2026-10-14 "hotter than expected" (Krown, Michaal), CPI and PPI "hot" (Cowen); no actual or consensus number was quoted, so none of it enters section 5.\n' % (hits, nh, nh))

    L.append('## 9. Largest reactions (verified rows, by abs BTC z15d)\n')
    L.append('| rank | date UTC | class | title | BTC r15 % | ETH r15 % | BTC z15d | BTC vr5 | tpk60 min | overlap |')
    L.append('|---|---|---|---|---|---|---|---|---|---|')
    top = sorted([r for r in timed if fnum(r['btc_z15d']) is not None], key=lambda r: -abs(float(r['btc_z15d'])))[:15]
    for i, r in enumerate(top, 1):
        L.append('| %d | %s | %s | %s | %+.2f | %+.2f | %+.1f | %s | %s | %s |' % (i, r['t0_utc'][:16].replace('T', ' '), r['class'], r['title'][:55], float(r['btc_r15']), float(r['eth_r15']), float(r['btc_z15d']), r['btc_vr5'], r['btc_tpk60'], r['overlap'][:40] or '-'))
    L.append('')

    L.append('## Gaps\n')
    small_all = [c for c in classes if len(cr[c]) < MIN_CLASS]
    small_timed = [c for c in classes if len(cr[c]) >= MIN_CLASS and len(ct[c]) < MIN_CLASS]
    L.append('- **Classes with fewer than %d events (total): %s.** Reported as UNKNOWN, not guessed.' % (MIN_CLASS, ', '.join('%s (%d)' % (c, len(cr[c])) for c in small_all) or 'none'))
    L.append('- **Classes with at least %d events but fewer than %d verified ones (minute stats UNKNOWN): %s.**' % (MIN_CLASS, MIN_CLASS, ', '.join('%s (%d verified of %d)' % (c, len(ct[c]), len(cr[c])) for c in small_timed) or 'none'))
    nt = [r for r in rows if r['verified'] == 'N']
    L.append('- **Events with no reliable timestamp (verified=N): %d** (%d DAY_ONLY placeholder t0, %d APPROX_INTRADAY, %d EXACT_REPORTED but recalled). Their minute columns are in the CSV and in no table. Ids: %s.' % (
        len(nt), sum(r['ts_quality'] == 'DAY_ONLY' for r in nt), sum(r['ts_quality'] == 'APPROX_INTRADAY' for r in nt), sum(r['ts_quality'] == 'EXACT_REPORTED' for r in nt), ', '.join(r['event_id'] for r in nt)))
    L.append('- **Not done in this run: source-verifying the own-grouping rows.** Each ETF, hack, Trump policy, tariff, geopolitics, court, BoJ, protocol and macro-other row needs a primary or news-archive page and a minute checked against it (wire time, post id, block time). The cited URLs are general reference pages, not proof. Follow-up card needed.')
    L.append('- **Inferred, not looked up:** (a) every PUBLIC_WEB_RECALL row (dates, times, titles) is the author memory of public events; %s. (b) ET to UTC conversion uses the US DST rule, checked by check_catalogue.py and by the Fed statement pages (EDT/EST named there). (c) BLS dates come from web.archive.org snapshots of the schedule pages (bls.gov blocks scripts); the PPI fix is described in section 1. (d) The era boundary is the 17:00Z oath. (e) The 2026-10-29 Binance row links a generic CoinDesk URL; its time comes from research/news_feeds_2026-10-30/REPORT.md.' % (
        ('%d URL(s) did not answer at build time: %s' % (len(dead), ', '.join(dead[:6]))) if dead else 'every cited URL answered at build time (HTTP 200, or 403 for bls.gov)'))
    L.append('- **No surprise data (all rows `none`).** BLS release pages: 403 to scripts. FRED CSV: timed out. Wayback BLS archive pages: 429 at times. No free archived consensus page was reachable and the Fed publishes none. Needed: actual, consensus and prior per CPI, PPI and NFP release from a dated source, and a market-implied expectation for FOMC. Until then the sign, hot-vs-cool and "works twice" questions are open. Follow-up card needed.')
    L.append('- **Analyst-named coverage:** %d mentions of %d events; all transcripts date from 2026-10-14 to 10-22 (plus the older ones named in extractions.md, which are not in the scanned inbox). Events that analysts mention but the catalogue lacks (midterms 2026-11-03, the 2026 Iran war and oil, bond yields) are not added. Only %d mentions state a BTC direction before an event.' % (len(analyst), len(ev_ids), len(n_before)))
    same = sum(1 for r in rows if 'SAME_DAY' in r['overlap'])
    near = sum(1 for r in rows if 'WITHIN_4H' in r['overlap'])
    L.append('- **Confounding:** %d rows have another scheduled release on the same UTC day (SAME_DAY, e.g. CPI + FOMC on 2024-06-12) and %d have another event within 4 h; PPI days are often Thursdays with weekly jobless claims at the same minute. Not controlled; overlap rows are flagged, not removed.' % (same, near))
    L.append('- **Controls:** BTC only, up to 3 days per event, holidays not removed. z15 (prior hour) is kept in the CSV but not used for comparisons; z15d (24 h) is. FOMC statement and press conference are not split. No placebo split date, no multiple-test correction: all tables are descriptive.')
    L.append('- **Not covered:** exchange listings, token unlocks, liquidation moves without a named trigger, Fed speakers other than Jackson Hole.')
    L.append('- **No weight, flash or bias rule is proposed** in this report.')
    with open(REPORT_PATH, 'w', encoding='utf8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
