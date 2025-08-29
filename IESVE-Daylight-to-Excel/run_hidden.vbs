Set WshShell = CreateObject("WScript.Shell")
Set args = WScript.Arguments
If args.Count < 2 Then
  WScript.Echo "Usage: run_hidden.vbs <python_exe> <script.py> [args...]"
  WScript.Quit 1
End If

pyExe = Chr(34) & args(0) & Chr(34)
script = Chr(34) & args(1) & Chr(34)

cmd = pyExe & " " & script
If args.Count > 2 Then
  For i = 2 To args.Count - 1
    cmd = cmd & " " & args(i)
  Next
End If

' 0 = hidden, do not wait
WshShell.Run cmd, 0, False
