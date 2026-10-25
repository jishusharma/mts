# OPERATOR DIRECTIVE - 2026-10-03 - HISTORICAL TESTING + EXPERIMENT VALUES

Recorded verbatim at operator instruction, session MTS-2026-10-03-0328Z-DSA-COO.

## Operator statement (verbatim, first)

"does it make sense to test this on historical data? And in the mean while - experiment with meaningful numbers on Jishu's request/words?"

## Operator statement (verbatim, second)

"See - I need things to be meaningful - So what is needed must be done - that is it!"

## Operator statement (verbatim, third)

"Ok - So record verbatim. And now - i need plan to strt the work end to end. I need all pending tasks to be in the continuos build and test workflow."

## Interpretation (not verbatim)

1. Historical testing on module-layer parameters is authorized. The rule that forbids inventing a value does not forbid measuring one. R4 is a non-engine layer under layers/fabio/; DSA section 10 exempts non-engine layers from three-snapshot proof.
2. Operator-supplied values for experimentation are authorized under the label OPERATOR-EXPERIMENT. Sourced to the operator, not fabricated.
3. All pending tasks move into one continuous build-and-test workflow: T0 questions, T1-T5 contract, gate on tests + Build-Check, commit, next task.
4. Nothing touches the live path until its task gate passes.
# END
