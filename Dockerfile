FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1 \
    MAKEFLAGS="-j4" \
    PYTHONPATH=/app \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry dentro del contenedor
RUN pip install poetry

# Copiar archivos de Poetry (solo estos primero para cachear mejor)
COPY README.md pyproject.toml poetry.lock* ./
# 5. Copiar el directorio app (lo que define tu paquete) para que Poetry lo “vea”
COPY app/ app/
# Configurar Poetry para que NO cree entornos virtuales dentro del contenedor
# e instalar dependencias
RUN poetry config virtualenvs.create false && \
    poetry install --with dev --no-interaction --no-ansi

# Copiar el resto de la aplicación
COPY . .


# Crear usuario no-root para seguridad
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Exponer puertos (para FastAPI o Jupyter)
EXPOSE 8000 8888

# Ejecutar la app usando Poetry 
CMD ["poetry", "run", "python", "-m", "app.main"]