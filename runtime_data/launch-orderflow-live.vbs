Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
sh.Run """C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\python.exe"" -m MyTradingSys.backtest.layers.fabio.orderflow_live", 0, False