import sys, json, os
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from math_object_builder import build_math_object


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        snap = json.load(f)
    mo = build_math_object(snap)
    tmp = sys.argv[2] + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(mo, f)
    os.replace(tmp, sys.argv[2])
    print("OK")


if __name__ == "__main__":
    # B071 fix (CORE_READINESS_PLAN.md task B1): any exception here must exit
    # non-zero and leave no output file, so the PowerShell caller's exit-code
    # check can tell "no signal" from "aligned" instead of silently defaulting.
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        try:
            if len(sys.argv) > 2 and os.path.exists(sys.argv[2] + ".tmp"):
                os.remove(sys.argv[2] + ".tmp")
        except Exception:
            pass
        sys.exit(1)
