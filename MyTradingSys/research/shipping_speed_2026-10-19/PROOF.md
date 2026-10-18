# Shipping verification — 19 October 2026

**Verdict: functional checks PASS; a 50% reduction against the preceding smoke gate is NOT demonstrated.**

Measured independently on JIS-NUC at Git HEAD `621f682891779cfdd1a3ec5912b72eb9fc99366d`. Exact source hashes, commands, interpreter and exit codes are in [receipt.json](receipt.json). Complete outputs are preserved beside this report.

| Check | Wall time | Result |
|---|---:|---|
| Gate impact, selection, runner and sync regression suites | 142.354 s | 187 tests, OK, exit 0 |
| Preceding smoke selection, `nowin.py` changed | 23.022 s | ALL TESTS PASSED, exit 0 |
| Fast selection, same changed path and checkout | 25.794 s | ALL TESTS PASSED, exit 0 |

The fast run was 12.04% slower in this pair. The 50% target for this baseline is at most 11.511 s. This is a single sequential pair, baseline first; it does not estimate a distribution or control other machine load. Both runs disable the pass-record option to prevent reuse of prior passing steps. The gate's own content-facts cache remains enabled in both. Neither run modifies `nowin.py`; this is a real execution of its selected gate, with a supplied changed-path list. It excludes fetch, merge, CI lookup and push time and therefore is not an end-to-end code-ship benchmark.

The fast plan reached 28 test files, retained 19 units, and deferred 13 units to CI. Its longest selected step was extra tests (`test_lab_flow.py`, `test_testnet_canary.py`, `test_sched_scripts.py`), 21.7 s. The preceding smoke plan ran six steps. This explains why an import graph and a time budget do not guarantee a lower wall time for this particular change: this fast plan executes more checks than its predecessor.

The regression suites exercise failed gates preventing pushes, live paths requiring the full gate, direct tests retained despite a budget, import-graph failure falling back, red CI blocking a code ship, separate fast slots, push-race overlap and same-tree record validity. They establish these tested behaviors, not the speed target or the success of all CI tests.

The earlier `GATE_SPEED.md` timings (469–636 s full gates; 23.8–51.3 s fast ships) remain historical observations from another host and different workloads. They cannot prove a 50% improvement in an equivalent workload on this host. The interrupted old gate from the preceding chat turn is not counted as a passing test or timing sample.

## Evidence

- [Regression output](regressions.txt)
- [Preceding smoke output](baseline_smoke.txt)
- [Fast smoke output](fast_smoke.txt)
- [Machine-readable receipt](receipt.json)
- [Reproduction script](measure.md)

No shipping implementation was changed in this verification. Further performance work is required before claiming the requested reduction against the preceding smoke gate. No lower test budget or extra quarantine was introduced to manufacture a faster result.
