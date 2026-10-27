Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
' MTS-Live-Health (every 5 min): stale recorder/loop file or dropped live process -> desktop popup.
' Runs the detector from the registry worktree against the live tree (read-only on the live system).
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "" & root & ".registry"
sh.Run """python"" scripts\sched\check_live_health.py --root """ & root & """ --alert", 0, True
