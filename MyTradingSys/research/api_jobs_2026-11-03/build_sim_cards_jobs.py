import json, glob, os, hashlib, sys
root = sys.argv[1]
out = sys.argv[2]
SYSTEM = ("You write one plain card for a trading-simulator result file for a non-developer operator. "
          "Use only numbers present in the JSON; never invent. Fee-net and filled trades only when the file says so. "
          "Format exactly 5 lines: Claim: ... | Method: ... | Finding: <numbers> | Verdict: PASSED|FAILED|NOT ENOUGH DATA|EMPTY (no trades) | Keep: YES|NO (NO when EMPTY or no decision value), one reason.")
seen = {}
rows = []
for f in sorted(glob.glob(os.path.join(root, '*.json'))):
    sid = os.path.basename(f)[:-5]
    if sid.startswith('_'):
        continue
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        rows.append({"id": sid, "prompt": "File unreadable (%s). Output: Claim: unreadable | Method: - | Finding: - | Verdict: EMPTY | Keep: NO, unreadable" % e, "system": SYSTEM}); continue
    params = d.get('params') or d.get('settings') or d.get('config') or {}
    key = hashlib.md5((sid.rsplit('-', 1)[0] + json.dumps(params, sort_keys=True)).encode()).hexdigest()[:8]
    dup = seen.get(key)
    seen.setdefault(key, sid)
    slim = {k: d[k] for k in d if k not in ('trades', 'days', 'rows', 'candles', 'equity', 'series')}
    ntr = len(d.get('trades') or [])
    slim['_trade_rows_in_file'] = ntr
    txt = json.dumps(slim, ensure_ascii=False)[:7000]
    p = "Result id: %s. Trade rows in file: %d.%s\nJSON:\n%s" % (
        sid, ntr, (" Same study and identical params as %s: say 'duplicate of %s' in Keep." % (dup, dup)) if dup else "", txt)
    rows.append({"id": sid, "prompt": p, "system": SYSTEM})
with open(out, 'w', encoding='utf-8', newline='\n') as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(rows), 'jobs;', sum(1 for r in rows if 'duplicate of' in r['prompt']), 'flagged duplicate params')
