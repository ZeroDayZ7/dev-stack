@echo off
chcp 65001 > nul

set TARGET_DIR=C:\Users\Neo\Desktop\WWW\dev-stack\piper\test\pl

:: Create target directory if it does not exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [INFO] Generating Polish audio test file...

:: Polish TTS Test File
curl -X POST "http://localhost:8000/api/tts" ^
  -H "Content-Type: application/json; charset=utf-8" ^
  -d "{\"text\": \"System ERP działa poprawnie. Test syntezy mowy zakończony sukcesem.\", \"lang\": \"pl\", \"speed\": 0.85, \"sentence_silence\": 0.75}" ^
  --output "%TARGET_DIR%\test.wav"

echo.
echo [SUCCESS] Polish audio file saved to %TARGET_DIR%\test.wav
pause