# Pages follow data (operator 2026-11-13)
A supervisor reading `plan` output keeps every line, or filters with `^(PLAN|RUN|SPAWN|CI|WAKE|REPUBLISH|NOTE|OPERATOR|STALLED-BG|BOARD)`. A filter without REPUBLISH and NOTE dropped the stale-page lines for weeks.
`PLAN pages-stale N` and `REPUBLISH <slug> <file> <url>` (publisher login C): build, Artifact publish over the url, `artifacts.py publish-record --slug <slug>` that wake (SUPER_SESSION.md 3b).
Registry keys per page: `feeds` (input paths or globs), `max_age_h`, `producer` (script that prints REPUBLISH when it finishes), `publish_file`. `artifacts.py stale` flags a feed newer than the last publish or a page older than max_age_h.
