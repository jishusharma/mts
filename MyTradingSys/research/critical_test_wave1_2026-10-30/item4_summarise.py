"""Item 4 summariser. Usage: python -I item4_summarise.py a.csv b.csv outSummaryCsv
Parses both replay CSVs (a = pitchfork only, b = pitchfork + spikeFade) and prints counts, the 15:00-16:30Z timeline,
the max-high bar, gate histogram, and whether any bar differs between a and b."""
import csv, sys, collections

def load(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

a, b = load(sys.argv[1]), load(sys.argv[2])
assert len(a) == len(b), (len(a), len(b))
print('bars', len(a), len(b))
for name, rows in (('a', a), ('b', b)):
    c = collections.Counter()
    for r in rows:
        for k in ('core_n', 'fadeA1_n', 'fadeA2_n', 'fadeA3_n', 'fadeProfile_n', 'pitchfork_n'):
            if int(r[k]) > 0:
                c[k] += 1
        if int(r['total_n']) > 0:
            c['any'] += 1
    print(name, dict(c))
    w = collections.Counter(r['winner_family'] + ':' + r['winner_type'] + ':' + r['winner_dir'] for r in rows if r['winner_family'])
    print(name, 'winner mix', dict(w))
    gc = collections.Counter(r['fade_gate'] for r in rows)
    print(name, 'gate histogram', dict(gc))
# differences a vs b
diff = [i for i in range(len(a)) if a[i]['all_candidates'] != b[i]['all_candidates'] and
        [x for x in a[i]['all_candidates'].split(' ; ') if x] != [x for x in b[i]['all_candidates'].split(' ; ') if x]]
core_diff = [i for i in range(len(a)) if (a[i]['core_n'], a[i]['core_rank1_type'], a[i]['core_rank1_zone'], a[i]['core_rank1_score']) != (b[i]['core_n'], b[i]['core_rank1_type'], b[i]['core_rank1_zone'], b[i]['core_rank1_score'])]
win_diff = [i for i in range(len(a)) if (a[i]['winner_family'], a[i]['winner_type'], a[i]['winner_zone']) != (b[i]['winner_family'], b[i]['winner_type'], b[i]['winner_zone'])]
print('bars with different candidate list a vs b:', len(diff), '| core part differs:', len(core_diff), '| winner differs:', len(win_diff))
# max-high bar
mi = max(range(len(b)), key=lambda i: float(b[i]['high']))
print('max-high bar', b[mi]['bar_open_utc'], 'high', b[mi]['high'], 'close', b[mi]['close'])
for nm, rows in (('a', a), ('b', b)):
    r = rows[mi]
    print(' ', nm, 'at max-high bar:', r['all_candidates'] or '(none)', '| gate', r['fade_gate'], '| sessHigh', r['sessHigh'], 'sessOpen', r['sessOpen'], 'leg', r['legPct'], 'median', r['legMedian'], 'priorDayHigh', r['priorDayHigh'])
print('timeline 15:00-16:30Z (a winner | b winner | b gate):')
for i, r in enumerate(a):
    hh = r['bar_open_utc'][11:16]
    if '15:00' <= hh <= '16:30':
        rb = b[i]
        print(hh, r['close'], '|', r['winner_family'] + '/' + r['winner_type'] + '@' + r['winner_zone'] + ' sc=' + r['winner_score_raw'], '|',
              rb['winner_family'] + '/' + rb['winner_type'] + '@' + rb['winner_zone'], '| n', r['total_n'], rb['total_n'], '|', rb['fade_gate'], 'leg', rb['legPct'], 'med', rb['legMedian'], 'pdh', rb['priorDayHigh'])
with open(sys.argv[3], 'w', newline='\n') as f:
    f.write('bar_open_utc,close,high,a_total_n,a_winner,a_winner_zone,a_winner_score,b_total_n,b_winner,b_winner_zone,b_fade_gate,legPct,legMedian,priorDayHigh,sessHigh,sessOpen,fadeA1_b,fadeA2_b,fadeA3_b,fadeProf_b,pitchfork_a' + chr(10))
    for i, r in enumerate(a):
        rb = b[i]
        f.write(','.join([r['bar_open_utc'], r['close'], r['high'], r['total_n'], r['winner_family'] + '/' + r['winner_type'], r['winner_zone'], r['winner_score_raw'],
                          rb['total_n'], rb['winner_family'] + '/' + rb['winner_type'], rb['winner_zone'], rb['fade_gate'].split('(')[0], rb['legPct'], rb['legMedian'], rb['priorDayHigh'], rb['sessHigh'], rb['sessOpen'],
                          rb['fadeA1_n'], rb['fadeA2_n'], rb['fadeA3_n'], rb['fadeProfile_n'], r['pitchfork_n']]) + chr(10))
