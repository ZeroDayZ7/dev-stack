@echo off
chcp 65001 > nul

:: Local target directory inside xtts-tts folder
set TARGET_DIR=%~dp0test\ja

:: Create target directory if it does not exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [INFO] Generating audio via XTTS v2...

:: Generate Japanese Audio Test File
curl -X POST "http://localhost:8020/api/tts" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"ERPシステムは正常に動作しています。音声合成テストが成功しました。\", \"language\": \"ja\"}" ^
  --output "%TARGET_DIR%\test_xtts.wav"

echo.
echo [SUCCESS] Audio file saved to: %TARGET_DIR%\test_xtts.wav
pause