Option Explicit
Dim fso, shell, scriptDir, target, iconPath, workingDir, shortcutPath

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir   = fso.GetParentFolderName(WScript.ScriptFullName)
target      = fso.BuildPath(scriptDir, "Run_IESVE_Daylight_to_Excell.bat")
iconPath    = fso.BuildPath(scriptDir, "DaylightExcel.ico")
workingDir  = scriptDir
shortcutPath = shell.SpecialFolders("Desktop") & "\IESVE Daylight → Excel.lnk"

Dim lnk
Set lnk = shell.CreateShortcut(shortcutPath)
lnk.TargetPath = target
lnk.IconLocation = iconPath
lnk.WorkingDirectory = workingDir
lnk.WindowStyle = 1 ' normal window
lnk.Description = "Launch the IESVE Daylight Metrics → Excel exporter"
lnk.Save

WScript.Echo "Shortcut created: " & shortcutPath
