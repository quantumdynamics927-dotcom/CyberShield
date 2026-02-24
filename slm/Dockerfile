FROM pytorch/pytorch:2.3.1-cpu

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /cache && \
    chmod -R 755 /app/bin/*

# Puerto para API local
EXPOSE 8010

# Comando por defecto
CMD ["python", "api.py"]
