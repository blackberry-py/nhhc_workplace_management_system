# Define constants
# DEV_ENV_RUNNING_IN_CONTAINER ?= false
VENV_DIR := .venv
PYTHON := python3
BIN := $(VENV_DIR)/bin
PYTHON_INTERPRETER := $(BIN)/$(PYTHON)
SHELL := /bin/bash
CURRENT_DATE := $(shell date +"%Y-%m-%d-%T")
TOKEN := ${DOPPLER_TOKEN}
DOCKER_PATH := $(CONTAINER_PATH_EX)

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY:
venv: ## Make a new virtual environment
	python3 -m venv $(VENV) && source $(BIN)/activate

.PHONY: collect
collect:
	doppler run -- python  manage.py collectstatic --no-input

.PHONY: install
install: ## Make venv and install requirements
	pip install -r ./requirements.txt


freeze: ## Pin current dependencies
	$(BIN)/pip freeze > ../requirements.txt

migrate: ## Make and run migrations
	doppler run   --  	python manage.py makemigrations
	doppler run  --  	python manage.py migrate

lint:
	doppler run -t $(TOKEN)  --  prospector  -w  pylint pyroma mypy dodgy mccabe bandit profile-validator > prospector_results_${CURRENTDATE}.json

db-shell: ## Access the Postgres Docker database interactively with psql. Pass in DBNAME=<name>.
	docker exec -it container_name psql -d $(DBNAME)
.PHONY: 	docs
docs:
	nohup doppler run  --command="cd ./docs && npx docsify init && npx docsify serve ." &
.PHONY: workers
workers: docs
	doppler run   --  celery -A nhhc worker -D --loglevel debug -n %d

.PHONY: test
test: ## Run tests
	doppler run -- coverage run manage.py test web --settings=nhhc.test_settings --verbosity=2 --keepdb   --failfast  --force-color

.PHONY: test
pipeline-test: ## Run tests
	${VIRTUAL_ENV}/bin/python $(DOCKER_PATH)manage.py test web employee portal  --verbosity=2  --keepdb   --force-color


.PHONY: flower
flower: workers
	nohup doppler run  --  celery -A nhhc flower --port=9050 &



.PHONY: run
run:
	doppler run   -- python manage.py runserver 9555

.PHONY: debug
debug: ## Run the Django server
	doppler run   --  	kolo run manage.py runserver --noreload --nothreading

.PHONY: admin
admin:
	doppler run --   python manage.py createsuperuser --no-input

.PHONY: start
start: flower
	doppler run  --  gunicorn --workers=2  --threads=2 nhhc.wsgi:application -b :8080