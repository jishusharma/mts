---
interview: yes
topic: AI coding agents - hooks, tokens, context, cost, process startup
level: beginner to interview
date: 2026-10-22
source: operator Q&A in a Claude Code session (MTS project); numbers measured on the laptop DESKTOP-F7IU69N that day
---
# Primer: hooks, tokens, context and cost in an AI coding agent

Written for a tester with a mechanical-engineering background. Each part ends with "Interview line": one sentence you can say.

## 1. What the agent actually is
Claude Code is a loop run by a program on your machine (the "harness"):
1. It sends the model everything so far: system prompt, tool descriptions, project rules (CLAUDE.md), and the whole conversation.
2. The model answers with text, or with a request to use a tool ("run this command", "read this file").
3. The harness runs the tool on your machine and adds the result to the conversation.
4. Back to step 1, until the model answers without a tool request. That is one "turn".

The model never touches your disk. The harness does, on its behalf. Mechanical analogy: the model is the engineer at the desk, the harness is the
shop-floor technician who does what the engineer writes on the job card and brings back the measurement.

Interview line: "An agent is an LLM in a loop with a tool executor; the model proposes actions, the harness executes them and feeds the results back."

## 2. Tokens and why every step costs more as a session grows
- A token is a chunk of text, about 4 characters of English or code. 1,000 tokens is about 750 words.
- The model has no memory between calls. Every step (step 1 above) re-sends the whole conversation, so a 200k-token session pays to read
  200k tokens again on every tool call, not once.
- Prompt caching softens this: the unchanged start of the conversation is cached, and cached reads are billed at about a tenth of fresh
  input. They are still not free, and the cache expires when the session is idle for a while.
- Output tokens (what the model writes) cost about 5 times input tokens.
- Fixed cost of a turn in the desktop app was measured at 70-80k tokens before any work (tool descriptions 39k, connector tools 26k, prompt 9k,
  skills 6k, memory 3k; SUPER_SESSION.md audit 2026-10-15). A headless CLI worker can load far fewer tools, so its fixed cost is much lower.

Interview line: "Cost grows with context length times number of steps; caching cuts the re-read price but does not remove it, so long-lived
sessions get progressively more expensive per step."

## 3. Compaction
Compaction replaces the long conversation with a written summary and continues from it.
- It costs one big step once (read everything, write the summary).
- It saves on every later step (each one re-reads the short summary instead of the long history).
- So it pays off when many steps follow. At 227k tokens with a new task ahead, it pays back within a few steps. At 60k tokens with two steps left, it
  never pays back. The MTS audit (2026-10-15) found 39 of 68 compactions lost money because they happened late in short-lived sessions.
- What you lose: fine detail. The full old transcript stays on disk and can be searched, so details can be recovered when needed.
- For unattended workers the cheaper pattern is "one task per session": finish, write a hand-over note, end. A fresh session starts small.

Interview line: "Compaction trades one expensive summarisation step for cheaper later steps; it is worth it only when enough steps follow."

## 4. Hooks
A hook is a small program the harness runs automatically at a fixed moment, configured in `.claude/settings.json`:
- SessionStart: when a session opens.
- UserPromptSubmit: when you send a message, before the model sees it.
- PreToolUse: before a tool runs. It can say allow, deny or ask.
- PostToolUse: after a tool runs. It can add a note for the model.
- Stop: when the model wants to end its turn. It can say "not yet, because ...".

Why they exist: written rules in a prompt are requests; the model can forget or misread them. A hook is code, so it is enforced every time.
In MTS, `safety_guard.py` denies reading secrets or force-pushing git, `model_guard.py` enforces the model rules, and `turn_meter.py` counts steps.
Testing analogy: the prompt is the test plan, the hook is the assertion that fails the build.

Why a tool call waits: a blocking (synchronous) hook must answer before the tool may run, because its answer can be "deny". The harness waits
for the hook program to finish. Hooks of the same event run in parallel, so the wait is the slowest one, not the sum.
Hooks that only add information (count a step, post a status line) do not need to block. Claude Code can run them in the background
(`"async": true`); their note arrives on the next turn.

Interview line: "Hooks are deterministic guardrails around a non-deterministic model: pre-execution hooks can veto an action, post-execution
hooks observe; only the veto ones need to block."

## 5. Why a hook costs about half a second on this laptop
It is not the CPU core count. Each hook is a new Python program, and starting a program on Windows has fixed costs:
- Process creation is slower on Windows than on Linux.
- The antivirus scans the program and every file it opens.
- Python loads its standard library from many small files (the `json`, `re`, `pathlib` modules), and each file open is checked again.
Measured on 2026-10-22: an empty Python program takes 0.26-0.55 s to start and stop. A typical MTS hook takes 0.5 s, of which about 0.3 s is
startup and imports and only a few milliseconds are its real work.

"Web library" means `urllib.request`, Python's built-in module for HTTP calls. `ci_watch.py` imported it at the top, so every prompt paid 0.47 s
to load it even when the CI status came from a 5-minute cache and no web call happened. The fix is to import it only inside the function
that fetches ("lazy import").

Levers, biggest first: run fewer hook processes (background the non-blocking ones, skip hooks that do not apply via the `if` filter), import
lazily, avoid git or network calls in hooks that run on every step.

Interview line: "On Windows, process start-up and AV scanning dominate short scripts, so the optimisation is fewer processes and lazy imports,
not faster code."

## 6. Weekly limits and pacing
Subscription plans have a rolling short window and a weekly allowance per login. Two failure modes: spend it all early in the week and stall,
or leave it unused and lose it at the reset (happened with Fable and GPT). The fix is pacing: compare "share of the week gone" with "share of
the allowance used"; behind plan, start more workers; ahead of plan, slow down. Cheaper models (Haiku, Sonnet) for routine work stretch the
allowance; the strongest model only where an error would be expensive.

Interview line: "Treat a token budget like a burn-down chart: pace consumption against elapsed time and route work to the cheapest model that is
good enough."
