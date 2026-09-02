; -- SystemInfoTool.iss --
; Inno Setup script for System Info Tool.
; Build the .exe FIRST (run build_windows_exe.bat, or PyInstaller
; manually) so dist\SystemInfoTool.exe exists before compiling this.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

#define MyAppName "System Info Tool"
#define MyAppVersion "1.0"
#define MyAppExeName "SystemInfoTool.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
WizardStyle=modern
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=SystemInfoTool-Setup
OutputDir=Output
; Installed (non-portable) copy: no admin rights required, per-user install.
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
; The compiled executable (built via build_windows_exe.bat / PyInstaller).
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\portable.flag"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: isreadme ignoreversion
; NOTE: portable.flag IS installed here to support portable mode if desired.
; This installer produces a normal per-user install which stores settings
; under %APPDATA%\SystemInfoTool, but users can delete portable.flag to
; switch to installed mode, or keep it for portable mode.

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up the per-user settings folder on uninstall (comment this out
; if you'd rather keep saved settings/exports across reinstalls).
Type: filesandordirs; Name: "{userappdata}\SystemInfoTool"
