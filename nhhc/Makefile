VENV := /workspaces/NettHands/.venv
# BIN := /usr/local/bin
PYTHON := $(BIN)/python3.11
# SHELL := /bin/bash

PYTHON := $(VENV)/bin/python3.11
SHELL := /bin/bash
CURRENTDATE=`date +"%Y-%m-%d-%T"`

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY:
venv: ## Make a new virtual environment
	python3 -m venv $(VENV) && source $(BIN)/activate

.PHONY: install
install: ## Make venv and install requirements
	doppler run  -t $(DOPPLER_TOKEN) -- pip install --upgrade -r ../requirements.txt

freeze: ## Pin current dependencies
	$(BIN)/pip freeze > ../requirements.txt

.PHONY: collect
collect:
	doppler run  -t $(DOPPLER_TOKEN) -- $(PYTHON)  manage.py collectstatic --no-input

migrate: ## Make and run migrations
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON) manage.py makemigrations
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON) manage.py migrate

lint:
	doppler run -t $(DOPPLER_TOKEN) -- prospector  -w  pylint pyroma mypy dodgy mccabe bandit profile-validator > prospector_results_${CURRENTDATE}.json

db-shell: ## Access the Postgres Docker database interactively with psql. Pass in DBNAME=<name>.
	docker exec -it container_name psql -d $(DBNAME)

.PHONY: test
test: ## Run tests
	doppler run -- coverage run manage.py test web employee portal  --verbosity=2 --keepdb   --failfast  --force-color

.PHONY: test
pipeline-test: ## Run tests
	${VIRTUAL_ENV}/bin/python manage.py test web employee portal  --verbosity=2  --keepdb   --force-color

.PHONY: run
run: ## Run the Django server
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON) manage.py runserver 7772

.PHONY: debug
debug: ## Run the Django server
	doppler run -t $(DOPPLER_TOKEN) -- 	kolo run manage.py runserver --noreload --nothreading

.PHONY: admin
admin:
	doppler run -t $(DOPPLER_TOKEN) --  $(PYTHON) manage.py createsuperuser --no-input

.PHONY: start
start:
	doppler run -t $(DOPPLER_TOKEN)  --  gunicorn --workers=2  --threads=2 nhhc.wsgi:application -b 127.0.0.1:8080
.PHONY: workers
workers:
	doppler run -t $(DOPPLER_TOKEN)  --  celery -A nhhc worker -D --loglevel debug
