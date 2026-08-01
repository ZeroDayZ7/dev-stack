@echo off
chcp 65001 > nul

set TARGET_DIR=C:\Users\Neo\Desktop\WWW\dev-stack\piper\test\ja

:: Create target directory if it does not exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [INFO] Generating Japanese audio test file...

:: Japanese TTS Test File
curl -X POST "http://localhost:8000/api/tts" ^
  -H "Content-Type: application/json; charset=utf-8" ^
  -d "{\"text\": \"ERPシステムは正常に動作しています。音声合成テストが成功しました。\", \"lang\": \"ja\", \"speed\": 0.85, \"sentence_silence\": 0.75}" ^
  --output "%TARGET_DIR%\test.wav"

echo.
echo [SUCCESS] Japanese audio file saved to %TARGET_DIR%\test.wav
pause