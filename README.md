# docx-to-markdown

<p>
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.119-009688?logo=fastapi&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="Status" src="https://img.shields.io/badge/status-stable-green">
</p>

> Convierte archivos `.docx` a Markdown preservando imágenes y estructura. Webapp + CLI.

## Features

- Webapp FastAPI + HTMX: subí el `.docx`, descargá un `.zip` con el `.md` y sus imágenes.
- CLI: `conversor.py` para conversiones locales sin servidor.
- Extracción automática de imágenes a carpeta `assets/` con rutas relativas resueltas en el `.md`.
- Conversión de párrafos, encabezados, listas y formato básico.
- Dockerfile incluido — deploy con gunicorn + uvicorn workers.

## Quickstart

### Requirements

- Python 3.11+
- `pip`

### Install

```bash
git clone https://github.com/GDelpo/docx-to-markdown.git
cd docx-to-markdown
python -m venv env
source env/bin/activate          # Linux/macOS
# .\env\Scripts\Activate.ps1     # Windows
pip install -r requirements.txt
```

### Run — Webapp

Desarrollo (con hot reload):

```bash
uvicorn webapp.main:app --reload
```

Producción:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker webapp.main:app --bind 0.0.0.0:8000
```

Abrí `http://localhost:8000` y subí un `.docx`.

### Run — CLI

```bash
python conversor.py ruta/al/archivo.docx
```

Genera el `.md` y una carpeta `assets/` con las imágenes al lado del archivo de entrada.

### Run — Docker

```bash
docker build -t docx-to-markdown .
docker run --rm -p 8000:8000 docx-to-markdown
```

## Architecture

```
docx-to-markdown/
├── conversor.py         # Lógica de conversión + CLI entry point
├── webapp/
│   ├── main.py          # FastAPI app, endpoints de upload y download
│   └── templates/       # Jinja2 + HTMX
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

**Stack:** FastAPI + Uvicorn + Jinja2 + HTMX para el frontend. `python-docx` y `markitdown` para el parseo. `lxml` para extracción de imágenes.

## Configuration

Este proyecto no requiere variables de entorno. Todo corre con defaults razonables.

## License

[MIT](LICENSE) © 2026 Guido Delponte
