Set sh = CreateObject("WScript.Shell")
ps = "powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File """ & WScript.Arguments(0) & """ -AlertFile """ & WScript.Arguments(1) & """"
sh.Run ps, 0, False
