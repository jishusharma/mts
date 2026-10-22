Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
sh.Run """python"" scripts\dev\refresh_klines.py", 0, True
sh.Run """python"" scripts\dev\alert_rate_check.py", 0, True
