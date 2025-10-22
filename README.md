# Conversor de DOCX a Markdown

Una herramienta web y de línea de comandos para convertir archivos de Microsoft Word (.docx) a Markdown (.md), preservando las imágenes y la estructura del documento.

## 🚀 Características

- **Interfaz Web Sencilla**: Sube tus archivos `.docx` a través de una interfaz web moderna y responsiva.
- **Conversión de Texto**: Convierte párrafos, encabezados, listas y otros elementos de formato a su equivalente en Markdown.
- **Extracción de Imágenes**: Extrae automáticamente las imágenes del documento `.docx`.
- **Estructura Organizada**: Guarda las imágenes en una carpeta `assets` y actualiza las rutas en el archivo `.md` para que todo funcione correctamente.
- **Descarga en ZIP**: Empaqueta el archivo `.md` resultante y su carpeta de imágenes en un único archivo `.zip` para una descarga fácil.
- **Uso como Script**: Incluye un script de Python (`conversor.py`) que se puede ejecutar directamente desde la línea de comandos para conversiones locales.

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, HTMX
- **Servidor**: Uvicorn
- **Librerías Principales**:
  - `python-docx`: Para leer el contenido y extraer imágenes de archivos `.docx`.
  - `markitdown`: Para la conversión inicial del contenido del documento a Markdown.
  - `Jinja2`: Para renderizar las plantillas HTML del frontend.

## ⚙️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

1. **Clona el repositorio** (o simplemente usa los archivos que ya tienes):

    ```bash
    git clone git@github.com:GDelpo/python_docx_to_md.git
    cd python_docx_to_md
    ```

2. **Crea y activa un entorno virtual**:

    ```bash
    # Crear el entorno
    python -m venv env

    # Activarlo en Windows
    .\env\Scripts\activate

    # Activarlo en macOS/Linux
    source env/bin/activate
    ```

3. **Instala las dependencias**:

    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♂️ Cómo Usar

Puedes usar la aplicación de dos maneras: a través de la interfaz web o como una herramienta de línea de comandos.

### 1. Usando la Aplicación Web (Recomendado)

1. **Inicia el servidor**:

    - **Para desarrollo (con recarga automática):**
        Usa este comando para que el servidor se reinicie solo cada vez que guardas un cambio en el código.

        ```bash
        uvicorn webapp.main:app --reload
        ```

    - **Para producción:**
        Para un despliegue real, se recomienda usar un servidor de aplicaciones como Gunicorn. Primero, instálalo (se recomienda añadirlo a `requirements.txt`).

        ```bash
        pip install gunicorn
        ```

        Luego, inicia la aplicación con varios trabajadores para manejar múltiples peticiones:

        ```bash
        gunicorn -w 4 -k uvicorn.workers.UvicornWorker webapp.main:app
        ```

2. **Abre tu navegador**:
    Ve a `http://127.0.0.1:8000`.

3. **Convierte tu archivo**:
    - Selecciona tu archivo `.docx`.
    - Haz clic en "Convertir y descargar ZIP".
    - Espera a que aparezca el enlace de descarga y haz clic en él para obtener tu `.zip`.

### 2. Usando el Script de Línea de Comandos

### 3. Usando Docker (Recomendado para Despliegue)

Dockerizar la aplicación garantiza un entorno consistente y facilita el despliegue.

1. **Construye la imagen de Docker**:
    Desde la raíz del proyecto, ejecuta:

    ```bash
    docker build -t docx-converter .
    ```

2. **Ejecuta el contenedor**:
    Este comando inicia el contenedor, mapea el puerto 8000 de tu máquina al 8000 del contenedor y crea un "volumen" para que los archivos ZIP generados persistan en tu máquina local.

    - **En Windows (PowerShell) y macOS/Linux:**

      ```powershell
      docker run -p 8000:8000 -v "$(pwd)/webapp/resultados:/app/webapp/resultados" --name docx-converter-app docx-converter
      ```

    - **En Windows (Símbolo del sistema / cmd.exe):**

      ```cmd
      docker run -p 8000:8000 -v "%cd%/webapp/resultados:/app/webapp/resultados" --name docx-converter-app docx-converter
      ```

    Puedes cambiar el primer `8000` por otro puerto si está ocupado (ej. `-p 8080:8000`).

3. **Accede a la aplicación**:
    Abre tu navegador y ve a `http://127.0.0.1:8000`.

4. **Encuentra tus archivos**:
    Los archivos `.zip` que descargues se guardarán en la carpeta `webapp/resultados` de tu proyecto local, gracias al volumen que configuramos.

5. **Para detener el contenedor**:

    ```bash
    docker stop docx-converter-app
    ```

El script `conversor.py` es útil para conversiones rápidas sin levantar el servidor web.

1. **Ejecuta el script**:
    Pasa la ruta de tu archivo `.docx` como argumento.

    ```bash
    python conversor.py "C:\ruta\a\tu\documento.docx"
    ```

2. **Encuentra los resultados**:
    El script creará una carpeta `test_output` en el directorio del proyecto. Dentro encontrarás el archivo `.md` y una carpeta `assets` con las imágenes extraídas.

## 📂 Estructura del Proyecto

```bash
/
├── conversor.py         # Lógica principal para la conversión de DOCX a MD.
├── webapp/
│   ├── main.py          # Servidor web FastAPI y endpoints.
│   ├── templates/
│   │   └── index.html   # Frontend de la aplicación.
│   └── resultados/      # Carpeta donde se guardan los zips generados.
├── requirements.txt     # Dependencias del proyecto.
└── README.md            # Este archivo.
```
