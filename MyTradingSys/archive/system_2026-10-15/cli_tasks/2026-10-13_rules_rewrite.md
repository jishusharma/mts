# CLI task: apply the 2026-10-13 rule rewrite (no fixed core; SOURCED/OURS numbers)

Operator ask, chat 2026-10-13 (verbatim in system/OPERATOR_DECISIONS.md q14): remove "Tom is core" and the hard layer rules; let
our own judgement set numbers. Decision record: q14 answered, q11 answered.

Why forced: the cloud session that staged this was blocked by its permission check from editing agent instruction files
(CLAUDE.md, LESSONS_DIGEST.md, 01_AI_BEHAVIOR.md, ...). The exact edits are in `scripts/dev/staged/apply_rules_2026_10_13.py`
(10 exact-text substitutions in 8 files). The dry run on 7d92ee47 matched all of them. Safety rules are not touched: testnet
only, live tree, keys, deploy path, AUTO_PAUSE.

Run in a worktree (not the live tree), after Jis says OK:

```powershell
python scripts/dev/staged/apply_rules_2026_10_13.py
python scripts/dev/staged/apply_rules_2026_10_13.py --apply
python scripts/dev/make_layers_md.py
python scripts/dev/run_all_tests.py --quick
python scripts/dev/sync.py ship
```

Expected result: the dry run lists 8 files. After `--apply`:
- CLAUDE.md "Hard rules" carries the Layers and Numbers lines.
- PROJECT_VISION.md starts with "DIRECTION UPDATE (2026-10-13 ...)".
- LAYERS.md line 5 reads "Rules: no fixed core ...".
- The gate is green.

Then delete `scripts/dev/staged/apply_rules_2026_10_13.py` in the same commit (it has done its job). Set q14 `Applied:` in
OPERATOR_DECISIONS.md to the commit.

If a substitution does not match, the script stops and writes nothing. Someone edited that text first: apply the same meaning by
hand, and keep the operator quote word for word.
