from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="planning-dia", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    # TODO: traitement image
    return {"filename": file.filename, "data": []}