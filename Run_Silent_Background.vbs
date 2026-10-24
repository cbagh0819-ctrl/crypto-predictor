Set WshShell = CreateObject("WScript.Shell")
' Run server in completely hidden window (0)
WshShell.Run "cmd /c .\.venv\Scripts\python.exe main.py --ui --port 8000", 0, False

' Wait 2 seconds then open browser
WScript.Sleep 2000
WshShell.Run "http://localhost:8000"
