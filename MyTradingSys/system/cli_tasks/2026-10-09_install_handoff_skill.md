# CLI task: install the mts-session-handoff skill

Why forced: remote file tools cannot write under `.claude/` (blocked call: writing `.claude/skills/mts-session-handoff/SKILL.md`). The skill text is staged at `scripts/dev/skill_src/mts-session-handoff/SKILL.md` (outside MyTradingSys, so the doc test does not scan it).

Run from the repo root in a worktree (PowerShell):

```powershell
New-Item -ItemType Directory -Force .claude/skills/mts-session-handoff | Out-Null
Copy-Item scripts/dev/skill_src/mts-session-handoff/SKILL.md .claude/skills/mts-session-handoff/SKILL.md
```

Expected result: `.claude/skills/mts-session-handoff/SKILL.md` exists, LF endings; a fresh Win App session lists `mts-session-handoff`. If it does not, add a pointer to that path in CLAUDE.md. Then delete `scripts/dev/skill_src/` or keep it as the canonical source.
