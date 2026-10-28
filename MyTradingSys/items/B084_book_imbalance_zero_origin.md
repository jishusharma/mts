# B084 - book_imbalance 0.0 origin in the Python proof block

Status: CLOSED 2026-10-06 (receipt in BUGS.md, MTS-2026-10-06-2122Z-APP-COO-registry-fix). Severity: MED. Opened 2026-10-03.

## Defect

math_object_builder.py reads book_imbalance from the Java candidate
proof block at L439: _book = _proof.get('book_imbalance', 1.0).
The archive snapshot path writes null (MarketDataSnapshot.java:1129
cond.putNull). The live snapshot path can write 0.0 (L214
bidDepth / askDepth when askDepth == 0; L212 catch keeps 0.0).
Where 0.0 enters the proof block on the backtest path is not
established. 13295c8 added _book != 0.0 at math_object_builder.py:454
without naming the source.

## Evidence

- math_object_builder.py L439, L445, L454, L455
- MarketDataSnapshot.java L1129 (archive: null)
- MarketDataSnapshot.java L214 (live: possible 0.0)
- SetupCandidatesBuilder.java L580 (Java counts only when it favours direction)
- 13295c8: WIP partial, unverified, 1 file, +3 -1

## Fix

Trace the value from source. One read of the proof-block emission
path in SetupCandidatesBuilder or the BT candidate builder settles
whether 0.0 is written or defaulted. Then either: default to 1.0
where the value is missing, or keep 0.0 treated as no-data on both
Python and Java sides symmetrically.

## Receipt

-

# END
