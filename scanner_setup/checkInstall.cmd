@echo off

set "NAPS2=C:\Program Files\NAPS2\NAPS2.Console.exe"

if not exist "%NAPS2%" (
    echo NAPS2 NOT FOUND:
    echo %NAPS2%
    exit /b 1
)

"%NAPS2%" --version

set "RESULT=%ERRORLEVEL%"

echo.
echo ==============================
echo RESULT = %RESULT%
echo ==============================

pause