Tests +5: `MyTradingSys/research/sim_desk/artifact/test_banner_spec_gpt.py`; implementation unchanged.

`python -m pytest -q MyTradingSys/research/sim_desk/artifact/test_banner_spec_gpt.py` — 5 passed. Pytest emitted a cache warning because it could not create `.pytest_cache` (`WinError 183`); this did not affect the test run.

Hand-derived expectations: `[1.2, -0.3, 0.6]` sums to `1.5`, so mean is `+0.500 %/trade` over 3 trades. Thirty trades at `+0.4` have mean `+0.400 %/trade`. Tests cover fallback count and mean, never PASS on the percentage fallback, TOO FEW at 29, and `net_r is None`.
