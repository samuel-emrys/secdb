update-deps:
	pip-compile --upgrade --generate-hashes --output-file requirements.txt requirements.in
	pip-compile --upgrade --generate-hashes --output-file dev-requirements.txt dev-requirements.in

init:
	#pip install --editable .
	pip install --upgrade -r requirements.txt  -r dev-requirements.txt
	rm -rf .tox

update: update-deps init

.PHONY: update-deps init update