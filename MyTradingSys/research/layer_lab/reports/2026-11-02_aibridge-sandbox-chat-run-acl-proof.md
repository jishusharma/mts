# BLOCKED — AIBridge sandbox chat-run ACL proof

## Result
BLOCKED: Windows denied creation of `F:\MTS\_sandbox\aibridge_acl` to the session identity `CodexSandboxOffline`; therefore the sandbox copy and both ACL probes could not be run. No ACLs were applied, and no claim is made that the probes were refused.

## Scope and evidence
- Requested copy source: `F:\AIBridge` (observed present). Its top-level listing includes `src`, `run`, `scripts`, `tests`, and `extension`.
- The secrets directory was not read or copied. No live install files were modified.
- Attempted sandbox setup command (PowerShell):
  ```powershell
  $src='F:\AIBridge'; $dst='F:\MTS\_sandbox\aibridge_acl'; New-Item -ItemType Directory -Force -Path $dst | Out-Null; robocopy $src $dst /E /XD .secrets .git /XF *.pyc
  ```
- Transcript: `New-Item : Access to the path '_sandbox' is denied.`; `UnauthorizedAccessException`; `robocopy failed 16`. The command stopped before creating the copy or placeholder file.
- `whoami` returned `CodexSandboxOffline`. The workspace permits writes under `F:\MTS\mts-codex-lab`; the requested `F:\MTS\_sandbox` location is outside it and denied by the Windows sandbox boundary.
- Before probes: 0/2 run (copy creation failed). After probes: 0/2 run (no ACL test was possible). Required 2/2-success then 2/2-refused counts are NOT established.
- Live-file hash comparison: NOT RUN. No hashes are claimed; no live files were changed by the attempted command.

## Operator ACL lines for review (not executed)
Run these only against the completed sandbox copy, under the intended chat-run identity, after an operator provides a writable sandbox location and appropriate ACL authority:
```cmd
icacls "F:\MTS\_sandbox\aibridge_acl\src\policy.json" /deny "CodexSandboxOffline:(W)"
icacls "F:\MTS\_sandbox\aibridge_acl\.secrets" /deny "CodexSandboxOffline:(RX)"
```
These are proposed command lines only; effectiveness and inheritance have not been demonstrated here.

## Next step
An operator with write access to `F:\MTS\_sandbox` (or an approved sandbox path inside the writable workspace) must run the copy and probes. Do not mark this card done until the before/after transcripts and matching live hashes are captured.

Noticed: sandbox boundary blocks the task's required out-of-workspace copy path.
