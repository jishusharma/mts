# CONTEXT_BASELINE - what every MTS session loads first (2026-10-15)

Measured on JIS-NB from `~/.claude/projects/*BinanceDataFeed*` transcripts, 2026-10-08..15 (284 sessions, 107 subagents).
First request (input + cache): Sonnet median **64.6k** (n=160), all models 66.8k, subagents 55.2k.
Est. = text size / 4 of each family's tool schemas, server notes and skill blurb (not an A/B run).

| Family | Used 7d (calls/sessions) | Est. tokens | Do |
|---|---|---|---|
| Computer use (27 tools + notes + skill) | 0 | 1.8k | off |
| Claude in Chrome (22 tools + notes + skill) | 3/3, tab probes only | 0.8k | off |
| Claude Docs connector (8 tools + docs skill) | 0 | 0.9k | off |
| visualize connector (2 tools) | 0 | 1.0k | off |
| Skills docx pptx xlsx pdf google-workspace morning import-memory skill-creator deep-research | 0 | 1.5k | off |
| Built-in browser (19 tools) | 91/6: YouTube, papers, page preview | 4.4k | keep |
| scheduled-tasks | 106/39 | 0.1k | keep |
| Rest: system prompt, core + app tools, Artifact, CLAUDE.md, memory | always | ~54k | fixed |

Saving if all "off": ~5.9k on every request (~9%); a 15-turn session reads ~89k fewer tokens.

## Clicks (operator, once per login: jishu.sharma, jishu.awgp, jishusharma1985)
1. Claude desktop > Settings > This computer > System > Computer use: switch off **Enable computer use**.
2. Claude desktop > your initials (lower left) > Settings > Connectors > Claude in Chrome > Configure: off.
3. claude.ai > Customize > Connectors: disconnect **Claude Docs** and **visualize**.
4. claude.ai > Customize > Skills: switch off the 9 skills in the table (keep built-in-browser).
Docs do not say each switch also drops the text from Code sessions; the re-measure below proves it.

Everything switches back on the same way; nothing is deleted. Decision: q-context-baseline (OPERATOR_DECISIONS.md).
Re-measure: `python scripts/dev/token_audit.py --days 7` (first-turn input) after the clicks.
