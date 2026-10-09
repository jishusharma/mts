# Pending patch - DSA_SESSION_PROMPT.md

Target: DSA_SESSION_PROMPT.md
Anchor: section 5 TASK LOOP, immediately before "1. RESTATE".
Status: blocked 2026-10-09. Target is UU (merge in progress).
Author: MTS-2026-10-09-DSA-COO

Splice this line immediately before step 1 of section 5:

0. GATE. If the task needs external evidence, run playbook PART I STEP 1 (method note) before any search. No method note, no search.

Context: on 2026-10-09 a research question was answered without the gate. The playbook trigger line was added the same day. This step 0 puts the gate in the path of every non-trivial task.
# Second pending change - DSA_SESSION_PROMPT.md section 9a

Anchor: section 9a AIBRIDGE, after the closing example block.

Add this line:

Block format: inside a fenced block, no source line may begin with a hash. Build a hash from [char]35 in PowerShell. Long single-line commands get wrapped and fail as CommandNotFoundException; keep source lines under about 200 chars. When the block contains a here-string or a comment that starts a line, the reader splits it into phantom blocks and only the first runs.

Context: on 2026-10-09 two write attempts were split into 17 and 12 phantom blocks. Diagnosis and the same rule are recorded in MyTradingSys/system/AIBRIDGE_LANE.md Open items.