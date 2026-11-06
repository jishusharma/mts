# GPT spec tests: candle_flip flip_model.py (card gpt-spec-tests-candle-flip-model-1106)

Producer: Claude Sonnet 5.5 worker. T0 only: no REVIEWED stamp.

- New: `MyTradingSys/research/candle_flip_probability_2026-11/test_flip_model_spec.py`, 6 spec tests from the docstrings (`p_keep` flip_model.py:32-35, `P_close_colour` :38-56, `cluster_mean_z` :59-76, `load_family` :85-92, `fit_baseline` :101-113). Expected numbers are hand-computed (normal table, a hand-worked cluster example), not read from the code. The module is loaded from env `FLIP_MODEL_PATH` when set, so a mutated copy can be tested; the source file is untouched.
- Trunk: `python -m pytest MyTradingSys/research/candle_flip_probability_2026-11/test_flip_model_spec.py -q` -> 6 passed (OURS, run 2026-11-06).
- Mutation (copy in %TEMP%, not committed): flip_model.py:35 `/ np.sqrt(np.asarray(t_left, float))` -> `/ np.asarray(t_left, float)` (sqrt(t) dropped). Same command with `FLIP_MODEL_PATH` set to the copy -> 1 failed, 5 passed: `test_p_keep_contract` fails (`p_keep(0.5, 0.25)` got 0.977250, expected 0.841345). Reverted by deleting the copy.
- Note: only one test catches this mutation, because the other tests use t = 1 where sqrt(t) = t. The older `test_null_model.py` also uses t = 0.25 in `test_known_values_from_the_normal_table`.
