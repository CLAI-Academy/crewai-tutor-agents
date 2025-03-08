.PHONY: dev jupyter test lint up up-jupyter up-all up-build logs logs-jupyter exec exec-jupyter restart restart-jupyter stop down down-v build ps top clean prune help

# === Development Commands ===

dev: ## Runs the main application
	python -m app.main

jupyter: ## Starts Jupyter Notebook using Poetry
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''


test: ## Runs tests with pytest
	pytest

lint: ## Formats code with black and sorts imports with isort
	black .
	isort .

# === Main Docker Commands ===

up-agent: ## Starts the main application service
	docker-compose up ai-agent

up-jupyter: ## Starts the Jupyter Notebook service
	docker-compose up jupyter

up: ## Starts all services defined in docker-compose.yml
	docker-compose up

up-build: ## Rebuilds and starts all services (use after changes in Dockerfile)
	docker-compose up --build

# === Docker Management Commands ===

logs: ## Shows real-time logs of the ai-agent service
	docker-compose logs -f ai-agent

logs-jupyter: ## Shows real-time logs of the jupyter service
	docker-compose logs -f jupyter

exec: ## Opens a bash terminal inside the ai-agent container
	docker-compose exec ai-agent bash

exec-jupyter: ## Opens a bash terminal inside the jupyter container
	docker-compose exec jupyter bash

restart-agent: ## Restarts the ai-agent service
	docker-compose restart ai-agent

restart-jupyter: ## Restarts the jupyter service
	docker-compose restart jupyter

stop: ## Stops all services without removing containers
	docker-compose stop

down: ## Stops and removes containers, networks created by docker-compose up
	docker-compose down

down-v: ## Stops and removes containers, networks, and volumes (WARNING! Removes persistent data)
	docker-compose down -v

build: ## Rebuilds the containers (useful after changes in Dockerfile or requirements.txt)
	docker-compose build

ps: ## Displays the status of all containers managed by docker-compose
	docker-compose ps

top: ## Shows running processes inside the containers
	docker-compose top

clean: ## Removes all unused images and stopped containers
	docker system prune -f

prune: ## Deep cleanup: removes all unused images, containers, networks, and volumes
	docker system prune -a --volumes -f

help: ## Displays this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $1, $2}'

.DEFAULT_GOAL := help