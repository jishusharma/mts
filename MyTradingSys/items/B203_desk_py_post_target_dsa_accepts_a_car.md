# B203 - `desk.py post --target DSA` accepts a card id that exists only as an uncommitted file in a worktree, so the DS

Filed: 2026-10-26
Status: OPEN
Priority: MED
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B203 | 2026-10-26 | OPEN | MED | `desk.py post --target DSA` accepts a card id that exists only as an uncommitted file in a worktree, so the DSA desk row pointed at a card no other machine could see for about 2 hours (cards lab-verify-rsi-40-60-bb-bounce-15m and lab-verify-mtf-bias-ladder). Fix: post refuses (or warns) unless `git cherry origin/fast-track` shows the card committed and shipped. | desk rows 20261026-181737-lab-verify-rsi-40-60-bollinger-boun, 20261026-200055-lab-verify-mtf-bias-ladder-higher-timefr; shipped later as CI green de501f71 | |
