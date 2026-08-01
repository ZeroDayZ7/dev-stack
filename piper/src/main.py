#region Imports
import os
import asyncio
import logging
import tempfile
from typing import Dict
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
#endregion

#region Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("piper-tts-service")
#endregion

#region FastAPI Initialization
app = FastAPI(
    title="CSOF Piper TTS Advanced Microservice",
    description="Wysoko wydajny, lokalny mikrousługowy silnik syntezy mowy (TTS) offline dla platformy CSOF.",
    version="2.0.0"
)
#endregion

#region Models & Constants Config
# Rejestr dostępnych modeli. Aby dodać nowy język, po prostu dodaj go do tego słownika:
SUPPORTED_MODELS: Dict[str, str] = {
    "pl": "/models/pl_gosia.onnx",
    "ja": "/models/ja_kanachan.onnx",
    # "en": "/models/en_lessac.onnx",  <-- przykład jak dodać kolejny język
}

DEFAULT_LANG = "pl"
DEFAULT_MODEL_PATH = SUPPORTED_MODELS[DEFAULT_LANG]
#endregion

#region Data Transfer Objects (Pydantic Models)
class TTSRequest(BaseModel):
    text: str = Field(..., description="Tekst wejściowy do przetworzenia na mowę")
    lang: str | None = Field(default=DEFAULT_LANG, description="Kod języka (np. 'pl', 'ja') zdefiniowany w SUPPORTED_MODELS")
    model: str | None = Field(default=None, description="Opcjonalna, bezpośrednia ścieżka do pliku .onnx (nadpisuje parametr lang)")
    speaker_id: int | None = Field(default=None, description="ID prelegenta dla modeli wielogłosowych (multi-speaker)")
    speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Skala długości dźwięku (length_scale). Mniej niż 1.0 = szybciej, więcej = wolniej.")
    sentence_silence: float = Field(default=0.2, ge=0.0, le=5.0, description="Czas ciszy w sekundach po każdym zdaniu")
    noise_scale: float = Field(default=0.667, ge=0.0, le=2.0, description="Skala szumu (modulacja intonacji/ekspresji głosu)")
    noise_w: float = Field(default=0.8, ge=0.0, le=2.0, description="Szerokość szumu fonemów (płynność przejść między głoskami)")
#endregion

#region Helper Functions
def remove_temp_file(path: str):
    """Bezpieczne usuwanie plików tymczasowych z logowaniem zdarzeń."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.debug(f"Pomyślnie usunięto plik tymczasowy: {path}")
    except Exception as e:
        logger.error(f"Błąd podczas czyszczenia pliku tymczasowego {path}: {str(e)}")
#endregion

#region Core Async TTS Logic
async def generate_wav_async(req: TTSRequest, output_path: str):
    """Asynchroniczne uruchomienie procesu Piper zapobiegające blokowaniu pętli zdarzeń FastAPI."""
    
    # Rozpoznawanie ścieżki do modelu:
    # 1. Priorytet ma podana bezpośrednia ścieżka w `req.model`
    # 2. Następnie szukamy modelu po podanym kodzie `req.lang` w słowniku SUPPORTED_MODELS
    # 3. Jeśli język jest nieznany, używamy domyślnego pliku DEFAULT_MODEL_PATH
    if req.model:
        target_model = req.model
    else:
        target_model = SUPPORTED_MODELS.get(req.lang.lower() if req.lang else DEFAULT_LANG, DEFAULT_MODEL_PATH)

    # Walidacja istnienia modelu przed uruchomieniem subprocesu
    if not os.path.exists(target_model):
        logger.error(f"Zażądano nieistniejącego modelu: {target_model}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model TTS nie został znaleziony w lokalizacji: {target_model}"
        )

    # Budowanie zaawansowanej listy argumentów CLI dla silnika Piper
    cmd = [
        "piper",
        "--model", target_model,
        "--output_file", output_path,
        "--length_scale", str(req.speed),
        "--sentence_silence", str(req.sentence_silence),
        "--noise_scale", str(req.noise_scale),
        "--noise_w", str(req.noise_w)
    ]

    # Dodaj ID speakera tylko jeśli zostało jawnie przekazane (dla modeli typu multi-speaker)
    if req.speaker_id is not None:
        cmd.extend(["--speaker", str(req.speaker_id)])

    logger.info(f"Rozpoczynanie generowania TTS dla języka '{req.lang}' [Model: {target_model}]...")
    
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
#endregion

#region API Endpoints
@app.get("/health")
async def health_check():
    """Sprawdzenie stanu aplikacji oraz weryfikacja obecności domyślnego modelu."""
    model_exists = os.path.exists(DEFAULT_MODEL_PATH)
    if not model_exists:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": f"Default model not found at {DEFAULT_MODEL_PATH}"
            }
        )
    return {
        "status": "healthy",
        "default_model": DEFAULT_MODEL_PATH,
        "available_languages": list(SUPPORTED_MODELS.keys())
    }

@app.post("/api/tts", response_class=FileResponse)
async def handle_tts(req: TTSRequest, background_tasks: BackgroundTasks):
    """
    Endpoint generujący strumień audio WAV na podstawie parametrów wejściowych.
    Automatycznie czyści pliki tymczasowe po zakończeniu transferu do klienta.
    """
    # Tworzenie bezpiecznego deskryptora pliku tymczasowego
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    try:
        # Generowanie mowy
        await generate_wav_async(req, path)
        
        # Rejestracja zadania w tle – usunięcie pliku natychmiast po wysłaniu odpowiedzi
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
#endregion