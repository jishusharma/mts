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

### 2026-10-04T10:15Z - builder, session MTS-2026-10-04-1009Z-APP-BLD-t052-b063-t046

OUTCOME: no Tom trigger exists. SETUP_CONFIRMED stays unused. No code, no flag, no emitter.
Method: read compiled_engine sec 5 and 8; read the fresh extracts for the confirmation language; grepped all 102
files in raw_transcripts_canonical for "confirm" (23 hit). Keyword search only; the 39 never-extracted transcripts
were not read in full.
Evidence:
- runtime/compiled_engine.md L378-388 (sec 5): Tom evaluates triggers contextually, "no fixed mapping". Sec 8 L443 defines
  SETUP CONFIRMED as "trigger confirmed" but nothing defines which event closes that trigger.
- extracts/fresh/extract_YopZ5ZDmMFw_fresh.md:146 and extract_rrHj24GSR6M_fresh.md:124, GAPS DOCUMENTED: "Tom does not
  address in this video: Exact entry trigger pattern or candle confirmation".
- extracts/fresh/extract_4MoNjEQ2Dd8_fresh.md:87 (verbatim in raw): "here it confirmed it again and showed us that there are
  aggressive buyers." Absorption at a zone used as confirmation; same file L413 records "No formal criteria for
  'aggressive buying'... used as confirmation but not defined". This is proof at the zone, already an input to
  proof_count / SETUP_FORMING, not a separate closing event.
- extracts/fresh/extract_rFPCtOcfUMI_fresh.md:71 (verbatim in raw rFPCtOcfUMI:13): "don't trade the delta divergence alone
  always use confirmation". Says to confirm; gives no definition of what confirms.
- extracts/fresh/extract_RwQBdF9TSvc_fresh.md:144 uses "the market confirms it" but L17 marks the speaker as a guest
  (Serge), not Tom. Excluded.
Fabio CC-3 (failed-auction confirmation, ANALYST_LAYER_FRAMEWORK.md:145) is not Tom. Under the Tom-core rule it can only
be a separate layer, never the SETUP_CONFIRMED trigger. No Tom-vs-Fabio override ruling was found in the files read.
Consequence: compiled_engine sec 8 L455-459 [SYSTEM] note stays as written (highest actionable verdict = SETUP_FORMING).
The dead SETUP_CONFIRMED entries in auto_trader.py:63 and auto_trader_config.json:12-15 remain a supervisor item (B076 residual).
Reopen only when a Tom quote names the closing event, with transcript position.
Register: BUGS.md T052 row still reads OPEN; not edited here (outside the four named files). Operator or supervisor may close it.
