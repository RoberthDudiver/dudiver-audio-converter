# Dudiver Music Audio Converter - Instalador PowerShell
# Ejecutar como Administrador

$AppName    = "Dudiver Music Audio Converter"
$InstallDir = "$env:ProgramFiles\Dudiver Music Audio Converter"
$ExeName    = "DudiverConverter.exe"
$MenuKey    = "DudiverMusicConverter"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir    = Join-Path $ScriptDir "dist"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  $AppName - Instalando..." -ForegroundColor Cyan
Write-Host "============================================"
Write-Host ""

# ── 1. Verificar admin ────────────────────────────────────────────────────────
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Host "[ERROR] Ejecuta este script como Administrador." -ForegroundColor Red
    Write-Host "        Click derecho en install.ps1 > Ejecutar con PowerShell (como admin)"
    pause; exit 1
}

# ── 2. Copiar archivos ────────────────────────────────────────────────────────
Write-Host "[1/3] Copiando archivos a: $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item "$DistDir\$ExeName"   $InstallDir -Force
Copy-Item "$DistDir\ffmpeg.exe" $InstallDir -Force
Write-Host "      OK" -ForegroundColor Green

# ── 3. Registrar menu contextual ─────────────────────────────────────────────
Write-Host "[2/3] Registrando menu contextual..."

$ExePath = "$InstallDir\$ExeName"

$Extensions = @('.mp3','.wav','.flac','.ogg','.m4a','.aiff','.aif',
                '.wma','.opus','.aac','.ape','.mka')

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

foreach ($ext in $Extensions) {
    $base = "HKCR:\SystemFileAssociations\$ext\shell\$MenuKey"

    # Menu padre
    New-Item -Path $base -Force | Out-Null
    Set-ItemProperty -Path $base -Name "(default)"    -Value $AppName
    Set-ItemProperty -Path $base -Name "MUIVerb"      -Value $AppName
    Set-ItemProperty -Path $base -Name "SubCommands"  -Value ""
    Set-ItemProperty -Path $base -Name "Icon"         -Value "`"$ExePath`",0"

    # Sub-items
    $idx = 0
    foreach ($fmt in $Formats) {
        $fmtKey  = "{0:D2}_{1}" -f $idx, $fmt.Key
        $subPath = "$base\shell\$fmtKey"
        New-Item -Path $subPath           -Force | Out-Null
        New-Item -Path "$subPath\command" -Force | Out-Null
        Set-ItemProperty -Path $subPath           -Name "(default)" -Value $fmt.Label
        Set-ItemProperty -Path "$subPath\command" -Name "(default)" -Value "`"$ExePath`" `"%1`" --format $($fmt.Key)"
        $idx++
    }
}
Write-Host "      OK - Menu registrado para: $($Extensions -join ' ')" -ForegroundColor Green

# ── 4. Acceso directo en Menu Inicio ─────────────────────────────────────────
Write-Host "[3/3] Creando acceso directo en Menu Inicio..."
$StartMenu = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\$AppName.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($StartMenu)
$Shortcut.TargetPath = $ExePath
$Shortcut.Description = $AppName
$Shortcut.Save()
Write-Host "      OK" -ForegroundColor Green

# ── Refrescar iconos del Explorador ──────────────────────────────────────────
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Instalacion completada!" -ForegroundColor Green
Write-Host "============================================"
Write-Host ""
Write-Host "  Ahora puedes hacer click derecho en cualquier"
Write-Host "  archivo de audio y elegir:"
Write-Host "  'Dudiver Music Audio Converter' > formato deseado"
Write-Host ""
Write-Host "  Instalado en: $InstallDir"
Write-Host ""
Start-Sleep -Seconds 2
