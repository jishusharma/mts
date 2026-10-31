SOUND

## Checked

- `scripts/dev/analyst_levels.py:10,85-95` — documented and implemented as-of cutoff and hit test.
- `scripts/dev/test_analyst_levels.py:53-61` — existing regression test independently confirms publish-day exclusion and next-day hit.
- Fixture: `MyTradingSys/research/layer_lab/analyst_levels_asof_fixture.json` (three BTC rows published 2026-10-28; bars are UTC epoch seconds). One 2026-10-28 bar touches 75,000. One 2026-10-29 bar closes at 76,000; its range is 76,000–76,100. No eligible bar touches 77,000.
- Execution: `python -c <inline harness>` imported `analyst_levels`, supplied the fixture bars via `spot_1h`, and called `main(['--store','MyTradingSys/research/layer_lab/analyst_levels_asof_fixture.json','--days','365','--json'])`. Output contained three ladder levels and `price: 76000`; no network data was used.

## Independent expected rows and comparison

Hand derivation from the docstring: the bar-open timestamp must be at or after 2026-10-29 00:00 UTC. Therefore the 75,000 touch on publish day is excluded; the 76,000 touch at the close of the eligible 2026-10-29 bar is included; and 77,000 has no touch in the fixture.

| Level | Published | Fixture touch | Expected hit | Script hit | Result |
|---:|---|---|---|---|---|
| 77,000 | 2026-10-28 | None | open / false | false | SAME |
| 76,000 | 2026-10-28 | 2026-10-29 bar close = 76,000 | hit / true | true | SAME |
| 75,000 | 2026-10-28 | 2026-10-28 only (before cutoff) | open / false | false | SAME |

## Rule and findings

`hit_from()` sets the first eligible instant to midnight UTC on the day after the date-only publication (`scripts/dev/analyst_levels.py:85-87`). `mark()` retains bars whose open timestamp is `>=` that instant and marks a level hit when it lies inclusively between the minimum eligible low and maximum eligible high (`scripts/dev/analyst_levels.py:90-95`). Because bars are selected by open time and hit is determined by the full OHLC range, any eligible bar whose range touches the level counts, including a close exactly at the level. The planted publish-day touch does not count.

| Severity | Location | Claim | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/analyst_levels.py:85-95` | MATCH | All three fixture rows match the independently derived as-of rule. | None. |

Follow-up cards: none.

Noticed: none.
