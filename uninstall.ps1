# Dudiver Music Audio Converter - Desinstalador
# Ejecutar como Administrador

$AppName    = "Dudiver Music Audio Converter"
$InstallDir = "$env:ProgramFiles\Dudiver Music Audio Converter"
$MenuKey    = "DudiverMusicConverter"

if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Host "[ERROR] Ejecuta como Administrador." -ForegroundColor Red; pause; exit 1
}

Write-Host "Desinstalando $AppName..." -ForegroundColor Yellow

$Extensions = @('.mp3','.wav','.flac','.ogg','.m4a','.aiff','.aif','.wma','.opus','.aac','.ape','.mka')
foreach ($ext in $Extensions) {
    $key = "HKCR:\SystemFileAssociations\$ext\shell\$MenuKey"
    if (Test-Path $key) { Remove-Item $key -Recurse -Force }
}

$StartMenu = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\$AppName.lnk"
if (Test-Path $StartMenu) { Remove-Item $StartMenu -Force }

if (Test-Path $InstallDir) { Remove-Item $InstallDir -Recurse -Force }

Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Write-Host "Desinstalado correctamente." -ForegroundColor Green
Start-Sleep -Seconds 1
