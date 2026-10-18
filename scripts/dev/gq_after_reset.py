"""Wait for the Gemini quota reset, then run the queued Flash jobs (operator 2026-10-18). Usage: python scripts/dev/gq_after_reset.py <wait_seconds> <card:effort> ..."""
import subprocess
import sys
import time

wait = int(sys.argv[1])
time.sleep(wait)
subprocess.run([sys.executable, "scripts/dev/gemini_queue.py", "run", *sys.argv[2:]])
