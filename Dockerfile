FROM python:3.11-slim

# tesseract-ocr: needed only for the scanned-document OCR fallback path
# (pytesseract is a wrapper around this binary, not a pure-Python OCR engine)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

COPY . .

RUN mkdir -p app/storage/uploads app/storage/processed app/storage/chroma_db

# Most hosts (Render, Railway, Fly.io) inject $PORT at runtime; default to 8000 locally.
ENV PORT=8000
EXPOSE 8000

# No --reload in production, and a single shell form so $PORT expands correctly.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}