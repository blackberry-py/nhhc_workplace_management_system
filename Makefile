# Define constants
# DEV_ENV_RUNNING_IN_CONTAINER ?= false
VENV_DIR=.venvy
venv: ## Make a new virtual environment
	python3 -m venv $(VENV) && source $(BIN)/activate

.PHONY: collect
collect:
	doppler -t $(TOKEN) run -- python  $(DOCKER_PATH)manage.py collectstatic --no-input

.PHONY: install
install: ## Make venv and install requirements
	pip install -r ./requirements.txtnhh

freeze: ## Pin current dependencies
	$(BIN)/pip freeze > ../requirements.txt

migrate: ## Make and run migrations
	doppler run -t $(TOKEN)  --  	$(PYTHON_INTERPRETER) $(DOCKER_PATH)manage.py makemigrations
	doppler run -t $(TOKEN)  --  	$(PYTHON_INTERPRETER) $(DOCKER_PATH)manage.py migrate

lint:
	doppler run -t $(TOKEN)  --  prospector  -w  pylint pyroma mypy dodgy mccabe bandit profile-validator > prospector_results_${CURRENTDATE}.json

db-shell: ## Access the Postgres Docker database interactively with psql. Pass in DBNAME=<name>.
	docker exec -it container_name psql -d $(DBNAME)

.PHONY: workers
workers:
	cd nhhc/
	doppler run -t $(TOKEN)  --  celery -A nhhc worker --without-heartbeat --without-gossip --without-mingle -D --loglevel debug

.PHONY: test
test: ## Run tests
	doppler run -- coverage run $(DOCKER_PATH)manage.py test web employee portal  --verbosity=2 --keepdb   --failfast  --force-color

.PHONY: test
pipeline-test: ## Run tests
	${VIRTUAL_ENV}/bin/python $(DOCKER_PATH)manage.py test web employee portal  --verbosity=2  --keepdb   --force-color


.PHONY: flower
flower:
	nohup doppler run -t $(TOKEN)  --  celery -A nhhc flower --port=9005

.PHONY: 	docs
docs:
	nohup doppler run -t $(DOPPL/Users/terry-brooks/Documents/NettHands/.venvER_TOKEN) -- cd ./docs && docsify serve docs

.PHONY: run
run:
	doppler run -t dp.st.prod.tzlzucONGjZqzA8yWrQxcYruK5DJInVfgOXAxrqfJsQ  --  python3  nhhc/manage.py runserver 9555

.PHONY: debug
debug: ## Run the Django server
	doppler run -t $(TOKEN)  --  	kolo run $(DOCKER_PATH)manage.py runserver --noreload --nothreading

.PHONY: admin
admin:
	doppler run -t $(TOKEN)  --   $(PYTHON_INTERPRETER) manage.py createsuperuser --no-input

.PHONY: start
start:
	doppler run -t $(TOKEN)  --  gunicorn --workers=2  --threads=2 nhhc.wsgi:application -b :7772
