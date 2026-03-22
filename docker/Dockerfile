FROM python:3.11-slim

# Dépendances système pour OpenCV headless
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl

WORKDIR /app

ENV PYTHONPATH=/app

# Copie tout avant l'install pour que setuptools trouve le package
COPY pyproject.toml .
COPY app/ ./app/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
 && pip install .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]