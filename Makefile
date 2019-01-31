update-deps:
	pip-compile --upgrade --generate-hashes --output-file requirements/main.txt requirements/main.in
	pip-compile --upgrade --generate-hashes --output-file requirements/dev.txt requirements/dev.in

init:
	pip install --editable .
	pip install --upgrade -r requirements.txt  -r dev-requirements.txt
	rm -rf .tox

update: update-deps init

.PHONY: update-deps init update