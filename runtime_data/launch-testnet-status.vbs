Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
sh.Run "cmd /c python scripts\dev\testnet_status.py", 0, False
