Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
sh.Run """C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\python.exe"" scripts\dev\retention.py --apply", 0, True
