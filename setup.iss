[Setup]
AppName=Ansh AI
AppVersion=1.0
DefaultDirName={localappdata}\AnshAI
DefaultGroupName=Ansh AI
OutputDir=.
OutputBaseFilename=AnshSetup
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\AnshAI.exe

[Files]
Source: "AnshAI_Release\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Ansh AI"; Filename: "{app}\AnshAI.exe"
Name: "{autodesktop}\Ansh AI"; Filename: "{app}\AnshAI.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\AnshAI.exe"; Description: "Launch Ansh AI"; Flags: nowait postinstall skipifsilent
