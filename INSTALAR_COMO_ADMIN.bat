@echo off
:: Auto-elevate si no somos admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Importando menu contextual al registro...
reg import "%~dp0install_context_menu.reg"
if errorlevel 1 (
    echo ERROR al importar. Asegurate de ejecutar como Administrador.
    pause
    exit /b 1
)

:: Reiniciar Explorer para que el menu aparezca de inmediato
taskkill /f /im explorer.exe >nul 2>&1
timeout /t 1 /nobreak >nul
start explorer.exe

echo.
echo Listo! Ahora cierra esta ventana y haz click derecho en un MP3.
echo Deberia aparecer "Dudiver Music Audio Converter" en el menu.
pause
