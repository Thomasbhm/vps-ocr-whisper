import os
import tempfile

import easyocr
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI(title="OCR API", version="1.0.0")

# Models are downloaded to /root/.EasyOCR (persisted via Docker volume)
reader = easyocr.Reader(["en", "fr"], gpu=False)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    """
    Upload an image (JPG, PNG, BMP…) and receive the extracted text.
    """
    allowed = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    ext = os.path.splitext(file.filename or "img.jpg")[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed)}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        results = reader.readtext(tmp_path)
        lines = [
            {"text": text, "confidence": round(float(conf), 4)}
            for _, text, conf in results
        ]
        full_text = "\n".join(l["text"] for l in lines)
        return JSONResponse({"text": full_text, "lines": lines})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        os.unlink(tmp_path)
