"""Append one JSON line to Dumps/operator/events.jsonl: {ts, source, kind, text}.
Usage: python scripts/operator/emit_event.py <source> <kind> "<text>"
Future use: auto-trader / NUC watcher can call this (subprocess or import emit()) on halt, flatten, etc.
Not wired into trading code."""
import json, sys, datetime, pathlib


def emit(source, kind, text, root=None):
    root = pathlib.Path(root) if root else pathlib.Path(__file__).resolve().parents[2] / "Dumps" / "operator"
    root.mkdir(parents=True, exist_ok=True)
    rec = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "source": source, "kind": kind, "text": text}
    with open(root / "events.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("usage: emit_event.py <source> <kind> <text>")
    emit(sys.argv[1], sys.argv[2], " ".join(sys.argv[3:]))
