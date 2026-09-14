import logging
import os
import tempfile
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

# Konfiguracja profesjonalnego loggera systemowego
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("whisper-stt-service")

MODEL_SIZE = os.getenv("WHISPER_MODEL", "medium")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float32")
CPU_THREADS = int(os.getenv("CTRANS_NUM_THREADS", "4"))

model: Optional[WhisperModel] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    logger.info(
        f"Loading Faster-Whisper model ({MODEL_SIZE}) on CPU (threads={CPU_THREADS}, compute_type={COMPUTE_TYPE})..."
    )
    try:
        model = WhisperModel(
            MODEL_SIZE,
            device="cpu",
            compute_type=COMPUTE_TYPE,
            cpu_threads=CPU_THREADS,
            # local_files_only=True,
        )
        logger.info("Model loaded successfully and ready for use.")
    except Exception as e:
        logger.warning(
            f"Failed to load with compute_type={COMPUTE_TYPE} ({e}). Retrying with float32 fallback..."
        )
        model = WhisperModel(
            MODEL_SIZE, device="cpu", compute_type="float32", cpu_threads=CPU_THREADS
        )
        logger.info("Model loaded successfully via float32 fallback.")

    yield
    logger.info("Shutting down Whisper STT service...")


app = FastAPI(
    title="CSOF Whisper STT Advanced Microservice",
    description="Wysoko wydajny, zaawansowany mikroserwis transkrypcji mowy (STT) offline dla platformy CSOF.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "service": "CSOF Whisper STT Microservice",
        "status": "online",
        "model": MODEL_SIZE,
    }


@app.get("/health")
async def health_check():
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": "Whisper model instance is not initialized",
            },
        )
    return {"status": "healthy", "model_size": MODEL_SIZE, "device": "cpu"}


def _execute_transcription(
    file_path: str,
    language: Optional[str],
    beam_size: int,
    temperature: float,
    vad_filter: bool,
    word_timestamps: bool,
):
    """Funkcja pomocnicza wykonująca ciężkie obliczenia CPU w osobnym wątku."""
    segments_raw, info = model.transcribe(
        file_path,
        language=language,
        beam_size=beam_size,
        temperature=temperature,
        vad_filter=vad_filter,
        word_timestamps=word_timestamps,
    )

    output_segments = []
    full_text_chunks = []

    for segment in segments_raw:
        full_text_chunks.append(segment.text)
        segment_data = {
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
        }

        if word_timestamps and segment.words:
            segment_data["words"] = [
                {
                    "word": w.word.strip(),
                    "start": round(w.start, 2),
                    "end": round(w.end, 2),
                    "probability": round(w.probability, 2),
                }
                for w in segment.words
            ]

        output_segments.append(segment_data)

    full_text = " ".join(full_text_chunks).strip()
    return full_text, info, output_segments


@app.post("/api/transcribe", response_class=JSONResponse)
async def transcribe_audio(
    file: UploadFile = File(
        ...,
        description="Plik audio w formacie wav, mp3, m4a, ogg, flac lub webm",
    ),
    language: Optional[str] = Query(
        default=None,
        description="Wymuszenie języka rozpoznawania (np. 'pl', 'ja').",
    ),
    beam_size: int = Query(
        default=5,
        ge=1,
        le=10,
        description="Rozmiar drzewa przeszukiwań (beam search).",
    ),
    temperature: float = Query(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Temperatura próbkowania.",
    ),
    vad_filter: bool = Query(
        default=True,
        description="Włączenie filtra VAD usuwającego ciszę.",
    ),
    word_timestamps: bool = Query(
        default=False,
        description="Zwracanie precyzyjnych znaczników czasowych dla słów.",
    ),
):
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model nie jest jeszcze gotowy.",
        )

    if not file.filename.lower().endswith(
        (".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niewłaściwy format pliku audio.",
        )

    temp_path = None
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        target_language = (
            None if (not language or language.lower() == "auto") else language
        )

        logger.info(
            f"Przetwarzanie STT: {file.filename} (Language: {target_language or 'AUTO'}, VAD: {vad_filter}, Beam: {beam_size})"
        )

        # Oddelegowanie ciężkiego zadania CPU do ThreadPoolExecutor, by nie blokować Event Loop
        full_text, info, output_segments = await run_in_threadpool(
            _execute_transcription,
            temp_path,
            target_language,
            beam_size,
            temperature,
            vad_filter,
            word_timestamps,
        )

        logger.info(f"Zakończono transkrypcję. Tekst: '{full_text}'")

        return JSONResponse(
            content={
                "text": full_text,
                "language": info.language,
                "language_probability": round(info.language_probability, 4),
                "duration": round(info.duration, 2),
                "segments": output_segments,
            }
        )

    except Exception as e:
        logger.error(f"Krytyczny błąd przetwarzania STT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Awaria przetwarzania sieci neuronowej: {str(e)}",
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as cleanup_err:
                logger.warning(
                    f"Nie udało się usunąć pliku tymczasowego: {cleanup_err}"
                )