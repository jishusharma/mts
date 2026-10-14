# B173 - Terminal window flashes on screen and steals focus

Status: OPEN (filed 2026-10-10). Severity HIGH.
Source: BUGS.md row B173; Control Room inbox rf1cr2yyvvbyny39zqei, 9nzi6mqzbkudp0c3lbmo.

## Verbatim ask

A terminal window flashes on screen (most likely Python, a scheduled job) and steals focus while typing. Try to fix it.

## State

Same class as B169 (MTS-Backup console hidden): find the Windows scheduled tasks and App jobs that start python.exe/cmd with a visible console (register_*.ps1, run_worker.py, tick.py) and switch them to pythonw or CREATE_NO_WINDOW; a builder may edit the register scripts, a registration change on the host is a desk task.

## Updates

- 2026-10-12: item file created by session MTS-2026-10-12-1403Z-DSA-COO to satisfy the Build-Check rule that every OPEN row has a matching items/ file. State copied from the BUGS.md row.
