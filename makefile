include common.mk

# Our directories
API_DIR = server
DB_DIR = data
SEC_DIR = security
REQ_DIR = .

FORCE:

prod: all_tests github

github: FORCE
	- git commit -a
	git push origin master

all_tests: FORCE
	cd $(API_DIR); make tests
	# cd $(DB_DIR); make tests

dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt

docs: FORCE
	cd $(API_DIR); make docs

local_db:
	docker compose exec -e PYTHON=python api bash data/places/load.sh

local_build:
	docker compose up -d mongo
	docker compose up --build --no-deps api

# detaches api container logs from terminal
local_build_quiet:
	docker compose up -d mongo
	docker compose up -d mariadb
	docker compose up --build --no-deps -d api

# disables security
# detaches api container logs from terminal
local_build_no_sec_quiet:
	docker compose up -d mongo
	docker compose up -d mariadb
	AUTH_BYPASS=1 docker compose up --build --no-deps -d api

clean: 
	docker compose down