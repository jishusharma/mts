# T052 — Define a real Tom-cited trigger for SETUP_CONFIRMED (D6b)
Opened: 2026-09-27 by session Opus 5.5 (session 4) | Type: research | Priority: P1 (blocks executor keying above SETUP_FORMING)
Source: D1_D7_DECISION_BRIEF.md, operator ruling D6b ("define a real Tom-cited trigger" instead of removal); B076 / finding F9.

Problem: SETUP_CONFIRMED is defined in compiled_engine sec 8 and listed in alert gating, but no code path emits it.
Goal: an operational trigger (what closes, where, confirmed by what) with a T1-T3 citation, or a documented
[SYSTEM] exception approved by the operator.

Candidates to evaluate (none accepted yet):
- Tom: trigger hierarchy, compiled_engine sec 5 — extract his exact confirmation language from the 39 unextracted
  transcripts first (R1 in ANALYST_LAYERS).
- Fabio: failed-auction confirmation (CC-3, ANALYST_LAYER_FRAMEWORK.md) — only fills the slot if the Tom-vs-Fabio
  override ruling allows Fabio definitions for "proof/trigger".
Acceptance: definition text + citation; implemented behind a flag; backtested per BACKTEST_PROTOCOL.md §6.
Until closed: no executor / alert / plan compiler may key on SETUP_CONFIRMED (compiled_engine sec 8 [SYSTEM] note, C5).
