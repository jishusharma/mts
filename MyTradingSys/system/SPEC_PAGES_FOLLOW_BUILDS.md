# SPEC: pages follow builds (card pages-follow-builds-1107)

Operator 2026-11-07 (d-pages-updated-stamp-follow-builds-1107): every page shows its last-updated time at the top; pages are
republished whenever their build changes. Root cause of the staleness: builds are scripted, but publishing needs the Artifact tool,
which only a Claude Code session on a publisher login has (owner jishusharma1985; logins given edit access after the operator shares
the pages). Scripts, API jobs, Gemini and DSA cannot publish; the ship gate only warns.

## Done when
1. `artifacts.py build` (make_home.py, make_layers_board.py) and `cbp_v2/tools/build_board.py` write `Updated YYYY-MM-DD HH:MM UTC`
   as the first visible element of every generated page (MTS Home already has a stamp; make it uniform and first).
2. `registry.json` gets a `publishers` list (jishusharma1985 + logins the operator gave edit access). The UserPromptSubmit hook prints
   `PAGES STALE n: <slugs>` (from `artifacts.py stale`) for sessions on a publisher login; nothing for other logins.
3. `supervisor.py plan` prints one `REPUBLISH <slug> <html> <url>` line per stale page; SUPER_SESSION.md "Every wake" gets the step
   (build at zero tokens, publish over the url, `artifacts.py publish-record --slug`).
4. `cbp_run.rebuild_dashboard` ends by printing the REPUBLISH line for cbp_analyst_desk and sending `mts_signal.py ask` to the
   publisher login when the run happened on a non-publisher login.
5. Tests for 1-3 fail on the pre-change tree; CI green; no scheduler, no second copies, no page content changes.
