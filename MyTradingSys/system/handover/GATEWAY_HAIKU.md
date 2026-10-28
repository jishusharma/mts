# Gateway watch: the Haiku worker list (operator 2026-10-28)

Who: one Haiku session on any station with the NUC gate key (`~/.ssh/nuc_gate`). It only watches and starts; the Opus
runs themselves bill the API gateway on JIS-NUC (`scripts/dev/gateway_run.py`). Never read keys, `.secrets`, `.env`,
`~/.mts_gateway` or env values. Never edit code. Never ask the operator; anything off goes in the reply.

Start line: `Run MyTradingSys/system/handover/GATEWAY_HAIKU.md`

1. Start ONE background shell (Bash, run_in_background) with exactly this, then wait for its notice:

       for i in $(seq 1 96); do out=$(timeout 300 ssh -i ~/.ssh/nuc_gate -o BatchMode=yes -o ConnectTimeout=20 e-ngineers@192.168.29.110 ps 2>/dev/null <<'EOF'
       Set-Location 'C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\.claude\worktrees\gw-probe'; git fetch -q origin fast-track; git merge -q --ff-only origin/fast-track; python scripts/dev/gateway_run.py tick
       EOF
       ); echo "$(date -u +%H:%MZ) ${out:-NUC unreachable}"; if echo "$out" | grep -q "opus-o1-self-heal-loop: done exit=0 OK" && ! echo "$out" | grep -q "opus-o3"; then echo START_O3; break; fi; if [ -n "$out" ] && ! echo "$out" | grep -q -E ": (running|resume|kill-resume|idle|quota-wait)"; then echo ALL_DONE; break; fi; sleep 300; done

   `tick` does the recovery itself: a run whose task stopped without finishing (NUC restart) or whose output has been
   silent 45 min (hung) is compacted, then resumed on the same session, at most 2 times. "NUC unreachable" lines are
   normal during a restart: keep waiting. `quota-wait` = the gateway's own 5-hour quota is spent; tick resumes the run after the reset, one run at a time.
2. Notice says START_O3: run this once, then go back to step 1:

       ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 ps <<'EOF'
       Set-Location 'C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\.claude\worktrees\gw-probe'; python scripts/dev/gateway_run.py start --card opus-o3-overhead-cut --run O3
       EOF

3. Notice says ALL_DONE: for each run line:
   - `done exit=0 OK`: `git fetch -q origin fast-track`; `git rev-list --count --grep=<card> origin/fast-track` must be >= 1;
     then run the test files named in `MyTradingSys/system/tasks/<card>.json` field `tests` with `python -m pytest -q`
     on a fresh `sync.py start gw-check` tree. Both true = OK.
   - anything else (`FAIL`, `gave-up`, non-zero exit): mark FAIL with the last 200 characters of its line.
     Do not relaunch.
4. Remove the worktree of every OK run:

       ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 ps <<'EOF'
       git -C 'C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed' worktree remove '.claude/worktrees/gw-<card>'
       EOF

5. Reply (and SendMessage the session that started you): one bold line, then a table run | on trunk | tests | resumes | note.
   `mark_completed` your session.
