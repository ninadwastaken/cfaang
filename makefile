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
	bash $(DB_DIR)/places/load.sh
