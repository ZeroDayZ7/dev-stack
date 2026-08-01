@echo off
chcp 65001 > nul

:: Configuration
set WHISPER_URL=http://localhost:8001/api/transcribe
set FILE_PATH=C:\Users\Neo\Desktop\WWW\csof\csof_backend_v2\platform\services\ai-whisper-stt\src\test\speech.webm

echo [INFO] Wysyłanie pliku audio do Whisper STT...
echo [INFO] URL: %WHISPER_URL%
echo [INFO] Plik: %FILE_PATH%
echo --------------------------------------------------

curl -X POST "%WHISPER_URL%" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@%FILE_PATH%"

echo.
echo.
echo --------------------------------------------------
echo [Sukces] Żądanie zostało przetworzone.
pause