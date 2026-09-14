import os
import requests

# --- KONFIGURACJA USŁUG ---
WHISPER_URL = "http://localhost:8001/api/transcribe"
OLLAMA_URL = "http://localhost:11434/api/generate"
XTTS_URL = "http://localhost:8002/api/tts"

# --- PLIKI WEJŚCIOWE / WYJŚCIOWE ---
INPUT_WAV = r"C:\Users\Neo\Desktop\WWW\dev-stack\whisper\test\input_ru.wav"
OUTPUT_PL_WAV = r"C:\Users\Neo\Desktop\WWW\dev-stack\whisper\test\output_pl.wav"
OLLAMA_MODEL = "qwen2.5"


def run_pipeline(wav_path: str, output_path: str) -> None:
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Plik wejściowy nie istnieje: {wav_path}")

    # 1. Transkrypcja STT (Whisper)
    print("[1/3] Wysyłanie audio do Whisper STT...")
    with open(wav_path, "rb") as f:
        file_bytes = f.read()  # Bezpieczne załadowanie bajtów w pamięci

    res = requests.post(
        WHISPER_URL,
        files={"file": (os.path.basename(wav_path), file_bytes, "audio/wav")},
        params={"language": "ru", "vad_filter": True},
        timeout=300  # Extended timeout for CPU inference
    )
    res.raise_for_status()
    text_ru = res.json().get("text", "").strip()

    print(f" -> Tekst RU: {text_ru}\n")
    if not text_ru:
        print("Brak mowy w pliku audio. Przerywam.")
        return

    # 2. Tłumaczenie RU -> PL (Ollama)
    print("[2/3] Tłumaczenie tekstu na polski (Ollama)...")
    prompt = (
        "Jesteś profesjonalnym tłumaczem. Przetłumacz poniższy tekst z języka rosyjskiego "
        "na język polski. Zwróć WYŁĄCZNIE samo tłumaczenie, bez wstępów, komentarzy i cudzysłowów.\n\n"
        f"Tekst: {text_ru}"
    )

    res = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    res.raise_for_status()
    text_pl = res.json().get("response", "").strip()

    print(f" -> Tekst PL: {text_pl}\n")

    # 3. Lektor PL + Klonowanie głosu (XTTS v2)
    print("[3/3] Generowanie syntezy mowy PL (XTTS v2)...")
    res = requests.post(
        XTTS_URL,
        data={"text": text_pl, "language": "pl"},
        files={"speaker_wav": (os.path.basename(wav_path), file_bytes, "audio/wav")},
        timeout=300
    )
    res.raise_for_status()

    with open(output_path, "wb") as f_out:
        f_out.write(res.content)

    print(f"[SUKCES] Wygenerowano polskiego lektora: {output_path}")


if __name__ == "__main__":
    run_pipeline(INPUT_WAV, OUTPUT_PL_WAV)