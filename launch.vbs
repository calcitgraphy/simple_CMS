Set WshShell = CreateObject("WScript.Shell")
scriptPath = Wscript.ScriptFullName
scriptDir = Left(scriptPath, InStrRev(scriptPath, "\"))

pythonExe = Chr(34) & scriptDir & "venv\Scripts\pythonw.exe" & Chr(34)
serverScript = Chr(34) & scriptDir & "server_manager.py" & Chr(34)

command = pythonExe & " " & serverScript

WshShell.Run command, 0, False
Set WshShell = Nothing