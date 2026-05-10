; Dudiver Music Audio Converter - Inno Setup 6
; No requiere admin - instala en AppData del usuario

#define AppName      "Dudiver Music Audio Converter"
#define AppVersion   "1.0.0"
#define AppPublisher "Roberth Dudiver"
#define AppExeName   "DudiverConverter.exe"
#define MenuKey      "DudiverMusicConverter"
#define AppId        "{{D1D2D3D4-E5F6-7890-ABCD-DUDIVER123456}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\DudiverMusicConverter
DefaultGroupName={#AppName}
OutputDir=installer_output
OutputBaseFilename=DudiverMusicAudioConverter_Setup_v{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExeName}
SetupIconFile=icon.ico
CloseApplications=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ffmpeg.exe";    DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico";           DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";       Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Desinstalar";      Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent

[Code]
// ─────────────────────────────────────────────────────────────────────────────
// Menu contextual en HKCU (sin admin)
// Archivos : SystemFileAssociations\audio\shell\ (cubre todos los formatos)
// Carpetas : Directory\shell\ y Directory\Background\shell\
// ─────────────────────────────────────────────────────────────────────────────

const
  MENU_KEY = 'DudiverMusicConverter';

procedure RegStr(Root: Integer; const Path, Name, Value: String);
begin
  RegWriteStringValue(Root, Path, Name, Value);
end;

procedure RegisterContextMenus;
var
  ExePath, IcoPath, Base, Sub, Cmd, FmtKey, IdxStr: String;
  FileFmtKeys, FileFmtLabels, FolFmtKeys, FolFmtLabels: TArrayOfString;
  i: Integer;
begin
  ExePath := ExpandConstant('"{app}\DudiverConverter.exe"');
  IcoPath := ExpandConstant('"{app}\icon.ico",0');

  // Formatos para archivos
  SetArrayLength(FileFmtKeys, 10);  SetArrayLength(FileFmtLabels, 10);
  FileFmtKeys[0]  := 'FLAC';    FileFmtLabels[0]  := 'a FLAC  (sin perdida)';
  FileFmtKeys[1]  := 'WAV24';   FileFmtLabels[1]  := 'a WAV 24-bit  (sin perdida)';
  FileFmtKeys[2]  := 'WAV16';   FileFmtLabels[2]  := 'a WAV 16-bit  (calidad CD)';
  FileFmtKeys[3]  := 'AIFF';    FileFmtLabels[3]  := 'a AIFF  (sin perdida)';
  FileFmtKeys[4]  := 'MP3_320'; FileFmtLabels[4]  := 'a MP3 320k';
  FileFmtKeys[5]  := 'MP3_VBR'; FileFmtLabels[5]  := 'a MP3 VBR V0';
  FileFmtKeys[6]  := 'AAC';     FileFmtLabels[6]  := 'a AAC / M4A';
  FileFmtKeys[7]  := 'OGG';     FileFmtLabels[7]  := 'a OGG Vorbis';
  FileFmtKeys[8]  := 'OPUS';    FileFmtLabels[8]  := 'a OPUS';
  FileFmtKeys[9]  := 'WMA';     FileFmtLabels[9]  := 'a WMA';

  // Formatos para carpetas
  SetArrayLength(FolFmtKeys, 8);  SetArrayLength(FolFmtLabels, 8);
  FolFmtKeys[0]  := 'FLAC';    FolFmtLabels[0]  := 'Convertir todo a FLAC  (sin perdida)';
  FolFmtKeys[1]  := 'WAV24';   FolFmtLabels[1]  := 'Convertir todo a WAV 24-bit';
  FolFmtKeys[2]  := 'WAV16';   FolFmtLabels[2]  := 'Convertir todo a WAV 16-bit';
  FolFmtKeys[3]  := 'MP3_320'; FolFmtLabels[3]  := 'Convertir todo a MP3 320k';
  FolFmtKeys[4]  := 'MP3_VBR'; FolFmtLabels[4]  := 'Convertir todo a MP3 VBR V0';
  FolFmtKeys[5]  := 'AAC';     FolFmtLabels[5]  := 'Convertir todo a AAC / M4A';
  FolFmtKeys[6]  := 'OGG';     FolFmtLabels[6]  := 'Convertir todo a OGG Vorbis';
  FolFmtKeys[7]  := 'OPUS';    FolFmtLabels[7]  := 'Convertir todo a OPUS';

  // 1. Archivos de audio — SystemFileAssociations\audio\shell\
  Base := 'SOFTWARE\Classes\SystemFileAssociations\audio\shell\' + MENU_KEY;
  RegStr(HKCU, Base, 'MUIVerb',     'Dudiver Music Audio Converter');
  RegStr(HKCU, Base, 'SubCommands', '');
  RegStr(HKCU, Base, 'Icon',         IcoPath);
  for i := 0 to GetArrayLength(FileFmtKeys) - 1 do
  begin
    if i < 10 then IdxStr := '0' + IntToStr(i) else IdxStr := IntToStr(i);
    FmtKey := IdxStr + '_' + FileFmtKeys[i];
    Sub    := Base + '\shell\' + FmtKey;
    Cmd    := ExePath + ' "%1" --format ' + FileFmtKeys[i];
    RegStr(HKCU, Sub,              'MUIVerb', FileFmtLabels[i]);
    RegStr(HKCU, Sub + '\command', '',         Cmd);
  end;

  // 2. Carpetas — Directory\shell\
  Base := 'SOFTWARE\Classes\Directory\shell\' + MENU_KEY;
  RegStr(HKCU, Base, 'MUIVerb',     'Dudiver Music Audio Converter');
  RegStr(HKCU, Base, 'SubCommands', '');
  RegStr(HKCU, Base, 'Icon',         IcoPath);
  for i := 0 to GetArrayLength(FolFmtKeys) - 1 do
  begin
    if i < 10 then IdxStr := '0' + IntToStr(i) else IdxStr := IntToStr(i);
    FmtKey := IdxStr + '_' + FolFmtKeys[i];
    Sub    := Base + '\shell\' + FmtKey;
    Cmd    := ExePath + ' "%1" --batch --format ' + FolFmtKeys[i];
    RegStr(HKCU, Sub,              'MUIVerb', FolFmtLabels[i]);
    RegStr(HKCU, Sub + '\command', '',         Cmd);
  end;

  // 3. Carpetas — Directory\Background\shell\
  Base := 'SOFTWARE\Classes\Directory\Background\shell\' + MENU_KEY;
  RegStr(HKCU, Base, 'MUIVerb',     'Dudiver Music Audio Converter');
  RegStr(HKCU, Base, 'SubCommands', '');
  RegStr(HKCU, Base, 'Icon',         IcoPath);
  for i := 0 to GetArrayLength(FolFmtKeys) - 1 do
  begin
    if i < 10 then IdxStr := '0' + IntToStr(i) else IdxStr := IntToStr(i);
    FmtKey := IdxStr + '_' + FolFmtKeys[i];
    Sub    := Base + '\shell\' + FmtKey;
    Cmd    := ExePath + ' "%V" --batch --format ' + FolFmtKeys[i];
    RegStr(HKCU, Sub,              'MUIVerb', FolFmtLabels[i]);
    RegStr(HKCU, Sub + '\command', '',         Cmd);
  end;
end;

procedure UnregisterContextMenus;
begin
  RegDeleteKeyIncludingSubkeys(HKCU,
    'SOFTWARE\Classes\SystemFileAssociations\audio\shell\' + MENU_KEY);
  RegDeleteKeyIncludingSubkeys(HKCU,
    'SOFTWARE\Classes\Directory\shell\' + MENU_KEY);
  RegDeleteKeyIncludingSubkeys(HKCU,
    'SOFTWARE\Classes\Directory\Background\shell\' + MENU_KEY);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    RegisterContextMenus;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    UnregisterContextMenus;
end;
