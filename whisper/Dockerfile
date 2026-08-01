# ==========================================================
# Etap 1: Budowanie i instalacja zależności (Builder)
# ==========================================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --user fastapi uvicorn faster-whisper python-multipart

# ==========================================================
# Etap 2: Finalny obraz produkcyjny (Runtime)
# ==========================================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

# Kopiujemy cały folder src do /app/src
COPY src/ /app/src/

EXPOSE 8000

# Uruchomienie z uwzględnieniem folderu src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]