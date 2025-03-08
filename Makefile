.PHONY: dev jupyter test lint up up-jupyter up-all up-build logs logs-jupyter exec exec-jupyter restart restart-jupyter stop down down-v build ps top clean prune help poetry-install poetry-add poetry-add-dev poetry-export poetry-update poetry-lock

# === Poetry Commands ===

poetry-install: ## Install dependencies using Poetry
	poetry install

poetry-add: ## Add a new package with Poetry (usage: make poetry-add pkg=package_name)
	poetry add $(pkg)

poetry-add-dev: ## Add a new development package with Poetry (usage: make poetry-add-dev pkg=package_name)
	poetry add --group dev $(pkg)

poetry-update: ## Update all dependencies to their latest compatible version
	poetry update

poetry-lock: ## Regenerate the poetry.lock file
	poetry lock

poetry-export: ## Export dependencies to requirements.txt
	poetry export --without-hashes > requirements.txt


# === Development Commands ===

dev: ## Run the main application
	python -m app.main

jupyter: ## Start Jupyter Notebook without password
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

test: ## Run tests with pytest
	pytest

lint: ## Format code with black and sort imports with isort
	black .
	isort .

# === Main Docker Commands ===

up-agent: ## Start the main application service
	docker-compose up ai-agent

up-jupyter: ## Start the Jupyter Notebook service
	docker-compose up jupyter

up: ## Start all services defined in docker-compose.yml
	docker-compose up

up-build: ## Rebuild and start all services (use after changes in Dockerfile)
	docker-compose up --build

# === Docker Management Commands ===

logs: ## Show real-time logs of the ai-agent service
	docker-compose logs -f ai-agent

logs-jupyter: ## Show real-time logs of the jupyter service
	docker-compose logs -f jupyter

exec: ## Open a bash terminal inside the ai-agent container
	docker-compose exec ai-agent bash

exec-jupyter: ## Open a bash terminal inside the jupyter container
	docker-compose exec jupyter bash

restart-agent: ## Restart the ai-agent service
	docker-compose restart ai-agent

restart-jupyter: ## Restart the jupyter service
	docker-compose restart jupyter

stop: ## Stop all services without removing containers
	docker-compose stop

down: ## Stop and remove containers and networks created by docker-compose up
	docker-compose down

down-v: ## Stop and remove containers, networks, and volumes (CAUTION! Deletes persistent data)
	docker-compose down -v

build: ## Rebuild containers (useful after changes in Dockerfile or requirements.txt)
	docker-compose build

ps: ## Show the status of all containers managed by docker-compose
	docker-compose ps

top: ## Show running processes inside the containers
	docker-compose top

clean: ## Remove all unused images and stopped containers
	docker system prune -f

prune: ## Deep cleaning: remove all unused images, containers, networks, and volumes
	docker system prune -a --volumes -f

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $1, $2}'

.DEFAULT_GOAL := help