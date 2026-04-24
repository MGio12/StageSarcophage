FROM python@sha256:520153e2deb359602c9cffd84e491e3431d76e7bf95a3255c9ce9433b76ab99a

# Utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Dépendances installées en premier (cache Docker optimal)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Script de démarrage
COPY entrypoint.sh /entrypoint.sh
# Supprime les CRLF éventuels (fichier édité sous Windows)
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

# Code applicatif
COPY . .

# Répertoires avec les bons droits
RUN mkdir -p /data/modes-degrades /app/instance /app/logs \
    && chown -R appuser:appuser /app /data/modes-degrades \
    && chown appuser:appuser /entrypoint.sh

USER appuser

ENV FLASK_ENV=production \
    FLASK_APP=run.py \
    STORAGE_DIR=/data/modes-degrades \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
