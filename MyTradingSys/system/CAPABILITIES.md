# CAPABILITIES.md - MTS Trigger Map
# MTS version: see VERSION
# Purpose: One router. Tells any AI session which module to load for which task.
# Load rule: DSA_SESSION_PROMPT.md §3 owns boot order. Everything else
#            loads on trigger.
# Canonical: MyTradingSys/system/CAPABILITIES.md

---

## TRIGGER TABLE

| Task arrives as... | Load | Skip | Reason |
|--------------------|------|------|--------|
| JSON snapshot (uploaded/pasted) | `mts/runtime/compiled_engine.md`, `Dumps/dump_runtime.md`, `Dumps/dump_data.md` | Everything else | Deterministic engine + math + schema |
| Screenshot (chart image) | `mts/research/visual_validation_protocol_vvp002.md` | Engine files | Vision spec, no execution path |
| New transcript (analyst video) | `methodology/extraction.md`, `methodology/playbook.md` Part J | Engine files | Extraction lifecycle + verbatim rules |
| New rule proposed for engine | `system/01_AI_BEHAVIOR.md` Rules 31-41 | Everything else | Integration gate |
| Rule validation request | `system/01_AI_BEHAVIOR.md` Rule 32 | Everything else | 3-snapshot proof |
| Research question | `methodology/playbook.md` Part I | Extraction/engine | Meta-research + source tiers |
| Coordinator task handoff | `DSA_SESSION_PROMPT.md`, `mts/runtime/session_log.json` | Engine files | Ledger + active state |
| Probability layer work | `mts/research/event_probability_layer_DESIGN.md` | Engine files | Parked design (needs 500+ labels) |
| Engine edit proposed | `mts/runtime/compiled_engine.md`, condition file for the section | Everything else | Runtime authority + canonical doc |
| Data schema question | `runtime_data/data_schema_v1.2.0.md` | Engine files | Field-level contract |
| Cross-trader integration | `mts/research/cross_trader_integration_plan.md` | Everything else | 4-phase workflow |
| Session state update | `mts/runtime/session_state.json`, `mts/runtime/session_log.json` | Engine files | SSOT |
| Task list / status review | `system/02a_CURRENT_STATUS.md`, `system/COMPILED_DECISIONS.md` | Everything else | Status + decisions reference |

---

See DSA_SESSION_PROMPT.md section 3 for session boot order.

---

## COORDINATOR PATTERN

One primary session coordinates. Workers are spawned for isolated tasks.

- Primary maintains `session_log.json` with `type: worker_task` events:
  `{"type":"worker_task","worker":"<id>","task":"<desc>","status":"assigned|reported|accepted","ts":...}`
- Workers report back five lines: TASK / STATUS / SUMMARY / FINDINGS / NEXT
- Primary appends results to `session_log.json` and forwards follow-ups.
- No locks. No multi-session protocol. The primary session's log IS the ledger.
- **Coordinator prompt rule:** every prompt block that references a file
  must contain the real content pasted inline. Run `Get-Content` BEFORE
  writing the prompt. Placeholders (`<paste here>`) cause the worker to
  block correctly — that is a coordinator bug, not worker failure.
  See `01_AI_BEHAVIOR.md` Rule 38 + M-033.

---

## ANTI-PATTERNS

- Do not paste all 12 dumps. Use the trigger table.
- Do not load `compiled_engine.md` for extraction tasks.
- Do not load `extraction.md` for JSON sessions.
- Do not hand-edit `compiled_engine.md` without Rule 32 evidence.
- Do not invent a load order. If task is not in the trigger table, ask.

---

# END
