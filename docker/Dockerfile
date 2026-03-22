FROM python:3.11-slim

# Dépendances système pour OpenCV headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installation des dépendances Python en premier (layer cache)
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
 && pip install .

# Copie du code source (écrasé en dev par le volume)
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]