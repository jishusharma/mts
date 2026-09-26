# DEVICES

Reference for every machine this project runs on. Read by any session or
person working across the desktop, the NUC, or a new device before touching
network paths, shares, or scheduled tasks. No fabricated values: an
unconfirmed field says NOT CAPTURED instead of a guess; fill it from the
command shown, then update this file.

## jis-nb (desktop) - primary, source of truth for the repository

- Role: repository lives here. Coordinator sessions run here (Cowork,
  linked via the desktop app's device bridge).
- Windows account (interactive, own login): E-ngineers.
- Windows account (queue-only, no admin rights): mtsworker. Hidden from
  the sign-in screen. Password known to the operator; not written here.
- Repo root: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed
- Share: \\JIS-NB\MTS-Queue -> Dumps\workers\NUC-QUEUE, change access for
  mtsworker only. The old whole-repo share (MTS-Repo, Everyone/Full) was
  removed 2026-09-25; ACL backup in backup_session\acl-before-worker-v2-*.txt.
- LAN IPv4: NOT CAPTURED. Run on the desktop: ipconfig | findstr /C:"IPv4"
- Remote Desktop: NOT SET UP as of 2026-09-26. Needs Windows Pro/Enterprise
  to host, a password on an account (auto sign-in account currently has
  none), Settings > System > Remote Desktop turned on. See T049 doc note
  2026-09-26 for the full checklist.

## JIS-NUC (NUC) - worker

- Role: runs the local model (Ollama) and the queue worker only. Holds no
  canonical copy of the repo; every task it runs is self-contained (see
  MyTradingSys/items/T049_nuc_worker_v2.md).
- Hardware: Intel NUC, i7-10710U, 32 GB RAM, Windows 10 Pro, CPU-only.
- Model: qwen3-coder:30b via Ollama, http://127.0.0.1:11434 (localhost on
  the NUC itself; not reachable from the desktop or over the LAN).
- Local files: C:\MTS-Worker\ (nuc-worker.ps1, nuc-launcher.ps1, logs\,
  outbox\). Installed and kept current by the launcher from the desktop's
  deploy folder; never hand-edited on the NUC.
- Scheduled task: MTS-NUC-Worker, trigger at sign-in, runs nuc-launcher.ps1.
- Stored credential: cmdkey entry for JIS-NB, user JIS-NB\mtsworker (fixed
  2026-09-25; a stale entry for the desktop's own account caused Access
  denied until corrected - see T049 doc).
- Automatic sign-in: ON (set 2026-09-26). BIOS power-on-after-power-failure:
  deliberately NOT set (operator switches both machines off/on manually;
  see T049 doc "operator requirement 2026-09-25").
- LAN IPv4: NOT CAPTURED. Run on the NUC: ipconfig | findstr /C:"IPv4"

## Third device (mentioned 2026-09-26, not yet detailed here)

- A separate Cowork session ("NUC project") is working on connecting all
  three devices and restructuring data folders. That session runs in a
  different claude.ai Project from this one (MTS-MyTradingSystem), so it
  does not share memory or docs with sessions here - the repo files below
  are the only things both sides can read.
- NOT CAPTURED: which physical device that session is linked to, and its
  role. Fill in once confirmed.
- Shared contract for any session touching the worker pipeline: read
  MyTradingSys/items/T049_nuc_worker_v2.md and
  Dumps/workers/NUC-QUEUE/README.md before moving, renaming, or
  restructuring anything under Dumps/workers/NUC-QUEUE/, scripts/worker/,
  or (on the NUC) C:\MTS-Worker\.

## Open items raised by the other session (2026-09-26, relayed, not yet verified)

- RESOLVED 2026-09-26: jis-nb is confirmed a desktop tower by the operator
  directly. The "nb" in the hostname does not mean notebook; no change to
  how this machine is referred to elsewhere.
- mtsworker should stay (it's the queue-only service account the pipeline
  depends on, not a login to consolidate) but must NOT be a member of the
  local Administrators group. NOT VERIFIED either way as of 2026-09-26.
  Check on jis-nb: net localgroup Administrators
  If mtsworker is listed: net localgroup Administrators mtsworker /delete

## How to update this file

Run the ipconfig command on each machine and replace the matching
NOT CAPTURED line. Add a new machine as its own section in the same
format the moment it's connected, even before you know its final role.
