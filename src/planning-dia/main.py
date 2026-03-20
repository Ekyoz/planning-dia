import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import io

from planning_dia.steps.rotate import rotate

app = FastAPI(title="planning-dia", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/debug/rotate")
async def debug_rotate(file: UploadFile = File(...)):
    """Retourne l'image après rotation pour vérifier visuellement."""
    data = await file.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    img = rotate(img)
    _, buffer = cv2.imencode(".jpg", img)
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpeg")


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    # TODO: pipeline complet
    return {"filename": file.filename, "data": []}