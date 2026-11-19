; Copyright (c) 2026 Nexuzy Lab
; Nexuzy Sheet - Inno Setup script for the Windows installer
; Build with:  python build_installers.py --platform windows
; --------------------------------------------------------------------

#ifndef MyAppVersion
  #define MyAppVersion "1.6.0"
#endif

#ifndef MyAppName
  #define MyAppName "Nexuzy Sheet"
#endif

#ifndef MyAppPublisher
  #define MyAppPublisher "Nexuzy Lab"
#endif

#ifndef MyAppURL
  #define MyAppURL "https://nexuzy.in"
#endif

#ifndef SourceDir
  #define SourceDir "..\..\dist\nexuzy-sheet"
#endif

#ifndef OutputDir
  #define OutputDir "..\..\dist\installers"
#endif

; The end user licence agreement is shown as the acceptance page.
#ifndef LicenseFile
  #define LicenseFile SourceDir + "\LICENSE"
#endif

[Setup]
AppId={{8B3E3C6A-6E2B-4C1E-9C43-9F0B3A6D7E51}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} spreadsheet workspace
VersionInfoCopyright=Copyright (c) 2026 Nexuzy Lab
DefaultDirName={autopf}\{#MyAppName}
UsePreviousAppDir=yes
Uninstallable=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile={#LicenseFile}
OutputDir={#OutputDir}
OutputBaseFilename=Nexuzy-Sheet-{#MyAppVersion}-windows-x64-setup
SetupIconFile=..\..\nxsheet\assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\nexuzy-sheet.exe
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=force
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associate"; Description: "Associate .nix Nexuzy Sheet workbooks"; GroupDescription: "File associations"

; Remove stale files from previous versions before installing the new bundle.
; User workbooks and model downloads are stored outside {app} and are preserved.
[InstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\changelog"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\nexuzy-sheet.exe"; IconFilename: "{app}\nexuzy-sheet.exe"
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\nexuzy-sheet.exe"; IconFilename: "{app}\nexuzy-sheet.exe"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\nexuzy-sheet.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Explorer\AppUserModelId\io.nexuzy.nexuzysheet"; ValueType: string; ValueName: "DisplayName"; ValueData: "Nexuzy Sheet"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\.nix"; ValueType: string; ValueName: ""; ValueData: "NexuzySheet.Document"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.nxl"; ValueType: string; ValueName: ""; ValueData: "NexuzySheet.Document"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.nxs"; ValueType: string; ValueName: ""; ValueData: "NexuzySheet.Document"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\NexuzySheet.Document"; ValueType: string; ValueName: ""; ValueData: "Nexuzy Sheet document"; Flags: uninsdeletekey; Tasks: associate
Root: HKA; Subkey: "Software\Classes\NexuzySheet.Document\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\nexuzy-sheet.exe,0"; Tasks: associate
Root: HKA; Subkey: "Software\Classes\NexuzySheet.Document\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\nexuzy-sheet.exe"" ""%1"""; Tasks: associate

[Run]
Filename: "{app}\nexuzy-sheet.exe"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
