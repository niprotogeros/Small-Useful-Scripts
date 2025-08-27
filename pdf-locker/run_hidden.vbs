Set oShell = CreateObject("WScript.Shell")
Dim cmd, i
cmd = """" & WScript.Arguments(0) & """"
For i = 1 To WScript.Arguments.Count - 1
  cmd = cmd & " " & Chr(34) & WScript.Arguments(i) & Chr(34)
Next
oShell.Run cmd, 0, False
