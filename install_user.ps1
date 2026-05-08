# Dudiver Music Audio Converter - Instalador de usuario (sin admin)

$AppName    = "Dudiver Music Audio Converter"
$InstallDir = "$env:LOCALAPPDATA\DudiverMusicConverter"
$ExeName    = "DudiverConverter.exe"
$MenuKey    = "DudiverMusicConverter"
$DistDir    = Join-Path $PSScriptRoot "dist"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  $AppName" -ForegroundColor Cyan
Write-Host "  Instalando (modo usuario, sin admin)..." -ForegroundColor Cyan
Write-Host "============================================"
Write-Host ""

# 1. Copiar archivos
Write-Host "[1/3] Copiando archivos a: $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item "$DistDir\$ExeName"   $InstallDir -Force
Copy-Item "$DistDir\ffmpeg.exe" $InstallDir -Force
Write-Host "      OK" -ForegroundColor Green

# 2. Registrar menu contextual en HKCU (no requiere admin)
Write-Host "[2/3] Registrando menu contextual..."
$ExePath    = "$InstallDir\$ExeName"
$HKCUBase   = "HKCU:\SOFTWARE\Classes"

$Extensions = @('.mp3','.wav','.flac','.ogg','.m4a','.aiff','.aif','.wma','.opus','.aac','.ape','.mka')
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
    $base = "$HKCUBase\SystemFileAssociations\$ext\shell\$MenuKey"

    New-Item -Path $base -Force | Out-Null
    Set-ItemProperty -Path $base -Name "(default)"   -Value $AppName
    Set-ItemProperty -Path $base -Name "MUIVerb"     -Value $AppName
    Set-ItemProperty -Path $base -Name "SubCommands" -Value ""
    Set-ItemProperty -Path $base -Name "Icon"        -Value "`"$ExePath`",0"

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
Write-Host "      OK - Registrado para: $($Extensions -join ' ')" -ForegroundColor Green

# 3. Acceso directo en Menu Inicio (carpeta de usuario, sin admin)
Write-Host "[3/3] Creando acceso directo en Menu Inicio..."
$StartMenu    = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\$AppName.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut     = $WScriptShell.CreateShortcut($StartMenu)
$Shortcut.TargetPath   = $ExePath
$Shortcut.Description  = $AppName
$Shortcut.Save()
Write-Host "      OK" -ForegroundColor Green

# 4. Refrescar iconos del Explorador
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 1000

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Instalacion completada!" -ForegroundColor Green
Write-Host "============================================"
Write-Host ""
Write-Host "  Click derecho en cualquier archivo de audio"
Write-Host "  y elige: '$AppName' > formato deseado"
Write-Host ""
Write-Host "  Instalado en: $InstallDir"
Write-Host ""
