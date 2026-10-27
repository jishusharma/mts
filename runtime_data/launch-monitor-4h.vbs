Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
sh.Run "pwsh.exe -NoProfile -File MyTradingSys\mts\research\rerun_monitor.ps1", 0, False
