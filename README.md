# table-extractor

Extrait les horaires depuis une photo de planning imprimé, et les injecte dans Home Assistant.

## Installation

```bash
uv sync
uv sync --extra dev  # avec outils de dev
```

## Usage

```bash
uv run table-extractor data/input/planning.jpg --debug
```

## Structure

```
table-extractor/
├── src/table_extractor/
│   ├── __init__.py
│   └── main.py
├── tests/
├── data/
│   ├── input/    # images sources
│   └── output/   # résultats + debug
├── pyproject.toml
└── README.md
```
