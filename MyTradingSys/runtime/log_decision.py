"""log_decision.py - one-line decision logger.
Usage:
  python log_decision.py passed "reason text" [--verdict V] [--setup S] [--alert N]
  python log_decision.py acted "reason text"
  python log_decision.py note "reason text"
"""
import sys, json
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
sys.dont_write_bytecode = True
import session_state as ss

if len(sys.argv) < 3:
    print("usage: log_decision.py <action> <reason> [--verdict V] [--setup S] [--alert N]")
    sys.exit(1)

action = sys.argv[1]
reason = sys.argv[2]
evt = {"type": "decision", "action": action, "reason": reason}

i = 3
while i < len(sys.argv):
    if sys.argv[i] == "--verdict" and i+1 < len(sys.argv):
        evt["verdict"] = sys.argv[i+1]; i += 2
    elif sys.argv[i] == "--setup" and i+1 < len(sys.argv):
        evt["setup"] = sys.argv[i+1]; i += 2
    elif sys.argv[i] == "--alert" and i+1 < len(sys.argv):
        try: evt["alert_id"] = int(sys.argv[i+1])
        except: pass
        i += 2
    else:
        i += 1

ss.append_log(evt)
print(f"logged: {action} - {reason}")
