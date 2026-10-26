#define AppVersion "0.3.0"
[Setup]
AppId={{8374260A-1672-4BC0-9782-6AD2FCDE7F22}
AppName=NETWATCH Terminal
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\NetwatchTerminal
DefaultGroupName=NETWATCH Terminal
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\installer-output
OutputBaseFilename=NetwatchTerminal-Setup-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\NetwatchTerminal.exe
[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked
Name: "startup"; Description: "{cm:StartupDescription}"; Flags: unchecked
[CustomMessages]
russian.StartupDescription=Запускать NETWATCH при входе в Windows (можно отключить в настройках)
english.StartupDescription=Start NETWATCH when signing in to Windows (can be disabled in Settings)
[Files]
Source: "..\dist\NetwatchTerminal\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\NETWATCH Terminal"; Filename: "{app}\NetwatchTerminal.exe"
Name: "{autodesktop}\NETWATCH Terminal"; Filename: "{app}\NetwatchTerminal.exe"; Tasks: desktopicon
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "NetwatchTerminal"; ValueData: """{app}\NetwatchTerminal.exe"""; Tasks: startup; Flags: uninsdeletevalue
[Run]
Filename: "{app}\NetwatchTerminal.exe"; Description: "{cm:LaunchProgram,NETWATCH Terminal}"; Flags: nowait postinstall skipifsilent
[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  StartupCommand: String;
begin
  if CurUninstallStep = usUninstall then
    if RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', 'NetwatchTerminal', StartupCommand) then
      if Pos(Lowercase(ExpandConstant('{app}\NetwatchTerminal.exe')), Lowercase(StartupCommand)) > 0 then
        RegDeleteValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', 'NetwatchTerminal');
end;
