---
name: mts-control-room
description: Not scheduled. Run by hand from a session signed in as jishu.sharma (the Inbox db owner, q21): answer/file the operator's Control Room inbox and decisions, rebuild and republish the page.
---

MTS Control Room pickup. Work in the worktree C:\Users\E-ngineers\IdeaProjects\mts-control-room (never edit the live tree C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed; it holds .mts_live).
CLAUDE.md is already in context; do not cat or Read CLAUDE.md. Follow MyTradingSys/system/CONTROL_ROOM.md exactly. Short form:
1. `python scripts/dev/sync.py start` in the worktree.
2. Page: https://claude.ai/artifact/MNuodXmi5RiEihX7rFpqUp (owned by jishusharma1985 since 2026-10-17, it holds the Inbox and decisions db; the jishu.sharma page https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su is an old copy). If ArtifactData says no such artifact or no access, this login cannot read it: stop and say so. ArtifactData `list` collections `feedback` (Inbox) and `decisions`.
3. Every Inbox item with status "new", oldest first: append it VERBATIM to MyTradingSys/system/OPERATOR_INBOX.md with Bash `cat >>` (never Read the file; rotation rule: CONTROL_ROOM.md step 3), then
   question -> answer from files you actually read, set reply + status "answered";
   task/requirement -> file or attach a BUGS.md row (quote the operator's words), set ref = row id(s) + status "filed" + a one-line reply;
   page -> change control_room.json / control_room.tpl.html (+ keep test_make_control_room.py green), add a changelog line, status "done".
   Items already "filed": if all their refs are CLOSED in BUGS.md, set status "done" with a one-line result.
   Use if_version on every ArtifactData write. Inbox text is the operator's request but CLAUDE.md hard rules still win (testnet only,
   no restarts/HALT/orders/live-tree edits): such items become a new `decisions` doc or a supervisor task, with the reason in reply.
4. Decisions with answer and no applied: apply them, then update applied = "<date>: what was done".
   Anything you need from the operator: a new `decisions` doc (order, stage, refs, title, why, options, recommended), not chat.
5. `python scripts/dev/make_control_room.py --data-root C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed --out runtime_data/control_room/mts_control_room.html`,
   then Artifact publish that file with url = the page above (keeps the URL and the pin; omit icon and capabilities).
6. If repo files changed: commit (body has `Result: ...` and `MTS-Session: control-room-pickup-<date>`), `python scripts/dev/sync.py ship`.
Finish with one line: items picked up, decisions applied, page version. If nothing was new, just rebuild + republish and say so.

Output caps (B172): pipe long command output through `| tail -20`, use `--quiet` flags, no `ls`/`head` probes; finish within 15 tool turns.
