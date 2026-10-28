# Qwen audit program (T056) - design, 2026-09-28 (supervisor)

Operator ask: regular Qwen auditing tasks - find gaps in MTS, anything that saves Claude cost, give Claude a
heads-up, research per MTS protocols - so Claude can plan ahead and schedule Qwen work.

## Principles
1. **T0 before T1.** Anything a script can find (dead file refs, stale `.new`, modules without tests,
   FORMULAS entries without code, items without STATE updates) is a T0 check, never a Qwen task.
2. **Qwen only for reading-and-judging** one small scope: <= ~4k tokens in, <= ~2k out (082 needed 55 min and
   was cut off at 6,144 out; 080/087/090 at 2-4k in finished in 4-9 min). One module or one doc section per task.
3. **Idle backfill only.** Audits are packed only when the queue has 0 waiting, so they never delay priority work.
4. **Every finding is mechanically checkable.** Reply format is fixed (below); a T0 digest keeps a finding only if
   its quoted line is found verbatim at `path:line` (+-3 lines). Unquoted or misquoted findings are dropped.
5. **Findings are leads, not facts.** Claude reads only the digest, spot-checks one finding per digest, and turns
   real ones into items/specs. Nothing Qwen says changes code or rules directly.
6. **No web research by Qwen.** The NUC has no browser and gate v3 (playbook Part I) requires every citation to be
   opened and matched; a local 30B model cannot do that. Qwen research = corpus research only (extracts,
   transcripts, condition files) with verbatim quotes + GPS, checked by `verify_extract_quotes.py`.

## Audit templates (one small scope each)
| ID | Audit | Scope packed | Finding looks like |
|---|---|---|---|
| A1 | Formula conformance | one module + its FORMULAS.md section | code line differs from canonical formula |
| A2 | Test gap | one module + its test file | branch/edge case with no test (empty input, NaN, boundary) |
| A3 | Spec pre-check | a Claude-written spec before packing | ambiguity, missing EXPECT, output won't fit OUTPUT_TOKENS |
| A4 | Corpus question | <= 3 extract/transcript files + one question | quote + GPS answering it, or "not in corpus" |
| A5 | Layer independence | one layer module | Tom logic used as a filter, or layer importing Tom internals |
| A6 | Doc-vs-code drift | one doc section + the code it describes | doc claim the code does not do |
| A7 | Safety invariants | one execution module (testnet-only, caps, kill switch) | path that could reach mainnet or skip a guard |

Reply format (all templates):
```
FINDING <n> | <A-id> | severity H/M/L | <path>:<line>
QUOTE: <exact line from that file>
WHY: <one sentence>
FIX: <one sentence>
```
or the single line `NO FINDINGS`.

## Pieces to build (Qwen implements, Sonnet writes tests from this doc)
- `scripts/worker/audit_rotation.py` (T0): registry `scripts/worker/audit_targets.json` (target, template,
  last_audited); `--backfill` packs the <= N least-recently-audited targets only when waiting == 0; `--t0` runs the
  script-only checks and writes `research/audits/T0_CHECKS.md`.
- `scripts/worker/audit_digest.py` (T0): reads verified audit replies, keeps findings whose QUOTE matches, dedupes
  against earlier digests, writes `research/audits/AUDIT_DIGEST.md` (newest first, <= 40 lines of open findings).
- Schedule (operator approval needed, desktop Task Scheduler, zero Claude tokens): every 3 h
  `python scripts/worker/audit_rotation.py --backfill` and `audit_digest.py` after it.

## Claude side
- Session start: read `research/audits/AUDIT_DIGEST.md` (<= 40 lines) after STATUS.md.
- Supervisor turns confirmed findings into items/specs; closes false ones in the digest (`closed: false-positive`).
