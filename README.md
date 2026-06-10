# StageSarcophage

Application Flask de centralisation et de suivi de documents PDF de modes dégradés.

L'application collecte des PDF depuis des sources internes SFTP, SMB/CIFS ou locales, conserve une copie dans un stockage contrôlé, calcule leur fraîcheur et permet la consultation par des utilisateurs autorisés. Elle fournit une interface web, une API REST avec tokens, des journaux d'audit, des jobs de synchronisation/purge et des exports de conformité.

## Fonctionnalités

- Authentification locale et LDAP optionnelle.
- Rôles, permissions et tokens API.
- Sources SFTP, SMB/CIFS et locales.
- Test de connexion et vérification des fingerprints SSH.
- Synchronisation manuelle et planifiée.
- Déduplication par hash SHA-256.
- Statuts document: OK, avertissement, critique, purgé.
- Viewer PDF, téléchargement PDF et export ZIP.
- Purge avec corbeille et restauration.
- Journaux d'audit.
- Rapports PDF et Excel.
- Notifications email configurables.

## Prérequis

- Python 3.12 recommandé.
- Docker et Docker Compose pour le lancement conteneurisé.
- Un fichier `.env` local non versionné.

## Configuration

Créer le fichier d'environnement:

```bash
cp .env.example .env
```

Variables minimales:

```env
SECRET_KEY=change-me
ENCRYPTION_KEY=change-me
STORAGE_DIR=/data/modes-degrades
FLASK_ENV=production
```

Générer les clés:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

En production, le fichier `.env` doit rester hors Git et lisible uniquement par l'utilisateur qui lance l'application.

## Lancement Docker

Construire et démarrer:

```bash
docker compose build
docker compose up -d
```

Initialiser la base et créer un administrateur:

```bash
docker compose exec web flask init-db
docker compose exec web flask create-admin --username admin --password 'mot-de-passe-solide'
```

Suivre les logs:

```bash
docker compose logs -f web
```

Arrêter:

```bash
docker compose down
```

Le conteneur expose HTTP sur le port `5000`. En production, placer l'application derrière un reverse proxy HTTPS. Si TLS est terminé par le proxy, configurer les variables suivantes selon l'infrastructure:

```env
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
TRUST_PROXY=true
```

## Lancement Local

Créer l'environnement Python:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Charger l'environnement et initialiser la base:

```bash
set -a
. ./.env
set +a
.venv/bin/flask --app run.py init-db
.venv/bin/flask --app run.py create-admin --username admin --password 'mot-de-passe-solide'
```

Démarrer le serveur:

```bash
.venv/bin/flask --app run.py run --host 0.0.0.0 --port 5000
```

Healthcheck:

```bash
curl http://127.0.0.1:5000/api/v1/health
```

Documentation API locale:

```text
http://127.0.0.1:5000/api/v1/docs
```

## Exploitation

Éléments à sauvegarder:

- base SQLite du volume `db_data` ou du dossier `instance`;
- stockage PDF du volume `pdf_data` ou du dossier configuré par `STORAGE_DIR`;
- fichier `.env`;
- logs si l'historique technique doit être conservé.

Commandes utiles:

```bash
.venv/bin/flask --app run.py init-db
.venv/bin/flask --app run.py upgrade-db
.venv/bin/flask --app run.py rotate-encryption-key
```

La rotation Fernet nécessite de définir `OLD_ENCRYPTION_KEY` et `NEW_ENCRYPTION_KEY` avant la commande.

## Qualité

Installer les dépendances de développement puis lancer:

```bash
make check
```

La commande exécute les tests, Ruff, Bandit, `pip-audit`, le scan de secrets suivis par Git et le contrôle des permissions du fichier `.env`.

Commandes ciblées:

```bash
make test
make lint
make security
make audit
make secrets
make permissions
```
