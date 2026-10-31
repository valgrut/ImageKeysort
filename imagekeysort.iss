#define MyAppName "ImageKeysort"
#define MyAppVersion "0.4.2"
#define MyAppPublisher "valgrut"
#define MyAppExeName "ImageKeysort.exe"

[Setup]
; IMPORTANT:
; Keep this AppId unchanged between releases.
AppId={{A18385C7-AD34-4DD4-9E2E-F3DDC1E06D71}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; Per-user install. No administrator rights needed.
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest

; Installer output
OutputDir=dist-installer
OutputBaseFilename={#MyAppName}-Setup-{#MyAppVersion}

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

; Icon shown in Windows Apps / Add or Remove Programs.
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; Don't allow user to choose Start Menu group name.
DisableProgramGroupPage=yes


[Files]
; PyInstaller --onedir:
; copy the ENTIRE generated directory, not only the .exe.
Source: "dist\ImageKeysort\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs


[Tasks]
; Explorer integration enabled by default.
Name: "contextmenu"; \
    Description: "Add ImageKeysort to Windows Explorer context menu"; \
    GroupDescription: "Windows Explorer integration:"

; Desktop shortcut disabled by default.
Name: "desktopicon"; \
    Description: "Create a desktop shortcut"; \
    GroupDescription: "Additional shortcuts:"; \
    Flags: unchecked


[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"

; Optional desktop shortcut
Name: "{userdesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    Tasks: desktopicon


[Registry]
; --------------------------------------------------------------------------
; Right-click directly on a directory:
;
;     C:\Pictures
;        -> Open in ImageKeysort
;
; %1 = selected directory
; --------------------------------------------------------------------------

Root: HKCU; \
    Subkey: "Software\Classes\Directory\shell\ImageKeysort"; \
    ValueType: string; \
    ValueName: ""; \
    ValueData: "Open in ImageKeysort"; \
    Flags: uninsdeletekey; \
    Tasks: contextmenu

Root: HKCU; \
    Subkey: "Software\Classes\Directory\shell\ImageKeysort"; \
    ValueType: string; \
    ValueName: "Icon"; \
    ValueData: "{app}\{#MyAppExeName}"; \
    Tasks: contextmenu

Root: HKCU; \
    Subkey: "Software\Classes\Directory\shell\ImageKeysort\command"; \
    ValueType: string; \
    ValueName: ""; \
    ValueData: """{app}\{#MyAppExeName}"" --src-path ""%1"""; \
    Tasks: contextmenu


; --------------------------------------------------------------------------
; Right-click empty background inside a directory:
;
;     Open this directory in ImageKeysort
;
; %V = current directory
; --------------------------------------------------------------------------

Root: HKCU; \
    Subkey: "Software\Classes\Directory\Background\shell\ImageKeysort"; \
    ValueType: string; \
    ValueName: ""; \
    ValueData: "Open this directory in ImageKeysort"; \
    Flags: uninsdeletekey; \
    Tasks: contextmenu

Root: HKCU; \
    Subkey: "Software\Classes\Directory\Background\shell\ImageKeysort"; \
    ValueType: string; \
    ValueName: "Icon"; \
    ValueData: "{app}\{#MyAppExeName}"; \
    Tasks: contextmenu

Root: HKCU; \
    Subkey: "Software\Classes\Directory\Background\shell\ImageKeysort\command"; \
    ValueType: string; \
    ValueName: ""; \
    ValueData: """{app}\{#MyAppExeName}"" --src-path ""%V"""; \
    Tasks: contextmenu


[Run]
; Checkbox on the final installer page.
Filename: "{app}\{#MyAppExeName}"; \
    Description: "Launch {#MyAppName}"; \
    WorkingDir: "{app}"; \
    Flags: nowait postinstall skipifsilent
