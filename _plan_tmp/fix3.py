import json
BASE = 'MyTradingSys/system/tasks/'
def load(cid):
    return json.load(open(BASE + cid + '.json', encoding='utf-8'))
def save(cid, d):
    open(BASE + cid + '.json', 'w', encoding='utf-8', newline='\n').write(json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

cid = 'control-room-page-nan-false-positive-1031'
d = load(cid)
d.update(size='S', worker='agent', est_turns=8, weight='ROUTINE', not_twin_of=['q17-p5-three-pages'], refined_by='planner-20261030-d',
  goal="scripts/dev/test_artifact_pages.py fails on mts_control_room.html with 'NaN' (S3 page gate red on trunk 488dd46db). The only NaN in the page is prose ('...regime boundaries, NaN prices...' inside the embedded data), not a rendering fault; reword that source string so the gate is green without weakening the checker.",
  scope_in=["scripts/dev/make_control_room.py", "MyTradingSys/system/artifacts/mts_control_room.html", "scripts/dev/test_artifact_pages.py"],
  scope_out=["no live-tree edit, no deploy, no process or HALT touch, no .secrets or .env read; the BAD_TEXT regex stays as it is; no Artifact publish"],
  steps=["grep -rn 'NaN prices' MyTradingSys scripts to find the source line the page data is built from (data file or make_control_room.py)",
         "reword it to 'not-a-number prices' (meaning unchanged), rebuild with python scripts/dev/artifacts.py build",
         "run python -m pytest -q scripts/dev/test_artifact_pages.py and scripts/dev/test_artifacts.py"],
  commands=["python -m pytest -q scripts/dev/test_artifact_pages.py", "python -m pytest -q scripts/dev/test_artifacts.py"],
  done_when="python -m pytest -q scripts/dev/test_artifact_pages.py reports 12 passed, 0 failed (was 11 passed, 1 failed on mts_control_room.html: NaN); artifacts.py stale shows the page changed so a republish card can follow.",
  tests="scripts/dev/test_artifact_pages.py::test_page_opens_clean_offline[mts_control_room.html] fails now (NaN) and passes after the reword",
  note="Final report ends with a Noticed: line. Blocked? List 2-3 non-destructive fixes, try the safest, verify, then report. Found by the planner's dry run 2026-10-31; the S3 page gate is red on trunk until fixed.")
save(cid, d)

stamp = "REVIEWED:2026-10-31 T0-ONLY "
for c in ['haiku-open-check-live-aid-tests-1031', 'haiku-recount-layer-review-and-gpt-audit-tables', 'haiku-artifact-registry-link-count-1031',
          'republish-6-stale-artifact-pages-flagged', 'flaky-scripts-dev-test-mts-doctor-py-tes', cid]:
    d = load(c)
    if not d['note'].startswith('REVIEWED'):
        d['note'] = stamp + d['note']
    save(c, d)
d = load('c24-oi-off-by-one-bar')
d['note'] = "PLANNER 2026-10-31: refined, IMPORTANT, parked as refined until a Sonnet reviewer stamps ACCEPT (no reviewer call this run). " + d['note']
save('c24-oi-off-by-one-bar', d)
