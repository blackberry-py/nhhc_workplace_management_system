# Define constants
# DEV_ENV_RUNNING_IN_CONTAINER ?= false
VENV_DIR := $(if $(DEV_ENV_RUNNING_IN_CONTAINER), /workspaces/NettHands/.venv, /Users/terry-brooks/GitHub/NettHands/.venv)
PYTHON := python3
BIN := $(VENV_DIR)/bin
PYTHON_INTERPRETER := $(BIN)/$(PYTHON)
SHELL := /bin/bash
CURRENT_DATE := $(shell date +"%Y-%m-%d-%T")


.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY:
venv: ## Make a new virtual environment
	python3 -m venv $(VENV) && source $(BIN)/activate

.PHONY: install
install: venv ## Make venv and install requirements
	doppler run  -t $(DOPPLER_TOKEN) -- pip install --upgrade -r ./requirements.txt

freeze: ## Pin current dependencies
	$(BIN)/pip freeze > ../requirements.txt

.PHONY: collect
collect:
	doppler run  -t $(DOPPLER_TOKEN) -- $(PYTHON_INTERPRETER)  manage.py collectstatic --no-input

migrate: ## Make and run migrations
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON_INTERPRETER) manage.py makemigrations
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON_INTERPRETER) manage.py migrate

lint:
	doppler run -t $(DOPPLER_TOKEN) -- prospector  -w  pylint pyroma mypy dodgy mccabe bandit profile-validator > prospector_results_${CURRENTDATE}.json

db-shell: ## Access the Postgres Docker database interactively with psql. Pass in DBNAME=<name>.
	docker exec -it container_name psql -d $(DBNAME)

.PHONY: workers
workers:
	cd nhhc/
	doppler run -t $(DOPPLER_TOKEN)  --  celery -A nhhc worker --without-heartbeat --without-gossip --without-mingle -D --loglevel debug

.PHONY: test
test: ## Run tests
	doppler run -- coverage run manage.py test web employee portal  --verbosity=2 --keepdb   --failfast  --force-color

.PHONY: test
pipeline-test: ## Run tests
	${VIRTUAL_ENV}/bin/python manage.py test web employee portal  --verbosity=2  --keepdb   --force-color


.PHONY: flower
flower:
	nohup doppler run -t $(DOPPLER_TOKEN) -- celery -A nhhc flower --port=9005

.PHONY: 	docs
docs:
	nohup doppler run -t $(DOPPL/Users/terry-brooks/Documents/NettHands/.venvER_TOKEN) -- cd ./docs && docsify serve docs






.PHONY: run
run:
	doppler run -t $(DOPPLER_TOKEN) -- 	$(PYTHON_INTERPRETER) manage.py runserver 9555

.PHONY: debug
debug: ## Run the Django server
	doppler run -t $(DOPPLER_TOKEN) -- 	kolo run manage.py runserver --noreload --nothreading

.PHONY: admin
admin:
	doppler run -t $(DOPPLER_TOKEN) --  $(PYTHON_INTERPRETER) manage.py createsuperuser --no-input

.PHONY: start
start:
	doppler run -t $(DOPPLER_TOKEN)  --  gunicorn --workers=2  --threads=2 nhhc.wsgi:application -b :7772
