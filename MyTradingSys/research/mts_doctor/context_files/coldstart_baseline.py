"""Cold start per session: first user prompt, tool calls before the first Edit/Write, files read that the prompt never named, tokens to first edit."""
import glob, json, os, re, sys, time

hours = float(sys.argv[1]) if len(sys.argv) > 1 else 30
nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
since = time.time() - hours * 3600
root = os.path.expanduser('~/.claude/projects')
files = [f for f in glob.glob(root + '/C--Users-E-ngineers-IdeaProjects-BinanceDataFeed*/*.jsonl') if os.path.getmtime(f) >= since]
files.sort(key=os.path.getmtime, reverse=True)
EDIT = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}
out = []
for f in files:
    prompt, calls, first_tok, tok_at_edit, nturn, edit_turn = None, [], None, None, 0, None
    for line in open(f, encoding='utf-8', errors='replace'):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        t = m.get('type')
        if t == 'user' and prompt is None:
            c = m.get('message', {}).get('content')
            if isinstance(c, str):
                prompt = c
            elif isinstance(c, list):
                prompt = ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
        if t != 'assistant':
            continue
        msg = m.get('message', {})
        u = msg.get('usage') or {}
        tot = u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0) + u.get('cache_creation_input_tokens', 0)
        if tot:
            nturn += 1
            if first_tok is None:
                first_tok = tot
        for blk in msg.get('content', []) if isinstance(msg.get('content'), list) else []:
            if blk.get('type') != 'tool_use':
                continue
            name = blk.get('name', '?')
            inp = blk.get('input', {})
            arg = inp.get('file_path') or inp.get('command') or inp.get('pattern') or inp.get('prompt') or ''
            if edit_turn is None:
                calls.append((name, str(arg)[:110].replace('\n', ' ')))
                if name in EDIT or (name == 'Bash' and re.search(r'sync\.py (ship|claim)|git commit|> ', str(arg))):
                    edit_turn, tok_at_edit = nturn, tot
    if not prompt or nturn < 5 or len(calls) < 3:
        continue
    p = prompt.replace('\n', ' ')
    named = set(re.findall(r'[\w./\\-]+\.(?:md|py|json|java|tsv|csv|txt|yaml|yml|ps1)', prompt))
    reads = [a for n, a in calls if n in ('Read',) or (n == 'Bash' and re.search(r'\b(cat|head|sed -n|type)\b', a))]
    unnamed = [a for a in reads if not any(os.path.basename(x) in a for x in named)]
    out.append((f, p, nturn, first_tok, edit_turn, tok_at_edit, calls, unnamed))
    if len(out) >= nmax:
        break
for f, p, nturn, first_tok, edit_turn, tok_at_edit, calls, unnamed in out:
    print('=' * 100)
    print(os.path.basename(f), f'turns={nturn} first_turn_ctx={first_tok} first_edit_turn={edit_turn} ctx_at_first_edit={tok_at_edit}')
    print('PROMPT:', p[:400])
    print(f'tool calls before first edit: {len(calls)}; reads not named in prompt: {len(unnamed)}')
    for n, a in calls[:14]:
        print('   ', n, '|', a)
    if len(calls) > 14:
        print('    ... +', len(calls) - 14)
    for a in unnamed[:8]:
        print('  UNNAMED:', a)
