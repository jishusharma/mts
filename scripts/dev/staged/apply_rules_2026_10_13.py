"""STAGED, NOT RUN: rule rewrite the operator asked for in chat 2026-10-13 (no fixed core; SOURCED/OURS numbers).

The cloud session that wrote this could not apply it: its permission check blocks an agent from editing its own instruction
files (CLAUDE.md, LESSONS_DIGEST.md, ...). Run it from a worktree once the operator says OK:
    python scripts/dev/staged/apply_rules_2026_10_13.py           # dry run: lists what would change, writes nothing
    python scripts/dev/staged/apply_rules_2026_10_13.py --apply   # writes; then make_layers_md.py, gate, ship
Every substitution is exact text. If one does not match, the script stops before writing anything.
Task: MyTradingSys/system/cli_tasks/2026-10-13_rules_rewrite.md
Safety rules are untouched: testnet only, live tree, keys, deploy path, AUTO_PAUSE.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[3]
APPLY = "--apply" in sys.argv
EDITS = []


def sub(rel, old, new, count=1):
    EDITS.append((rel, old, new, count))


QUOTE = ('"We need flexible system now that can adapt to whatever change we need to bring. So we have to remove all those uh, '
         'hard rules about layers and everything." ... "why do not we just apply our own brains rather than uh, depending on uh, '
         'what we find where we have the core idea and we have the chart we have the data so let us apply the core idea on the '
         'chart and uh, see how it needs to be adjusted in order to make profitable trades."')

# 1. CLAUDE.md hard rules (layers + numbers)
sub("CLAUDE.md",
    "- Tom is core; every other indicator system is a separate layer (PROJECT_VISION), never a Tom filter.\n"
    "- Provenance (operator 2026-09-30): every engine/layer parameter, gate and label comes from that trader's own words\n"
    "  (transcript quote + file:line) or it does not exist. Unsourced = NO-SOURCE: flag, then remove or replace; never tune it.\n",
    "- Layers (operator 2026-10-13, replaces \"Tom is core\"): no fixed core. Tom, Fabio and every other system are layers that may be\n"
    "  combined, used as filters or switched off; fee-net out-of-sample results decide what trades, never doctrine (PROJECT_VISION 2026-10-13).\n"
    "- Numbers (operator 2026-10-13, replaces the 2026-09-30 provenance ban): label every engine/layer parameter SOURCED (trader's words,\n"
    "  quote + file:line) or OURS (our judgement or tuned). OURS is allowed: chosen on DEV, checked once on VALIDATION, holdout read once,\n"
    "  every variant in the trial ledger. Never present an OURS number as the trader's.\n")

# 2. PROJECT_VISION: new direction entry on top; mark the superseded interpretation lines (not verbatim sections)
sub("MyTradingSys/PROJECT_VISION.md",
    "# Change rule: verbatim sections change only by operator edit. No agent rewrite.\n\n",
    "# Change rule: verbatim sections change only by operator edit. No agent rewrite.\n\n"
    "## DIRECTION UPDATE (2026-10-13, operator chat; supersedes the ARCHITECTURE DOCTRINE, PRINCIPLES and \"Cores and layers\" / "
    "\"Provenance\" below where they conflict)\n\n"
    "### OPERATOR STATEMENT (verbatim, 2026-10-13)\n" + QUOTE + "\n"
    "Also: \"Orderflow is real and works on all markets.\" and, on \"Tom is core, non-negotiable\": \"It was a long time ago when we "
    "started - now it makes no sense to have anything like this.\"\n\n"
    "### INTERPRETATION (not verbatim)\n"
    "1. No fixed core. Tom, Fabio and every other system are layers. Layers may be combined or used as filters on each other; evidence\n"
    "   (fee-net, out of sample) decides what trades.\n"
    "2. Our own judgement is allowed. A number is SOURCED (trader's words, file:line) or OURS (our judgement or tuned). OURS numbers are\n"
    "   chosen on DEV, checked once on VALIDATION, and the holdout is read once; every variant is counted. That replaces the NO-SOURCE ban.\n"
    "3. Market: BTC. Tom's core idea (order flow + volume profile) is applied on BTC charts and BTC data, which carry the order flow the DAX\n"
    "   CFD feed lacked. The DAX chain is parked and no FDAX data is bought (q11). Plan: research/tom_btc_2026-10-13/TOM_ON_BTC.md.\n"
    "4. Unchanged: testnet only until the GO-LIVE BAR holds; live-tree and safety rules in CLAUDE.md.\n\n")
sub("MyTradingSys/PROJECT_VISION.md",
    "1. TOM IS CORE. Tom's rules are the core layer. Non-negotiable.",
    "1. [SUPERSEDED 2026-10-13: no fixed core, see DIRECTION UPDATE 2026-10-13] TOM IS CORE. Tom's rules are the core layer. Non-negotiable.")
sub("MyTradingSys/PROJECT_VISION.md",
    "- Tom is core. Everything else is a module. Modules never gate core behavior.",
    "- [SUPERSEDED 2026-10-13] Tom is core. Everything else is a module. Modules never gate core behavior.")

# 3. LESSONS_DIGEST rule lines (boot read)
sub("MyTradingSys/system/LESSONS_DIGEST.md",
    "- Parameters come only from the trader's own words (Provenance); unsourced = NO-SOURCE, flagged, never tuned. [E]",
    "- Every parameter is labelled SOURCED (trader's words, file:line) or OURS; OURS is chosen on DEV, checked once on VALIDATION, "
    "holdout read once (operator 2026-10-13, replaces the NO-SOURCE ban). [E]")
sub("MyTradingSys/system/LESSONS_DIGEST.md",
    "- Non-Tom systems are separate layers (PROJECT_VISION), never filters on Tom; read \"INTEGRATIONS TRACKED\" first. [E]",
    "- No fixed core (operator 2026-10-13): layers may combine or filter each other; fee-net out-of-sample results decide what trades. [E]")

# 4. Generated LAYERS.md header, refinement rule, playbook
sub("scripts/dev/make_layers_md.py",
    "\"Rules: Tom is core; every other family is a separate layer, never a Tom filter (CLAUDE.md). A new backtest is a row in\",",
    "\"Rules: no fixed core; layers may combine or filter each other, results decide (CLAUDE.md, 2026-10-13). A new backtest is a row in\",")
sub("MyTradingSys/system/TASK_REFINEMENT.md",
    "- Provenance rule still applies: a card that sets a parameter cites the trader quote + file:line in `sources`, or it is NO-SOURCE.",
    "- Numbers rule (2026-10-13): a card that sets a parameter labels it SOURCED (quote + file:line in `sources`) or OURS "
    "(chosen on DEV, checked once on VALIDATION).")
sub("MyTradingSys/methodology/playbook.md",
    "Tom is core; other systems are separate layers, never Tom filters.",
    "No fixed core (operator 2026-10-13): layers may combine or filter each other; results decide.")

# 5. Chat-era hard rules that forbid our own price levels
sub("MyTradingSys/system/01_AI_BEHAVIOR.md",
    "- **NEVER suggest AI picks trading targets, entries, stop levels, or any price levels.**",
    "- [SUPERSEDED 2026-10-13, operator: our own judgement is allowed as OURS numbers checked out of sample; PROJECT_VISION "
    "DIRECTION UPDATE 2026-10-13] **NEVER suggest AI picks trading targets, entries, stop levels, or any price levels.**")
sub("MyTradingSys/system/COMPILED_DECISIONS.md",
    "## 8. HARD RULES (NON-NEGOTIABLE)\n",
    "## 8. HARD RULES (NON-NEGOTIABLE)\n\nH1, H6 and H7 are SUPERSEDED 2026-10-13 (operator): numbers may be OURS (our judgement or "
    "tuned on DEV, checked once out of sample); see PROJECT_VISION DIRECTION UPDATE 2026-10-13.\n")

texts = {}
for rel, old, new, count in EDITS:
    s = texts.get(rel) or (R / rel).read_text(encoding="utf-8")
    n = s.count(old)
    if n != count:
        sys.exit(f"STOP, nothing written: {rel}: expected {count} match(es), found {n}: {old[:70]!r}")
    texts[rel] = s.replace(old, new)
for rel, s in texts.items():
    print(("write " if APPLY else "would write ") + rel)
    if APPLY:
        (R / rel).write_text(s, encoding="utf-8", newline="\n")
if not APPLY:
    print("dry run: add --apply to write")
