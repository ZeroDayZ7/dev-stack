import os
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

# Konfiguracja profesjonalnego loggera systemowego
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("whisper-stt-service")

app = FastAPI(
    title="CSOF Whisper STT Advanced Microservice",
    description="Wysoko wydajny, zaawansowany mikroserwis transkrypcji mowy (STT) offline dla platformy CSOF.",
    version="2.0.0"
)

# Initializing the model on CPU optimized for older CPUs (AMD FX-8350 / AVX1)
MODEL_SIZE = os.getenv("WHISPER_MODEL", "medium")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float32")
CPU_THREADS = int(os.getenv("CTRANS_NUM_THREADS", "4"))

logger.info(f"Loading Faster-Whisper model ({MODEL_SIZE}) on CPU (threads={CPU_THREADS}, compute_type={COMPUTE_TYPE})...")

try:
    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type=COMPUTE_TYPE,
        cpu_threads=CPU_THREADS
    )
    logger.info("Model loaded successfully and ready for use.")
except Exception as e:
    logger.warning(f"Failed to load with compute_type={COMPUTE_TYPE} ({e}). Retrying with float32 fallback...")
    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="float32",
        cpu_threads=CPU_THREADS
    )
    logger.info("Model loaded successfully via float32 fallback.")

#region @app.get("/health")
@app.get("/health")
async def health_check():
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": "Whisper model instance is not initialized"
            }
        )
    return {
        "status": "healthy",
        "model_size": MODEL_SIZE,
        "device": "cpu"
    }

#region @app.post("/api/transcribe",
@app.post("/api/transcribe", response_class=JSONResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Plik audio w formacie wav, mp3, m4a, ogg lub flac"),
    language: str | None = Query(default=None, description="Wymuszenie języka rozpoznawania (np. 'pl', 'ja'). Pozostaw brak/None dla autodetekcji."),
    beam_size: int = Query(default=5, ge=1, le=10, description="Rozmiar drzewa przeszukiwań (beam search). Większy = dokładniejszy, ale wolniejszy."),
    temperature: float = Query(default=0.0, ge=0.0, le=1.0, description="Temperatura próbkowania. 0.0 oznacza maksymalną powtarzalność i stabilność."),
    vad_filter: bool = Query(default=True, description="Włączenie filtra VAD (Voice Activity Detection) usuwającego ciszę i szum przed transkrypcją."),
    word_timestamps: bool = Query(default=False, description="Zwracanie precyzyjnych znaczników czasowych dla każdego pojedynczego słowa.")
):
    """
    Zaawansowany endpoint zamiany mowy na tekst (STT).
    Obsługuje filtrowanie szumów (VAD), dostrajanie precyzji algorytmu oraz opcjonalne tokeny czasowe.
    """
    # Podstawowa walidacja formatu pliku
    if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niewłaściwy format pliku audio. Akceptowane formaty: wav, mp3, m4a, ogg, flac, webm"
        )

    # Zapis strumienia do pliku tymczasowego
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        try:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        except Exception as e:
            logger.error(f"Błąd zapisu pliku tymczasowego: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Błąd wewnętrzny systemu dyskowego kontenera."
            )

    try:
        target_language = None if (not language or language.lower() == "auto") else language

        logger.info(f"Przetwarzanie STT: {file.filename} (Language: {target_language or 'AUTO'}, VAD: {vad_filter}, Beam: {beam_size}, Temp: {temperature})")
        
        # Wywołanie silnika z kompletem zaawansowanych parametrów
        segments, info = model.transcribe(
            temp_path,
            language=target_language,
            beam_size=beam_size,
            temperature=temperature,
            vad_filter=vad_filter,
            word_timestamps=word_timestamps
        )
        
        # Budowanie struktury odpowiedzi
        output_segments = []
        full_text_chunks = []
        
        for segment in segments:
            full_text_chunks.append(segment.text)
            
            segment_data = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            }
            
            # Jeśli włączono word_timestamps, dołącz szczegółowe dane słów
            if word_timestamps and segment.words:
                segment_data["words"] = [
                    {"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2), "probability": round(w.probability, 2)}
                    for w in segment.words
                ]
                
            output_segments.append(segment_data)
            
        full_text = " ".join(full_text_chunks).strip()
        logger.info(f"Zakończono transkrypcję. Tekst: '{full_text}'")
        
        return JSONResponse(content={
            "text": full_text,
            "language": info.language,
            "language_probability": round(info.language_probability, 4),
            "duration": round(info.duration, 2),
            "segments": output_segments
        })

    except Exception as e:
        logger.error(f"Krytyczny błąd silnika Faster-Whisper: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Awaria przetwarzania sieci neuronowej: {str(e)}"
        )
        
    finally:
        # Bezwarunkowe czyszczenie dysku kontenera
        if os.path.exists(temp_path):
            os.remove(temp_path)