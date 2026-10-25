"""PreToolUse/PostToolUse hook: remind to meter usage around Agent/Task/Workflow.

A hook cannot call MCP, so it only prints a reminder. Never raises, exit 0.
Usage: usage_reminder.py pre|post  (hook JSON on stdin)
"""
import json
import sys

TOOLS = {"Agent", "Task", "Workflow"}


def main(argv):
    try:
        mode = argv[1] if len(argv) > 1 else "pre"
        word = "after" if mode == "post" else "before"
        data = json.loads(sys.stdin.read() or "{}")
        if data.get("tool_name") in TOOLS:
            print(f"USAGE: call get_usage then usage_log.py {word} <card>")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
