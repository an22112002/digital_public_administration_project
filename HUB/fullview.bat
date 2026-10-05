@echo off
setlocal

if "%~1"=="" (
    echo Usage: open_kiosk.bat ^<view^>
    echo Example: open_kiosk.bat scan
    exit /b 1
)

set "VIEW=%~1"
set "URL=http://localhost:5174/%VIEW%"

set "EDGE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if not exist "%EDGE%" (
    set "EDGE=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

if not exist "%EDGE%" (
    echo Microsoft Edge not found.
    exit /b 1
)

start "" "%EDGE%" ^
    --kiosk "%URL%" ^
    --edge-kiosk-type=fullscreen ^
    --no-first-run ^
    --disable-session-crashed-bubble ^
    --disable-features=TranslateUI

endlocal