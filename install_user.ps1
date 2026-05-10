# Dudiver Music Audio Converter - Instalador de usuario (sin admin requerido)

$AppName    = "Dudiver Music Audio Converter"
$MenuKey    = "DudiverMusicConverter"
$InstallDir = "$env:LOCALAPPDATA\DudiverMusicConverter"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$DistDir    = Join-Path $ScriptDir "dist"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  $AppName" -ForegroundColor Cyan
Write-Host "  Instalando..." -ForegroundColor Cyan
Write-Host "============================================"
Write-Host ""

# ── 1. Copiar archivos ────────────────────────────────────────────────────────
Write-Host "[1/3] Copiando archivos a: $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item "$DistDir\DudiverConverter.exe" $InstallDir -Force
Copy-Item "$DistDir\ffmpeg.exe"           $InstallDir -Force -ErrorAction SilentlyContinue
if (Test-Path "$ScriptDir\icon.ico") {
    Copy-Item "$ScriptDir\icon.ico" $InstallDir -Force
} elseif (Test-Path "$DistDir\icon.ico") {
    Copy-Item "$DistDir\icon.ico"   $InstallDir -Force
}
Write-Host "      OK" -ForegroundColor Green

$ExePath  = "$InstallDir\DudiverConverter.exe"
$IconPath = if (Test-Path "$InstallDir\icon.ico") { "$InstallDir\icon.ico" } else { $ExePath }

# ── Limpiar entradas viejas ───────────────────────────────────────────────────
$OldPaths = @(
    "HKCU:\SOFTWARE\Classes\SystemFileAssociations\.mp3\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\SystemFileAssociations\.wav\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\SystemFileAssociations\.flac\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.mp3\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.wav\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.flac\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.ogg\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.m4a\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.aiff\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.aif\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.wma\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.opus\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.aac\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.ape\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\.mka\shell\$MenuKey",
    "HKCU:\SOFTWARE\Classes\SystemFileAssociations\audio\shell\DudiverTest"
)
foreach ($p in $OldPaths) {
    if (Test-Path $p) { Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue }
}

# ── 2. Menu contextual para ARCHIVOS de audio ─────────────────────────────────
# SystemFileAssociations\audio\shell\ cubre TODOS los formatos de audio
# con una sola entrada, igual que hacen Play y Enqueue del sistema
Write-Host "[2/3] Registrando menu contextual (archivos de audio)..."

$Formats = @(
    @{ Key="FLAC";    Label="a FLAC  (sin perdida)" },
    @{ Key="WAV24";   Label="a WAV 24-bit  (sin perdida)" },
    @{ Key="WAV16";   Label="a WAV 16-bit  (calidad CD)" },
    @{ Key="AIFF";    Label="a AIFF  (sin perdida)" },
    @{ Key="MP3_320"; Label="a MP3 320k" },
    @{ Key="MP3_VBR"; Label="a MP3 VBR V0" },
    @{ Key="AAC";     Label="a AAC / M4A" },
    @{ Key="OGG";     Label="a OGG Vorbis" },
    @{ Key="OPUS";    Label="a OPUS" },
    @{ Key="WMA";     Label="a WMA" }
)

$base = "HKCU:\SOFTWARE\Classes\SystemFileAssociations\audio\shell\$MenuKey"
New-Item -Path $base -Force | Out-Null
Set-ItemProperty -Path $base -Name "MUIVerb"     -Value $AppName
Set-ItemProperty -Path $base -Name "SubCommands" -Value ""
Set-ItemProperty -Path $base -Name "Icon"        -Value "`"$IconPath`",0"

$idx = 0
foreach ($fmt in $Formats) {
    $fmtKey  = "{0:D2}_{1}" -f $idx, $fmt.Key
    $subPath = "$base\shell\$fmtKey"
    New-Item -Path $subPath           -Force | Out-Null
    New-Item -Path "$subPath\command" -Force | Out-Null
    Set-ItemProperty -Path $subPath           -Name "MUIVerb"   -Value $fmt.Label
    Set-ItemProperty -Path "$subPath\command" -Name "(default)" `
        -Value "`"$ExePath`" `"%1`" --format $($fmt.Key)"
    $idx++
}
Write-Host "      OK - Cubre todos los formatos de audio" -ForegroundColor Green

# ── 3. Menu contextual para CARPETAS (conversion en lote) ─────────────────────
Write-Host "[3/3] Registrando menu contextual (carpetas)..."

$FolderFormats = @(
    @{ Key="FLAC";    Label="Convertir todo a FLAC  (sin perdida)" },
    @{ Key="WAV24";   Label="Convertir todo a WAV 24-bit" },
    @{ Key="WAV16";   Label="Convertir todo a WAV 16-bit" },
    @{ Key="MP3_320"; Label="Convertir todo a MP3 320k" },
    @{ Key="MP3_VBR"; Label="Convertir todo a MP3 VBR V0" },
    @{ Key="AAC";     Label="Convertir todo a AAC / M4A" },
    @{ Key="OGG";     Label="Convertir todo a OGG Vorbis" },
    @{ Key="OPUS";    Label="Convertir todo a OPUS" }
)

foreach ($dirType in @("Directory", "Directory\Background")) {
    $dbase = "HKCU:\SOFTWARE\Classes\$dirType\shell\$MenuKey"
    if (Test-Path $dbase) { Remove-Item $dbase -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -Path $dbase -Force | Out-Null
    Set-ItemProperty -Path $dbase -Name "MUIVerb"     -Value $AppName
    Set-ItemProperty -Path $dbase -Name "SubCommands" -Value ""
    Set-ItemProperty -Path $dbase -Name "Icon"        -Value "`"$IconPath`",0"

    $idx = 0
    foreach ($fmt in $FolderFormats) {
        $fmtKey  = "{0:D2}_{1}" -f $idx, $fmt.Key
        $subPath = "$dbase\shell\$fmtKey"
        New-Item -Path $subPath           -Force | Out-Null
        New-Item -Path "$subPath\command" -Force | Out-Null
        Set-ItemProperty -Path $subPath           -Name "MUIVerb"   -Value $fmt.Label
        $arg = if ($dirType -eq "Directory\Background") { "%V" } else { "%1" }
        Set-ItemProperty -Path "$subPath\command" -Name "(default)" `
            -Value "`"$ExePath`" `"$arg`" --batch --format $($fmt.Key)"
        $idx++
    }
}
Write-Host "      OK - Menu de carpetas registrado" -ForegroundColor Green

# ── Reiniciar Explorer ────────────────────────────────────────────────────────
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 1500

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Instalacion completada!" -ForegroundColor Green
Write-Host "============================================"
Write-Host ""
Write-Host "  Archivos de audio : click derecho -> Mostrar mas opciones"
Write-Host "                      -> '$AppName'"
Write-Host "  Carpetas          : click derecho -> Mostrar mas opciones"
Write-Host "                      -> '$AppName' -> formato"
Write-Host ""
Write-Host "  Instalado en: $InstallDir"
Write-Host ""
