FROM python:3.11-slim

# tesseract-ocr system package is required for pytesseract (Phase 1 OCR).
# Comment out if you're running in dev/demo mode with requirements-dev.txt only.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

COPY requirements.txt requirements-dev.txt ./
# Use requirements-dev.txt for a fast build without the ML stack, or
# requirements.txt for the full Phase 1-5 pipeline.
ARG REQUIREMENTS_FILE=requirements-dev.txt
RUN pip install --no-cache-dir -r ${REQUIREMENTS_FILE}

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
