#!/bin/sh
set -e

# Initialise les tables SQLite au premier démarrage (idempotent)
flask init-db

# 1 worker pour éviter les doublons APScheduler (scheduler in-process)
exec gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 1 \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  run:app
