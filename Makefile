# Common tasks
.PHONY: init migrate run shell test

init:
	python -m pip install --upgrade pip
	pip install -r backend/requirements.txt
	cp .env.example .env || true

migrate:
	python backend/manage.py migrate

run:
	python backend/manage.py runserver 0.0.0.0:8000

shell:
	python backend/manage.py shell

test:
	pytest
