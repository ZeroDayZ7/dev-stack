# ==========================================================
# Etap 1: Budowanie i instalacja zależności (Builder)
# ==========================================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --user \
    fastapi \
    uvicorn \
    faster-whisper \
    python-multipart

# ==========================================================
# Etap 2: Finalny obraz produkcyjny (Runtime)
# ==========================================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app

WORKDIR /app

# Wymagane libgomp1 dla OpenMP/CTranslate2 oraz ffmpeg dla dekodowania audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

COPY src/ /app/src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]