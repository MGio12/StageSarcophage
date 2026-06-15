# Arche

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
chmod 600 .env
```

Variables minimales:

```env
SECRET_KEY=change-me
ENCRYPTION_KEY=change-me
STORAGE_DIR=/data/modes-degrades
FLASK_ENV=development
```

Générer les clés:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

En production, le fichier `.env` doit rester hors Git et lisible uniquement par l'utilisateur qui lance l'application.
En Docker, `docker-compose.yml` force `FLASK_ENV=production` et `STORAGE_DIR=/data/modes-degrades`; le fichier `.env` fournit surtout les secrets et les options d'infrastructure.

Pour un lancement local depuis le dépôt, `STORAGE_DIR` peut pointer vers le dossier `data` du projet. Remplacer `/chemin/vers/Arche` par le chemin absolu du dépôt:

```env
STORAGE_DIR=/chemin/vers/Arche/data
```

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

## Configuration SMTP

Les emails servent aux notifications et aux rapports envoyés depuis l'interface d'administration. La configuration se fait dans le fichier `.env` local, non versionné. En Docker, ce fichier est chargé par le service `web` via `env_file: .env`.

Variables disponibles:

| Variable | Obligatoire | Rôle |
| --- | --- | --- |
| `SMTP_HOST` | Oui pour activer l'envoi | Hostname ou IP du serveur SMTP. Si vide, aucun email n'est envoyé. |
| `SMTP_PORT` | Oui | Port du serveur SMTP. Utiliser généralement `587` avec STARTTLS, ou `25` pour un relais interne sans TLS applicatif. |
| `SMTP_USER` | Selon serveur | Identifiant SMTP. À laisser vide si le relais n'exige pas d'authentification. |
| `SMTP_PASSWORD` | Selon serveur | Mot de passe SMTP. À laisser vide si le relais n'exige pas d'authentification. |
| `SMTP_FROM` | Oui | Adresse expéditeur visible dans les emails. Elle doit souvent être autorisée par le serveur SMTP. |
| `SMTP_USE_TLS` | Oui | `true` active STARTTLS après connexion SMTP ; `false` désactive STARTTLS. |

Exemple pour un relais interne sans authentification:

```env
SMTP_HOST=smtp.interne.local
SMTP_PORT=25
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=arche@example.local
SMTP_USE_TLS=false
```

Exemple pour un SMTP authentifié avec STARTTLS:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=arche@example.com
SMTP_PASSWORD=mot-de-passe-ou-token
SMTP_FROM=arche@example.com
SMTP_USE_TLS=true
```

Le port `465` correspond souvent à SMTPS implicite. L'application actuelle utilise `SMTP` puis `STARTTLS`, pas `SMTP_SSL`; préférer donc le port `587` si TLS est requis.

Après modification de `.env` en Docker, recréer le conteneur web pour relire les variables:

```bash
docker compose up -d --force-recreate web
```

En lancement local, arrêter Flask puis relancer après avoir rechargé `.env`:

```bash
set -a
. ./.env
set +a
.venv/bin/flask --app run.py run --host 0.0.0.0 --port 5000
```

Tester ensuite depuis l'interface: `Administration > Notifications > Envoyer un email test`.

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

Ouvrir ensuite l'interface:

```text
http://127.0.0.1:5000
```

Healthcheck:

```bash
curl http://127.0.0.1:5000/api/v1/health
```

Documentation API locale:

```text
http://127.0.0.1:5000/api/v1/docs
```

## Tester une collecte locale

Pour vérifier le fonctionnement sans serveur SFTP ou SMB, utiliser une source locale.

Ajouter une racine locale autorisée dans `.env`:

```env
LOCAL_SOURCE_ALLOWED_ROOTS=/chemin/vers/Arche/data/sources
```

Créer un dossier source de test avec un PDF minimal:

```bash
mkdir -p data/sources/demo
printf '%s\n' '%PDF-1.4 test' > data/sources/demo/test.pdf
```

Redémarrer Flask si le serveur était déjà lancé, puis dans l'interface:

1. Aller dans `Sources`.
2. Cliquer sur `Nouvelle source`.
3. Choisir le protocole `Local / Montage réseau`.
4. Renseigner le chemin `/chemin/vers/Arche/data/sources/demo`.
5. Cocher `Synchroniser après création` ou lancer la synchronisation depuis la fiche source.

Le document doit ensuite apparaître dans `Documents`, avec un statut de fraîcheur.

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
