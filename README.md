# StageSarcophage

Application web Flask pour centraliser des documents PDF de modes dégradés.

Le but est de récupérer régulièrement des PDF depuis des sources internes
SFTP, SMB/CIFS ou locales, de les stocker localement, de vérifier leur fraîcheur
et de permettre aux utilisateurs autorisés de les consulter même si les outils
métier habituels sont indisponibles.

## Technologies

- Python 3 avec Flask pour le backend web.
- Jinja pour générer les pages HTML côté serveur.
- Bootstrap pour l'interface.
- SQLite avec SQLAlchemy pour la base de données.
- Flask-Login pour les sessions utilisateur.
- bcrypt pour les mots de passe.
- Paramiko pour SFTP.
- smbprotocol pour SMB/CIFS.
- APScheduler pour les tâches automatiques.
- SMTP pour les notifications email.
- Docker et Gunicorn pour un lancement production.
- Pytest pour les tests.

## Lancement local

Créer l'environnement Python:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Créer un fichier `.env` à partir de l'exemple:

```bash
cp .env.example .env
```

Modifier au minimum:

```bash
SECRET_KEY=...
ENCRYPTION_KEY=...
STORAGE_DIR=/chemin/vers/le/dossier/data
FLASK_ENV=development
```

Pour générer les clés:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
.venv/bin/python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Initialiser la base:

```bash
set -a
. ./.env
set +a
.venv/bin/flask --app run.py init-db
```

Créer un administrateur:

```bash
.venv/bin/flask --app run.py create-admin --username admin --password admin12345
```

Lancer le serveur:

```bash
.venv/bin/flask --app run.py run --host 0.0.0.0 --port 5000
```

Ouvrir ensuite:

```text
http://127.0.0.1:5000/login
```

Identifiants de test si vous avez créé l'admin ci-dessus:

```text
Utilisateur: admin
Mot de passe: admin12345
```

## Lancement déjà préparé sur ce poste

Dans l'environnement actuel, le serveur peut être lancé avec:

```bash
set -a
. ./.env
set +a
.venv/bin/flask --app run.py run --host 0.0.0.0 --port 5000
```

Pour l'arrêter si un serveur est déjà lancé en arrière-plan:

```bash
kill $(cat logs/dev-server.pid)
```

Pour voir les logs:

```bash
tail -f logs/dev-server.log
```

## Vérifications rapides

Healthcheck public:

```bash
curl http://127.0.0.1:5000/api/v1/health
```

Tests automatisés:

```bash
.venv/bin/python -m pytest -q
```

## Tester l'application

Depuis l'interface web:

1. Se connecter avec un compte administrateur.
2. Aller dans `Sources`.
3. Créer une source SFTP, SMB ou locale.
4. Tester la connexion.
5. Lancer une synchronisation.
6. Aller dans `Documents`.
7. Vérifier la liste, les filtres, le tri et la pagination.
8. Ouvrir un PDF avec `Voir`.
9. Télécharger un PDF.
10. Sélectionner plusieurs documents et télécharger un ZIP.
11. Aller dans `Journaux` pour vérifier les événements.
12. Aller dans `Administration` pour gérer utilisateurs, rôles, tokens et notifications.

API:

```text
http://127.0.0.1:5000/api/v1/docs
```

## Fonctionnalités principales

- Authentification locale.
- Authentification LDAP optionnelle.
- Gestion des rôles et permissions.
- Sources SFTP, SMB/CIFS et locales.
- Test de connexion des sources.
- Vérification des fingerprints SSH SFTP.
- Synchronisation manuelle et planifiée.
- Statuts document: OK, avertissement, critique, purgé.
- Notifications email pour documents critiques et erreurs répétées.
- Liste des documents avec filtres, tri et pagination.
- Viewer PDF.
- Téléchargement PDF et ZIP.
- Archivage et restauration des sources.
- Purge avec corbeille.
- Journaux d'audit.
- Rapports PDF et Excel.
- API REST avec tokens.
- Documentation Swagger.

## Docker

Construire et lancer:

```bash
docker compose build
docker compose up -d
```

Initialiser la base dans le conteneur:

```bash
docker compose exec web flask init-db
docker compose exec web flask create-admin --username admin --password admin12345
```

Logs:

```bash
docker compose logs -f web
```

Arrêt:

```bash
docker compose down
```

En production, placer l'application derrière un reverse proxy HTTPS et configurer
les variables `FORCE_HTTPS`, `TRUST_PROXY` et `SESSION_COOKIE_SECURE` selon le
mode de terminaison TLS.

## Commandes utiles

Mettre à jour une base existante après changement de version:

```bash
.venv/bin/flask --app run.py upgrade-db
```

Relancer une initialisation idempotente:

```bash
.venv/bin/flask --app run.py init-db
```

## Données importantes

À sauvegarder en production:

- la base SQLite;
- le dossier de stockage des PDF;
- le fichier `.env`;
- les logs si l'historique technique est nécessaire.
