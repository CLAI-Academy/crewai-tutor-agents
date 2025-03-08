FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1 \
    MAKEFLAGS="-j4" \
    PYTHONPATH=/app \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install system dependencies
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

# Install Poetry inside the container
RUN pip install poetry

# Copy Poetry files (only these first to optimize caching)
COPY README.md pyproject.toml poetry.lock* ./
# Copy the app directory (what defines your package) so Poetry can "see" it
COPY app/ app/
# Configure Poetry to NOT create virtual environments inside the container
# and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --with dev --no-interaction --no-ansi

# Copy the rest of the application
COPY . .

# Create non-root user for security
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports (for FastAPI or Jupyter)
EXPOSE 8000 8888

# Run the app using Poetry
CMD ["poetry", "run", "python", "-m", "app.main"]
