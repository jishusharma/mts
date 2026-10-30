# Spec tests: scripts/dev/aibridge_version.py

13 tests in scripts/dev/test_aibridge_version.py, temp dirs only, source unchanged. Expected values derived from the module docstring; golden fingerprint hand-computed (sha256 of `rel\0len\0data`).

Boundary cases: at limit (consistent = no problems), one off (single version string), above (extra bridge file), empty payload (sha256 of nothing), malformed (bad JSON, missing pattern), error path (no recorded fingerprint, missing file, duplicate --record).

Scratch mutations (on a copy, 3/3 caught): CRLF not normalised (1 fail), fingerprint mismatch ignored (2 fail), duplicate record allowed (1 fail).
