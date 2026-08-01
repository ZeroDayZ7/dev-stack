FROM python:3.11-slim

WORKDIR /app

# Instalacja podstawowych systemowych zależności
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Instalacja Pipera bezpośrednio przez menedżer pakietów Pythona
RUN pip install --no-cache-dir piper-tts

# Kopiowanie zależności z lokalnego katalogu piper/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu źródłowego z lokalnego katalogu piper/src/
COPY src/ /app/src/

EXPOSE 8000

# Skrypt weryfikujący i pobierający modele (polski i japoński) na wolumen przy starcie
CMD ["sh", "-c", "\
    mkdir -p /models && \
    \
    # Pobieranie głosu polskiego (Gosia)
    if [ ! -f /models/pl_gosia.onnx ]; then \
        echo 'Downloading Polish TTS Model (Gosia)...' && \
        wget -O /models/pl_gosia.onnx 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx?download=true' && \
        wget -O /models/pl_gosia.onnx.json 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json?download=true'; \
    fi && \
    \
    # Pobieranie głosu japońskiego (Kanachan) - POPRAWIONY URL (ja zamiast jp)
    if [ ! -f /models/ja_kanachan.onnx ]; then \
        echo 'Downloading Japanese TTS Model (Kanachan)...' && \
        wget -O /models/ja_kanachan.onnx 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ja/ja_JP/kanachan/medium/ja_JP-kanachan-medium.onnx?download=true' && \
        wget -O /models/ja_kanachan.onnx.json 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ja/ja_JP/kanachan/medium/ja_JP-kanachan-medium.onnx.json?download=true'; \
    fi && \
    \
    echo 'All TTS models are ready.' && \
    uvicorn src.main:app --host 0.0.0.0 --port 8000"]