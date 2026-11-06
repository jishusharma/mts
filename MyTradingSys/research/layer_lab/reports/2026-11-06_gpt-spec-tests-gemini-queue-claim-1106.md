# gemini_queue own-host claim spec test (2026-11-06)

- Test: MyTradingSys/tests/test_gemini_queue_spec_1106.py, 6 spec tests from the claim_with_retry/claim_holder docstrings (scripts/dev/gemini_queue.py:69-76, 91-111). OURS: written from the contract, not the code body.
- Trunk: `python -m pytest MyTradingSys/tests/test_gemini_queue_spec_1106.py -q` -> 6 passed.
- Mutation: scripts/dev/gemini_queue.py:104 `== socket.gethostname().lower() else ('skip'` changed to `!=` (own host and other host swapped). Result: 2 failed, 4 passed (test_own_host_holder_is_ok, test_other_host_holder_skips_at_once). Reverted with `git checkout`; source unchanged.
- "Fails on old code first": the tests cover a fix already on trunk (f724f4eeb); the mutation stands in for the old behaviour.
