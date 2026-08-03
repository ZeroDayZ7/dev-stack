@echo off
chcp 65001 > nul

:: Configuration
set WHISPER_URL=http://localhost:8001/api/transcribe
set FILE_PATH=C:\Users\Neo\Desktop\WWW\dev-stack\xtts-tts\test\ja\speech.wav

echo [INFO] Wysyłanie pliku audio do Whisper STT...
echo [INFO] URL: %WHISPER_URL%
echo [INFO] Plik: %FILE_PATH%
echo --------------------------------------------------

curl -X POST "%WHISPER_URL%" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@%FILE_PATH%" ^
  -F "language=ja"

echo.
echo.
echo --------------------------------------------------
echo [Sukces] Żądanie zostało przetworzone.
pause