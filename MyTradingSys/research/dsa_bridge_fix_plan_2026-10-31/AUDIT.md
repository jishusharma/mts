# DSA bridge fixes 0.7.4-0.7.6: independent audit (card dsabr-c8), 2026-10-31

Auditor: Builder (Opus), JIS-NUC, read-only on product code. Tree: fast-track @a152eaf3c, bridge 0.7.6.
Baseline for "fails on 0.7.3": `git archive 12b43fe17 scripts/aibridge` (the 0.7.3 commit; FIX_PLAN names 6ca00caa1, same
bridge bytes) into a scratch dir. Fix commits: 6b2e089fc (extension + prompt, 0.7.4), 92024c7da (runner + D5, merged as 0.7.5
in 0b081d042), f9d724567 (test flake), ff2135661 (e2e script), 4e4e70240 (0.7.6 bump), da76b6df9 (c7 run).

## Verdicts per card

| card | verdict | one line |
|---|---|---|
| dsabr-c1-block-select | FIX (minor) | core selection, keys, per-reply duplicate guard and cap 200 are right and tested; the "why nothing ran" status is computed and thrown away, fail-closed covers only an empty ancestor chain, fixture is hand-built |
| dsabr-c2-dropped-gen | FIX | notice/stop works in the fake page; a stale watch survives an operator untick and fires a notice right after re-arm; a short final answer (<40 chars) counts as "no answer" and the notice asks DSA to re-send (re-run) blocks |
| dsabr-c3-task-exit | PASS | native exit propagates, EXIT_CODE line fails, gate needs ALL TESTS PASSED, cmd+cwd logged; all new cases fail on 0.7.3 and pass now |
| dsabr-c4-gate-tmp | FIX | test_wiring_scan repro fails on the 0.7.3 body and passes now; the test_mts_signal repro PASSES on the full 0.7.3 code (not failing-first); V07_CONTRACT still states the old child TEMP |
| dsabr-c5-dsa-prompt | PASS | every section 2 sentence present and asserted; two lines go stale with the E5 fix below (follow-up, not a defect today) |
| dsabr-c6-e2e-script | PASS | re-run here against the real 0.7.3 payload: E1-E4 FAIL, rc 1; trunk PASS |
| dsabr-c7-install-e2e | FIX | JIS-NUC verified; jis-nb got only the install command (no verify, no e2e), so done_when "both hosts" is unmet; no real gate run through the bridge (item 7) |

## Checklist (FIX_PLAN section 5)

1. **Failing-first on 0.7.3** (re-run by the auditor, scratch copy of 12b43fe17):
   - c1 `node tests/block_select.test.js` on 0.7.3 loop.js: exit 1 (selectBlocks missing); trunk 7/7. PASS.
   - c2 `node tests/handsfree.test.js` on 0.7.3: `TypeError: W is not a function` at the replyWatch block; trunk 19/19; loop 18/18. PASS.
   - c3 `MTS_REPO_ROOT=<0.7.3> pytest test_aibridge_task_gate_exit.py`: 4 failed (native exit then Write-Output, EXIT_CODE line,
     gate playbook expect, child TEMP in repo), 3 guards passed; trunk 7/7. PASS.
   - c4 test_wiring_scan `TempInsideGitRepo` with line 205 put back to `ImportCache(tempfile.gettempdir())`: FAILED; trunk OK. PASS.
     test_mts_signal `TempInsideGitRepo` against 0.7.3 `mts_signal.py` + 0.7.3 `test_mts_signal.py` (repro class added): **OK**,
     i.e. it does not fail on the pre-change code. FIX: the D5 test_mts_signal failure (082122) is not reproduced; the ensure()
     identity change (mts_signal.py:228-229) and the stdout-in-error change (:186) are untested guesses.
   - c5 0.7.3 DSA_SESSION_PROMPT.md holds 0 of the new sentences; `test_prompt_carries_the_bridge_0_7_4_rules` would fail. PASS.
   - c6 `e2e_bridge.py --payload <0.7.3>`: E0 PASS, E1/E2/E4 FAIL (node: no selectBlocks/replyWatch), E3 FAIL (exit=0), rc 1. PASS.
     Note: E1/E2/E4 fail by a thrown "pre-0.7.4 extension" error (e2e_bridge.py:35), not by an assertion; acceptable (fails closed).
2. **Thinking excluded by structure; fail closed.** loop.js:217-227 `isThinking` looks at tag/class/role of the ancestor chain
   (content.js:137-145 `chainOf`), never the block text. PASS for structure. Gaps (FIX c1):
   - Fail closed only when the chain is empty (loop.js:219). A thinking panel whose class names do not match
     `/think|thought|reason|cot[-_ ]|chain[-_ ]?of/` and whose header is not "Thought for/Thinking/DeepThink" runs drafts again.
     The DeepSeek selector comes from a HAND-BUILT fixture (tests/fixtures/deepseek_reply.html:1), not a saved live DOM.
   - The opposite failure is silent: `lead` (content.js:140, loop.js:224) is checked on EVERY ancestor up to body, so a chat
     container whose text starts with "Thinking..." (e.g. the operator's first message) or a page root with "reason" in a class
     ignores every block. `sel.status` (loop.js:232) is discarded and `lastIgnored` (content.js:33, 169) is written but never
     read, so the panel never says why nothing ran. The card required "status says why".
   - Fix: when `selected` is empty and `ignored` is not, `setStatus(sel.status)`; stop the `lead` test at the first ancestor
     whose class/tag marks a message (or after 4 levels); capture the real DOM with the E5 live run and replace the fixture.
   - Perf (same card): `chainOf` reads `cur.textContent` of every ancestor up to body (whole-page text) per block, and
     `blockKey` (content.js:173-179) calls `allBlocks()` per block; runBatch:459/465, replyTick:544, watchdog:576 and dbgDump:187
     make it O(blocks^2 x depth x page text) per second. Fine at 6 blocks; risk on a 200-block chat. Fix: compute keys once per
     scan (`batchKeys` over one `allBlocks()` result) and cap `lead` to the element's first text node.
3. **Duplicate guard is per batch only.** loop.js:240-243 `dupOf` runs over the items of one runBatch (content.js:467, 474);
   keys are per occurrence among selected blocks (loop.js:235-238, content.js:176), so the same command in the NEXT reply is
   occurrence +1, a fresh key, and runs. Test: block_select.test.js "a later reply gets a fresh one". PASS.
4. **Mark-first and Stop.** content.js:465 marks every item in `ranKeys` before the loop at :470; NOT_RUN duplicates/overflow are
   marked too. Stop: `stopAuto` (content.js:424-425) bumps `token`; runBatch returns at :484 after the in-flight call. PASS.
5. **replyWatch.** One notice then stop: loop.js:256-259; reset on reply :253. Not during a run: content.js:547 `busy: inRun`
   (set :468, cleared :484/:488). Draft: postToChat keeps and restores an operator draft (content.js:395, 408-412, B196). FIX c2:
   - `stopAuto` (content.js:424-429) does not reset `watch`; only the stop at :560 nulls it. Untick within 45 s of a post, re-tick
     later: replyTick (:543-549) sees `since` long past and posts a notice at once. Fix: `watch = null` in stopAuto and on re-arm.
   - "answered" needs `answerLen() - postedAnsLen >= 40` (content.js:545). A short final answer ("Done, all PASS.") is a
     dropped generation; the notice text (loop.js:261) says "Re-send the blocks of that answer once", inviting a second run of
     write/ship blocks. Fix: any growth of non-thinking text after quiet counts as a reply (>= 1 visible char outside our UI, the
     posted bubble measured after it renders), and the notice says "if you already answered, reply ok; do not repeat blocks
     that already have a result".
   - `busy` is documented as "in-flight run or draft being typed" (loop.js:246) but content.js:547 passes only `inRun`. Fix:
     `busy: inRun || !!inputText(findInput() || {})` so no notice lands while the operator types.
   - Real DeepSeek DOM untested: `answerLen` (content.js:529-538) relies on the same class guess; if thinking text is not
     subtracted, thinking counts as an answer and the notice never fires. Verify in the E5 live run.
6. **run-task exit.** Control: `test_control_write_output_after_clean_native_passes` and `test_clean_step_still_passes` PASS.
   Footer only when a native command ran: run-task.ps1:72 sets `$global:LASTEXITCODE=$null` first and appends
   `if ($null -ne $global:LASTEXITCODE) { exit ... }`; no stale code. Same footer for plain blocks: agent.ps1:117. Task-level
   `; exit $LASTEXITCODE`: agent.ps1:355, unchanged. Default fail_on adds `EXIT_CODE=[1-9]` (run-task.ps1:92); cmd+cwd logged
   (:97); PYTHONUNBUFFERED in steps (:72). PASS. Note: plain blocks (agent.ps1:117) do not get PYTHONUNBUFFERED, so a timed-out
   python block can still lose its tail.
7. **Gate playbooks.** tasks/mts-gate.json:6 and mts-ship.json gate step carry `"expect": "ALL TESTS PASSED"`, which matches
   run_all_tests.py:1425. Crash without summary -> FAIL: test_aibridge_exploratory.py:104-122 PASS. A real `--quick` run through
   the bridge (PASS, then one injected failing test -> FAIL) was NOT done by c7 or anyone: NOT VERIFIED (FIX c7). Also: the gate
   step asks `timeout_s: 900` but a task without `timeout=` gets the agent's 600 s default (agent.ps1:336, 358), so the agent
   kills a long gate at 600 s; the prompt's `timeout=1200` (DSA_SESSION_PROMPT.md:38) is what saves it.
8. **Hermetic tests.** test_wiring_scan.py:206-209 uses its own TemporaryDirectory + GIT_CEILING_DIRECTORIES; repro class
   :224-240 with TEMP inside a repo and GIT_CONFIG_GLOBAL=devnull. test_mts_signal.py `sh()` passes `-c user.name/email`, setUp
   sets GIT_CEILING_DIRECTORIES. Both repro classes pass on trunk. No test writes into the %TEMP% root (mkdtemp subfolders only).
   PASS for behaviour; FIX for the non-failing mts_signal repro (item 1). Agent side: child TEMP leaves the repo
   (agent.ps1:132-139 -> %LOCALAPPDATA%\AIBridge\run-tmp); `test_child_temp_is_outside_a_git_repo_around_the_bridge_folder` PASS.
   docs/V07_CONTRACT.md:47 still says "Child TEMP/TMP = `<AIBridge>\run\tmp`": stale (FIX c4, doc).
9. **Version.** RELEASES.json current 0.7.6 = loop.js:4 = manifest.json:4 = agent.ps1:2. test_aibridge_version_bump.py 2/2 PASS.
   c7: aibridge_verify 0 FAIL of 29, every file row "identical to payload" (c7_nuc_results.md:38-70). PASS.
10. **Prompt.** test_dsa_direct_mode.py 17/17 PASS incl. `test_prompt_carries_the_bridge_0_7_4_rules`; docs/test_integrity size
    tests 6/6 PASS. Contract: no contradiction today, but V07_CONTRACT.md has none of the 0.7.4 rules (thinking ignored,
    duplicate NOT RUN, notice, cap 200) and :47 is stale (item 8). Stale-later lines: DSA_SESSION_PROMPT.md:26-28 and
    V07_CONTRACT.md:15-16 state the kind=read exemption that the E5 fix removes; :47 "it turns a failure into exit 0" is no
    longer true since the 0.7.5 footer (the rule itself is still good). Header :1 says v0.7.4 (bridge is 0.7.6; harmless).
11. **E2E both hosts.** JIS-NUC: E0-E4 PASS, E5 NOT_CHECKED (c7_nuc_results.md:77-84). jis-nb: none. The broadcast b-93631b
    carried only `aibridge_install.py F:/AIBridge --restart-agent` (c7_nuc_results.md:110), so no jis-nb verify/e2e JSON can
    arrive. FIX c7: broadcast `python scripts/dev/aibridge_verify.py F:/AIBridge && python scripts/aibridge/tests/e2e_bridge.py
    --target installed F:/AIBridge --json` and quote the ack. Extension reload + F5 on both hosts is still a manual step.
12. **Off-limits paths.** Name lists of all seven commits: no `.mts_live`, HALT, `policy.json`, `config.json`, `.secrets` or `.env`
    path. The agent restart happened only inside `aibridge_install.py --restart-agent` (c7_nuc_results.md:5-10). PASS.

## Known xfails (still xfail on trunk: exploratory run 31 passed, 2 xfailed)

### E5: a non-zero exit on kind=read does not stop the next block (test_aibridge_exploratory.py:174-185)
Cause: content.js:241 `if (b.exit !== 0 && b.kind !== 'read') return 'exit ' + b.exit;` exempts reads, as documented in
V07_CONTRACT.md:15-16 and DSA_SESSION_PROMPT.md:26-28. Since 0.7.5 plain blocks report the real native exit (agent.ps1:117),
so `git fetch` exit 128 followed by a dependent block now reaches this exemption more often.
Fix (DECISION (OURS): no allow-list, fail closed):
1. Move `failed()` into loop.js as pure `L.blockFailed(resp)`; any `exit !== 0` stops the rest of the reply, the receipt says
   `exit N (read)` for a read. content.js:237-243 calls it.
2. loop.test.js cases: `{exit:128, kind:'read'}` -> 'exit 128 (read)'; `{exit:0, kind:'read'}` -> null; refused/timeout unchanged.
3. Delete the xfail mark at test_aibridge_exploratory.py:175; the test then asserts runs == ['git fetch FAILME'].
4. V07_CONTRACT.md:15-16 and DSA_SESSION_PROMPT.md:26-28: "any non-zero exit skips the rest; a search that may find nothing
   (rg, findstr) ends with `; exit 0` when later blocks do not depend on it"; add the sentence to test_dsa_direct_mode.py.
5. Bump to 0.7.7 (RELEASES.json, manifest.json, loop.js:4, agent.ps1:2).

### E6: LOCK_EXPIRED at 240 s for a task without timeout= (test_aibridge_exploratory.py:188-200)
Cause: content.js:479 `L.expireMs(it.opts.timeout_s)`; with no `timeout=` loop.js:180-183 uses 120 s x 2 = 240 s, while the
agent runs a task for 600 s by default (agent.ps1:336, V07_CONTRACT.md:30) and the gate step asks 900 s (mts-gate.json:6). The
extension releases the lock, posts LOCK_EXPIRED, loses the real result and invites a duplicate gate run.
Fix:
1. loop.js `L.expireMs(timeoutS, isTask)`: default 600 s for a task, 120 s otherwise; result max(30, t) x 2 (task default 1200 s).
   content.js:479 passes `!!it.opts.task`.
2. loop.js `raceDeadline`: on expiry, when the ping says `running > 0`, extend once to the agent hard cap (task 1800 s, block
   300 s) + 60 s before releasing; release at once when `running === 0` (B210 behaviour kept for a truly lost reply).
3. loop.test.js: `expireMs(undefined, true) === 1200000`, `expireMs(undefined) === 240000`, `expireMs(1200, true) === 2400000`;
   handsfree/loop raceDeadline case "running 1 at expiry -> extended, result arrives -> no LOCK_EXPIRED".
4. Delete the xfail mark at test_aibridge_exploratory.py:189 (400 s delay < 1200 s: PASS).
5. Agent side (same card): agent.ps1:336 task default = min(hard, max(600, sum of step timeout_s + 60)) when the spec is known,
   so mts-gate without `timeout=` gets 960 s instead of being killed at 600 s.
6. Same 0.7.7 bump as E5 (one release, E5 + E6 + the c1/c2 FIX items).

## Follow-ups (Agent: not filed as cards, per the brief)
- c1: status when all blocks are ignored; bound the `lead` test; key once per scan; real DeepSeek DOM fixture.
- c2: reset `watch` in stopAuto; answered on any visible growth; draft = busy; notice wording "do not repeat".
- c4: make the test_mts_signal repro fail on 0.7.3 (capture the real 082122 stdout first) or delete it; fix V07_CONTRACT.md:47.
- c7: jis-nb verify + e2e by broadcast; one real `--quick` gate through the bridge (PASS, then an injected failure -> FAIL);
  E5 `--live` from a Chrome-capable session, which also yields the real DOM snapshot for c1/c2.
- E5 + E6 fixes above as AIBridge 0.7.7.
