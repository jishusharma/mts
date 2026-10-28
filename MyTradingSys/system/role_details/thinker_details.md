# Thinker details (read when the operator says `scan <word>`; not injected by the hook)

## Improvement scan commands
| Word | Built from |
|---|---|
| `waste` | `python scripts/dev/worker_cost_report.py --days 7` (cost per worker/session), `python scripts/dev/traffic_report.py 72` (commit mix: claim/merge overhead vs work), `traffic.py measure --hours 72` (idle hours, duplicate work). Top 5 by cost, each against TRAFFIC_BUSTERS.md so a known buster is not re-proposed |
| `budget` | `traffic.py budget`, `get_usage`, the Model column of ROLES.md: where a cheaper model or a hand-over earns weekly % back; which login is idle while another throttles |
| `automation` | steps a session repeats by hand in the last 3 days of SUPER_SESSION.md / handover notes / `OPERATOR_DECISIONS.md` that a script or hook could do (never a scheduler); each priced in turns saved per week |
| `tests` | `python scripts/dev/run_all_tests.py --quick` timing and failures, areas on `ship` smoke gate without a fail-first test (`tasks.py list` cards of kind build touching `scripts/dev` or `MyTradingSys/execution` with no test path), flaky or slow tests (GATE_SPEED.md) |
| `scale` | what breaks at 2x: more logins/lanes (CLOUD_ACCOUNTS.md, traffic_inventory.json), more layers (LAYERS.md: every TF/family map), repo size and public-repo limits, ship-gate time at 2x commits |
| `speed` | ship gate and CI time (GATE_SPEED.md, `sync.py ship` phases), startup cost of a role session (boot reads, context size) |
| `ideas` | 3 innovation options from the open research questions in STATUS.md and PROJECT_VISION: each with the cheapest experiment, the number that would prove it, and the fee-net out-of-sample test that decides (CLAUDE.md Layers rule) |
| `cut` | what to delete or merge: dead scripts, duplicate docs, roles never started (trunk commit counts), cards stale > 14 days (`tasks.py stale`) |
