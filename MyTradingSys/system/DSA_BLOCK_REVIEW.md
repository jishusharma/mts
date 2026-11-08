# DSA bridge block review: every bridge bug and fix, DeepSeek rules, the DSA prompt, one ranked fix list

Card dsa-bridge-fix-review-opus-1108 (OPUS, Builder run on the Platform credit, 2026-11-08 UTC). Read-only review: no edit of
the bridge (F:\AIBridge, scripts\aibridge\) or of DSA_SESSION_PROMPT.md. Check: `python MyTradingSys/system/check_dsa_review.py`.

## 0. Summary in plain words

- What happened: DeepSeek suspended the account used by the AWGP Chrome profile "for violation of user policies" until
  2026-11-11 10:22 (operator screenshot 2026-11-08; time zone not shown). It is an account-level suspension, not a rate notice.
- The cause is UNPROVED. DeepSeek publishes no trigger and no numeric limit for the chat site; the operator has only the
  one-line suspension text. Every cause below is ranked by evidence, none is proved.
- What the bridge did the day before (JIS-NB `F:\AIBridge\src\audit.jsonl`, counts only, read 2026-11-08): 205 agent rows on
  2026-11-07 between 05:45Z and 18:47Z, 147 of them hands-free (auto), peak 45 rows in the 18Z hour (43 at 16Z, 41 at 17Z),
  median gap between auto runs 16 s, 43 gaps under 10 s, 99 under 30 s; results: 134 ok, 59 refused, 12 extension events.
  That is one host only; the block card says three machines drove the same account that day. Daily totals the week before:
  59 (11-02), 96 (11-03), 22 (11-04), 43 (11-06): 11-07 was 2 to 9 times a normal day.
- The bug history (section 1, 76 rows) shows one design fault that matters for the block: every fix since 2026-10-10 made
  the bridge send faster or longer (idle wait 4000 to 2000 ms, cap 25 to 50 to 200, 8 parallel chats, auto-start, a watcher
  that re-sends), and no fix ever added a brake on the account side. The pacing class has 7 rows and zero brakes.
- Recommendation: build the first three fixes (pacing guard, one machine per account, stop on warning) before the account
  is used again; move truly unattended work to the official DeepSeek API, which is the sanctioned channel for automation.

## 1. Bug table

Sources: MyTradingSys/system/tasks/*dsa*.json and *aibridge*.json (live and archive; the ten dsa-audit-* strategy-audit cards
and the rv-dsa-* revalidation cards are not bridge bugs and are left out), AIBridge release commits 0.7.0 to 0.7.32 (the
release notes; scripts/aibridge/RELEASES.json holds only file hashes), FIX_PLAN.md D1-D7, ROOT_CAUSES.md, the Argon review,
F:\AIBridge\HANDOFF.md and DECISIONS.md, AIBRIDGE_LANE.md, DSA_DELEGATION.md, and the status field of the desk rows DSA filed.
State: closed = a shipped fix with a test or a verified install; mitigated = a rule or partial fix, the failure can still
happen; open = no fix shipped. "desk" = MyTradingSys/system/desk_queue row (date-time id).

| id | symptom | fix | state | class |
|---|---|---|---|---|
| v0.3.x selector (F:/AIBridge DECISIONS.md) | DeepSeek code blocks not found; one version sent cmd="" | v0.3.2 findBlock walks up to the block ancestor | closed | block-read |
| hash-line phantom blocks (AIBRIDGE_LANE 2026-10-09) | a line starting with a hash splits one block, only the first part runs | prompt rule: build the hash from [char]35; no code fix | mitigated | block-read |
| aibridge-multi-block-f1-f7 (B184) | multi-block replies partly run, no per-block receipt | v0.7.0 af9f3446: all blocks in order, batch header and receipts | closed | block-read |
| D1 dsabr-c1-block-select, desk 082119 | AIRUN fences inside the thinking panel ran | 0.7.4 6b2e089fc excludes the thinking container; 0.7.9 nearest-2-ancestors rule | closed | block-read |
| D2 desk 130944 | blocks 1-2 replayed in a 6-block reply | 0.7.4 per-reply duplicate guard | closed | block-read |
| aibridge-blockkey-whitespace-fragile | whitespace difference made block 1 run twice | 0.7.18 whitespace-normalised block key | closed | block-read |
| aibridge-reply-drop-4-blocks, desk 054813 | 4-block reply: block 3 skipped, block 4 empty | no extension defect (DSA-side drop); 4-block fixture test 0.7.10 | closed | block-read |
| ROOT_CAUSES 10, desk 131341 | blocks arrived empty, 11 NOT RUN in the 54-block real-page chain | 0.7.19 bodyless block waits up to 30 s | closed | block-read |
| ROOT_CAUSES 11, desk 111238 | long lines cut before running (stream pause over 2 s) | 0.7.19 second identical read 1.2 s later | closed | block-read |
| Argon A1 | half-written block ran, then ran again when it grew | 0.7.22 a block element that ran never runs again; first half-run still possible after a pause over about 3.4 s | mitigated | block-read |
| 0.7.27 complete-reply read | a block ran while DSA was still writing it | 0.7.27 c32d5102f runs only when the DeepSeek action bar shows the reply complete | closed | block-read |
| desk 151558 | bridge dropped command lines across 11 blocks | covered by 0.7.19 and 0.7.27; desk row still pending, no replay test names it | mitigated | block-read |
| desk 205556 and 205747 | truncates mid-string on NB 0.7.x | none named; filed 11-03 after 0.7.22, rows pending | open | block-read |
| Argon F10 | findBlock climbs out of a bare pre into prose; hidden lines fuse | not traced | open | block-read |
| aibridge-handsfree-unchecks | hands-free box unchecked itself mid-chat | 0.7.1 3270e742 stays armed when a post landed | closed | chain-stop |
| stuck auto-run 2026-10-10 (AIBRIDGE_LANE) | panel stuck on waiting for DSA after #2 | v0.6.0 visible-text quiet, rescan, watchdog | closed | chain-stop |
| B210 fix-aibridge-four-defects | run lock never expired, chain stuck | 0.7.3 12b43fe17 lock expires at twice the block timeout | closed | chain-stop |
| desk 173311 expiresMs lock bug | lock expiry bug B2 reported after 0.7.3 | none named; row pending | open | chain-stop |
| D4 dsabr-c2-dropped-gen, desk 095323 | waiting for DSA forever after a dropped generation | 0.7.4 replyWatch: one notice, then stop banner | closed | chain-stop |
| B168 | auto-run stopped between turns | verified stay-armed in 0.7.3 | closed | chain-stop |
| 0.7.11 idle wobble | hands-free auto-OFF on timer wobble or operator typing | 0.7.11 tolerance plus one retry before auto-OFF | closed | chain-stop |
| ROOT_CAUSES 8 | a short final answer (Done.) read as a dropped generation | 0.7.16 a short answer no longer ends the chain | closed | chain-stop |
| ROOT_CAUSES 12 | result post waited 180 s for an idle chat, then hands-free OFF | 0.7.19 busy-chat results queued and retried | closed | chain-stop |
| desk 113539 | hands-free OFF, no final answer | 0.7.19 and 0.7.26; real-page unattended still NOT proven (ROOT_CAUSES) | mitigated | chain-stop |
| Argon A2 | clickSend clicked Stop or attach; failed post left text in the box | 0.7.22 pickSendButton and draft restore | closed | chain-stop |
| Argon A3 | extension self-update fired during an armed chain | 0.7.22 self-update only when hands-free is OFF | closed | chain-stop |
| 0.7.26 send not landed | a result whose send did not land was lost | 0.7.26 0cbb60d1b retries the post | closed | chain-stop |
| ROOT_CAUSES 4 | hidden or covered tab throttles timers, reply never settles | worker and port tick in 0.7.x; not proven on the real page | mitigated | chain-stop |
| Argon F5 | MV3 service worker idle stop and blob Worker blocked under hidden-tab throttling | partly by the worker tick; not traced on the real page | open | chain-stop |
| Argon postLanded | postLanded true when the input stayed empty: result silently dropped | none; listed OPEN in ROOT_CAUSES | open | chain-stop |
| D3 dsabr-c3-task-exit, desk 082116 | task step reported PASS over EXIT_CODE=1 | 0.7.4 92024c7da native exit code propagates, fail_on EXIT_CODE | closed | exit-truth |
| B209 task gate | task=mts-gate PASS over FAILED | 0.7.3 FAILED line fails the step | closed | exit-truth |
| D3b gate without summary | gate died mid-run with no summary, still read as a result | 0.7.4 expect ALL TESTS PASSED, PYTHONUNBUFFERED=1 | closed | exit-truth |
| desk 113613 | task=inline reports pass on failure | covered by D3 and E5 fixes; row pending, no replay test names it | mitigated | exit-truth |
| desk 100013 | bridge ignores a PowerShell command failure | invalid: PowerShell continues after a non-terminating error; prompt 0.5 ErrorActionPreference rule | closed | exit-truth |
| E5 (0.7.7) | a batch kept running after a failed block | 0.7.7 a9300f5bd any non-zero exit stops the batch | closed | exit-truth |
| aibridge-extension-guard-no-store | no-store fetch contract untested (mutant M4 survived) | regression test in test_aibridge_payload.py | closed | exit-truth |
| aibridge-version-not-bumped | panel showed 0.7.0 after 0.7.1 | already 0.7.1 in 3270e742; card dropped | closed | version-drift |
| B196 shipped unbumped | a fix shipped without a version change | 0.7.2 5bb07ccc6 version guard test | closed | version-drift |
| 0.7.8 revert | 0.7.8 turned trunk CI red (version bump test) | reverted 94f5a22ca, re-landed as 0.7.9 | closed | version-drift |
| ROOT_CAUSES 1 | extension, page, disk and agent versions drift invisibly | 0.7.16 drift detection, 0.7.21 one version source and label | closed | version-drift |
| aibridge-desk-no-inject-after-075 | panel shows agent 0.7.5 but 0/200, blocks not run after F5 | ready card: retest on the current build first | open | version-drift |
| aibridge-072-desktop-install | desktop still on 0.7.1, Chrome on the pre-B196 extension | refined card, not done | open | version-drift |
| dsabr-c7-install-e2e, desk 054027 | install and e2e routed to the wrong lane | installed 0.7.10 on JIS-NUC, d7d58219e | closed | version-drift |
| trunk CI red 2026-11-07 (dsa-tests-quick-trunk-1107) | unregistered test_aibridge_version_bump and test_dsa_seed turned CI red | revert; quick gate rerun by DSA | closed | version-drift |
| B176 ask-p0-73 | read-only python scripts needed a click | v0.7.0 af9f3446 runs read-only scripts without a click | closed | permission |
| aibridge-sandbox-chat-run-acl-proof | a chat-run command can edit src/policy.json and read the secrets folder | sandbox ACL proof done; limited account on the live install NOT applied | open | permission |
| ROOT_CAUSES policy self-edit hole | DSA reasoning planned a policy.json write to bypass the regex; [System.IO.File] not matched | prompt rule only (a refusal is reported, never worked around) | open | permission |
| ROOT_CAUSES 9 | git branch -d click-gated by a regex meant for -D | 0.7.16 case-sensitive rule, own-worktree exemption | closed | permission |
| desk 100020 | cwd sandbox escape via Set-Location | none named; row pending | open | permission |
| desk 181828 | the screen refused a task card write | none named; row pending | open | permission |
| aibridge-posts-the-dsa-seed-itself | chat start needed clipboard plus Ctrl+V | superseded by the 0.7.30 trigger | closed | seed-boot |
| aibridge-start-dsa-trigger-1107 | no terminal-free way to boot DSA | 0.7.30 typed Start DSA bridge fetches and sends the seed | closed | seed-boot |
| aibridge-seed-bad-origin-1107 | GET /seed refused bad_origin on every press | 0.7.31 fb94f3b46 POST /seed | closed | seed-boot |
| 0.7.32 seed root | /seed ran from a stale repo_root | 0.7.32 ee59257a8 seed_root or a current sibling worktree | closed | seed-boot |
| dsa-block-stdout-utf8-1107 | cp1251 decode error hid ship and tasks.py results | prompt 0b rule 6 and seed set UTF-8 per block; card raw | mitigated | seed-boot |
| aibridge-live-selftest-flaky | selftest port 7199 clash in parallel gates | 3e9e1601 free port, 5086eea4 no self-race | closed | test-harness |
| aibridge-dom-find-browser-edge-headless-empty | headless Edge gave an empty DOM, 8 tests failed | find_browser probes and skips empty Edge | closed | test-harness |
| D5 dsabr-c4-gate-tmp | gate tests failed with TEMP inside the bridge repo | 92024c7da hermetic TEMP and git config | closed | test-harness |
| test-aibridge-chain-hidden-tab-test-test | 54-block hidden-tab test times out under load and blocks ship step 4b | parked | open | test-harness |
| gate-4c-edge-shard-timeout-aibridge-exploratory-1108 | exploratory browser tests time out in smoke shard 4c | raw card, not ready | open | test-harness |
| ROOT_CAUSES 5 | bare TCP probes were 43 percent of the audit log | 0.7.12 empty connect no longer audited | closed | test-harness |
| desk 113608 | task=inline ignores the repo parameter | none named; row pending | open | task-mode |
| E6 (0.7.7) | task lock did not follow the agent default | 0.7.7 a9300f5bd | closed | task-mode |
| desk 185143 | task mode file lock crash | none named; row pending | open | task-mode |
| dsa-py-end-cannot-remove-its-own-worktree | dsa.py end died on Permission denied | fffa732ce prints the fallback remove command | closed | task-mode |
| dsa-py-edit-refuses-json-state-anchor-js | dsa.py edit refuses a JSON state anchor | parked | open | task-mode |
| desk 100219 | output truncation floods the chat | none named; row pending | open | output-size |
| Argon F6 | multi-part results over 60000 chars: duplicate posts or skipped blocks | dead anyPosted removed; guard not built | open | output-size |
| D7 desk 125045 | cap 50 consecutive runs stopped long chains | 0.7.4 cap raised to 200 (removed a brake) | closed | pacing-account |
| extension tuning 2026-10-10 (DSA_DELEGATION) | auto-run felt slow | idle wait 4000 to 2000 ms, poll 700 to 250 ms, post wait 1500 to 600 ms (removed a brake) | closed | pacing-account |
| B182 ask-p0-58 | tasks could not run in parallel | v0.7.0 parallel chats, max_parallel 8 | closed | pacing-account |
| item ldkziormfnb5jzgtosjy (DSA_DELEGATION) | second chat on the same DeepSeek account stops answering | not reproduced; advice only (do not drive both from one account) | open | pacing-account |
| dsa-multi-chat-driver-1107 | operator wants 2-3 DSA chats per host under Haiku control | raw card; would multiply sends per account | open | pacing-account |
| Argon F11 | HTTP 429 aborts batches unretried; socket reset retried as agent_unreachable double-runs | not traced | open | pacing-account |
| dsa-bridge-avoid-deepseek-block-1108 | account suspended until 2026-11-11 for violation of user policies | blocked card; this review feeds it | open | pacing-account |

## 2. Repeat classes

Count = rows of that class in section 1. A class with 2 or more rows is a design fault: the same kind of failure came back
after a fix, so the fix treated a symptom.

| class | count | design fault | why it repeats |
|---|---|---|---|
| block-read | 14 | yes | The bridge reads commands out of a third-party page DOM that streams, re-renders and changes class names; every DeepSeek UI change opens a new hole. |
| chain-stop | 16 | yes | Hands-free is a long unattended loop over a page built for a person; each new stall cause gets its own timer and retry. |
| exit-truth | 7 | yes | Pass or fail was read from text, not from exit codes, until 0.7.4. |
| version-drift | 8 | yes | An unpacked extension on three machines needs a hand reload per release; 32 releases in 25 days. |
| permission | 6 | yes | The real boundary (a limited Windows account) was never applied; regex screens leak. |
| seed-boot | 5 | yes | Each automation of the chat start added a new path (clipboard, trigger, GET, POST, seed root). |
| test-harness | 6 | yes | Browser tests are slow and load-sensitive inside a shared gate. |
| task-mode | 5 | yes | Task mode and dsa.py grew features faster than tests. |
| output-size | 2 | yes | Results are pasted back into the chat in full; no size budget. |
| pacing-account | 7 | yes | No limit exists on how fast, how much, from how many chats or machines one DeepSeek account is driven; the three shipped rows each removed a brake. |

## 3. DeepSeek rules

Fetched by curl on 2026-11-08 (public pages only; no login, no account page, no bot-check page).

| source | date | URL | what it says on automated use |
|---|---|---|---|
| DeepSeek Terms of Use, s3.5(3) | Last Update 2026-03-27 | https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html | Bans "capturing, copying any content of the Services, including but not limited to using any robots, spiders, or other automatic setups, setting mirrors". |
| DeepSeek Terms of Use, s3.3 | Last Update 2026-03-27 | https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html | "DeepSeek has the right to use technical means to review the behavior of users using the Services, including ... establishing risk filtering mechanisms". |
| DeepSeek Terms of Use, s2.2 and s2.3 | Last Update 2026-03-27 | https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html | "The account is non-transferable, non-giftable, and non-inheritable"; the user "must not register an account or use the Services on behalf of others". |
| DeepSeek Terms of Use, s8.2 | Last Update 2026-03-27 | https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html | DeepSeek may "independently judge" and act: "issuing warnings, setting deadlines for correction, restricting account functions, suspending usage, closing accounts, prohibiting re-registration". No numeric rate limit for the chat site anywhere in the terms. |
| DeepSeek API docs, Rate Limit and Isolation | page undated, fetched 2026-11-08 | https://api-docs.deepseek.com/quick_start/rate_limit | The API is built for automation: per-account concurrency limits (2500 for deepseek-flash, 500 for deepseek-v4-pro), HTTP 429 above the limit, user_id isolation. This is the sanctioned channel for programs. |
| better-deepseek issue 186 (owner test) | 2026-10-14 and 2026-11-04 | https://github.com/EdgeTypE/better-deepseek/issues/186 | Owner: "making the same request repeatedly in a short time triggers a suspension, especially if you keep opening new chats and heavily using the regenerate button"; 11-04: a new ban wave "cracking down on heavy, agent-like usage patterns". A user on 11-06: do not use MCP or bridges. Anecdotal. |
| better-deepseek issue 229 | 2026-11-03 | https://github.com/EdgeTypE/better-deepseek/issues/229 | Title "Causes account suspension"; screenshot only. Same week as our block. |
| OmniRoute issue 16972 | 2026-10-17 to 2026-10-20 | https://github.com/cheaper-inference/OmniRoute/issues/16972 | Same text as ours ("Due to violation of user policies, your account has been suspended until ..."); maintainers: DeepSeek anti-abuse flags automated or unofficial web-session access; the message is account-level, not retryable; use the official API. |
| ZeroScript-Free issues 82 and 115 | 2026-09-30 and 2026-10-27 | https://github.com/sebattfg/ZeroScript-Free/issues/115 | 82: a browser tool used for one night, then a 3-day suspension. 115: "logged me out like 7 times i ignored it until" the same suspension text: forced logouts came first and were a warning. |

Could not be fetched or not tried: the DeepSeek Open Platform Terms of Service
(https://platform.deepseek.com/downloads/DeepSeek%20Open%20Platform%20Terms%20of%20Service.html) returned HTTP 403 to curl on
2026-11-08, so the API-side terms text is not quoted here; the reddit threads cited in issue 186 were not fetched (script-only
pages); chat.deepseek.com itself and any account or appeal page were not opened (login wall; out of scope). No public DeepSeek
page names the exact trigger, a threshold, or a cooldown rule. The operator's own block text has no reason code.

## 4. Bridge behaviours

Rank = how likely this behaviour is to trigger an account block, judged from section 3 and the audit counts. Every row is
unproved: DeepSeek gives no reason code and we have one block, so no behaviour can be isolated.

| behaviour | rank | proof | evidence |
|---|---|---|---|
| auto-send | likely | unproved | 147 of 205 rows on 11-07 were hands-free; terms s3.5(3) bans automatic setups; three unrelated tools that auto-send on the chat site report the same suspension text (section 3). |
| rate | likely | unproved | 205 rows in 13 h on one host, peak 45 an hour, median 16 s between auto runs, 43 gaps under 10 s; 2 to 9 times the previous days; issue 186 owner test ties suspension to many requests in a short time. |
| parallel chats | possible | unproved | Bridge allows 8 parallel chats (0.7.0), the prompt tells DSA it is one of several chats, each task chat is a new chat; issue 186 names "opening new chats". |
| one account on several machines | possible | unproved | Block card: three machines on 11-07 with one account; terms s2.2/s2.3 make the account personal and non-transferable; DSA_DELEGATION already warned against two chats on one account (item ldkziormfnb5jzgtosjy). No source says concurrent devices trigger a block. |
| fixed-format messages | likely | unproved | Every result the bridge posts has the same template ([AIRUN RESULT] or [AIRUN BATCH] header, receipts) seconds after the reply; 59 refused rows on 11-07 fed near-identical refusal receipts back; issue 186: "too many similar requests". |
| command text | unlikely | unproved | The content rules (s3.4, s3.6) target harmful content, not PowerShell; no report links code or shell text to suspension. The 11-02 reasoning trace that planned a policy bypass (ROOT_CAUSES) is the only content risk seen. |

## 5. DSA prompt

DSA_SESSION_PROMPT.md is a critical file and is NOT edited by this card. These lines make DSA emit many AIRUN blocks, retry, or
run long without a person. Each has replacement text for the build card; the change needs the operator's word and the
critical_files.json update in the same commit (prompt 6b).

1. FIRST A. Current: "If the task is not finished, every reply ends with the next block."
   Replacement: "If the task is not finished, end the reply with the next block, unless the pacing guard, a warning or the
   session limit says stop; then end with one line saying which, and no block."
2. FIRST B and 9a. Current: "Up to 6 blocks per reply: group reads and small edits."
   Replacement: "Up to 3 blocks per reply, and only when one cannot do the job; prefer one task=inline call. Fewer replies
   per hour matter more than speed."
3. 0.1. Current: "Per chain the bridge runs 200 blocks, then hands-free turns off and says so."
   Replacement: "Per chat the bridge runs at most 40 blocks and 15 results an hour, then hands-free turns off and says so;
   do not ask for it back."
4. 0.1. Current: "Emit AIRUN whenever the task needs a command; never wait to be asked."
   Replacement: "Emit AIRUN when the task needs a command and the last result is in; a paused or refused bridge means wait."
5. FIRST G. Current: "\"go\" = the queue of section 5 until it is empty or section 12 says end"
   Replacement: "\"go\" = the next task of section 5 only; after it ships, the five lines of section 13 and stop. The
   operator says go again for the next task."
6. 5 heading and 5a step 10. Current: "in \"go\" mode never idle while a step has work" and "\"go\" mode: next task, no pause."
   Replacement: "Idle is allowed and normal. After each task: the five lines, then stop and wait for the operator."
7. 9a. Current: "Continuous execution: after a result, send the next step yourself. A reply without a block ends the run."
   Replacement: "After a result, send the next step of the same task yourself; a new task needs a new order."
8. 0.7. Current: "Re-send the blocks of that answer once." (dropped generation) and FIRST D "fix it and resend it once" and 0.1
   "lines=N lower than the lines you sent means a line was lost: resend."
   Replacement: "One resend per chat for all causes together. A second failure of any kind: no block, one line, stop."
9. 2. Current: "one chat runs at most 4 tasks or about 60 results, then hands off (section 12)."
   Replacement: "one chat runs at most 1 task or 20 results, then hands off (section 12)."
10. 0b. Current: "You are one of several DSA chats on this host and on the other host."
    Replacement: "You are the only DSA chat on this DeepSeek account. If the seed lists another chat holding cards on the same
    account, print one line and stop."
11. New rule, add after 0.9. Current: none (no rule covers a DeepSeek warning).
    Replacement: "STOP ON WARNING. If the page shows a logout, a captcha or human check, a rate or busy notice, 'unusual
    activity', 'violation' or 'suspended', send no block, write one line quoting it, and stop the chat. Never retry, never
    open a new chat, never switch account or machine to continue."

Outside the prompt, DSA_DELEGATION.md:108-110 lets a supervisor spawn a Haiku agent that opens a new DeepSeek chat on its own
and a watcher that presses Run and re-sends dropped blocks: the same retry loop at the browser level. Replacement: the watcher
reports only; it never opens a chat or re-sends while a warning or the pacing cooldown stands.

## 6. Ranked fix list

The build card (dsa-bridge-avoid-deepseek-block-1108) follows this order. Lanes: SONNET builds bridge code (the bridge is
Claude-only per prompt 5d); OPERATOR gives the word for the critical prompt file and money.

| rank | fix | failure prevented | fail-first test | owner lane |
|---|---|---|---|---|
| 1 | Pacing guard in the agent and extension: at least 60 s between auto posts per account, at most 15 an hour and 80 a day, random 10-30 s jitter; refused posts say paced and wait | burst sending (45 an hour, gaps under 10 s) that most likely drew the block | test_aibridge_pacing.py: replay the 2026-11-07 audit timestamps through the guard: 0 posts closer than 60 s, no hour over 15; fails on 0.7.32 (no guard) | SONNET |
| 2 | One machine per account: account lease (account label, host, heartbeat) checked before hands-free arms; a second host for the same account is refused | one account driven from three machines at once | test_aibridge_account_lease.py: two fake hosts arm the same account label: the second gets refused account_in_use; fails on 0.7.32 | SONNET |
| 3 | Stop on warning: the extension watches for logout, captcha, rate or busy notice, violation or suspended text; hands-free OFF, no retry, EXT-EVENT audit row, 24 h cooldown per profile, one line to the operator | driving the account through warnings into a suspension (ZeroScript 115: 7 logouts first) | handsfree.test.js case stop_on_warning: fixture page with a suspended banner and one with a logout redirect: 0 posts after it, hands-free OFF; fails on 0.7.32 | SONNET |
| 4 | One armed chat per account: max_parallel 8 to 1; a second armed tab on the same account is refused | parallel chats multiplying sends per account | handsfree.test.js case second_tab_refused: two armed tabs, one account: second refused; fails on 0.7.32 | SONNET |
| 5 | Prompt pacing text of section 5 (items 1-11) into DSA_SESSION_PROMPT.md with the operator's word and critical_files.json | the model itself asking for long unattended runs and resends | test_dsa_direct_mode.py asserts the stop-on-warning sentence and the absence of "never idle" and "no pause"; fails on the current prompt | OPERATOR then SONNET |
| 6 | One retry budget per chat across all causes (dropped generation, bad_task_spec, lost lines, busy post); the watcher never re-sends | retry loops that repeat near-identical messages | handsfree.test.js case retry_budget: dropped generation twice plus a busy post: exactly 1 resend; fails on 0.7.32 (one per cause) | SONNET |
| 7 | Two refusals in a row end the chain instead of posting refusal receipts back for DSA to rewrite | 59 refused rows on 11-07 fed back as fixed-format messages | test_aibridge_refusal_stop.py: replay of three refused rows: chain stops after the second; fails on 0.7.32 | SONNET |
| 8 | New-chat cap: /seed and the Start DSA bridge trigger serve at most 3 seeds per account a day; the Haiku spawn in DSA_DELEGATION.md:108 needs the operator | many new chats a day (issue 186 trigger) | test_aibridge_start_seed.py case fourth_seed_refused: the fourth /seed in one day is refused; fails on 0.7.32 | SONNET |
| 9 | Unattended work moves to the official DeepSeek API (operator money decision, priced on the block card; no key handled here) | using the chat site for automation, which the terms bar | test_dsa_api_runner.py: the runner refuses to start without an operator budget line in the config; fails because no runner exists | OPERATOR then SONNET |
| 10 | Hold dsa-multi-chat-driver-1107 until ranks 1-4 ship (depends_on) | a planned fan-out of 2-3 chats per host on one account | test in tasks.py check: the card lists the pacing card in depends_on; fails today (depends_on empty) | CLAUDE |
| 11 | No stress tests on the real account: 54-block chains run only on the fake page (desk 131341 and 163350 ran 54 blocks on chat.deepseek.com) | heavy test traffic counted against the account | test_aibridge_chain.py guard test: every chain test targets a localhost fixture URL; fails if a test names chat.deepseek.com | SONNET |
| 12 | Close or re-verify the 20 bridge desk rows still pending though a release covers most of them, each with a replay test or a dropped note | DSA re-filing and re-working fixed bugs (more traffic, more noise) | per row a replay test in scripts/aibridge/tests naming the desk id; fails while a row has neither a test nor a closing note | CODEX |

Not ranked, by design: anything that gets around a block or a bot check, a second account, a new profile to continue on the
suspended account before 2026-11-11, or rotating machines. Wait the suspension out.
