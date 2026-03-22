from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.processing import extract_table

app = FastAPI(
    title="Table Extractor",
    description="Extraction de tableaux depuis une image via morphologie mathématique (OpenCV).",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Fichier image requis.")

    image_bytes = await file.read()

    try:
        grid = extract_table(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not grid:
        raise HTTPException(status_code=404, detail="Aucun tableau détecté dans l'image.")

    return JSONResponse({
        "rows": len(grid),
        "cols": len(grid[0]) if grid else 0,
        "cells": grid,
    })