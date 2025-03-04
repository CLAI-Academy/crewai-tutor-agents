# AI Agents Docker Environment

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

## Estructura del Proyecto

```
proyecto/
├── app/                    # Carpeta principal de la aplicación
│   ├── __init__.py         # Archivo necesario para reconocer app como paquete
│   └── main.py             # Punto de entrada de la aplicación
├── Dockerfile              # Configuración para construir la imagen Docker
├── docker-compose.yml      # Configuración de servicios
├── Makefile                # Comandos para ejecutar diferentes tareas
├── requirements.txt        # Dependencias de Python
└── README.md               # Este archivo
```

## Configuración Inicial

1. **Clona el repositorio** (si aplica):

   ```bash
   git clone <url-del-repositorio>
   cd <nombre-del-repositorio>
   ```

2. **Archivo .env** (opcional):
   Crea un archivo `.env` en la raíz del proyecto para almacenar variables de entorno:
   ```
   OPENAI_API_KEY=sk-...
   ```

## Iniciar los Servicios

### Para iniciar la aplicación principal:

```bash
docker-compose up ai-agent
```

### Para iniciar Jupyter Notebook:

```bash
docker-compose up jupyter
```

### Para iniciar ambos servicios:

```bash
docker-compose up
```

### Para construir e iniciar (primera vez o después de cambios en Dockerfile):

```bash
docker-compose up --build
```

## Acceder a los Servicios

- **Aplicación principal**: http://localhost:8000
- **Jupyter Notebook**: http://localhost:8888

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
