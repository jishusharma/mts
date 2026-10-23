Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & root & "\scripts\live\feed-watchdog.ps1""", 0, False
