# NEXT SESSION (hand-over 2026-10-22, branch claude/krown-layer-audit, commit 86d3cec0 + this)
Task: ship the prereq hook (scripts/dev/prereq_guard.py, tasks.py `need`, cards) to origin/fast-track.
1. Gate step 4c: register scripts/dev/test_prereq_guard.py in scripts/dev/run_extra_tests.py EXTRA (next to test_stop_guard.py), so
   MyTradingSys/tests/test_gate_discovery_b150.py passes.
2. Gate step 3ad: test_auto_deploy.py test_sh_timeout_kills_the_whole_process_tree_not_only_the_direct_child failed in the cloud
   container (grandchild alive after timeout); not touched by this change; passed on two ships earlier 2026-10-22. Rerun; if still red,
   file a card (`tasks.py new "Network: auto_deploy grandchild kill flaky in cloud" --lane SONNET`).
3. Check NeedTest fails on HEAD~1 tasks.py (not yet verified), then `python scripts/dev/sync.py ship`; `git cherry origin/fast-track` empty.
