VENV := /workspaces/NettHands/.venv
# # BIN := /usr/local/bin
# BIN := /
# PYTHON := $(BIN)/python3.12
# SHELL := /bin/bash

PYTHON := $(VENV)/bin/python
SHELL := /bin/bash

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY:
venv: ## Make a new virtual environment
	python3 -m venv $(VENV) && source $(BIN)/activate

.PHONY: install
install: ## Make venv and install requirements
	$(BIN)/pip install --upgrade -r requirements.txt

freeze: ## Pin current dependencies
	$(BIN)/pip freeze > requirements.txt

.PHONY: collect
collect:
	doppler run  -t $(DOPPLER_TOKEN) -- $(PYTHON)  manage.py collectstatic --no-input

migrate: ## Make and run migrations
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON) manage.py makemigrations
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON) manage.py migrate


db-shell: ## Access the Postgres Docker database interactively with psql. Pass in DBNAME=<name>.
	docker exec -it container_name psql -d $(DBNAME)

.PHONY: test
test: ## Run tests
	doppler run -- coverage run manage.py test web employee portal  --verbosity=2 --keepdb   --failfast  --force-color

.PHONY: test
pipeline-test: ## Run tests
	${VIRTUAL_ENV}/bin/python manage.py test web employee portal  --verbosity=2  --keepdb    --force-color

.PHONY: run
run: ## Run the Django server
	doppler run -- 	$(PYTHON) manage.py runserver 8080

.PHONY: admin
admin:
	doppler run  --  $(PYTHON) manage.py createsuperuser --no-input

.PHONY: start
start:
	doppler run  --  gunicorn --workers=2  --threads=2 nhhc.wsgi:application -b :8080

deploy: install migrate start ## Install requirements, apply migrations, then start development server\\\\\\\\\
