"""Det-only reply-shape guardrail: run the operator reply-shape checks WITHOUT a model.

  python scripts/dev/reply_shape_check.py [REPLY_FILE] [--scenario h-reply-shape]

Applies the `det` checks of an eval scenario (default h-reply-shape: max_lines:8 +
bold_first_line) to one operator-facing reply and exits 1 when any check fails. No model
call, so it is cheap and safe to wire into the ship gate. The reply is read from REPLY_FILE,
or stdin when no file is given. `check()` is the importable core (the test drives it directly).

DECISION (OURS): a separate det-only check + registered test instead of a CI/ship-gate step:
the least invasive running guardrail. behavior_eval.py's model runs are NOT part of the gate
(they call the model), so we extract just the deterministic checks here and prove them with a
tracked test, leaving the gate/CI untouched.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import behavior_eval as be  # noqa: E402

DEFAULT_SCENARIO = "h-reply-shape"


def det_checks(scenario_id=DEFAULT_SCENARIO, eval_dir=be.EVAL_DIR):
    """The `det` check list of one scenario (its deterministic guards)."""
    scen, errs = be.load_scenarios(eval_dir, scenario_id)
    if scen:
        return scen[0].get("det", [])
    raise SystemExit(f"no scenario {scenario_id}: {errs}")


def check(reply, checks=None):
    """Return the list of failing det checks for one reply text ([] when the reply is shaped right)."""
    if checks is None:
        checks = det_checks()
    ok, failed = be.grade_det(checks, reply)
    return failed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("reply_file", nargs="?", help="file with the reply to check (default: stdin)")
    ap.add_argument("--scenario", default=DEFAULT_SCENARIO, help=f"eval scenario whose det checks to run (default {DEFAULT_SCENARIO})")
    a = ap.parse_args(argv)
    reply = Path(a.reply_file).read_text(encoding="utf-8") if a.reply_file else sys.stdin.read()
    checks = det_checks(a.scenario)
    failed = check(reply, checks)
    for c in failed:
        print(f"VIOLATION {c}")
    if failed:
        print(f"reply-shape: {len(failed)} check(s) failed of {checks}")
        return 1
    print(f"reply-shape: ok ({len(checks)} det check(s) passed: {', '.join(checks)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
