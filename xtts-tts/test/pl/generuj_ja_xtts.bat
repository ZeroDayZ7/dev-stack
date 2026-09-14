@echo off
chcp 65001 > nul

:: ==============================================================================
:: PARAMETRY SYNTEZY XTTS v2 (Odkomentuj/edytuj flagi w sekcji CLI poniżej)
:: ==============================================================================
:: --speed 1.0           - Predkosc mowy (np. 0.85 = wolniej, 1.0 = domyslne, 1.15 = szybciej)
:: --temperature 0.75    - Losowosc/emocjonalnosc (zostaw w srodku 0.65 - 0.85; wyzsze = bardziej zmienna intonacja, nizsze = monotoniczny/stabilny glos)
:: --length_penalty 1.0  - Kara za dlugosc fraz (wplywa na tempo i pauzy miedzy zdaniami)
:: --repetition_penalty 2.0 - Zapobiega zapetlaniu sie slów lub przerysowanym pauzom
:: --top_k 50            - Ograniczenie probkowania k-najbardziej prawdopodobnych tokenow
:: --top_p 0.85          - Probkowanie nucleus (kontrola naturalnosci i stabilnosci artykulacji)
:: --enable_text_splitting - Automatyczne rozbijanie dlugich zdan na krotsze frazy
:: ==============================================================================

:: Ustawienie sciezek lokalnych (skrypt lezy w tym samym folderze co sample.wav i input.txt)
set "LOCAL_SAMPLE=%~dp0sample.wav"
set "LOCAL_TEXT=%~dp0input.txt"
set "LOCAL_OUTPUT=%~dp0speech.wav"

:: Sciezki wewnatrz kontenera Docker
set "CONTAINER_SAMPLE=/app/output/pl/sample.wav"
set "CONTAINER_TEXT=/app/output/pl/input.txt"
set "CONTAINER_OUTPUT=/app/output/pl/speech.wav"

:: Walidacja pliku probki
if not exist "%LOCAL_SAMPLE%" (
    echo [ERROR] Brak pliku probki glosu!
    echo Szukana sciezka: %LOCAL_SAMPLE%
    pause
    exit /b 1
)

:: Walidacja pliku tekstowego
if not exist "%LOCAL_TEXT%" (
    echo [ERROR] Brak pliku input.txt!
    echo Szukana sciezka: %LOCAL_TEXT%
    pause
    exit /b 1
)

echo [INFO] Pliki znalezione. Uruchamianie syntezy XTTS v2...

:: Wykonanie syntezy w Dockerze z opcjonalnymi parametrami (odkomentowane domyslne + przyklady zakomentowane)
docker exec -i -e CUDA_VISIBLE_DEVICES="" ai-coqui-tts bash -c "tts --model_name \"tts_models/multilingual/multi-dataset/xtts_v2\" --text \"$(cat %CONTAINER_TEXT%)\" --language_idx \"pl\" --speaker_wav \"%CONTAINER_SAMPLE%\" --out_path \"%CONTAINER_OUTPUT%\" --enable_text_splitting"

:: PRZYKLAD Z PEŁNYM ZESTAWEM PARAMETROW DO TESTOWANIA (zastap powyzsza komende, jesli chcesz testowac konkretne wartosci):
:: docker exec -i -e CUDA_VISIBLE_DEVICES="" ai-coqui-tts bash -c "tts --model_name \"tts_models/multilingual/multi-dataset/xtts_v2\" --text \"$(cat %CONTAINER_TEXT%)\" --language_idx \"pl\" --speaker_wav \"%CONTAINER_SAMPLE%\" --out_path \"%CONTAINER_OUTPUT%\" --speed 1.05 --temperature 0.75 --length_penalty 1.0 --repetition_penalty 2.0 --top_k 50 --top_p 0.85 --enable_text_splitting"

echo.
if exist "%LOCAL_OUTPUT%" (
    echo [SUCCESS] Wygenerowano plik: %LOCAL_OUTPUT%
) else (
    echo [ERROR] Wystapil problem podczas generowania audio.
)

pause