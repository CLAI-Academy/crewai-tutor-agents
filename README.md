# AI Agents Docker Environment

<div align="center">
  <img src="public/Logo-completo.png" alt="CrewAI Tutor Agents Logo" width="400"/>
</div>

## Descripción del Proyecto

Este es un proyecto con fines educativos en el que exploramos cómo mejorar la experiencia de usuario en aplicaciones de IA, utilizando websockets para comunicación en tiempo real y CrewAI como framework de orquestación de agentes. El objetivo es crear un entorno interactivo donde los agentes de IA puedan colaborar y resolver tareas complejas mientras mantienen una comunicación fluida con el usuario.

Este repositorio contiene la configuración de Docker para ejecutar un entorno de desarrollo para agentes de IA basados en Python, con soporte para aplicaciones y Jupyter Notebooks.

## Prerequisitos

Antes de comenzar, asegúrate de tener instalado:

- Docker y Docker Compose
- Git (opcional, para clonar el repositorio)

Compatibilidad:

- Funciona en macOS (incluyendo Apple Silicon M1/M2)
- Funciona en Windows
- Funciona en Linux

### Instalación de Docker

#### Para macOS:

1. Descarga [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)
2. Para usuarios de Apple Silicon (M1/M2):

   - Asegúrate de descargar la versión compatible con Apple Silicon
   - Docker Desktop para Mac incluye soporte para Rosetta 2 automáticamente

3. Instala Docker Desktop:

   - Abre el archivo .dmg descargado
   - Arrastra el ícono de Docker a la carpeta Applications
   - Abre Docker desde Applications
   - Sigue las instrucciones de configuración inicial

4. Verifica la instalación:
   ```bash
   docker --version
   docker-compose --version
   ```

#### Para Windows:

1. **Requisitos previos**:

   - Windows 10/11 64-bit: Pro, Enterprise, o Education (Build 19041 o posterior)
   - Habilitar características de Hyper-V y Contenedores de Windows
   - WSL 2 (Windows Subsystem for Linux 2)

2. Instala WSL 2 (si no está instalado):

   ```powershell
   wsl --install
   ```

3. Descarga [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)

4. Instala Docker Desktop:

   - Ejecuta el instalador descargado
   - Sigue las instrucciones en pantalla
   - Asegúrate de marcar la opción "Use WSL 2 instead of Hyper-V"
   - Reinicia tu computadora después de la instalación

5. Verifica la instalación:

   ```powershell
   docker --version
   docker-compose --version
   ```

6. Configuración recomendada para Windows:
   - Abre Docker Desktop
   - Ve a Settings > Resources > WSL Integration
   - Habilita la integración con tu distribución de WSL 2

### Instalación de Poetry

Para la gestión de dependencias, utilizamos Poetry. Sigue estos pasos para instalarlo:

#### Para macOS / Linux:

1. Instalación mediante curl:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Añade Poetry a tu PATH en tu archivo `.zshrc` o `.bashrc`:

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. Reinicia tu terminal o ejecuta `source ~/.zshrc` (o `source ~/.bashrc`).

4. Verifica la instalación:
   ```bash
   poetry --version
   ```

#### Para Windows:

1. Usando PowerShell:

   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

2. Añade Poetry a tu PATH:

   - Busca "Variables de entorno" en el menú Inicio
   - Selecciona "Editar las variables de entorno del sistema"
   - Haz clic en "Variables de entorno"
   - Edita la variable "Path" del usuario
   - Añade la ruta `%APPDATA%\Python\Scripts`
   - Haz clic en "Aceptar" para guardar los cambios

3. Verifica la instalación:
   ```powershell
   poetry --version
   ```

### Uso básico de Poetry en el proyecto

1. **Instalar dependencias** (si ya existe un archivo `pyproject.toml`):

   ```bash
   poetry install
   ```

2. **Añadir una nueva dependencia**:

   ```bash
   poetry add nombre-del-paquete
   ```

3. **Añadir una dependencia solo para desarrollo**:

   ```bash
   poetry add --dev nombre-del-paquete
   ```

4. **Actualizar dependencias**:
   ```bash
   poetry update
   ```

## Estructura del Proyecto

```
proyecto/
├── app/                    # Carpeta principal de la aplicación
│   ├── __init__.py         # Archivo necesario para reconocer app como paquete
│   └── main.py             # Punto de entrada de la aplicación
├── Dockerfile              # Configuración para construir la imagen Docker
├── docker-compose.yml      # Configuración de servicios
├── Makefile                # Comandos para ejecutar diferentes tareas
├── pyproject.toml          # Configuración de Poetry y dependencias
├── poetry.lock             # Archivo de bloqueo para versiones exactas de dependencias
├── notebooks/              # Directorio para Jupyter Notebooks
└── README.md               # Este archivo
```

## Cómo clonar e iniciar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/crewai-tutor-agents.git
cd crewai-tutor-agents
```

### 2. Configurar el archivo de variables de entorno

Copia el archivo plantilla `.env-template` a `.env` y añade tus claves API:

```bash
cp .env-template .env
```

Edita el archivo `.env` para incluir tus claves API:
```
OPENAI_API_KEY=tu_clave_de_openai
ANTHROPIC_API_KEY=tu_clave_de_anthropic
# ... otras variables según sea necesario
```

### 3. Iniciar el proyecto con Docker (recomendado)

Docker ya está completamente configurado y listo para usar. Simplemente ejecuta:

```bash
# Para iniciar todos los servicios
docker-compose up

# O para construir e iniciar en el primer uso
docker-compose up --build
```

### 4. Alternativamente, para desarrollo local con Poetry

Si prefieres trabajar sin Docker, usando Poetry directamente:

```bash
# Instalar todas las dependencias del proyecto
poetry install

# Activar el entorno virtual
poetry shell

# Iniciar la aplicación
make dev

# O iniciar Jupyter Notebook
make jupyter
```

## Acceder a los Servicios

- **Aplicación principal**: http://localhost:8000
- **Jupyter Notebook**: http://localhost:8888 (sin contraseña)

## Comandos Útiles

### Ver logs de un servicio específico:

```bash
docker-compose logs -f ai-agent
```

o

```bash
docker-compose logs -f jupyter
```

### Entrar al contenedor:

```bash
docker-compose exec ai-agent bash
```

o

```bash
docker-compose exec jupyter bash
```

### Reiniciar un servicio:

```bash
docker-compose restart ai-agent
```

o

```bash
docker-compose restart jupyter
```

## Detener y Limpiar

### Detener los servicios (mantiene los datos):

```bash
docker-compose stop
```

### Detener y eliminar los contenedores:

```bash
docker-compose down
```

### Detener, eliminar contenedores y volúmenes (CUIDADO: elimina datos):

```bash
docker-compose down -v
```

## Desarrollo Colaborativo

Para trabajar con este proyecto en un equipo:

1. Cada miembro debe tener Docker y Docker Compose instalados
2. Clonar el repositorio y configurar el archivo `.env` si es necesario
3. Ejecutar `docker-compose up` para iniciar el entorno
4. Los cambios en el código se reflejan en tiempo real gracias a los volúmenes montados

## Solución de Problemas

### Módulo no encontrado

Si ves un error sobre módulos no encontrados:

```
ModuleNotFoundError: No module named 'app'
```

Verifica que:

- La carpeta `app` existe y contiene un archivo `__init__.py`
- El archivo `main.py` está dentro de la carpeta `app`
- El valor `PYTHONPATH=/app` está correctamente configurado en el Dockerfile

### Problemas de permisos

En sistemas Unix (macOS/Linux), si hay problemas de permisos:

```bash
chmod -R 755 .
```

### Puertos ocupados

Si los puertos 8000 u 8888 están ocupados, modifica los puertos en `docker-compose.yml`:

```yaml
ports:
  - "8001:8000" # Cambia 8001 por otro puerto disponible
```

### Problemas con Poetry en Docker

Si enfrentas problemas con Poetry dentro de los contenedores:

1. Verifica que el Dockerfile instale Poetry correctamente:

   ```dockerfile
   RUN pip install poetry && \
       poetry config virtualenvs.create false
   ```

2. Asegúrate de que el archivo `pyproject.toml` esté correctamente copiado al contenedor:

   ```dockerfile
   COPY pyproject.toml poetry.lock* /app/
   ```

3. Si las dependencias no se instalan, ejecuta:
   ```bash
   docker-compose exec ai-agent poetry install
   ```

