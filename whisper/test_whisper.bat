@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ============================================================
:: Whisper STT - automatyczne generowanie SRT
:: ============================================================

set "TEST_DIR=%~dp0test"
set "WHISPER_URL=http://localhost:8001/api/transcribe?language=ru&vad_filter=true&word_timestamps=false"

echo.
echo ============================================================
echo             WHISPER STT - AUDIO TO SRT
echo ============================================================
echo.

:: ------------------------------------------------------------
:: Znajdz pierwszy plik audio
:: ------------------------------------------------------------

set "INPUT_FILE="

for %%F in ("%TEST_DIR%\*.wav" "%TEST_DIR%\*.mp3" "%TEST_DIR%\*.m4a" "%TEST_DIR%\*.flac" "%TEST_DIR%\*.ogg" "%TEST_DIR%\*.webm") do (
    if exist "%%~F" (
        set "INPUT_FILE=%%~F"
        goto :file_found
    )
)

echo [ERROR] Nie znaleziono pliku audio w:
echo %TEST_DIR%
echo.
echo Obslugiwane: WAV, MP3, M4A, FLAC, OGG, WEBM
pause
exit /b 1

:file_found

echo [INFO] Plik:
echo        %INPUT_FILE%
echo.

:: ------------------------------------------------------------
:: Nazwa wyjsciowa
:: ------------------------------------------------------------

for %%F in ("%INPUT_FILE%") do (
    set "BASENAME=%%~nF"
)

set "JSON_FILE=%TEST_DIR%\!BASENAME!.json"
set "SRT_FILE=%TEST_DIR%\!BASENAME!.srt"

echo [INFO] JSON:
echo        !JSON_FILE!
echo.
echo [INFO] SRT:
echo        !SRT_FILE!
echo.

:: ------------------------------------------------------------
:: Whisper API
:: ------------------------------------------------------------

echo [INFO] Wysylanie do Whisper...
echo ------------------------------------------------------------

curl -s -f -X POST "%WHISPER_URL%" ^
  -H "accept: application/json" ^
  -F "file=@%INPUT_FILE%" ^
  > "!JSON_FILE!"

if errorlevel 1 (
    echo.
    echo [ERROR] Whisper API zwrocilo blad.
    del "!JSON_FILE!" > nul 2>&1
    pause
    exit /b 1
)

echo [OK] Transkrypcja zakonczona.
echo.

:: ------------------------------------------------------------
:: JSON -> SRT
:: ------------------------------------------------------------

echo [INFO] Generowanie SRT...

python "%~dp0process_video.py" "!JSON_FILE!" "!SRT_FILE!"

if errorlevel 1 (
    echo.
    echo [ERROR] Nie udalo sie wygenerowac SRT.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [OK] GOTOWE
echo ============================================================
echo.
echo Audio:
echo   %INPUT_FILE%
echo.
echo SRT:
echo   !SRT_FILE!
echo.
echo JSON:
echo   !JSON_FILE!
echo.

pause