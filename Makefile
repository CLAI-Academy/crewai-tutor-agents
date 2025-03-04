.PHONY: dev jupyter test lint logs logs-jupyter exec exec-jupyter restart restart-jupyter stop down down-v build ps top clean prune help

# === Comandos de desarrollo ===

dev: ## Ejecuta la aplicación principal
	python -m app.main

jupyter: ## Inicia Jupyter Notebook sin contraseña
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

test: ## Ejecuta las pruebas con pytest
	pytest

lint: ## Formatea el código con black y ordena imports con isort
	black .
	isort .

# === Comandos de gestión de Docker ===

logs: ## Muestra logs en tiempo real del servicio ai-agent
	docker-compose logs -f ai-agent

logs-jupyter: ## Muestra logs en tiempo real del servicio jupyter
	docker-compose logs -f jupyter

exec: ## Abre una terminal bash dentro del contenedor ai-agent
	docker-compose exec ai-agent bash

exec-jupyter: ## Abre una terminal bash dentro del contenedor jupyter
	docker-compose exec jupyter bash

restart: ## Reinicia el servicio ai-agent
	docker-compose restart ai-agent

restart-jupyter: ## Reinicia el servicio jupyter
	docker-compose restart jupyter

stop: ## Detiene todos los servicios sin eliminar contenedores
	docker-compose stop

down: ## Detiene y elimina contenedores, redes creadas por docker-compose up
	docker-compose down

down-v: ## Detiene y elimina contenedores, redes y volúmenes (¡CUIDADO! Elimina datos persistentes)
	docker-compose down -v

build: ## Reconstruye los contenedores (útil después de cambios en Dockerfile o requirements.txt)
	docker-compose build

ps: ## Muestra el estado de todos los contenedores gestionados por docker-compose
	docker-compose ps

top: ## Muestra los procesos en ejecución dentro de los contenedores
	docker-compose top

clean: ## Elimina todas las imágenes no utilizadas y contenedores detenidos
	docker system prune -f

prune: ## Limpieza profunda: elimina todas las imágenes, contenedores, redes y volúmenes no utilizados
	docker system prune -a --volumes -f

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $1, $2}'

.DEFAULT_GOAL := help