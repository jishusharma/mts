import json, sys
BASE = 'MyTradingSys/system/tasks/'
def edit(cid, **kw):
    p = BASE + cid + '.json'
    d = json.load(open(p, encoding='utf-8'))
    d.update(kw)
    open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

NOTE = "Final report ends with a Noticed: line. Blocked? List 2-3 non-destructive fixes, try the safest, verify, then report."
OUT = "no live-tree edit, no deploy, no process or HALT touch, no .secrets or .env read; no product-code edit"
D11 = ["MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md"]

edit('haiku-recount-layer-review-and-gpt-audit-tables',
     size='S', worker='agent', est_turns=10, weight='ROUTINE', refs=D11, scope_out=[OUT + "; the audited files are read only"],
     goal="Recount structure claims by hand: the layer review sheet's headings and each GPT formula-audit report's inventory rows against what the report itself says it covers. SAME/DIFF per file, no edits.",
     scope_in=["MyTradingSys/research/layer_lab/reports/layer_review_tom_guidance.md",
               "MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-krown-layer.md",
               "MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-kurisko-layer.md",
               "MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-pitchfork-layer.md",
               "MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-pizzino-layer.md",
               "MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-rsi-layer.md"],
     steps=["layer_review_tom_guidance.md: count lines starting '## ' (expect 4: tom_core, tom_proofs, tom_vp_pivot, bb_lvn_triggers) and '### ' under each (expect 5 each: Idea and source, Parameters, Backtests, Bugs and assumptions, Confluence); compare with the 4 layers its line 7 names",
            "each gpt-audit-formulas-vs-*.md: count the data rows of its 'Formula inventory' table, and count the distinct FORMULAS.md section numbers its 'What was checked' line cites; for each report note rows with MATCH vs not (rsi report: 7 rows, 6 MATCH, 1 NOT_IN_DATA)",
            "report one line per file: <file>: <n> counted vs <m> claimed, SAME or DIFF; a DIFF is filed as a raw card via tasks.py new"],
     commands=[],
     done_when="report has 6 lines (1 sheet + 5 audits), each with a counted number and the file's own claimed number side by side, SAME or DIFF; no repo file changed.",
     tests="count-based: 6 SAME/DIFF lines; the rsi audit must show 7 rows / 6 MATCH / 1 NOT_IN_DATA or a DIFF explaining why",
     note=NOTE)

edit('haiku-artifact-registry-link-count-1031',
     size='S', worker='agent', est_turns=6, weight='ROUTINE', refs=D11, scope_out=[OUT + "; no Artifact publish"],
     goal="Count what artifacts.py check and audit-links say about the registry today (the feeder-rule check after a page ship), so a drift shows as a number.",
     scope_in=["MyTradingSys/system/artifacts/registry.json", "scripts/dev/artifacts.py"],
     steps=["run python scripts/dev/artifacts.py check and keep the final summary line (reference 2026-10-31: 'artifacts: 11 pages ok')",
            "run python scripts/dev/artifacts.py audit-links and count rows whose status column is OK vs anything else (reference: 5 link rows, all OK)",
            "report: <n> pages ok of <total>; <k> link rows OK, <j> not OK with each not-OK row quoted; a changed number is filed as a raw card via tasks.py new"],
     commands=["python scripts/dev/artifacts.py check", "python scripts/dev/artifacts.py audit-links"],
     done_when="report holds 'pages ok n of N' and 'links OK k, not OK j' parsed from the two commands' own output, each next to the 2026-10-31 reference; no repo file changed.",
     tests="count-based: both numbers present; card not done on a command crash or an empty parse",
     note=NOTE)

edit('republish-6-stale-artifact-pages-flagged',
     lane='HAIKU', size='S', worker='agent', est_turns=15, weight='ROUTINE', prio=3, asks="", refs=[],
     title="Republish the stale artifact pages that login C (jishusharma1985) owns (artifacts.py stale; 2 stale on 2026-10-31, was 6)",
     goal="Bring every stale page that login C owns back to its repo build: Artifact read then publish over the page's own url, then publish-record. Pages C does not own or cannot edit are listed, not published.",
     scope_in=["MyTradingSys/system/artifacts/registry.json", "MyTradingSys/system/artifacts/mts_control_room.html", "MyTradingSys/system/artifacts/layer_map.html"],
     scope_out=[OUT + "; never publish a second copy (a new url); no page without edit access ('writer' in Artifact read)"],
     steps=["run python scripts/dev/artifacts.py build, then python scripts/dev/artifacts.py stale; keep the STALE lines (2026-10-31: mts_control_room, mts_layer_map)",
            "per STALE slug: take the url in registry.json under urls.jishusharma1985; Artifact action read that url; only if the header says writer, Artifact publish the repo html over that same url",
            "after each publish: python scripts/dev/artifacts.py publish-record --slug <slug>",
            "re-run artifacts.py stale and report the count before and after; list any page skipped (not owned by C, no edit access) with the reason"],
     commands=["python scripts/dev/artifacts.py build", "python scripts/dev/artifacts.py stale", "python scripts/dev/artifacts.py publish-record --slug <slug>"],
     done_when="artifacts.py stale prints no STALE line for a page login C can edit (count N -> 0); every page skipped is listed with its reason; registry.json pub date for each republished slug is today.",
     tests="count-based: artifacts.py stale STALE-line count before vs after, reported",
     refined_by="planner-20261030-d",
     note=NOTE + " | PLANNER 2026-10-31 refined to HAIKU: the 2026-10-30 SKIPPED note is superseded (both remaining stale pages have a jishusharma1985 url; per-login Artifact publish is the step, run from login C). Pages a later q17-p5-three-pages retires are dropped from the list.")

edit('flaky-scripts-dev-test-mts-doctor-py-tes',
     lane='SONNET', size='S', worker='agent', est_turns=8, weight='ROUTINE', prio=3,
     goal="Make test_same_day_run_twice_gives_the_same_report deterministic: pin the free-disk reading so the report text cannot differ between the two runs (CI run 41126898994: 93 vs 94 GB).",
     scope_in=["scripts/dev/test_mts_doctor.py", "scripts/dev/mts_doctor.py"],
     scope_out=[OUT + "; the doctor's real disk check stays as it is"],
     steps=["in test_same_day_run_twice_gives_the_same_report monkeypatch shutil.disk_usage (or D.disk) to a fixed value",
            "fail-first: add test_report_text_changes_with_disk_reading that patches disk_usage to 93 GB then 94 GB between two runs and asserts the two texts differ only on the DISK line; confirm the original unpatched test shape fails under that patch",
            "run python -m pytest -q scripts/dev/test_mts_doctor.py until green"],
     commands=["python -m pytest -q scripts/dev/test_mts_doctor.py"],
     done_when="python -m pytest -q scripts/dev/test_mts_doctor.py exits 0 with the pinned test passing 20 times in a row (loop of 20 runs of that test, 0 failures).",
     tests="scripts/dev/test_mts_doctor.py::test_report_text_changes_with_disk_reading fails on the pre-change test shape under a moving disk value; the pinned same-day test passes",
     refs=[], refined_by="planner-20261030-d", note=NOTE)

edit('c24-oi-off-by-one-bar',
     lane='SONNET', size='M', worker='session', est_turns=20, weight='IMPORTANT', prio=3,
     goal="Fix the bar/OI pairing in oi_after_flush.py (Bybit OI is stamped at snapshot time t = bar open, so a flush bar's OI change is oi[t+5m]/oi[t]) and recheck the group counts n=18/9/22.",
     scope_in=["MyTradingSys/research/eagle_eyes_picture_2026-10-28/oi_after_flush.py", "MyTradingSys/research/eagle_eyes_picture_2026-10-28/test_oi_after_flush_pairing.py"],
     scope_out=[OUT + "; public Bybit market data only; no order or account call"],
     steps=["move the pairing into a pure function flush_oi_change(O, C, I, j) so a test can call it without the network fetch",
            "fail-first: test_oi_after_flush_pairing.py builds a 4-bar synthetic series where bar 1 drops price 0.4% and I[2]/I[1]-1 = -0.3%; asserts the function returns -0.3%, which the old i vs i-1 pairing does not",
            "fix the pairing, rerun the script, write both group-count tables (old vs new pairing) to MyTradingSys/research/eagle_eyes_picture_2026-10-28/OI_PAIRING_RECHECK.md; label thresholds OURS"],
     commands=["python -m pytest -q MyTradingSys/research/eagle_eyes_picture_2026-10-28/test_oi_after_flush_pairing.py", "python MyTradingSys/research/eagle_eyes_picture_2026-10-28/oi_after_flush.py"],
     done_when="test_oi_after_flush_pairing.py passes and failed before the fix; OI_PAIRING_RECHECK.md lists group n for old and new pairing (old: 18/9/22) and states whether any forward-return claim changed.",
     tests="MyTradingSys/research/eagle_eyes_picture_2026-10-28/test_oi_after_flush_pairing.py fails on the pre-change pairing",
     refs=[], refined_by="planner-20261030-d", note=NOTE + " Public data (q-gap-c) is pre-approved.")
