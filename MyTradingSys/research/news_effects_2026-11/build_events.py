"""Build news_events.csv and REPORT.md (card news-effect-event-catalogue-1108).

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
from check_catalogue import COLS, NUM, SYMS, TRUMP_TAKES_OFFICE, us_dst, MIN_CLASS  # noqa: E402

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
CSV_PATH = os.path.join(HERE, 'news_events.csv')
REPORT_PATH = os.path.join(HERE, 'REPORT.md')
CAL_PATH = os.path.join(HERE, 'calendar_cache.json')
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
SNAPS = ['20240201', '20240801', '20250201', '20250801', '20260101', '20260601', '20261001', '20261101']


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


def load_calendar():
    if os.path.exists(CAL_PATH):
        return json.load(open(CAL_PATH, encoding='utf8'))
    cal = {'note': 'Public release dates. BLS: web.archive.org snapshots of bls.gov/schedule/news_release/<rel>.htm; FOMC: federalreserve.gov fomccalendars.htm',
           'bls': {}, 'fomc': fetch_fomc(), 'skipped_snapshots': []}
    for key, (_c, rel, _t) in BLS.items():
        cal['bls'][key] = merge_snaps(fetch_bls(rel))
    cal['skipped_snapshots'] = SKIPPED
    if FAILED:
        print('WARNING: wayback snapshots failed (calendar NOT cached, rerun): %s' % FAILED)
        return cal
    with open(CAL_PATH, 'w', encoding='utf8', newline='\n') as f:
        json.dump(cal, f, indent=1, sort_keys=True)
        f.write('\n')
    return cal


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
                                 ts_quality='SCHEDULED'))
    for day in cal['fomc']:
        y, mo, d = map(int, day.split('-'))
        t0 = et_to_utc(y, mo, d, 14, 0)
        if FIRST_T0 <= t0 <= LAST_T0:
            rows.append(dict(event_id='fomc-%s' % day, t0=t0, cls='FOMC', subtype='FOMC_STATEMENT',
                             title='FOMC rate decision statement %s' % day, url='https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
                             source_kind='PUBLIC_CALENDAR', ts_quality='SCHEDULED'))
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
ANALYST_SUB = {('CPI', '2026-10-14'), ('PPI', '2026-10-15'), ('FOMC_STATEMENT', '2026-10-28')}
ANALYST_IDS = {'hack-20261029', 'pol-20250120'}


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


def measure(sym, t0, days):
    m = int(t0.timestamp() // 60) * 60 * 1000
    ks = {k[0]: k for k in klines(sym, m - 61 * 60000, m + 245 * 60000)}
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
            events.append(dict(event_id=eid, t0=t0, cls=cls, subtype=sub, title=title, url=url, source_kind=kind, ts_quality=tsq))
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
    rows = []
    for e, mm in zip(events, meas):
        day = e['t0'].strftime('%Y-%m-%d')
        ok = all(mm[s] for s in SYMS)
        r = {'event_id': e['event_id'], 't0_utc': e['t0'].strftime('%Y-%m-%dT%H:%M:%SZ'),
             'era': 'PRE_TRUMP2' if e['t0'] < TRUMP_TAKES_OFFICE else 'POST_TRUMP2', 'class': e['cls'],
             'class_label': CLASS_LABEL.get(e['cls'], 'OURS'), 'subtype': e['subtype'], 'title': e['title'], 'url': e['url'],
             'source_kind': e['source_kind'],
             'analyst_named': 'Y' if ((e['subtype'], day) in ANALYST_SUB or e['event_id'] in ANALYST_IDS) else 'N',
             'ts_quality': e['ts_quality'], 'measured_ok': 'Y' if ok else 'N', 'class_seq': e['class_seq'], 'class_n': seq[e['cls']]}
        for s in SYMS:
            for n in NUM:
                r['%s_%s' % (s, n)] = (mm[s] or {}).get(n, '') if mm[s] else ''
        rows.append(r)
    with open(CSV_PATH, 'w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print('wrote %d rows; measured_ok %d; dead urls %d' % (len(rows), sum(r['measured_ok'] == 'Y' for r in rows), len(dead)))
    for u in dead:
        print('  DEAD URL', u)
    write_report(rows, dead)


def write_report(rows, dead):
    L = []
    ok = [r for r in rows if r['measured_ok'] == 'Y']
    timed = [r for r in ok if r['ts_quality'] in ('SCHEDULED', 'EXACT_REPORTED')]
    classes = sorted({r['class'] for r in rows})
    cr = {c: [r for r in rows if r['class'] == c] for c in classes}
    ct = {c: [r for r in timed if r['class'] == c] for c in classes}
    pre_n = sum(r['era'] == 'PRE_TRUMP2' for r in rows)
    L.append('# News effects on BTC and ETH: event catalogue and measured reaction (2026-11-08)\n')
    L.append('Card news-effect-event-catalogue-1108. Observation only: no trade gate, no Live Aid change, no weight, flash or bias rule is proposed here.')
    L.append('Files: `news_events.csv` (one row per event), `build_events.py` (rebuilds CSV and this report), `check_catalogue.py` (acceptance check), `calendar_cache.json` (public release dates).\n')
    L.append('## 1. What is in the catalogue\n')
    L.append('- **%d events**, %d measured on 1m klines (both BTCUSDT and ETHUSDT); %d before and %d after the 2025-01-20 17:00Z inauguration.' % (len(rows), len(ok), pre_n, len(rows) - pre_n))
    L.append('- **%d classes.** Label SOURCED = a public calendar fixes the date and time (BLS release schedule via web.archive.org snapshots, Fed FOMC calendar, chain block time). Label OURS = our own grouping of recalled public events.' % len(classes))
    L.append('- Timestamp quality: SCHEDULED (calendar, minute exact) %d, EXACT_REPORTED (publicly stated time) %d, APPROX_INTRADAY (time recalled, maybe +-30 min) %d, DAY_ONLY (date known, t0 set to a placeholder time) %d.' % tuple(
        sum(r['ts_quality'] == q for r in rows) for q in ('SCHEDULED', 'EXACT_REPORTED', 'APPROX_INTRADAY', 'DAY_ONLY')))
    L.append('- Analyst-named (found in the CBP extractions or transcripts, dated): %d. See Gaps.' % sum(r['analyst_named'] == 'Y' for r in rows))
    L.append('- Reaction columns (percent, per symbol): r1/r5/r15/r60/r240 = close of the minute window vs the close of the minute before t0; up60/dn60 = highest/lowest 1m extreme in the first 60 min; vr5 = mean 1m volume of first 5 min / mean of the prior 60 min; rv60 = stdev of 1m returns of prior 60 min; z15 = r15 / (rv60 * sqrt(15)) (for Gaussian noise the median |z15| is about 0.67; 1m crypto returns are fatter-tailed, so the real noise level is unmeasured); tpk60 = minute of the largest closing excursion in the first 60 min; retr60 = how much of that excursion was given back by minute 60 (0 = none, 1 = all); day_ret = UTC-day open to close.')
    L.append('- Minute-level tables below use only the **timed** rows (SCHEDULED + EXACT_REPORTED, measured_ok): %d rows. APPROX and DAY_ONLY rows are in the CSV but their minute columns are not trustworthy.\n' % len(timed))

    L.append('## 2. Class table (timed rows; classes with fewer than %d timed events are shown as UNKNOWN)\n' % MIN_CLASS)
    L.append('| class | label | n all | n timed | pre/post 01-20 (timed) | med abs BTC r15 % | med abs BTC z15 | med abs ETH r15 % | med BTC vr5 | med tpk60 min | med retr60 | share abs r60 > abs r15 |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for c in classes:
        t = ct[c]
        pre = sum(r['era'] == 'PRE_TRUMP2' for r in t)
        if len(t) < MIN_CLASS:
            L.append('| %s | %s | %d | %d | %d/%d | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |' % (c, cr[c][0]['class_label'], len(cr[c]), len(t), pre, len(t) - pre))
            continue
        pers = [abs(float(r['btc_r60'])) > abs(float(r['btc_r15'])) for r in t]
        L.append('| %s | %s | %d | %d | %d/%d | %s | %s | %s | %s | %s | %s | %s |' % (
            c, cr[c][0]['class_label'], len(cr[c]), len(t), pre, len(t) - pre,
            f2(med([abs(float(r['btc_r15'])) for r in t])), f2(med([abs(fnum(r['btc_z15'])) for r in t if fnum(r['btc_z15']) is not None])),
            f2(med([abs(float(r['eth_r15'])) for r in t])), f2(med([float(r['btc_vr5']) for r in t])),
            f2(med([float(r['btc_tpk60']) for r in t]), 0), f2(med([fnum(r['btc_retr60']) for r in t])), '%.0f%%' % (100 * sum(pers) / len(pers))))
    L.append('')
    L.append('Speed reading (timed rows, all classes with n >= %d): median first-60-min peak minute above is the answer to "how fast"; share abs r60 > abs r15 says whether the 15-min move was extended or faded by one hour.\n' % MIN_CLASS)

    L.append('## 3. Before vs after 2025-01-20 (timed rows, classes with at least 4 timed events on each side)\n')
    L.append('| class | pre n | pre med abs BTC r15 % | pre med abs z15 | post n | post med abs BTC r15 % | post med abs z15 |')
    L.append('|---|---|---|---|---|---|---|')
    anyrow = False
    for c in classes:
        a = [r for r in ct[c] if r['era'] == 'PRE_TRUMP2']
        b = [r for r in ct[c] if r['era'] == 'POST_TRUMP2']
        if len(a) >= 4 and len(b) >= 4:
            anyrow = True
            g = lambda t, k: med([abs(fnum(r[k])) for r in t if fnum(r[k]) is not None])  # noqa: E731
            L.append('| %s | %d | %s | %s | %d | %s | %s |' % (c, len(a), f2(g(a, 'btc_r15')), f2(g(a, 'btc_z15')), len(b), f2(g(b, 'btc_r15')), f2(g(b, 'btc_z15'))))
    if not anyrow:
        L.append('| (no class has 4 timed events on both sides) | | | | | | |')
    L.append('')

    L.append('## 4. Repeat decay: did the same kind of news work a second time? (timed rows, classes with at least %d)\n' % MIN_CLASS)
    L.append('Per class, events in time order. "first 3" = the first three occurrences, "later" = the rest. rho = Spearman rank correlation of occurrence number vs abs BTC z15 (negative = fading). Sign agreement = share of events whose BTC r15 has the same sign as the previous event of the class (for data releases the sign depends on a surprise we do not have, see Gaps).\n')
    L.append('| class | n | med abs z15 first 3 | med abs z15 later | rho(seq, abs z15) | med abs r15 % first 3 | med abs r15 % later | sign agreement with previous |')
    L.append('|---|---|---|---|---|---|---|---|')
    for c in classes:
        t = sorted(ct[c], key=lambda r: r['t0_utc'])
        if len(t) < MIN_CLASS:
            continue
        z = [abs(fnum(r['btc_z15'])) if fnum(r['btc_z15']) is not None else None for r in t]
        zz = [(i, v) for i, v in enumerate(z) if v is not None]
        rho = spearman([i for i, _ in zz], [v for _, v in zz])
        ra = [abs(float(r['btc_r15'])) for r in t]
        sg = [(float(t[i]['btc_r15']) > 0) == (float(t[i - 1]['btc_r15']) > 0) for i in range(1, len(t))]
        L.append('| %s | %d | %s | %s | %s | %s | %s | %.0f%% (%d pairs) |' % (
            c, len(t), f2(med(z[:3])), f2(med(z[3:])), f2(rho), f2(med(ra[:3])), f2(med(ra[3:])), 100 * sum(sg) / len(sg), len(sg)))
    L.append('')
    L.append('Same-subtype repeats inside the OURS classes (timed rows only, so counts are small):\n')
    L.append('| class / subtype | timed events in order: UTC date, BTC r15 %, BTC z15 |')
    L.append('|---|---|')
    subs = {}
    for r in timed:
        if r['source_kind'] != 'PUBLIC_CALENDAR':
            subs.setdefault((r['class'], r['subtype']), []).append(r)
    for k, v in sorted(subs.items()):
        if len(v) >= 2:
            L.append('| %s / %s | %s |' % (k[0], k[1], '; '.join('%s %+.2f z%s' % (r['t0_utc'][:10], float(r['btc_r15']), f2(fnum(r['btc_z15']), 1)) for r in sorted(v, key=lambda r: r['t0_utc']))))
    L.append('')

    L.append('## 5. Largest reactions (timed rows, by abs BTC z15)\n')
    L.append('| rank | date UTC | class | title | BTC r15 % | ETH r15 % | BTC z15 | BTC vr5 | tpk60 min |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    top = sorted([r for r in timed if fnum(r['btc_z15']) is not None], key=lambda r: -abs(float(r['btc_z15'])))[:15]
    for i, r in enumerate(top, 1):
        L.append('| %d | %s | %s | %s | %+.2f | %+.2f | %+.1f | %s | %s |' % (i, r['t0_utc'][:16].replace('T', ' '), r['class'], r['title'][:60], float(r['btc_r15']), float(r['eth_r15']), float(r['btc_z15']), r['btc_vr5'], r['btc_tpk60']))
    L.append('')

    L.append('## 6. Classes without a reliable minute timestamp (day-level view, all measured rows)\n')
    L.append('Placeholder t0 rows: the only trustworthy columns are day_ret (UTC day open to close) and the sign/size of up60/dn60 as a rough envelope.\n')
    L.append('| class | n approx/day-only | med abs BTC day_ret % | med abs ETH day_ret % | share BTC day_ret < 0 |')
    L.append('|---|---|---|---|---|')
    for c in classes:
        t = [r for r in ok if r['class'] == c and r['ts_quality'] in ('APPROX_INTRADAY', 'DAY_ONLY') and fnum(r['btc_day_ret']) is not None]
        if len(t) >= 3:
            dn = sum(float(r['btc_day_ret']) < 0 for r in t)
            L.append('| %s | %d | %s | %s | %.0f%% |' % (c, len(t), f2(med([abs(float(r['btc_day_ret'])) for r in t])), f2(med([abs(float(r['eth_day_ret'])) for r in t if fnum(r['eth_day_ret']) is not None])), 100 * dn / len(t)))
    L.append('\nFor comparison, median abs BTC day_ret over all UTC days in range is not computed here (one more request); the numbers above have no baseline. Treat them as descriptive.\n')

    L.append('## Gaps\n')
    small_all = [c for c in classes if len(cr[c]) < MIN_CLASS]
    small_timed = [c for c in classes if len(cr[c]) >= MIN_CLASS and len(ct[c]) < MIN_CLASS]
    L.append('- **Classes with fewer than %d events (total): %s.** Reported as UNKNOWN, not guessed.' % (MIN_CLASS, ', '.join('%s (%d)' % (c, len(cr[c])) for c in small_all) or 'none'))
    L.append('- **Classes with at least %d events but fewer than %d timed ones (minute stats UNKNOWN): %s.**' % (MIN_CLASS, MIN_CLASS, ', '.join('%s (%d timed of %d)' % (c, len(ct[c]), len(cr[c])) for c in small_timed) or 'none'))
    nt = [r for r in rows if r['ts_quality'] in ('APPROX_INTRADAY', 'DAY_ONLY')]
    L.append('- **Events with no reliable timestamp: %d** (%d DAY_ONLY with a placeholder t0 of the author choosing, %d APPROX_INTRADAY recalled to about +-30 min). Their minute columns are in the CSV but excluded from sections 2 to 5. Ids: %s.' % (
        len(nt), sum(r['ts_quality'] == 'DAY_ONLY' for r in nt), sum(r['ts_quality'] == 'APPROX_INTRADAY' for r in nt), ', '.join(r['event_id'] for r in nt)))
    L.append('- **Inferred, not looked up:** (a) all PUBLIC_WEB_RECALL rows (dates, times, titles) are from the author memory of public events; they were NOT re-fetched one by one from the cited page. The URL is a general public reference page, not proof of the date; %s. Treat a wrong date as possible; the volume-spike check below only covers scheduled releases. (b) ET to UTC conversion of BLS/Fed times uses the US DST rule, checked by check_catalogue.py (clock) and by a volume spike at the release minute. (c) BLS dates come from web.archive.org snapshots of the BLS schedule pages (bls.gov itself blocks scripts); entries that later snapshots no longer list (shutdown-cancelled releases) were dropped by a coverage rule. (d) The era boundary uses the 17:00Z oath, not the election. (e) The Fed calendar page parse also returned a one-day non-meeting item (2025-08-22, the Jackson Hole date), dropped by a two-day-meeting filter; the 2026-10-29 Binance row links a generic CoinDesk URL and its time comes from the repo report research/news_feeds_2026-10-30/REPORT.md (Tree News headline 20:39:00Z).' % (
        ('%d URL(s) did not answer at build time: %s' % (len(dead), ', '.join(dead[:6]))) if dead else 'every URL answered at build time (HTTP 200, or 403 for bls.gov)'))
    L.append('- **No surprise data.** Actual vs consensus is not in the catalogue (no free timestamped consensus source was used), so the sign of a CPI/NFP/PPI/FOMC reaction cannot be read as good or bad news; only size, speed and persistence are measured. Sign agreement in section 4 is therefore weak evidence.')
    L.append('- **Analyst-named coverage is thin.** The CBP extractions (2026-09-27, 74 KB) and the 24 inbox plus 61 raw transcripts are almost all Oct 2026 videos. Dated named events found and catalogued: the 2026-10-14 CPI, the PPI (extraction says Oct 16, the BLS calendar says 2026-10-15; the calendar date is used), 2026-10-28 FOMC, the 2026-10-29 Binance hack and the 2025-01-20 inauguration. Named but NOT catalogued because no reliable date is on file: the 2026 Iran war (oil to 120), Powell remarks on long rates, "Trump says war is over" headlines, and the generic 2025 tariff references. Transcripts older than Sept 2026 were not found in the scanned folders.')
    L.append('- **Confounding.** Many events sit within 4 hours of another catalogued event (e.g. FOMC with a Powell speech, CPI with PPI the same week, weekend vs weekday liquidity). Overlap count: %d of %d events have another event within +-4h. Not controlled.' % (
        sum(1 for r in rows if any(o is not r and abs((dt.datetime.strptime(o['t0_utc'], '%Y-%m-%dT%H:%M:%SZ') - dt.datetime.strptime(r['t0_utc'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()) < 14400 for o in rows)), len(rows)))
    L.append('- **No random-time control.** z15 normalises by the prior hour volatility (Gaussian noise median about 0.67, real baseline unmeasured); no matched same-clock-time control sample was drawn. Small classes, no multiple-test correction: every medians table is descriptive, not a finding.')
    L.append('- **Not covered:** exchange listings, token unlocks, liquidations-driven moves without a named trigger, Fed speakers other than Jackson Hole, 2026 events other than the five above, stock-market-hours effects on ETH/BTC beyond the volume ratio.')
    L.append('- **No weight, flash or bias rule is proposed** in this report. The next step in the operator plan (model reviews, then one combined analysis) starts from this table and the CSV.')
    with open(REPORT_PATH, 'w', encoding='utf8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
