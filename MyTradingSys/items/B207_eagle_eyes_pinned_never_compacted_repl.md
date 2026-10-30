# B207 - Eagle_Eyes 'pinned, never compacted, replaced at the cap' (roles/eagle_eyes.md line 7; CLAUDE.md step 5: live 

Filed: 2026-10-27
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B207 | 2026-10-27 | OPEN | HIGH | Eagle_Eyes 'pinned, never compacted, replaced at the cap' (roles/eagle_eyes.md line 7; CLAUDE.md step 5: live threads hand over after 5 screenshot reads) is not enforced: one live-market session ran past 24 h and was auto-compacted by Claude Code several times, with state carried by a summary. Each compaction cost accuracy (said BTC triggers worked during the Yahoo stall; said no close above 79,836 when one existed). Nothing counts screenshot reads or warns the operator. Also the watcher that keeps the session awake (Monitor, 30 min cap, B202) is not documented in the role file, so the operator cannot tell it is not continuous. Candidate fix: a read counter in the role hook that prints HAND OVER at 5 reads or first compaction; a 'Live mode' paragraph in eagle_eyes.md (what wakes the session, what is lost between arms, how to restart). | 10-27 operator question 'what is the mechanism, and what about context'; eagle_eyes.md:7; 33 watcher arms | |
