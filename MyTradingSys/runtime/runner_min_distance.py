"""Single Python reader of the runner minimum distance: MyTradingSys/system/runner_min_distance.json.

Key runner_min_distance_pct = percent of the target price (NO-SOURCE; value and reasoning are in the session record that
set it). src/main/java/datafeed/RunnerMinDistance.java reads the same file; no code may carry a second copy of the value.

Fail closed: a missing, unparsable, non-numeric, non-finite or negative value raises RunnerMinDistanceError and the
caller picks no runner (single-target plan). 0 is valid (any strictly farther node qualifies). No fallback literal.
Call load_runner_min_distance_pct() on every decision so an edit applies on the next cycle without a restart.
"""
import json
import math
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "system" / "runner_min_distance.json"


class RunnerMinDistanceError(RuntimeError):
    pass


def load_runner_min_distance_pct(path=None) -> float:
    p = Path(path) if path is not None else PATH
    try:
        with open(p, encoding="utf-8-sig") as f:
            v = json.load(f)["runner_min_distance_pct"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise RunnerMinDistanceError("runner min distance unreadable (%s): %s" % (p, e)) from e
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
        raise RunnerMinDistanceError("runner min distance invalid in %s: %r" % (p, v))
    return float(v)
