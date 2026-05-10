@echo off
setlocal
title Dudiver Music Audio Converter - Build
cd /d "%~dp0"

echo.
echo ============================================
echo   Dudiver Music Audio Converter - Build
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 ( echo [ERROR] Python no encontrado. & pause & exit /b 1 )

echo [1/4] Instalando dependencias...
pip install customtkinter pyinstaller --quiet --upgrade

echo [2/4] Compilando DudiverConverter.exe...
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "DudiverConverter.spec" del "DudiverConverter.spec" >nul 2>&1

pyinstaller --onefile --noconsole ^
    --name=DudiverConverter ^
    --hidden-import=customtkinter ^
    --collect-all=customtkinter ^
    converter.py

if errorlevel 1 ( echo [ERROR] PyInstaller fallo en converter.py. & pause & exit /b 1 )

echo [3/4] Compilando DudiverInstaller.exe (con UAC admin)...
if exist "DudiverInstaller.spec" del "DudiverInstaller.spec" >nul 2>&1

pyinstaller --onefile --console ^
    --name=DudiverInstaller ^
    --uac-admin ^
    installer.py

if errorlevel 1 ( echo [ERROR] PyInstaller fallo en installer.py. & pause & exit /b 1 )

echo [4/4] Copiando ffmpeg.exe...
if exist "ffmpeg.exe" (
    copy /Y "ffmpeg.exe" "dist\ffmpeg.exe" >nul
) else (
    for /f "delims=" %%i in ('where ffmpeg 2^>nul') do (
        copy /Y "%%i" "dist\ffmpeg.exe" >nul
        goto :found_ffmpeg
    )
    echo [WARN] ffmpeg.exe no encontrado. Copialo manualmente a dist\
    :found_ffmpeg
)

echo.
echo ============================================
echo   Build completado!
echo   Archivos en: dist\
echo     - DudiverConverter.exe   (la app)
echo     - DudiverInstaller.exe   (el instalador, pide UAC solo)
echo     - ffmpeg.exe
echo.
echo   Para instalar: doble clic en DudiverInstaller.exe
echo   Windows pedira UAC -> Aceptar -> listo.
echo ============================================
pause
