"""AI health, last N hours vs baseline: per-session turns, context per turn, first-turn base, mid-session full cache rewrites."""
import glob, json, os, statistics, sys, time

hours = float(sys.argv[1]) if len(sys.argv) > 1 else 24
since = time.time() - hours * 3600
root = os.path.expanduser('~/.claude/projects')
files = [f for f in glob.glob(root + '/C--Users-E-ngineers-IdeaProjects-BinanceDataFeed*/*.jsonl') if os.path.getmtime(f) >= since]
sess, ctxs, firsts, misses, models = [], [], [], 0, {}
for f in files:
    turns = []
    for line in open(f, encoding='utf-8', errors='replace'):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get('type') != 'assistant':
            continue
        msg = m.get('message', {})
        u = msg.get('usage')
        if not u:
            continue
        cr, cw = u.get('cache_read_input_tokens', 0), u.get('cache_creation_input_tokens', 0)
        tot = u.get('input_tokens', 0) + cr + cw
        turns.append((tot, cr, cw))
        mo = msg.get('model', '?')
        models[mo] = models.get(mo, 0) + tot
    if not turns:
        continue
    sess.append(len(turns))
    firsts.append(turns[0][0])
    ctxs += [t[0] for t in turns]
    misses += sum(1 for t in turns[1:] if t[2] > 0.5 * t[0] and t[0] > 50000)
big = [n for n in sess if n > 200]
tot_ctx = sum(ctxs)
print(f'window {hours} h: sessions {len(sess)}, turns {len(ctxs)}')
print(f'first-turn base median {statistics.median(firsts):.0f}')
print(f'context per turn median {statistics.median(ctxs):.0f}, p90 {sorted(ctxs)[int(0.9*len(ctxs))]:.0f}')
print(f'turns per session median {statistics.median(sess):.0f}, p90 {sorted(sess)[int(0.9*len(sess))]}, max {max(sess)}')
print(f'sessions over 200 turns {len(big)}')
print(f'mid-session full cache rewrites {misses} ({misses/len(sess):.2f} per session)')
for mo, v in sorted(models.items(), key=lambda x: -x[1])[:5]:
    print(f'  {mo}: {100*v/tot_ctx:.0f}% of context')
