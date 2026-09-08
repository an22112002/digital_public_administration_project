@echo off
setlocal

REM ==============================
REM CẤU HÌNH
REM ==============================
set "NAPS2=C:\Program Files\NAPS2\NAPS2.Console.exe"

REM ==============================
REM KIỂM TRA NAPS2
REM ==============================
if not exist "%NAPS2%" (
    echo [ERROR] Khong tim thay NAPS2:
    echo %NAPS2%
    pause
    exit /b 1
)

echo.
echo ========================================
echo        NAPS2 SCANNER CHECK
echo ========================================

REM ==============================
REM KIỂM TRA CÁC DRIVER
REM ==============================
call :check_driver wia
call :check_driver twain
call :check_driver escl

echo.
echo ========================================
echo KET THUC
echo ========================================

pause
exit /b 0


REM ==============================
REM FUNCTION CHECK DRIVER
REM ==============================
:check_driver

set "DRIVER=%~1"

echo.
echo ----------------------------------------
echo DRIVER: %DRIVER%
echo ----------------------------------------

"%NAPS2%" --listdevices --driver "%DRIVER%"

set "RESULT=%ERRORLEVEL%"

if "%RESULT%"=="0" (
    echo [OK] %DRIVER% - NAPS2 chay thanh cong
) else (
    echo [ERROR] %DRIVER% - ERRORLEVEL = %RESULT%
)

exit /b