# B194 - Claude dispatcher lacks explicit tagging/assignment for Gemini-tailored task cards in task queue

Opened 2026-10-21 | Status OPEN | Severity MED | FIXER: Claude | LOGGER: Gemini
Carried from origin/fast-track during a DSA registry merge. This file is a placeholder so the registry check
finds an item doc for an open row; the owning session fills in the detail.

## Registry row

| B194 | 2026-10-21 | OPEN | MED | Claude dispatcher lacks explicit tagging/assignment for Gemini-tailored task cards in task queue | [FIXER: Claude] [LOGGER: Gemini] Operator request 2026-10-21: tasks.py has no dedicated GEMINI lane (only CODEX, HAIKU, SONNET, OPUS, DSA) and ready tasks lack unambiguous routing tags for Gemini/Argon sessions, leading to picking ambiguity between Claude and Gemini. Card gemini-task-dispatch-assignment. | - |
