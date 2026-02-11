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

# Usar gunicorn directamente para producción
# --access-logfile -: logs a stdout
# --error-logfile -: errores a stderr
# --log-level info: nivel de logging
# --timeout 120: timeout de requests
# --keep-alive 5: mantener conexiones vivas
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "app:app"]
