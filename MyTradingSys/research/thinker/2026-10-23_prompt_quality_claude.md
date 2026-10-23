# Prompt quality for MTS sessions: Claude-specific research (Thinker, 2026-10-23)

Operator ask: every casual prompt gets structured before work starts (a "Prompt_Guy"), fixed rules, tested hooks, fail-safe.
Every row below has a source; anything without one is labelled OPINION.

## Findings
| # | Finding | Source |
|---|---|---|
| 1 | A UserPromptSubmit hook cannot replace the prompt text. It can only add `additionalContext` beside it, or block it. So "rewrite the prompt" is impossible in a hook; "add a structured header, original kept" is the supported shape. | code.claude.com/docs/en/hooks (decision-control table, fetched 2026-10-23) |
| 2 | Hook failure is non-blocking: non-zero exit (not 2), timeout (30 s default on UserPromptSubmit) or invalid JSON lets the prompt through. Fail-safe by default; `onFailure: block` exists (v2.1.295+) and must NOT be used here. | same |
| 3 | additionalContext / stdout cap: 10,000 characters each; longer goes to a file with a 2,000-char preview. Header must stay far under that. | same |
| 4 | Anthropic's rule: an unclear prompt confuses the model as it would a new colleague; be explicit on format, constraints, and why. | prompting best practices, "Be clear and direct", "Add context" |
| 5 | Phrasing decides act-vs-suggest: "Can you suggest..." yields suggestions; "Change this function..." yields edits. A question ("what do you think?") invites an answer and a go-ahead request, not work. | same page, "Tool usage" |
| 6 | Anthropic's recommended fix is a standing instruction `<default_to_action>`: implement rather than suggest. We already have the same rule in CLAUDE.md ("do it now") but the Thinker role file overrides it with "NEXT: pick A/B/C". | same page; thinker.md reply format |
| 7 | Research tasks: give clear success criteria, verify across sources, keep competing hypotheses, self-critique. This is the criteria-first prompt the operator wanted. | same page, "Research and information gathering" |
| 8 | Anthropic's own prompt improver rewrites prompts with a model (Console tool, 2024); their 30% gain is their own test on Claude 3 Haiku, a classification task; not our task. Model rewriting needs an eval to trust it. | claude.com/blog/prompt-improver; overview page "Before prompt engineering" says: define success criteria and a way to test first |
| 9 | Long inputs: documents on top, the question at the end (up to 30% better in their tests). Applies to the header: original text first, then the task line last. | best practices, "Long context prompting" |
| 10 | Our hook already exists: `scripts/dev/role_loader.py` emits `hookSpecificOutput.additionalContext` on UserPromptSubmit and has `MyTradingSys/tests/test_role_loader.py`. A prompt header is one more branch there, no new hook. | role_loader.py:398,416,461 |

## What this changes in the plan
- Option A (hook plus fixed rules) is confirmed feasible and is the only shape the platform allows (1). A model rewriter (option B) would also have to live in the hook or a role; it cannot replace text and has no eval (8).
- The header goes at the END of the injected context (9), original prompt untouched (1).
- Fail-safe is free (2): a crashed hook passes the raw prompt.
- The "say go" bug is caused by (5)+(6): question-shaped prompts and a role file that ends every reply in a gate.
- One measured step remains (the only claim without our own number): do structured-header prompts beat raw ones on our tasks? A/B on 5 past operator prompts, same task, scored on the criteria in the card. Not run this turn: it costs 10 session runs; it is card step 1.

## Options
| # | Option | Cost (OURS) | ROI | Risk / undo |
|---|---|---|---|---|
| A | Header branch in role_loader (script, no LLM): TASK / CRITERIA / PROOF / OUT OF SCOPE / DEFAULTS filled from the operator's words, `not stated` otherwise; verbatim-original test; `default_to_action` line when the prompt asks for work | ~2 cards | Structure on every prompt, zero model cost, fail-safe by platform | Regex extraction misses vague prompts; undo = remove one branch |
| B | Prompt_Guy role (model rewrite per message) | ~1 card + a model turn per message | Smarter wording | Cannot replace the prompt (1); extra cost each turn; meaning drift; no eval |
| C | Only fix the Thinker role (no gate at end of reply) + CLAUDE.md `default_to_action` | the bug card | Fixes the "say go" failure | Does not structure casual prompts |

RECOMMEND: C now (already filed: bug-ask-go-for-asked-work), then A with the A/B test as its first step.
