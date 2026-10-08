"""Check 7: Dumps/SESSION_PASTE.txt over 400 KB (400*1024 bytes). Digest check: WARN.

Operator 2026-10-08: a 100-250 KB paste is normal and must work; the limit only catches a runaway paste.

Hash = check + 400 KB size band, so it re-fires only when the band changes (SCHEDULER_PLAN s4).
"""
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import REPO, emit, run

LIMIT = 400 * 1024


def main():
    p = REPO / "Dumps" / "SESSION_PASTE.txt"
    if not p.exists():
        return emit("paste_size", "OK", "SESSION_PASTE.txt absent", ["absent"])
    size = p.stat().st_size
    if size > LIMIT:
        band = size // LIMIT
        return emit("paste_size", "WARN", f"SESSION_PASTE.txt {size} bytes > {LIMIT}", [f"band{band}"])
    return emit("paste_size", "OK", f"SESSION_PASTE.txt {size} bytes", ["ok"])


if __name__ == "__main__":
    run(main)
