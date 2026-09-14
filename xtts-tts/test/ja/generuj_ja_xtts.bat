@echo off
chcp 65001 > nul

set LOCAL_DIR=%~dp0test\pl
set LOCAL_SAMPLE=%LOCAL_DIR%\sample.wav
set LOCAL_TEXT=%LOCAL_DIR%\input.txt

set CONTAINER_SAMPLE=/app/output/pl/sample.wav
set CONTAINER_TEXT=/app/output/pl/input.txt
set CONTAINER_OUTPUT=/app/output/pl/speech.wav

if not exist "%LOCAL_SAMPLE%" (
    echo [ERROR] Brak pliku probki glosu! (%LOCAL_SAMPLE%)
    pause
    exit /b 1
)

if not exist "%LOCAL_TEXT%" (
    echo [ERROR] Brak pliku tekstowego! (%LOCAL_TEXT%)
    pause
    exit /b 1
)

echo [INFO] Pliki znalezione. Uruchamianie syntezy XTTS v2...

:: Odczytujemy zawartosc pliku input.txt i przekazujemy bezpośrednio do tts
docker exec -i -e CUDA_VISIBLE_DEVICES="" ai-coqui-tts bash -c "tts --model_name \"tts_models/multilingual/multi-dataset/xtts_v2\" --text \"$(cat %CONTAINER_TEXT%)\" --language_idx \"pl\" --speaker_wav \"%CONTAINER_SAMPLE%\" --out_path \"%CONTAINER_OUTPUT%\""

echo.
if exist "%LOCAL_DIR%\speech.wav" (
    echo [SUCCESS] Wygenerowano plik: %LOCAL_DIR%\speech.wav
) else (
    echo [ERROR] Wystapil problem podczas generowania audio.
)

pause