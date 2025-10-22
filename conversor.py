import os
import re
import itertools
from docx import Document
from markitdown import MarkItDown
from pathlib import Path
import logging

# Configurar un logger para este módulo
logger = logging.getLogger(__name__)


def extraer_imagenes_docx(path_docx: Path, output_folder: Path) -> list[Path]:
    """
    Extrae imágenes del DOCX en orden y las guarda en output_folder.
    Retorna una lista de Paths (objetos Path) guardados en orden.
    """
    doc = Document(path_docx)
    # Aseguramos que la carpeta de salida exista
    output_folder.mkdir(parents=True, exist_ok=True)

    rutas_guardadas = []
    contador = itertools.count(1)

    try:
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                data = rel.target_part.blob
                extension = Path(rel.target_ref).suffix or ".png"
                filename = f"imagen_{next(contador):03d}{extension}"
                filepath = output_folder / filename

                with filepath.open("wb") as f:
                    f.write(data)
                rutas_guardadas.append(filepath)

        logger.info(
            f"📸 {len(rutas_guardadas)} imágenes extraídas en '{output_folder}'"
        )

    except Exception as e:
        logger.error(f"Error extrayendo imágenes: {e}", exc_info=True)

    return rutas_guardadas


def convertir_docx_a_markdown_con_imagenes(path_docx: Path, output_dir: Path):
    """
    Convierte un DOCX a Markdown.

    Escribe el .md y la carpeta de imágenes dentro del 'output_dir' especificado.
    """

    # pathlib.Path para manejar las rutas
    docx_path = Path(path_docx)

    # Nombre base para carpeta y archivo, reemplazando espacios por _
    base_name = docx_path.stem
    base_name_safe = re.sub(r"[^\w-]", "_", base_name)

    # --- ¡CAMBIO CLAVE! ---
    # Todas las salidas ahora usan 'output_dir' como base

    # Carpeta de imágenes DENTRO del directorio de salida
    img_dir_path = output_dir / "assets" / "img" / base_name_safe

    # Archivo .md DENTRO del directorio de salida
    output_md_path = output_dir / f"{base_name_safe}.md"

    # --- Fin Cambio ---

    # 1️⃣ Extraer imágenes reales
    rutas_imagenes = extraer_imagenes_docx(docx_path, img_dir_path)

    # 2️⃣ Usar MarkItDown para convertir el texto a Markdown
    md = MarkItDown(enable_plugins=True)
    result = md.convert(docx_path)
    markdown = result.text_content

    # 3️⃣ Reemplazar cualquier línea que comience con ![ por la ruta física de la imagen extraída, en orden
    markdown_lines = markdown.splitlines()
    nuevas_lineas = []
    img_counter = 0
    reemplazos = 0
    for linea in markdown_lines:
        if linea.strip().startswith("!["):
            if img_counter < len(rutas_imagenes):
                # --- Lógica de ruta relativa simplificada ---
                # Queremos la ruta relativa al 'output_dir'
                # ej: assets/img/mi_doc/imagen_001.png

                # rutas_imagenes[img_counter] es un Path absoluto, ej: /tmp/xyz/assets/img/mi_doc/img_001.png
                # output_dir es un Path, ej: /tmp/xyz
                # .relative_to() nos da -> assets/img/mi_doc/img_001.png
                ruta_relativa = rutas_imagenes[img_counter].relative_to(output_dir)

                # .as_posix() asegura que usemos '/' (formato web/unix) en lugar de '\' (windows)
                ruta_rel_posix = ruta_relativa.as_posix()

                nuevas_lineas.append(f"![imagen {img_counter + 1}]({ruta_rel_posix})")
                img_counter += 1
                reemplazos += 1
            else:
                # Si MarkItDown encontró más placeholders de imagen de las que extrajimos
                nuevas_lineas.append(linea)
        else:
            nuevas_lineas.append(linea)

    markdown = "\n".join(nuevas_lineas)
    logger.info(f"🔄 {reemplazos} reemplazos de imágenes aplicados")

    # 4️⃣ Guardar resultado final
    output_md_path.write_text(markdown, encoding="utf-8")

    logger.info(f"✅ Markdown generado en: {output_md_path}")
    logger.info(f"🖼️ Imágenes disponibles en: {img_dir_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("⚠️ Uso: python conversor.py <archivo.docx>")
    else:
        # Ejemplo de cómo llamarlo localmente para testear:
        input_file = Path(sys.argv[1]).resolve()
        # Creamos una carpeta 'test_output' al lado del script
        output_folder = Path(__file__).parent / "test_output"
        output_folder.mkdir(exist_ok=True)

        print(f"Convirtiendo '{input_file.name}'...")
        print(f"Guardando resultado en: '{output_folder.resolve()}'")

        convertir_docx_a_markdown_con_imagenes(input_file, output_folder)
        print("¡Conversión de prueba finalizada!")
