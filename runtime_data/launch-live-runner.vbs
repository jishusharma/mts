Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
sh.Run "cmd /c """"C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\python.exe"" -u -m MyTradingSys.backtest.layers.alerts.live_runner_cli >> runtime_data\live_runner.log 2>&1""", 0, False