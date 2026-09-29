# SUPERVISOR INBOX - notes for the Opus supervisor session

The supervisor reads this file on every wake (every 3 h at :17) and after acting moves each handled note to
SUPERVISOR_LOG.md as "- inbox <date>: <note> -> <action>". Append notes below the line, one per bullet:
`- 2026-09-29 22:30 IST | from: operator/DSA | <note>`
Direct routes that act immediately: paste into the supervisor session, or (from another Claude session on this machine) SendMessage.

---
- 2026-09-29 23:10 IST | from: supervisor | NUC worker c2e908f (num_thread 4) deployed to NUC-QUEUE/deploy: confirm the status WORKER hash changes to 778a6ee4da7e after the running task ends; if not after 2 wakes, check nuc-launcher logs via the ssh gate.
