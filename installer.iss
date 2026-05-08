; Dudiver Music Audio Converter - Inno Setup 6
; Instala menu contextual con submenus por formato para archivos de audio

#define AppName      "Dudiver Music Audio Converter"
#define AppVersion   "1.0.0"
#define AppPublisher "Roberth Dudiver"
#define AppExeName   "DudiverConverter.exe"
#define AppId        "{{D1D2D3D4-E5F6-7890-ABCD-DUDIVER123456}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=installer_output
OutputBaseFilename=DudiverMusicAudioConverter_Setup_v{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#AppExeName}
CloseApplications=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ffmpeg.exe";    DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";             Filename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar";            Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent

[Code]
// ─────────────────────────────────────────────────────────────────────────────
// Registro de menu contextual con submenus para cada extension de audio
// ─────────────────────────────────────────────────────────────────────────────

const
  MENU_KEY = 'DudiverMusicConverter';

procedure RegisterContextMenus;
var
  AppPath: String;
  Exts: TArrayOfString;
  Fmts: TArrayOfString;
  Labels: TArrayOfString;
  i, j: Integer;
  BaseKey, FmtKey: String;
begin
  AppPath := ExpandConstant('"{app}\DudiverConverter.exe"');

  // Extensiones de audio soportadas
  SetArrayLength(Exts, 12);
  Exts[0]  := '.mp3';
  Exts[1]  := '.wav';
  Exts[2]  := '.flac';
  Exts[3]  := '.ogg';
  Exts[4]  := '.m4a';
  Exts[5]  := '.aiff';
  Exts[6]  := '.aif';
  Exts[7]  := '.wma';
  Exts[8]  := '.opus';
  Exts[9]  := '.aac';
  Exts[10] := '.ape';
  Exts[11] := '.mka';

  // Claves internas de formato (deben coincidir con FORMATS en converter.py)
  SetArrayLength(Fmts, 10);
  Fmts[0] := 'FLAC';
  Fmts[1] := 'WAV24';
  Fmts[2] := 'WAV16';
  Fmts[3] := 'AIFF';
  Fmts[4] := 'MP3_320';
  Fmts[5] := 'MP3_VBR';
  Fmts[6] := 'AAC';
  Fmts[7] := 'OGG';
  Fmts[8] := 'OPUS';
  Fmts[9] := 'WMA';

  // Etiquetas visibles en el subMenu
  SetArrayLength(Labels, 10);
  Labels[0] := 'a FLAC  (sin perdida)';
  Labels[1] := 'a WAV 24-bit  (sin perdida)';
  Labels[2] := 'a WAV 16-bit  (calidad CD)';
  Labels[3] := 'a AIFF  (sin perdida)';
  Labels[4] := 'a MP3 320k';
  Labels[5] := 'a MP3 VBR V0';
  Labels[6] := 'a AAC / M4A';
  Labels[7] := 'a OGG Vorbis';
  Labels[8] := 'a OPUS';
  Labels[9] := 'a WMA';

  for i := 0 to GetArrayLength(Exts) - 1 do
  begin
    BaseKey := 'SystemFileAssociations\' + Exts[i] + '\shell\' + MENU_KEY;

    // Menu padre
    RegWriteStringValue(HKCR, BaseKey, '',          'Dudiver Music Audio Converter');
    RegWriteStringValue(HKCR, BaseKey, 'MUIVerb',   'Dudiver Music Audio Converter');
    RegWriteStringValue(HKCR, BaseKey, 'SubCommands', '');
    RegWriteStringValue(HKCR, BaseKey, 'Icon',
      ExpandConstant('{app}\DudiverConverter.exe') + ',0');

    // Items del subMenu
    for j := 0 to GetArrayLength(Fmts) - 1 do
    begin
      FmtKey := Format('%02d', [j]) + '_' + Fmts[j];
      RegWriteStringValue(HKCR,
        BaseKey + '\shell\' + FmtKey,
        '', Labels[j]);
      RegWriteStringValue(HKCR,
        BaseKey + '\shell\' + FmtKey + '\command',
        '', AppPath + ' "%1" --format ' + Fmts[j]);
    end;
  end;
end;

procedure UnregisterContextMenus;
var
  Exts: TArrayOfString;
  i: Integer;
  BaseKey: String;
begin
  SetArrayLength(Exts, 12);
  Exts[0]  := '.mp3';  Exts[1]  := '.wav';  Exts[2]  := '.flac';
  Exts[3]  := '.ogg';  Exts[4]  := '.m4a';  Exts[5]  := '.aiff';
  Exts[6]  := '.aif';  Exts[7]  := '.wma';  Exts[8]  := '.opus';
  Exts[9]  := '.aac';  Exts[10] := '.ape';  Exts[11] := '.mka';

  for i := 0 to GetArrayLength(Exts) - 1 do
  begin
    BaseKey := 'SystemFileAssociations\' + Exts[i] + '\shell\' + MENU_KEY;
    RegDeleteKeyIncludingSubkeys(HKCR, BaseKey);
  end;
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
