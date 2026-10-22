Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
sh.Run "cmd /c """"python"" -u -m MyTradingSys.backtest.layers.alerts.live_runner_cli >> runtime_data\live_runner.log 2>&1""", 0, False