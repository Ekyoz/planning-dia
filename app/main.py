import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.processing import extract_table

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("table-extractor")

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
    logger.info("Image reçue : %s (%.1f KB)", file.filename, len(image_bytes) / 1024)

    try:
        grid = extract_table(image_bytes)
    except ValueError as e:
        logger.error("Erreur traitement : %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    if not grid:
        logger.warning("Aucun tableau détecté dans %s", file.filename)
        raise HTTPException(status_code=404, detail="Aucun tableau détecté dans l'image.")

    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    filled = sum(1 for row in grid for cell in row if cell)
    total = rows * cols
    empty = total - filled

    logger.info(
        "Tableau détecté : %d×%d | cellules remplies=%d vides=%d (%.0f%%)",
        rows, cols, filled, empty, (filled / total * 100) if total else 0,
    )

    return JSONResponse({
        "summary": {
            "rows": rows,
            "cols": cols,
            "total_cells": total,
            "filled_cells": filled,
            "empty_cells": empty,
            "fill_rate": round(filled / total, 2) if total else 0,
        },
        "cells": grid,
    })