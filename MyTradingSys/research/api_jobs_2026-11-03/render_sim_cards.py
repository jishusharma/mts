import json, re, sys, collections
src, out = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(src, encoding='utf-8')]
def field(t, k):
    m = re.search(r'%s:\s*(.+?)(?=\s*\|\s*\w+:|\n\w+:|$)' % k, t, re.S)
    return m.group(1).strip().replace('\n', ' ') if m else ''
cards = []
for r in rows:
    t = r.get('text') or ''
    v = field(t, 'Verdict').upper()
    verdict = next((x for x in ('PASSED', 'FAILED', 'NOT ENOUGH DATA', 'EMPTY') if x in v), 'UNPARSED' if t else 'NO TEXT')
    keep = field(t, 'Keep')
    cards.append((r['id'], verdict, keep[:140], field(t, 'Claim')[:120], field(t, 'Finding')[:160], r.get('in_tokens', 0), r.get('out_tokens', 0)))
cnt = collections.Counter(c[1] for c in cards)
keep_no = sum(1 for c in cards if c[2].upper().startswith('NO'))
dups = sum(1 for c in cards if 'duplicate of' in c[2].lower())
tin = sum(c[5] for c in cards); tout = sum(c[6] for c in cards)
cost = (tin * 1.0 + tout * 5.0) / 1e6 / 2  # Haiku batch, half price
L = []
L.append('# Simulator results: one plain card per result file (Haiku 5.5 on the Console Batch API, 2026-11-03)\n')
L.append('Source: every `research/sim_desk/results/*.json` (337), jobs built by `research/api_jobs_2026-11-03/build_sim_cards_jobs.py`, batch msgbatch_01VrQRnGRLr21FeMyrzxtt6P. Raw replies: `sim_results_cards_raw.jsonl`. Numbers in a card come only from its JSON; a card is a reading aid, not a verdict of record.\n')
L.append('Cost: %d in + %d out tokens, about %.2f USD at batch price.\n' % (tin, tout, cost))
L.append('## Totals\n| Verdict | Files |\n|---|---|')
for k, v in cnt.most_common():
    L.append('| %s | %d |' % (k, v))
L.append('| Keep: NO | %d |\n| flagged duplicate params | %d |\n' % (keep_no, dups))
L.append('## Cards\n| id | Verdict | Keep | Claim | Finding |\n|---|---|---|---|---|')
for c in sorted(cards, key=lambda c: (c[1], c[0])):
    L.append('| %s | %s | %s | %s | %s |' % (c[0], c[1], c[2].replace('|', '/'), c[3].replace('|', '/'), c[4].replace('|', '/')))
L.append('\nNoticed: %d replies came back without text (max_tokens 400 spent before any output: rerun those with max-tokens 800 if needed).' % cnt.get('NO TEXT', 0))
open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print(dict(cnt), 'keep_no', keep_no, 'dups', dups, 'cost %.2f' % cost)
