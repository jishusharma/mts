# lab-crossvendor-stage

**DONE — cross-vendor recipe stages carry vendor/model identity; `test_lab_flow.py`: 24 passed.**

## Work and evidence

- `scripts/dev/lab_flow.py:13-18` adds a vendor field to every recipe stage; `build-review` now routes its second lens to Gemini 2.5 Pro.
- `scripts/dev/lab_flow.py:111-120` gates stage metadata against the recipe and rejects any reviewer model matching the producer model.
- `scripts/dev/lab_flow.py:188` adds the Gemini headless instruction: use `agy.exe --print` and inline the complete report text.
- `scripts/dev/lab_flow.py:242-244` stores vendor and model id in the finish receipt. `accepted()` checks those values against the recipe (`scripts/dev/lab_flow.py:75-83`).
- `scripts/dev/test_lab_flow.py:47-81` covers a different-vendor Gemini stage, same-model refusal, inline report instruction, and model id in the receipt.
- `MyTradingSys/system/LAB_RECIPES.md:10,19-24,58-60` documents vendor routing, Gemini prompt handling, model distinctness, and receipt identity.

## Verification

Fail-first run against the old implementation, after setting a workspace-local pytest temp directory:

```text
python -m pytest scripts/dev/test_lab_flow.py -q --basetemp F:/MTS/mts-codex-lab/.pytest-tmp-lab-crossvendor
2 failed, 22 passed
ValueError: too many values to unpack (expected 5, got 6)
```

Final run:

```text
python -m pytest scripts/dev/test_lab_flow.py -q --basetemp F:/MTS/mts-codex-lab/.pytest-tmp-lab-crossvendor-5 -p no:cacheprovider
24 passed in 0.38s
```

`pytest`'s default temp root was inaccessible in this environment; both recorded runs use the workspace-local `--basetemp` workaround. No market data was needed or read.

## Scope note

The task scope names `lab_flow.py`, its test, and `LAB_RECIPES.md`; the separate `codex_run.py` executable dispatcher was not in scope. Generated Gemini stage cards carry the vendor/model and `agy.exe --print` instruction. The dispatcher itself remains Codex-only in the current tree (`scripts/dev/codex_run.py:1`); actual automatic vendor dispatch requires a separately scoped runner change.

Follow-up cards created: none.
