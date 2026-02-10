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

# Hacer el script ejecutable
RUN chmod +x start.sh

# Usar script de inicio que asegura respuesta inmediata
CMD ["./start.sh"]
