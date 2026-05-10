@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Desinstalando version antigua de Program Files...

:: Borrar carpeta Program Files
if exist "C:\Program Files\Dudiver Music Audio Converter" (
    rmdir /s /q "C:\Program Files\Dudiver Music Audio Converter"
    echo - Carpeta eliminada
)

:: Borrar acceso directo sistema
if exist "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Dudiver Music Audio Converter.lnk" (
    del /f "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Dudiver Music Audio Converter.lnk"
    echo - Acceso directo eliminado
)

:: Limpiar claves HKLM (SystemFileAssociations)
for %%e in (.mp3 .wav .flac .ogg .m4a .aiff .aif .wma .opus .aac .ape .mka) do (
    reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\%%e\shell\DudiverMusicConverter" /f >nul 2>&1
    reg delete "HKLM\SOFTWARE\Classes\%%e\shell\DudiverMusicConverter" /f >nul 2>&1
)
echo - Registro HKLM limpiado

echo.
echo Listo. Ahora instala la nueva version con el Setup de Inno Setup.
pause
