@echo off
chcp 65001 > nul

set LOCAL_SAMPLE=%~dp0test\ja\sample.wav
set CONTAINER_SAMPLE=/app/output/ja/sample.wav
set CONTAINER_OUTPUT=/app/output/ja/speech.wav

if not exist "%LOCAL_SAMPLE%" (
    echo [ERROR] Brak pliku probki glosu!
    echo Szukana sciezka: %LOCAL_SAMPLE%
    pause
    exit /b 1
)

echo [INFO] Plik probki znaleziony. Uruchamianie syntezy XTTS v2...

docker exec -e CUDA_VISIBLE_DEVICES="" ai-coqui-tts tts ^
  --model_name "tts_models/multilingual/multi-dataset/xtts_v2" ^
  --text "ERPシステムは正常に動作しています。" ^
  --language_idx "ja" ^
  --speaker_wav "%CONTAINER_SAMPLE%" ^
  --out_path "%CONTAINER_OUTPUT%"

echo.
if exist "%~dp0test\ja\speech.wav" (
    echo [SUCCESS] Wygenerowano plik: %~dp0test\ja\speech.wav
) else (
    echo [ERROR] Wystapil problem podczas generowania audio.
)

pause