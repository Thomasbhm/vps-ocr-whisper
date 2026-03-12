import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR

app = FastAPI(title="PaddleOCR API", version="1.0.0")

# Load models once at startup (use_gpu=False = CPU only)
ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=False, show_log=False)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    """
    Upload an image (JPG, PNG, BMP...) and receive the extracted text.
    """
    allowed = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    ext = os.path.splitext(file.filename or "img.jpg")[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed)}",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = ocr.ocr(tmp_path, cls=True)
        lines = []
        if result and result[0]:
            for line in result[0]:
                text, confidence = line[1]
                lines.append({"text": text, "confidence": round(float(confidence), 4)})
        full_text = "\n".join(l["text"] for l in lines)
        return JSONResponse({"text": full_text, "lines": lines})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        os.unlink(tmp_path)
