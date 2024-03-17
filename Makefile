
PYTHON := .venv/bin/python
SHELL := /bin/bash


.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Make a new virtual environment
	python3 -m venv $(VENV) && source $(BIN)/activate

.PHONY: install
install: venv ## Make venv and install requirements
	$(BIN)/pip install --upgrade -r requirements.txt

freeze: ## Pin current dependencies
	$(BIN)/pip freeze > requirements.txt

migrate: ## Make and run migrations
	$(PYTHON) nhhc/manage.py makemigrations
	$(PYTHON) nhhc/manage.py migrate


db-shell: ## Access the Postgres Docker database interactively with psql. Pass in DBNAME=<name>.
	docker exec -it container_name psql -d $(DBNAME)

.PHONY: test
test: ## Run tests
	doppler run -- coverage run nhhc/manage.py test web employee portal  --verbosity=2  --keepdb  --failfast  --force-color

.PHONY: test
pipeline-test: ## Run tests
	$(PYTHON) nhhc/manage.py test web employee portal  --verbosity=2  --keepdb  --failfast  --force-color

.PHONY: run
run: ## Run the Django server
	doppler run -- 	$(PYTHON) nhhc/manage.py runserver

start: install migrate run ## Install requirements, apply migrations, then start development server
