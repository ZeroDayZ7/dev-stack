import os
import asyncio
import logging
import tempfile
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Konfiguracja profesjonalnego loggera systemowego
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("piper-tts-service")

app = FastAPI(
    title="CSOF Piper TTS Advanced Microservice",
    description="Wysoko wydajny, lokalny mikrousługowy silnik syntezy mowy (TTS) offline dla platformy CSOF.",
    version="2.0.0"
)

class TTSRequest(BaseModel):
    text: str = Field(..., description="Tekst wejściowy do przetworzenia na mowę")
    model: str = Field(default="/models/pl_gosia.onnx", description="Ścieżka do pliku modelu .onnx")
    speaker_id: int | None = Field(default=None, description="ID prelegenta dla modeli wielogłosowych (multi-speaker)")
    speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Skala długości dźwięku (length_scale). Mniej niż 1.0 = szybciej, więcej = wolniej.")
    sentence_silence: float = Field(default=0.2, ge=0.0, le=5.0, description="Czas ciszy w sekundach po każdym zdaniu")
    noise_scale: float = Field(default=0.667, ge=0.0, le=2.0, description="Skala szumu (modulacja intonacji/ekspresji głosu)")
    noise_w: float = Field(default=0.8, ge=0.0, le=2.0, description="Szerokość szumu fonemów (płynność przejść między głoskami)")

#region remove_temp_file(path: str):
def remove_temp_file(path: str):
    """Bezpieczne usuwanie plików tymczasowych z logowaniem zdarzeń."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.debug(f"Pomyślnie usunięto plik tymczasowy: {path}")
    except Exception as e:
        logger.error(f"Błąd podczas czyszczenia pliku tymczasowego {path}: {str(e)}")

#region generate_wav_async(req: TTSRequest, output_path: str):
async def generate_wav_async(req: TTSRequest, output_path: str):
    """Asynchroniczne uruchomienie procesu Piper zapobiegające blokowaniu pętli zdarzeń FastAPI."""
    # Walidacja istnienia modelu przed uruchomieniem subprocesu
    if not os.path.exists(req.model):
        logger.error(f"Zażądano nieistniejącego modelu: {req.model}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model TTS nie został znaleziony w lokalizacji: {req.model}"
        )

    # Budowanie zaawansowanej listy argumentów CLI dla silnika Piper
    cmd = [
        "piper",
        "--model", req.model,
        "--output_file", output_path,
        "--length_scale", str(req.speed),
        "--sentence_silence", str(req.sentence_silence),
        "--noise_scale", str(req.noise_scale),
        "--noise_w", str(req.noise_w)
    ]

    # Dodaj ID speakera tylko jeśli zostało jawnie przekazane (dla modeli typu multi-speaker)
    if req.speaker_id is not None:
        cmd.extend(["--speaker", str(req.speaker_id)])

    logger.info(f"Rozpoczynanie generowania TTS dla tekstu o długości {len(req.text)} znaków...")
    
    try:
        # Uruchomienie nieblokującego procesu systemowego
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Przekazanie tekstu zakodowanego w UTF-8 bezpośrednio do stdin procesu
        stdout, stderr = await process.communicate(input=req.text.encode("utf-8"))

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore").strip()
            logger.error(f"Proces Piper zakończył się błędem (kod {process.returncode}): {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Błąd wewnętrzny silnika Piper: {error_msg}"
            )
            
        logger.info(f"Pomyślnie wygenerowano plik audio: {output_path}")

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Nieoczekiwana awaria podczas przetwarzania subprocesu TTS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Krytyczny błąd systemu operacyjnego: {str(e)}"
        )

#region @app.get("/health")
@app.get("/health")
async def health_check():
    model_exists = os.path.exists(DEFAULT_MODEL)
    if not model_exists:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": f"Default model not found at {DEFAULT_MODEL}"
            }
        )
    return {
        "status": "healthy",
        "model": DEFAULT_MODEL
    }

#region @app.post("/api/tts",
@app.post("/api/tts", response_class=FileResponse)
async def handle_tts(req: TTSRequest, background_tasks: BackgroundTasks):
    """
    Endpoint generujący strumień audio WAV na podstawie zaawansowanych parametrów wejściowych.
    Automatycznie czyści pliki tymczasowe po zakończeniu transferu do klienta.
    """
    # Tworzenie bezpiecznego deskryptora pliku tymczasowego
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    try:
        # Generowanie mowy
        await generate_wav_async(req, path)
        
        # Rejestracja zadania w tle – usunięcie pliku natychmiast po wysłaniu odpowiedzi do Go/CURL
        background_tasks.add_task(remove_temp_file, path)
        
        return FileResponse(
            path=path, 
            media_type="audio/wav", 
            filename="speech.wav"
        )
        
    except Exception:
        # W razie błędu przed wysłaniem odpowiedzi, natychmiast sprzątaj plik śmieciowy
        remove_temp_file(path)
        raise