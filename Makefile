.PHONY: dev jupyter test lint

dev:
	python -m app.main

jupyter:
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

test:
	pytest

lint:
	black .
	isort .