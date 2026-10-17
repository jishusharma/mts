# SELECTION_RULES (closed with the key; readers must not open it)

Seed 20261017, per unit `<seed>-<code>` (python `random.Random(f"{seed}-{code}")`). Per unit: 10 ENRICHED + 10 RANDOM windows, each set minimum-spaced (48 / 24 / 15 bars), then all 20 shuffled and numbered `<unit>-NN`.

Edge pool: closed bars with at least `shown` bars before them, first allowed edge 2022-03-01 (1h), 2022-04-01 (4h), 2022-07-01 (1d), and bar close at or before 2024-07-01.

ENRICHED = pre-filter true at the edge bar t. Pre-filter (OURS, written before any mark, causal): the contract's primary detector family (`trendline_core.TrendlineDetector`, k=3, wick, log, max_age 500; contract v1) has a line that is (a) already eligible (arm A or B) with the eligibility event known before the contact, (b) not broken and not retired by t, and (c) a new contact episode ("touched" event) began on bars t-3..t. Computed from the append-only event list with `known_at <= t`; test_prefilter_is_causal checks that cutting or poisoning data after t leaves the flag unchanged.
RANDOM = uniform seeded draw from the whole edge pool, spaced from the enriched windows; its `prefilter_tag` records whether the pre-filter happened to be true there.

Counts (pool / pre-filter positives): 1h 20472 / 1150, 4h 4932 / 273, 1d 731 / 48 (`python g3_pack.py counts`).
Use in G3_REPORT: YES rate per half shows whether the pre-filter finds what readers call obvious (enriched vs random), kappa shows reproducibility.
