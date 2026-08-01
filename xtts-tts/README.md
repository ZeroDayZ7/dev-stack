# 🎙️ Coqui XTTS v2 Microservice

A local microservice for high-quality multilingual Text-to-Speech (TTS) synthesis powered by the **Coqui XTTS v2** model.

---

## 🌍 Supported Languages (`language`)

The XTTS v2 model natively supports **17 languages** within the same container. Simply provide the appropriate language code in the `"language"` parameter:

| Code | Language | Code | Language |
| :--- | :--- | :--- | :--- |
| `ja` | Japanese | `pl` | Polish |
| `en` | English | `de` | German |
| `es` | Spanish | `fr` | French |
| `it` | Italian | `pt` | Portuguese |
| `zh` | Chinese | `ko` | Korean |
| `ru` | Russian | `nl` | Dutch |
| `tr` | Turkish | `ar` | Arabic |
| `cs` | Czech | `hu` | Hungarian |

---

## 🛠️ How to Change Language in a `.bat` Script?

To generate speech in a different language, modify **three key values** in your script file:
1. The target output subdirectory (e.g., `test\pl` instead of `test\ja`).
2. The language code in the `"language"` parameter (e.g., `"pl"`).
3. The input text itself in the selected language.

---

## 📋 Sample Test Scripts

### 1. Japanese (`generuj_ja_xtts.bat`)
```bat
@echo off
chcp 65001 > nul

:: Local target directory inside xtts-tts folder
set TARGET_DIR=%~dp0test\ja

:: Create target directory if it does not exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [INFO] Generating Japanese audio via XTTS v2...

:: Generate Japanese Audio Test File
curl -X POST "http://localhost:8020/api/tts" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"ERPシステムは正常に動作しています。音声合成テストが成功しました。\", \"language\": \"ja\"}" ^
  --output "%TARGET_DIR%\test_xtts.wav"

echo.
echo [SUCCESS] Audio file saved to: %TARGET_DIR%\test_xtts.wav
pause

```

### 2. English (`generuj_en_xtts.bat`)

```bat
@echo off
chcp 65001 > nul

:: Local target directory inside xtts-tts folder
set TARGET_DIR=%~dp0test\en

:: Create target directory if it does not exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [INFO] Generating English audio via XTTS v2...

:: Generate English Audio Test File
curl -X POST "http://localhost:8020/api/tts" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"The ERP system is working correctly. Speech synthesis test completed successfully.\", \"language\": \"en\"}" ^
  --output "%TARGET_DIR%\test_en.wav"

echo.
echo [SUCCESS] Audio file saved to: %TARGET_DIR%\test_en.wav
pause

```

### 3. Polish (`generuj_pl_xtts.bat`)

```bat
@echo off
chcp 65001 > nul

:: Local target directory inside xtts-tts folder
set TARGET_DIR=%~dp0test\pl

:: Create target directory if it does not exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [INFO] Generating Polish audio via XTTS v2...

:: Generate Polish Audio Test File
curl -X POST "http://localhost:8020/api/tts" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"System ERP działa poprawnie. Test syntezy mowy zakończony sukcesem.\", \"language\": \"pl\"}" ^
  --output "%TARGET_DIR%\test_pl.wav"

echo.
echo [SUCCESS] Audio file saved to: %TARGET_DIR%\test_pl.wav
pause

```

---

## ⚙️ API Reference

* **Base URL:** `http://localhost:8020`
* **Endpoint:** `POST /api/tts`
* **Headers:** `Content-Type: application/json`
* **Request Payload:**
```json
{
  "text": "Your text goes here",
  "language": "language_code"
}

```
