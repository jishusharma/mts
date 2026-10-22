Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
' MTS-Live-Health (every 5 min): stale recorder/loop file or dropped live process -> desktop popup.
' Runs the detector from the registry worktree against the live tree (read-only on the live system).
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "" & root & ".registry"
sh.Run """C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\python.exe"" scripts\sched\check_live_health.py --root """ & root & """ --alert", 0, True
