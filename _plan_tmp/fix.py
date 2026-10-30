import json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'MyTradingSys/system/tasks/'
def edit(cid, **kw):
    p = BASE + cid + '.json'
    d = json.load(open(p, encoding='utf-8'))
    d.update(kw)
    open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

fs = ["MyTradingSys/tools/live_aid/test_live_aid.py", "MyTradingSys/tools/live_aid/test_live_aid_replay.py",
      "MyTradingSys/research/sim_desk/test_page_click.py", "scripts/dev/test_artifact_pages.py"]
edit('haiku-open-check-live-aid-tests-1031',
     commands=["python -m pytest -q " + f for f in fs],
     steps=["run each command from the repo root, one at a time (these are pytest files: plain python prints nothing); keep the last 15 lines",
            "parse the pytest summary line of each (passed/failed/skipped); never judge from truncated output",
            "report 4 lines: <file>: <p> passed, <f> failed, <s> skipped; quote each failure's first error line and file it as a raw card via tasks.py new (id suffix -1031)"],
     note="Final report ends with a Noticed: line. Blocked? List 2-3 non-destructive fixes, try the safest, verify, then report. PLANNER 2026-10-31 dry run on trunk 488dd46db: 34 + 11 + 4 passed; test_artifact_pages 11 passed, 1 failed (mts_control_room.html: NaN): expect that failure reported, not fixed.")
