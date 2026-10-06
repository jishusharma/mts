Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
sh.Run """C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"" -m MyTradingSys.backtest.layers.alerts.live_runner_cli", 0, False