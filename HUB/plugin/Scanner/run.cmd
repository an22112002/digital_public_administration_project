@echo off

REM ==============================
REM CẤU HÌNH
REM ==============================

set "NAPS2=C:\Program Files\NAPS2\NAPS2.Console.exe"

set "DRIVER=escl"
set "DEVICE=Canon MF240 Series"

set "OUTPUT_FOLDER=F:\scan"


REM ==============================
REM HIỂN THỊ CONFIG
REM ==============================

echo ==============================
echo NAPS2 SCAN
echo ==============================
echo NAPS2   = %NAPS2%
echo DRIVER  = %DRIVER%
echo DEVICE  = %DEVICE%
echo OUTPUT  = %OUTPUT_FILE%
echo ==============================
echo.


REM ==============================
REM TẠO OUTPUT FOLDER
REM ==============================

if not exist "%OUTPUT_FOLDER%" (
    mkdir "%OUTPUT_FOLDER%"
)


REM ==============================
REM CHẠY NAPS2
REM ==============================

"%NAPS2%" ^
    --noprofile ^
    --driver "%DRIVER%" ^
    --device "%DEVICE%" ^
    --source duplex ^
    --bitdepth color ^
    --dpi 300 ^
    -o "%OUTPUT_FOLDER%\scan.pdf"


REM ==============================
REM LẤY RESULT
REM ==============================

set "RESULT=%ERRORLEVEL%"


echo.
echo ==============================
echo RESULT = %RESULT%
echo ==============================

if "%RESULT%"=="0" (
    echo Scan thanh cong.
) else (
    echo Scan that bai.
)

pause