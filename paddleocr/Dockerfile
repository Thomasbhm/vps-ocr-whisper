FROM python:3.10-slim

WORKDIR /app

# System deps for OpenCV / image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender1 libgomp1 \
    libgl1 wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PaddlePaddle first, then the rest
RUN pip install --no-cache-dir paddlepaddle==2.6.1 \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Pre-download OCR models so the first request isn't slow
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)"

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
