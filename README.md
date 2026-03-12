# VPS OCR & Whisper — Docker Compose

Two self-hosted AI services running **CPU-only** on a Hostinger KVM4 VPS (4 vCPU / 16 GB RAM).

| Service | Port | Image |
|---|---|---|
| PaddleOCR | `8000` | Built from `./paddleocr` |
| Whisper | `9000` | `onerahmet/openai-whisper-asr-webservice:latest-cpu` |

---

## Deploy on Hostinger VPS

```bash
# 1. SSH into your VPS
ssh root@<YOUR_VPS_IP>

# 2. Clone this repo
git clone https://github.com/<YOUR_USERNAME>/vps-ocr-whisper.git
cd vps-ocr-whisper

# 3. Build & start (first run takes ~5-10 min — models are downloaded)
docker compose up -d --build

# 4. Check logs
docker compose logs -f
```

> The `--build` flag is only needed the first time (or after a code change).

---

## PaddleOCR API — port 8000

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### POST /ocr — Extract text from an image

**Request** — multipart/form-data, field `file` (JPG, PNG, BMP, TIFF, WEBP)

```bash
curl -X POST http://localhost:8000/ocr \
  -F "file=@business_card.jpg"
```

**Response**

```json
{
  "text": "John Doe\nSenior Engineer\njohn@example.com\n+33 6 00 00 00 00",
  "lines": [
    { "text": "John Doe",            "confidence": 0.9981 },
    { "text": "Senior Engineer",     "confidence": 0.9874 },
    { "text": "john@example.com",    "confidence": 0.9763 },
    { "text": "+33 6 00 00 00 00",   "confidence": 0.9910 }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `text` | string | Full extracted text, lines joined with `\n` |
| `lines` | array | Each detected line with its confidence score (0–1) |

**Python example**

```python
import requests

with open("business_card.jpg", "rb") as f:
    r = requests.post("http://localhost:8000/ocr", files={"file": f})

print(r.json()["text"])
```

---

## Whisper API — port 9000

Interactive Swagger UI available at `http://localhost:9000/docs`.

### POST /asr — Transcribe an audio file

**Query parameters**

| Param | Default | Description |
|---|---|---|
| `task` | `transcribe` | `transcribe` or `translate` (→ English) |
| `language` | auto-detect | ISO 639-1 code, e.g. `fr`, `en`, `es` |
| `output` | `txt` | `txt`, `json`, `srt`, `tsv`, `vtt` |

**Request** — multipart/form-data, field `audio_file`

```bash
curl -X POST "http://localhost:9000/asr?task=transcribe&language=fr&output=txt" \
  -H "accept: application/json" \
  -F "audio_file=@note_vocale.mp3"
```

**Response** (output=txt)

```
Bonjour, voici ma note vocale du jour. N'oublie pas la réunion à 14h.
```

**Response** (output=json)

```json
{
  "text": "Bonjour, voici ma note vocale du jour...",
  "segments": [ { "start": 0.0, "end": 3.2, "text": "Bonjour..." } ],
  "language": "fr"
}
```

**Python example**

```python
import requests

with open("note_vocale.mp3", "rb") as f:
    r = requests.post(
        "http://localhost:9000/asr",
        params={"task": "transcribe", "language": "fr", "output": "json"},
        files={"audio_file": f},
    )

print(r.json()["text"])
```

Supported audio formats: MP3, WAV, M4A, OGG, FLAC, AAC, WEBM.

---

## Resource usage (approximate)

| Service | RAM | CPU (idle) | CPU (inference) |
|---|---|---|---|
| PaddleOCR | ~1.5 GB | < 1% | 1–2 cores |
| Whisper small | ~1 GB | < 1% | 2–3 cores |

---

## Useful commands

```bash
# Stop all services
docker compose down

# View real-time logs for one service
docker compose logs -f paddleocr
docker compose logs -f whisper

# Restart a single service
docker compose restart paddleocr

# Update Whisper image
docker compose pull whisper && docker compose up -d whisper
```
