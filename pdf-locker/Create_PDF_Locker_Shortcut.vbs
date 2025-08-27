' Create_PDF_Locker_Shortcut.vbs
' Creates a Desktop shortcut to Run_PDF_Locker.bat with a custom icon.

Option Explicit
Dim WshShell, FSO, desktop, lnk
Dim target, workdir, icon

Set WshShell = CreateObject("WScript.Shell")
Set FSO      = CreateObject("Scripting.FileSystemObject")

' === Paths (edit if needed) ===
target  = "C:\Python_Scripts\Run_PDF_Locker.bat"
workdir = "C:\Python_Scripts"
icon    = "C:\Python_Scripts\pdf-locker.ico"
' ===============================

If Not FSO.FileExists(target) Then
  MsgBox "Not found: " & target, vbCritical, "PDF Locker"
  WScript.Quit 1
End If

If Not FSO.FileExists(icon) Then
  MsgBox "Icon not found: " & icon & vbCrLf & "Place pdf-locker.ico there and run again.", vbCritical, "PDF Locker"
  WScript.Quit 1
End If

desktop = WshShell.SpecialFolders("Desktop")
Set lnk = WshShell.CreateShortcut(desktop & "\PDF Locker.lnk")
lnk.TargetPath       = target
lnk.WorkingDirectory = workdir
lnk.IconLocation     = icon
lnk.Arguments        = ""   ' optional
lnk.WindowStyle      = 1    ' normal window
lnk.Save

MsgBox "Shortcut created on your Desktop.", vbInformation, "PDF Locker"
