FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Crear directorio de datos
RUN mkdir -p /app/data

# Exponer puerto
EXPOSE 5000

# Usar gunicorn para producción
# --access-logfile -: logs a stdout
# --error-logfile -: errores a stderr
# --log-level info: nivel de logging
# --preload: precargar aplicación antes de fork workers
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "--preload", "app:app"]
