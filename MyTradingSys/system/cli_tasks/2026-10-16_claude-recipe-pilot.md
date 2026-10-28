# Headless Claude recipe pilot fallback

Why forced: Claude app screenshot/input automation failed, and the operator then explicitly prohibited
further computer-control calls. No screen control is used. A single Sonnet read-only model call supplies
independent feedback; the standard CLAUDE desk request remains if allowance is exhausted.

Exact argv: `claude -p --model sonnet --effort medium --tools Read --strict-mcp-config --no-chrome --permission-mode dontAsk --output-format json`
Working directory: `F:/MTS/mts-lab-reuse`. Feed the block below on stdin; capture JSON outside the repo
at `F:/codex_home/lab_runs/claude_recipe_pilot.json`. Codex files the sanitized result and any actionable
findings. Expected result: a brief sourced review or an explicit allowance error. No writes or shell tool.

```text
The operator asks for reusable ordered MTS lab recipes and a pilot with Claude. This is the explanation and first design pilot.
Sol 6.1 maps/builds; Astra independently challenges critical work; Luna then Sol handles mechanical DEV runs.
Every stage shares the goal and criteria; PASS receipts hash sources and reports before unlocking the next stage.
Token economy uses compact source indexes and avoids duplicate work, rather than adding a token cap.
You are the independent read-only reviewer. Codex owns the claim and shipping; do not execute the boot/git ritual.
Read MyTradingSys/system/LAB_RECIPES.md, scripts/dev/lab_flow.py and scripts/dev/test_lab_flow.py.
Review the stage-gate logic and reuse ergonomics; identify concrete correctness defects, not speculative redesigns.
Independently compute sum and mean of 10,11,9; the seeded sum claim is 31 and fee data is missing.
Return a concise report with verdict, exact file:line evidence, computed values, and any fix needed before wider use.
No UI, subagents, code changes, holdout reads or further operator questions. Missing access is NOT_IN_DATA.
```
