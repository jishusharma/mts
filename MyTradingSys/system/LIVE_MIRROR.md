# LIVE MIRROR - bringing JIS-NUC (and any work tree) level with the desktop (built 2026-10-10 after Opus review; tool scripts/dev/live_mirror.py, tests test_live_mirror.py, gate step 3lm)

## The gap (verified 2026-10-10 on JIS-NUC)
- Code, docs, claims, queue: already level through git (`sync.py`). Nothing to add.
- Live state is not: `runtime_data/snapshots`, `last_alert.json`, `live_runner.log`, orderflow/OI series, `auto_trades.jsonl`,
  loop state live only on JIS-NB and are gitignored. On the NUC they are empty or days old, so "market read per MTS"
  cannot be answered there (2026-10-09 20:13Z: Tom, Fabio, regime, VP all NOT_IN_DATA).
- Three Claude logins / three machines share the repo, not the runtime. Per-machine stores (screenshots, observations) do not meet either.

## Options considered
| # | Option | Verdict |
|---|---|---|
| A | NUC runs its own recorder/feeds | rejected: second writer of market state, drift, and the live loop must stay one-owner (DEVICES s3) |
| B | Commit runtime data to git / orphan branch | rejected: churn, secrets risk, no force-push rule, repo bloat |
| C | Remote into JIS-NB for every read | rejected as the standard: needs the desktop awake and a human; fine as fallback |
| D | One-way read-only mirror over the existing SMB share | CHOSEN: transport already works (NUC holds `mtsworker` credential for `\\JIS-NB\MTS-Queue`, port 445 open, checked 2026-10-10) |

## Design (D)
Files: `scripts/dev/live_mirror.py` (publish | pull | brief | status), `scripts/dev/test_live_mirror.py`, this file.
1. PUBLISH (desktop only, refuses unless `.mts_live` exists): copies an ALLOWLIST into
   `<share>\live_mirror\<stage>` then swaps to `current` by rename; writes `manifest.json`
   {host, utc, git head, files[{rel,size,sha256,mtime}], excluded_count}. Read-only: never writes into the live tree,
   never touches processes, HALT, orders. Scheduled by the supervisor every 5 min (task install = desk task, not done from here).
2. ALLOWLIST (relative to repo root; patterns in code, deny wins): `runtime_data/snapshots/` newest 48 `*.json` + any `*latest*`,
   `runtime_data/last_alert.json`, `alert_counter.txt`, `loop_state.json`, `canary_state.json`, `naked_pocs/*.json`,
   tail 3000 lines of `live_runner.log`, `execution/auto_trades.jsonl` tail 500, `MyTradingSys/runtime/alerts/*.jsonl` today+yesterday,
   `MyTradingSys/runtime/orderflow_live` and `oi_live` newest 2 days, `state_code.json`, `current_market_state.md`.
   DENY (hard, checked by name and by content-sniff of the first 4 KB): `.secrets`, `.env*`, `*key*`, `*token*`, `*secret*`, `*.pem`,
   `credentials*`, anything matching an API-key-shaped string. A denied hit is counted in `excluded_count`, never copied, and fails the publish loudly if it was on the allowlist.
3. PULL (any work tree; refuses in the live tree): reads `manifest.json`, verifies every sha256, copies into
   `runtime_data/_mirror/` (git-ignored; the share is the only channel, never git; NOT the real runtime paths, so no NUC process can mistake mirrored files for local live state),
   writes `_mirror/.MIRROR_OF_JIS-NB` with the manifest time. Atomic: staged then renamed. A bad hash or missing manifest keeps the previous mirror and exits non-zero.
4. BRIEF: `live_mirror.py brief` prints the answer sessions need in one screen: mirror age (WARN > 15 min, STALE > 60 min, never presented as live),
   latest snapshot key fields, last Tom/Fabio alert + age, regime/day_type, open testnet positions summary, OI/CVD step since 1 h. Every line is labelled `mirror@<utc>`. In a work tree whose copy is missing or older than 15 min, `brief` pulls first (45 s cap, never in the live tree), prints one `mirror: pulled <version>` or `mirror: pull skipped (...)` line, and clips each line to 160 chars.
5. Sessions use it: CLAUDE.md "Where to look" and QUICK_ANSWERS.md carry the line, "off the desktop: `live_mirror.py pull && brief` before any live read". A read quoting mirror numbers says so (`mirror@<utc>`).

## Fail-closed rules
- Unreadable/missing/old manifest: brief says NO MIRROR, never falls back to the stale 10-03 git snapshot silently.
- Mirror is data, not authority: no code path reads `_mirror/` for trading, gating or auto-pause.
- Pull is idempotent; two NUC sessions pulling at once serialise on a lock file.
- Desktop off = mirror ages and brief says so (same "machine off = stack down" rule as QUICK_ANSWERS.md).

## Return path (v1: minimal)
Per-machine stores that matter to the others (observation captures) ship as files under `MyTradingSys/research/` through git
(already the practice for screenshot extracts). `capture.py` stays per machine; the NUC's captures are exported by `live_mirror.py export-obs`
into `research/missed_trades/observations/<host>_<date>.jsonl` for the next `sync.py ship`. Screenshots stay local (extract + id is the record).

## Out of scope / open (defaults chosen)
- Control Room (ArtifactData) is per-owning-account; not mirrored. Default: every login keeps reading it via CONTROL_ROOM.md.
- Tailscale/remote access (DEVICES s4) stays the fallback for what the mirror lacks.
- Moving the live loop to the NUC is a separate decision (DEVICES s3); the mirror works the same from either owner.

## Changes made after the Opus review (2026-10-10, agent aeffde92e539212b1) - these override the text above
1. Separate share `MTS-Mirror` (F:\MTS\Mirror), READ access only for `mtsworker`. The existing MTS-Queue share is change-access, so the NUC could have rewritten what it reads. Default root `\JIS-NB\MTS-Mirror`, override `--root` or env `MTS_MIRROR_ROOT`. On JIS-NB (live tree and every work tree) the default is the local folder `F:\MTS\Mirror`: sessions there run as a user the share ACL does not list, so the UNC path answers `Permission denied` while the folder reads fine (`live_mirror.default_root`).
2. No folder rename over SMB: each publish writes `v<utc>/`, then replaces the one-line `CURRENT` pointer last; last 3 versions kept. Pull reads the pointer, then that folder.
3. Allowlist paths corrected from the code that writes them (`MyTradingSys/execution/...`, `runtime/alerts/<tf>.jsonl` tailed per file, `htf_context` under `MyTradingSys/research`); a test fails if an allowlisted name vanishes from the source.
4. Added: trader state, plans, journal, pm_heartbeats, daily-loss state, live_alert_state, consensus state, supervisor and apparatus logs, observation captures. HALT / HALT_DAILY_LOSS / AUTO_PAUSE publish as flags in the manifest (existence only).
5. Secrets: deny by path (fatal if an allowlisted file hits it); content match = the line is redacted and counted, never fatal (hashes and order ids pass).
6. Brief reports two ages: manifest age (desktop clock vs now) and publish-minus-newest-snapshot (both desktop clock, skew-proof). STALE if either exceeds 60 min.
7. The brief has no "open positions" line: positions come from the Deribit API and need secrets. Decisions come from auto_trades.jsonl instead.
8. Publish is a separate process outside the trading loop, installed by desk task `install-live-mirror-on-jis-nb`; it reaches the live tree by the normal manual or coordinator-run deploy (DEPLOY_RUNBOOK.md; MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md; task MTS-LiveMirror was every 5 min, `register_live_mirror.ps1`).
9. `sync.py start` runs `live_mirror.py pull` (45 s cap, never fatal) in any work tree.
10. Known and left open: Control Room (ArtifactData) is readable only from its owning account; screenshot stores and `shot.py status` differ per machine.

## Publish failure record (2026-10-15)
A failing scheduled publish writes `<root>/PUBLISH_FAIL.json` (since, last, error) and exits 3; a good publish clears it. `live_mirror.py brief` prints `PUBLISHER FAILING for N min` when it exists. Task MTS-LiveMirror is registered (launcher F:\MTS\launchers\launch-live-mirror.vbs, 5-min repeat, 5-min limit).

## The mirror follows the live owner (2026-10-25, card eagle-eyes-follows-live-owner)
The loop moved to DESKTOP-F7IU69N; the mirror no longer assumes JIS-NB. The owner is whoever `live_owner.py` names (marker `live_owner.json` in MTS_LIVE_OWNER_DIR, heartbeat younger than 180 s).
- PUBLISH: `live_mirror.py publish` refuses (exit 2) unless the marker names THIS host with a fresh heartbeat; missing, stale or unreadable marker also refuses (fail closed). It writes the local folder (`F:\MTS\Mirror` on JIS-NB, `C:\MTS\Mirror` elsewhere, env MTS_MIRROR_LIVE_ROOT) and a second copy to `<MTS_LIVE_OWNER_DIR>\mirror` (the share both hosts already reach for the owner marker; no new share needed). A failure of the second copy is recorded in that folder's PUBLISH_FAIL.json and never fails the local publish.
- REPEAT: no scheduled task. `scripts/core/loop-supervisor.ps1` calls `live_mirror.py publish --every-min 5` on its 30 s tick right after `live_owner.py claim` (try/catch, never fatal). It takes effect when the live tree runs the new supervisor (next deploy + `mts start`).
- PULL / BRIEF: default root = the local folder when this host is the owner, else `<MTS_LIVE_OWNER_DIR>\mirror`. The first line of `brief` is `LIVE OWNER: <host> (heartbeat Ns ago)`. Owner missing, stale or unreadable -> `LIVE OWNER: UNCONFIRMED (...)` and no numbers. A copy whose manifest host is not the owner (e.g. the old JIS-NB copy) -> `UNCONFIRMED ... read on <owner>` and no numbers; `pull` refuses such a copy.
- Allowlist, deny names, deny dirs and the key-line redaction are unchanged (tests pin them). The old live_host.txt rule stays only as the fallback when no owner is resolved.
- DECISION (OURS): the share copy lives in MTS_LIVE_OWNER_DIR (change-access for both hosts) instead of a read-only MTS-Mirror share on the laptop; the mirror is data, never authority, sha256 is verified on pull, and a new share would need an elevated step. Signal heartbeats (`mts_signal.py who`) show session hosts, not the loop, so the owner comes from live_owner.py only.

