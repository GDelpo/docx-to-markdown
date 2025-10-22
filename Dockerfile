# Etapa 1: Usar una imagen base oficial de Python.
# Usamos la versión 'slim' que es más ligera, ideal para producción.
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor.
# Todos los comandos siguientes se ejecutarán desde esta ruta.
WORKDIR /app

# Copiar solo el archivo de requerimientos primero.
# Esto aprovecha el sistema de caché de Docker: si requirements.txt no cambia,
# no se volverán a instalar las dependencias en reconstrucciones posteriores.
COPY requirements.txt .

# Instalar las dependencias del proyecto.
# --no-cache-dir para no guardar la caché de pip y mantener la imagen ligera.
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación al directorio de trabajo.
# El .dockerignore evitará que se copien archivos innecesarios.
COPY . .

# Exponer el puerto 8000, que es el puerto por defecto en el que Gunicorn/Uvicorn escuchará.
EXPOSE 8000

# Comando para ejecutar la aplicación cuando se inicie el contenedor.
# Usamos Gunicorn como servidor de producción, con trabajadores de Uvicorn para FastAPI.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "webapp.main:app", "--bind", "0.0.0.0:8000"]