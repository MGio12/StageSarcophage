PYTHON ?= .venv/bin/python

.PHONY: check test lint security audit secrets permissions

check: lint test security audit secrets permissions

test:
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check app tests scripts --select E9,F63,F7,F82

security:
	$(PYTHON) -m bandit -r app config.py run.py -q

audit:
	$(PYTHON) -m pip_audit -r requirements.txt -r requirements-dev.txt

secrets:
	$(PYTHON) scripts/scan_tracked_secrets.py

permissions:
	$(PYTHON) scripts/check_permissions.py --env-file .env
