"""Apply API triage answers to task cards. Usage: apply_refine.py <results.jsonl> [--apply]. Each line has id and text.
Model output is data: only whitelisted fields are written; tasks.py check alone promotes a card; DROP never touches p1, live-path or operator-quoted cards."""
import json
import re
import subprocess
import sys
from pathlib import Path

T = Path('MyTradingSys/system/tasks')
FIELDS = ('goal', 'done_when', 'tests', 'steps', 'scope_in', 'scope_out', 'commands', 'lane', 'kind', 'size', 'est_turns', 'worker')


def parse(text):
    m = re.search(r'\{.*\}', text, re.S)
    return json.loads(m.group(0)) if m else None


def decide(card, ans):
    """Return (new card fields, label), or (None, why it was skipped)."""
    if not isinstance(ans, dict) or ans.get('action') not in ('KEEP', 'DROP'):
        return None, 'bad answer'
    if card.get('state') not in ('raw', 'refined'):
        return None, 'state moved'
    why = str(ans.get('reason') or '')[:200]
    tag = 'API triage 2026-11-03: ' + why + ' | ' + str(card.get('note') or '')
    if ans['action'] == 'DROP':
        if card.get('prio') == 1 or card.get('live_path') or 'OPERATOR' in str(card.get('note')):
            return {'note': 'API triage suggested DROP, kept for review: ' + why + ' | ' + str(card.get('note') or '')}, 'KEEP-REVIEW'
        return {'state': 'dropped', 'note': tag}, 'DROP'
    new = {k: ans[k] for k in FIELDS if k in ans and not card.get(k)}
    if card.get('live_path') or new.get('lane') == 'JIS-NB':
        new.pop('lane', None)
    return {**new, 'note': tag}, 'KEEP'


def main():
    do = '--apply' in sys.argv
    counts = {}
    for line in open(sys.argv[1], encoding='utf-8'):
        row = json.loads(line)
        p = T / (row['id'] + '.json')
        if not p.exists():
            continue
        card = json.loads(p.read_text(encoding='utf-8-sig'))
        try:
            new, label = decide(card, parse(row.get('text') or ''))
        except ValueError:
            new, label = None, 'bad json'
        counts[label] = counts.get(label, 0) + 1
        if do and new:
            card.update(new)
            p.write_text(json.dumps(card, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
            if label == 'KEEP':
                subprocess.run([sys.executable, '-X', 'utf8', 'scripts/dev/tasks.py', 'check', row['id']], capture_output=True)
    print(counts, 'applied' if do else 'dry')


if __name__ == '__main__':
    main()
