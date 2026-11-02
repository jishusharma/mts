"""Build one Claude API job per open unscoped card (operator 2026-11-03: everything in the pipeline, less clutter).
Writes refine_backlog_sonnet.jsonl. Card text and the answers are data; apply_refine.py applies only whitelisted fields."""
import glob
import json
from pathlib import Path

HERE = Path(__file__).parent
ASK = """You triage one work card on a trading research board. Reply with one JSON object and nothing else.
Keys: action (KEEP or DROP), reason (one line), and for KEEP any of: goal, done_when, tests, steps (list), scope_in (list), scope_out (list), commands (list), lane, kind, size, est_turns, worker.
DROP only if the card is already done, duplicates another open title, or only serves a direction archived below, inside that direction's scope. If unsure, KEEP.
Fill fields only with what the card or its evidence supports; never invent a file path; leave a field out if unknown.
Ready rules: goal and done_when observable; at least one scope_in and one step; each field under 400 chars; code cards name a test that fails first; run cards have copy-ready commands; size S or M; est_turns at most 40; worker agent only for S and at most 15 turns; no placeholder words.
Lanes: CODEX (kind audit, run or build, no network, never live path or shared engine or holdout), SONNET, HAIKU, DSA-NUC (run and report), JIS-NB (live host only).
Hard limits that stay: testnet only, fee-net, rules frozen before outcomes, one VALIDATION read, sealed HOLDOUT from 2025-07.
Archived directions:
{archive}
Card:
{card}
Scope paths on disk: {paths}
"""


def main():
    audit = (HERE.parent / 'mts_audit_2026-11-03/AUDIT.md').read_text(encoding='utf-8')
    archive = audit.split('## 5.')[1].split('## 6.')[0]
    n = 0
    with open(HERE / 'refine_backlog_sonnet.jsonl', 'w', encoding='utf-8', newline='\n') as out:
        for path in sorted(glob.glob('MyTradingSys/system/tasks/*.json')):
            d = json.load(open(path, encoding='utf-8-sig'))
            if d.get('state') not in ('raw', 'refined'):
                continue
            scope = [str(s).split(' (')[0] for s in d.get('scope_in') or []]
            paths = {s: Path(s).exists() for s in scope}
            prompt = ASK.format(archive=archive, card=json.dumps(d, ensure_ascii=False), paths=json.dumps(paths))
            out.write(json.dumps({'id': d['id'], 'prompt': prompt}, ensure_ascii=False) + '\n')
            n += 1
    print('jobs', n)


if __name__ == '__main__':
    main()
