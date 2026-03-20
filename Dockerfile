FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app/src"

WORKDIR /app

COPY pyproject.toml .
RUN uv sync

CMD ["uv", "run", "uvicorn", "planning_dia.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]