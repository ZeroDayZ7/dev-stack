@echo off
chcp 65001 > nul

:: Configuration
set FILE_PATH=C:\Users\Neo\Desktop\WWW\dev-stack\whisper\test\input_ru.wav
set WHISPER_URL=http://localhost:8001/api/transcribe?language=ru^&vad_filter=true
set OUTPUT_FILE=C:\Users\Neo\Desktop\WWW\dev-stack\whisper\test\response_ru.json

echo [INFO] Wysylanie pliku audio do Whisper STT (Rosyjski)...
echo [INFO] URL: %WHISPER_URL%
echo [INFO] Plik: %FILE_PATH%
echo --------------------------------------------------

curl -s -X POST "%WHISPER_URL%" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@%FILE_PATH%" > "%OUTPUT_FILE%"

echo [Wynik JSON z Whisper STT]:
type "%OUTPUT_FILE%"

echo.
echo.
echo --------------------------------------------------
echo [Sukces] Odpowiedz zapisana w %OUTPUT_FILE%
pause