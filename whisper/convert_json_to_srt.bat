@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ============================================================
:: Konwersja istniejącego JSON do SRT (Bez wywoływania Whisper)
:: ============================================================

set "JSON_FILE=%~dp0test\audio.json"
set "SRT_FILE=%~dp0test\audio.srt"
set "PYTHON_SCRIPT=%~dp0process_video.py"

echo.
echo ============================================================
echo             CONVERT JSON TO SRT (OFFLINE)
echo ============================================================
echo.

if not exist "%JSON_FILE%" (
    echo [ERROR] Nie znaleziono pliku JSON: %JSON_FILE%
    echo.
    pause
    exit /b 1
)

if not exist "%PYTHON_SCRIPT%" (
    echo [ERROR] Nie znaleziono skryptu Python: %PYTHON_SCRIPT%
    echo.
    pause
    exit /b 1
)

echo [INFO] Wskazany JSON: %JSON_FILE%
echo [INFO] Wynikowy SRT:  %SRT_FILE%
echo.
echo [INFO] Generowanie napisow...

python "%PYTHON_SCRIPT%" "%JSON_FILE%" "%SRT_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] Wystąpił błąd podczas generowania pliku SRT.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [OK] GOTOWE! Plik SRT zostal utworzony:
echo      %SRT_FILE%
echo ============================================================
echo.

pause