"""Single Python reader of the net_rr floor: MyTradingSys/system/net_rr_floor.json.

That file is the only place the number is written. PowerShell (start-trading-day.ps1) and Java
(NetRrFloor.java) read the same file; no code or config may carry a second copy of the value.

Fail closed: a missing, unparsable, non-numeric, non-finite or non-positive value raises
NetRrFloorError. There is no fallback literal (a fallback would be a second copy).
Call load_floor() on every decision, not once at import, so an edit to the file applies
to a running process on its next cycle without a restart.
"""
import json
import math
from pathlib import Path

FLOOR_PATH = Path(__file__).resolve().parents[1] / "system" / "net_rr_floor.json"


class NetRrFloorError(RuntimeError):
    pass


def load_floor(path=None) -> float:
    p = Path(path) if path is not None else FLOOR_PATH
    try:
        with open(p, encoding="utf-8-sig") as f:
            v = json.load(f)["net_rr_floor"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise NetRrFloorError("net_rr floor unreadable (%s): %s" % (p, e)) from e
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
        raise NetRrFloorError("net_rr floor invalid in %s: %r" % (p, v))
    return float(v)
