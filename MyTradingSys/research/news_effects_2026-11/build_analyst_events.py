"""Write analyst_events.md: analyst mentions of catalogued events, each with transcript id and a verbatim quote.

Run: python MyTradingSys/research/news_effects_2026-11/build_analyst_events.py
Reads the CBP transcripts in F:/CryptoScrapper/cbp_v2/inbox (24 files, 2026-10-14..22). Public YouTube auto-captions only.
Candidates are found by keyword (CPI, PPI, FOMC, inaugurated, elected, rate hike ...) with the same dedupe rule every run; PICKS
below is the reviewed selection (candidate number -> catalogue event, stated BTC direction, timing). A quote is a slice of the
transcript, so it is verbatim by construction; scripts/dev/verify_extract_quotes.py re-checks it (check_catalogue.py runs it).

expected_btc_dir = the analyst says what BTC will do around the event (up/down), else none. timing = before the event
(a stated expectation) or after it (a description of what happened); only 'before' + a direction is compared to the measured move.
No transcript text beyond a ~25-word quote is stored.
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
INBOX = 'F:/CryptoScrapper/cbp_v2/inbox'
KW = re.compile(r'\b(CPI|PPI|FOMC|inaugurated|jobs report|elected|rate hike|raised rates|raise rates)\b')
F, G, C, P = 'fomc-2026-10-28', 'fomc-2026-09-16', 'cpi-2026-10-14', 'ppi-2026-10-15'
# n: (event_id, expected_btc_dir, timing, stated)
PICKS = {
    2: (G, 'up', 'after', 'BTC often rallies after a September rate hike in a midterm year'),
    3: (G, 'up', 'after', 'after a rate hike BTC often rallies, then the market drops'),
    5: (G, 'none', 'after', 'S&P expected to drop after the hike (not BTC)'),
    6: (C, 'none', 'after', 'hot CPI and hot PPI, 10-year yield down'),
    7: (F, 'none', 'before', 'October hike odds 85 percent (speaker)'),
    8: (F, 'none', 'before', 'October hike odds 85 percent (speaker)'),
    9: (F, 'none', 'before', 'if no October hike the 10-year bounces'),
    10: (G, 'down', 'before', 'earlier thesis: September hike drops BTC below realized price'),
    11: (G, 'none', 'before', 'earlier thesis: hike then S&P drops (not BTC)'),
    14: (F, 'none', 'before', 'Fed may not hike in October, 84.5 percent no hike'),
    16: (F, 'none', 'before', 'Fed will not raise at the October meeting'),
    17: (C, 'none', 'after', 'hot CPI with falling 10-year yield means local top'),
    19: (F, 'none', 'before', 'video is about what the Fed does at the next FOMC'),
    20: (G, 'none', 'after', 'Fed raised in September despite pushback'),
    21: (F, 'none', 'before', 'market sees 80s percent chance of a hold'),
    29: (F, 'none', 'before', 'only about 16 percent chance of an October hike'),
    31: (F, 'none', 'before', 'guess: no hike at the October FOMC'),
    32: (F, 'none', 'before', 'FOMC the next major catalyst'),
    33: (pol := 'pol-20250120', 'down', 'after', 'BTC top 109k at the inauguration then falls 33 percent'),
    34: ('pol-20241106', 'none', 'after', 'price did not move on the election day'),
    35: (P, 'none', 'before', 'PPI tomorrow probably matters more for Fed odds'),
    36: (C, 'none', 'after', 'CPI print study, little edge'),
    37: (C, 'none', 'after', 'CPI-based setups only 43 or 57 percent'),
    38: (C, 'none', 'after', 'CPI slightly hotter than expected'),
    39: (P, 'down', 'after', 'BTC correction target hit on the PPI morning move'),
    41: (F, 'none', 'before', 'neither hike nor cut likely'),
    42: (F, 'none', 'before', 'week into FOMC stats'),
    43: (F, 'none', 'before', 'run-up to FOMC is a coin flip, 54 percent green'),
    44: (F, 'none', 'before', 'FOMC decision next Wednesday, the 28th'),
    46: (C, 'down', 'after', 'CPI hotter than expected by 0.1, market tumbled'),
    47: (C, 'down', 'after', 'market move fuelled by the CPI news'),
}


def candidates():
    n = 0
    for f in sorted(glob.glob(INBOX + '/*.txt')):
        t = open(f, encoding='utf8', errors='replace').read()
        head, _, body = t.partition('\n\n')
        body = re.sub(r'\s+', ' ', body)
        meta = dict(re.findall(r'^(\w+): (.*)$', head, re.M))
        last = -999
        for m in KW.finditer(body):
            if m.start() - last < 450:
                continue
            last = m.start()
            n += 1
            yield n, os.path.basename(f), meta, body, m.start()


def window(body, pos):
    a, b = max(0, pos - 90), pos + 170
    s = body[a:b]
    s = s.split(' ', 1)[1] if a > 0 and ' ' in s else s
    s = s.rsplit(' ', 1)[0] if ' ' in s else s
    return s.replace('"', '').strip()


def main():
    names = {'Benjamin': 'Benjamin Cowen', 'Krown': 'Krown', 'Michaal': 'Michaal', 'Jason': 'Jason Pizzino', 'Jala': 'Jala'}
    out = ['# Analyst-named events (CBP transcripts, 2026-10): analyst mention, stated expectation, verbatim quote\n',
           'Card news-effect-catalogue-v2-gaps-1108. Built by build_analyst_events.py; quotes checked by scripts/dev/verify_extract_quotes.py.',
           'expected_btc_dir: what the analyst says BTC will do (up, down, none). timing: before = a stated expectation, after = a description of what happened.\n']
    k = 0
    for n, fn, meta, body, pos in candidates():
        if n not in PICKS:
            continue
        ev, d, tm, stated = PICKS[n]
        k += 1
        who = names.get(fn.split('_')[0], fn.split('_')[0])
        out.append('### %s | %s | %s | %s' % (who, meta.get('publish_date', ''), meta.get('video_id', ''), meta.get('title', '')))
        out.append('event: %s' % ev)
        out.append('expected_btc_dir: %s' % d)
        out.append('timing: %s' % tm)
        out.append('stated: %s' % stated)
        out.append('evidence: "%s"' % window(body, pos))
        out.append('')
    with open(os.path.join(HERE, 'analyst_events.md'), 'w', encoding='utf8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('wrote %d analyst mention blocks' % k)


if __name__ == '__main__':
    main()
