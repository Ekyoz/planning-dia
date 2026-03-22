# Table Extractor

Service FastAPI d'extraction de tableaux depuis des images, via morphologie mathématique OpenCV.  
Conçu pour tourner sur **Raspberry Pi 4 (ARM64)** — aucun modèle IA lourd.

---

## Stack

| Composant | Rôle |
|-----------|------|
| FastAPI | API REST |
| OpenCV headless | Détection de tableau (kernels morphologiques) |
| Uvicorn | Serveur ASGI |
| Docker + Compose | Packaging & déploiement (compatible Portainer) |

---

## Lancement rapide

```bash
# Build + start
docker compose up --build

# Test rapide
curl -X POST http://localhost:8000/extract \
  -F "file=@mon_tableau.png"
```

---

## Endpoint

### `POST /extract`

**Body** : `multipart/form-data` avec un champ `file` (image PNG/JPEG).

**Réponse 200** :
```json
{
  "rows": 3,
  "cols": 4,
  "cells": [
    [
      {"x": 10, "y": 10, "width": 120, "height": 40},
      ...
    ],
    ...
  ]
}
```

---

## Algorithme (processing.py)

1. **Binarisation adaptative** — robuste aux variations d'éclairage.
2. **Kernel horizontal** (`MORPH_RECT w//30 × 1`) → isole les lignes H.
3. **Kernel vertical** (`MORPH_RECT 1 × h//30`) → isole les lignes V.
4. **Fusion + dilatation** → grille complète.
5. **Contours** (`findContours RETR_TREE`) → bounding boxes des cellules.
6. **Clustering** par centre Y/X → attribution `row`/`col`.

---

## Développement (Hot-Reload)

Le volume Docker monte `./app` dans le container.  
Toute modification de `app/*.py` rechargée automatiquement par Uvicorn (`--reload`).

```bash
docker compose up   # pas besoin de --build à chaque changement
```

---

## Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI + endpoint /extract
│   └── processing.py   # Pipeline OpenCV
├── docker/
│   └── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```