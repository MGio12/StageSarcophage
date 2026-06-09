PYTHON ?= .venv/bin/python
CHROME ?= google-chrome
RAPPORT_DIR = rapport_stage
RAPPORT_MD  = $(RAPPORT_DIR)/rapport_stage.md
RAPPORT_HTML= $(RAPPORT_DIR)/rapport_stage.html
RAPPORT_PDF = $(RAPPORT_DIR)/rapport_stage.pdf
RAPPORT_CSS = $(RAPPORT_DIR)/rapport_stage.css

.PHONY: check test lint security audit secrets permissions rapport rapport-html rapport-pdf rapport-odt

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

rapport: rapport-html rapport-pdf

rapport-html:
	pandoc $(RAPPORT_MD) \
	  --standalone \
	  --css $(RAPPORT_CSS) \
	  --metadata title="Rapport de stage - Maxime Giovanelli" \
	  -o $(RAPPORT_HTML)

rapport-pdf:
	$(CHROME) --headless=new --disable-gpu \
	  --no-pdf-header-footer \
	  --print-to-pdf=$(RAPPORT_PDF) \
	  "file://$(abspath $(RAPPORT_HTML))"

rapport-odt:
	pandoc $(RAPPORT_MD) --resource-path=$(RAPPORT_DIR) -o $(RAPPORT_DIR)/rapport_stage.odt
