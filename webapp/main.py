from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import tempfile
import zipfile
import logging
import uuid
import re
from pathlib import Path
from urllib.parse import quote_plus
from conversor import convertir_docx_a_markdown_con_imagenes

# Configura un logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="webapp/templates")

# Usamos Pathlib para manejar rutas de forma más limpia y segura
BASE_DIR = Path(__file__).parent
RESULTADOS_DIR = BASE_DIR / "resultados"
RESULTADOS_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Sirve la página principal."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convertir/")
async def convertir(request: Request, docx: UploadFile = File(...)):
    """
    Recibe un .docx, lo convierte, lo zipea y devuelve un link de descarga.
    Todo el trabajo se realiza en un directorio temporal seguro.
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. Guardar el archivo subido de forma segura
            # Usamos un nombre genérico dentro del temp, aunque guardar el original también es seguro aquí.
            original_filename = docx.filename
            docx_path = tmp_path / original_filename

            with docx_path.open("wb") as buffer:
                shutil.copyfileobj(docx.file, buffer)

            # --- [RECOMENDACIÓN CRÍTICA] ---
            # Modificamos la lógica para que la función conversora
            # reciba un 'output_dir' y escriba TODO dentro de 'tmp_path'.
            # ¡NUNCA debe escribir en el CWD ('.')!

            # Asumimos que tu función ahora escribe en tmp_path
            convertir_docx_a_markdown_con_imagenes(docx_path, output_dir=tmp_path)

            # --- Fin Recomendación ---

            # 2. Definir nombres y rutas (basado en tu lógica original, pero seguro)
            # Usamos Path.stem para obtener el nombre base sin extensión
            original_base_name = Path(original_filename).stem
            # Sanitizamos el nombre para usarlo en el zip
            safe_base_name = re.sub(r"[^\w-]", "_", original_base_name)

            md_file_name = f"{safe_base_name}.md"
            md_path = tmp_path / md_file_name

            # Esta es la estructura que usabas, pero ahora relativa a tmp_path
            img_dir = tmp_path / "assets" / "img" / safe_base_name

            # Verificación: ¿Se generó el archivo MD?
            if not md_path.exists():
                logger.error(
                    f"El archivo Markdown '{md_path}' no fue generado por el conversor."
                )
                raise FileNotFoundError("Error: El archivo Markdown no se generó.")

            # 3. Crear el ZIP de forma segura

            # Nombre SEGURO en el servidor (UUID)
            server_zip_uuid = uuid.uuid4()
            server_zip_file = RESULTADOS_DIR / f"{server_zip_uuid}.zip"

            # Nombre AMIGABLE para la descarga del usuario
            download_zip_name = f"{safe_base_name}_resultado.zip"

            with zipfile.ZipFile(server_zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Añadir el .md al zip
                zipf.write(md_path, arcname=md_file_name)

                # Añadir la carpeta de imágenes si existe
                if img_dir.is_dir():
                    # Usamos rglob() para recorrer recursivamente
                    for file_path in img_dir.rglob("*"):
                        if file_path.is_file():
                            # Calculamos la ruta relativa para guardarla en el zip
                            relative_path = file_path.relative_to(tmp_path)
                            zipf.write(file_path, arcname=relative_path)

            logger.info(f"ZIP generado: {server_zip_file}")

            # 4. Generar la respuesta HTMX
            # Pasamos el UUID como path y el nombre de descarga como query param
            href = f"/descargar/{server_zip_uuid}?download_name={quote_plus(download_zip_name)}"

            # Usamos HTMLResponse para evitar que FastAPI intente parsear el string como JSON
            return HTMLResponse(
                content=f'<a href="{href}" class="btn-descarga">Descargar {download_zip_name}</a>'
            )

    except FileNotFoundError as e:
        logger.warning(f"Error de conversión (archivo no encontrado): {e}")
        return HTMLResponse(
            content=f'<p class="error">Error: No se pudo generar el archivo. ¿El .docx es válido?</p>',
            status_code=400,  # Bad Request
        )
    except Exception as e:
        logger.error(f"Error inesperado en /convertir: {e}", exc_info=True)
        return HTMLResponse(
            content=f'<p class="error">Error interno del servidor. Intente de nuevo.</p>',
            status_code=500,  # Internal Server Error
        )


@app.get("/descargar/{zip_id}")
async def descargar(zip_id: uuid.UUID, download_name: str = "resultado.zip"):
    """
    Sirve el archivo ZIP de forma segura usando su UUID.
    """
    try:
        # 1. Sanitizar el nombre de descarga (defensa extra)
        safe_download_name = re.sub(r"[^\w.-]", "_", Path(download_name).name)

        # 2. Construir la ruta segura en el servidor
        server_file = (RESULTADOS_DIR / f"{zip_id}.zip").resolve()

        # 3. Validación de seguridad (Path Traversal)
        # Verificamos que el archivo resuelto siga estando DENTRO de RESULTADOS_DIR
        if not server_file.exists() or not str(server_file).startswith(
            str(RESULTADOS_DIR.resolve())
        ):
            logger.warning(
                f"Intento de Path Traversal o archivo no encontrado: {zip_id}"
            )
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        logger.info(f"Sirviendo archivo: {server_file} como {safe_download_name}")

        return FileResponse(
            path=server_file, filename=safe_download_name, media_type="application/zip"
        )
    except Exception as e:
        logger.error(f"Error en /descargar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al descargar el archivo")
