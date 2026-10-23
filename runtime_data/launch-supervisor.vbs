Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
sh.Run """C:\Users\E-ngineers\AppData\Local\Microsoft\WindowsApps\pwsh.exe"" -NoProfile -ExecutionPolicy Bypass -File """ & root & "\scripts\core\loop-supervisor.ps1"" -Mode armed -IntervalMin 1", 0, False
