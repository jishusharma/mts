# CBP scorecard spec tests

Card: `gpt-spec-tests-cbp-scorecard`.

`scripts/dev/cbp_scorecard.py:20-28` has one recount loop: default absent `rows` to an empty list, default missing analyst to `UNKNOWN`, increment rows once, count every trade in `trades or []`, and increment tradable rows once when `cbp.is_tradable` accepts the row. The source docstring at lines 6-8 requires analyst names to remain exact, including distinct `Michael` and `Michaal`. `MyTradingSys/cbp/__init__.py:101-108` defines tradable as a LONG or SHORT trade with nonblank, non-em-dash entry, target, and invalidation.

Hand-derived boundaries before running the implementation:

1. Missing `rows` -> empty result.
2. Empty `rows` -> empty result.
3. Missing analyst -> one `UNKNOWN` row with zero trades and zero tradable rows.
4. `Michael` and `Michaal` -> separate keys and counts.
5. `trades=None` and `trades=[]` -> zero trades.
6. Every listed trade counts even if malformed or not tradable; only LONG/SHORT with all three stated levels makes its row tradable; multiple qualifying trades still make one tradable row.

Added 13 tests in `scripts/dev/test_cbp_scorecard.py` and registered the path in `scripts/dev/extra_tests.tsv`.

Verification:

- `python -m pytest scripts/dev/test_cbp_scorecard.py -q --basetemp=F:/MTS/_pt_codex_cbp_scorecard_eco` -> 13 passed.
- Scratch mutations in `F:/MTS/_codex_cbp_scorecard_mutation_eco` each caused the suite to fail: folded analyst names, counted qualifying trades instead of qualifying rows, and accepted `SIDEWAYS` as a direction. All mutations were reverted in the scratch copy; no source mutation was made in the checkout.
- `scripts/dev/cbp_scorecard.py` and `MyTradingSys/cbp/__init__.py` remain unchanged.
