import json
p="MyTradingSys/system/tasks/live-host-txt-owner-and-test-fixtures.json"
c=json.load(open(p,encoding="utf-8"))
c.update(
not_twin_of=["live-mirror-follow-live-host-move"],
goal="live_host.txt says JIS-NB but the live owner is DESKTOP-F7IU69N (heartbeat under 10 s). Write the real owner into the file; first make test_hostname_case_does_not_matter and test_worktree_on_jis_nb_reads_local_folder use a fixture, not the real file.",
scope_in=["scripts/dev/test_live_mirror.py","scripts/dev/live_mirror.py","MyTradingSys/system/live_host.txt"],
scope_out=["live tree .mts_live","HALT files","supervisor.py behaviour","deploy"],
steps=["Confirm owner: python scripts/dev/live_owner.py check (heartbeat < 10 s) and live_mirror.py brief name DESKTOP-F7IU69N; if not, stop and note it",
"Fail-first: first write DESKTOP-F7IU69N to live_host.txt only in the working copy and run test_live_mirror.py: the two named tests fail (record it)",
"Patch lm.LIVE_HOST and lm.DEFAULT_ROOT to JIS-NB values in that test class setUp (mock.patch.object, like test_live_host_file_moves_the_share_and_local_folder_rule), so the two tests ignore the real file",
"Keep DESKTOP-F7IU69N in live_host.txt; run test_live_mirror.py and test_supervisor.py; ship. Verify: content sha, git cherry origin/fast-track <sha> empty, files in ls-tree."],
tests="scripts/dev/test_live_mirror.py: with live_host.txt = DESKTOP-F7IU69N the two named tests fail before the setUp fixture and pass after (record both runs).",
commands=["python scripts/dev/live_owner.py check","python scripts/dev/test_live_mirror.py","python -m pytest scripts/dev/test_supervisor.py -q"],
done_when="live_host.txt reads DESKTOP-F7IU69N; test_live_mirror.py and test_supervisor.py pass with it; the fail-first run (two tests red when the file changed, before the fixture) is quoted in the result; shipped.",
size="S",est_turns=12,worker="agent",weight="IMPORTANT",
sources=["MyTradingSys/system/live_host.txt:1","scripts/dev/test_live_mirror.py:381-387"],
note="PLANNER 2026-10-31 model sonnet. live_host.txt also routes the JIS-NB lane in supervisor.py: after the write JIS-NB cards go to the Lenovo (intended, LIVE_HOST_MOVE.md). Twin check: live-mirror-follow-live-host-move is a publish run, not a twin.")
json.dump(c,open(p,"w",encoding="utf-8",newline="\n"),indent=2,sort_keys=True)
open(p,"a",newline="\n").write("\n")
