; Inno Setup script — Phone Backup Tool installer/uninstaller
#define MyAppName "Phone Backup Tool"
#define MyAppVersion "1.1"
#define MyAppExeName "PhoneBackupTool.exe"
; Android platform-tools with adb (Apache 2.0, see adb\NOTICE.txt)
#define AdbDir "C:\platform-tools"

[Setup]
AppId={{B8F1E4C0-6C2E-4C7A-9C1E-2A6E7D9F1A01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Pepe5rog
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=PhoneBackupTool-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать значок на рабочем столе"; GroupDescription: "Дополнительные значки:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#AdbDir}\adb.exe"; DestDir: "{app}\adb"; Flags: ignoreversion
Source: "{#AdbDir}\AdbWinApi.dll"; DestDir: "{app}\adb"; Flags: ignoreversion
Source: "{#AdbDir}\AdbWinUsbApi.dll"; DestDir: "{app}\adb"; Flags: ignoreversion
Source: "{#AdbDir}\NOTICE.txt"; DestDir: "{app}\adb"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Удалить {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\adb\adb.exe"; Parameters: "kill-server"; Flags: runhidden; RunOnceId: "KillAdb"
