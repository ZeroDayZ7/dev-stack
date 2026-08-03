# 🎙️ Coqui XTTS v2 Microservice

Local TTS service with voice cloning powered by **Coqui XTTS v2** (`http://localhost:8020`).

---

## 📂 Directory Structure

Place your voice clone sample in the target language folder before running:

```text
xtts-tts/
└── test/
    └── ja/
        ├── sample.wav   <-- Your 3-5 sec voice sample
        └── speech.wav   <-- Generated output audio

```

---

## ⚡ Quick Start: Voice Cloning (`docker exec`)

```bat
@echo off
chcp 65001 > nul

set LOCAL_SAMPLE=%~dp0test\ja\sample.wav
set CONTAINER_SAMPLE=/app/output/ja/sample.wav
set CONTAINER_OUTPUT=/app/output/ja/speech.wav

if not exist "%LOCAL_SAMPLE%" (
    echo [ERROR] Voice sample missing at: %LOCAL_SAMPLE%
    pause & exit /b 1
)

echo [INFO] Running XTTS v2 synthesis...
docker exec -e CUDA_VISIBLE_DEVICES="" ai-coqui-tts tts ^
  --model_name "tts_models/multilingual/multi-dataset/xtts_v2" ^
  --text "ERPシステムは正常に動作しています。" ^
  --language_idx "ja" ^
  --speaker_wav "%CONTAINER_SAMPLE%" ^
  --out_path "%CONTAINER_OUTPUT%"

echo [SUCCESS] Audio generated at: %~dp0test\ja\speech.wav
pause

```

---

## 🌐 REST API (`POST /api/tts`)

```bash
curl -X POST "http://localhost:8020/api/tts" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"The ERP system is operating normally.\", \"language\": \"en\"}" \
  --output "speech.wav"

```