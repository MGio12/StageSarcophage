# Documentation Technique — Modes Dégradés

## 1. Architecture générale

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NAVIGATEUR WEB                              │
│                    (interface utilisateur)                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FLASK (Gunicorn)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   Routes     │  │   Services   │  │   Scheduler  │               │
│  │  (Blueprints)│  │   (Sync,     │  │ (APScheduler)│               │
│  │              │  │    Purge)    │  │              │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                              │                                       │
│                     SQLAlchemy ORM                                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  SQLite       │    │   Stockage      │    │   Sources       │
│  (instance/)  │    │   local (PDF)   │    │   distantes     │
│               │    │   (/data)       │    │ (SFTP/SMB/Local)│
└───────────────┘    └─────────────────┘    └─────────────────┘
```

### Composants principaux

| Composant | Rôle |
|-----------|------|
| **Flask** | Framework web, factory pattern (`create_app`) |
| **SQLAlchemy** | ORM pour la base SQLite |
| **Flask-Login** | Gestion des sessions utilisateur |
| **APScheduler** | Tâches planifiées (sync, purge) |
| **Paramiko** | Connexions SFTP |
| **smbprotocol** | Connexions SMB |
| **Fernet** | Chiffrement des identifiants sources |
| **bcrypt** | Hachage des mots de passe utilisateurs |

---

## 2. Schéma de base de données

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │     sources     │       │  ssh_fingerprints│
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │◄──────│ source_id (FK)  │
│ username        │       │ nom             │       │ hostname        │
│ password_hash   │       │ description     │       │ port            │
│ is_active       │       │ type_serveur    │       │ key_type        │
│ created_at      │       │ protocole       │       │ fingerprint     │
│ last_login      │       │ adresse         │       │ created_at      │
└────────┬────────┘       │ port            │       └─────────────────┘
         │                │ chemin_distant  │
         │                │ login (chiffré) │
         │                │ mot_de_passe    │
         │                │   (chiffré)     │
         │                │ filtre_fichiers │
         │                │ frequence_sync  │
         │                │ retention_jours │
         │                │ seuil_avert.    │
         │                │ seuil_critique  │
         │                │ actif           │
         │                │ deleted_at      │
         │                │ created_at      │
         │                │ updated_at      │
         │                └────────┬────────┘
         │                         │
         │         ┌───────────────┴───────────────┐
         │         ▼                               ▼
         │  ┌─────────────────┐           ┌─────────────────┐
         │  │   documents     │           │    journaux     │
         │  ├─────────────────┤           ├─────────────────┤
         │  │ id (PK)         │           │ id (PK)         │
         │  │ source_id (FK)  │           │ source_id (FK)  │
         │  │ nom_fichier     │           │ user_id (FK) ◄──┼────┘
         │  │ chemin_local    │           │ type_evenement  │
         │  │ hash_sha256     │           │ message         │
         │  │ taille_octets   │           │ details (JSON)  │
         │  │ date_modif_src  │           │ created_at      │
         │  │ date_collecte   │           └─────────────────┘
         │  │ statut          │
         │  │ created_at      │
         │  │ updated_at      │
         │  └─────────────────┘
```

### Énumérations

**StatutDocument** : `ok`, `avertissement`, `critique`, `purge`

**TypeEvenement** : `sync`, `purge`, `erreur`, `connexion`, `acces`

---

## 3. API interne (Routes)

### Authentification (`/auth`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET/POST | `/auth/login` | Connexion utilisateur |
| GET | `/auth/logout` | Déconnexion |

### Tableau de bord (`/`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Tableau de bord (compteurs, alertes) |

### Sources (`/sources`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/sources/` | Liste des sources actives |
| GET | `/sources/archivees` | Liste des sources archivées |
| GET | `/sources/nouvelle` | Formulaire création |
| POST | `/sources/nouvelle` | Créer une source |
| GET | `/sources/<id>` | Détails source |
| GET | `/sources/<id>/modifier` | Formulaire modification |
| POST | `/sources/<id>/modifier` | Modifier source |
| POST | `/sources/<id>/supprimer` | Suppression logique |
| POST | `/sources/<id>/restaurer` | Restaurer source |
| POST | `/sources/<id>/tester` | Tester connexion |
| POST | `/sources/<id>/synchroniser` | Sync manuelle |
| POST | `/sources/<id>/purger` | Purge manuelle |
| POST | `/sources/<id>/accepter-fingerprint` | Accepter clé SSH |

### Documents (`/documents`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/documents/` | Liste paginée avec filtres |
| GET | `/documents/<id>/telecharger` | Télécharger PDF |
| POST | `/documents/telecharger-selection` | ZIP des sélectionnés |

**Paramètres de filtre** : `source_id`, `statut`, `depuis`, `jusqua`

### Journaux (`/journaux`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/journaux/` | Liste paginée avec filtres |
| GET | `/journaux/exporter` | Export CSV |

---

## 4. Guide de déploiement Docker

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+

### Structure des fichiers

```
.
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── .env              # À créer depuis .env.example
├── requirements.txt
└── ...
```

### Déploiement

```bash
# 1. Cloner le dépôt
git clone <url> && cd StageSarcophage

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec les clés de production (voir section 5)

# 3. Construire et lancer
docker compose build
docker compose up -d

# 4. Initialiser la base et créer un admin
docker compose exec web flask init-db
docker compose exec web flask create-admin --username admin --password <motdepasse>

# 5. Vérifier le statut
docker compose ps
docker compose logs -f web
```

### Volumes persistants

| Volume | Chemin conteneur | Usage |
|--------|------------------|-------|
| `pdf_data` | `/data/modes-degrades` | Stockage PDF |
| `db_data` | `/app/instance` | Base SQLite |
| `./logs` | `/app/logs` | Logs applicatifs |

### Arrêt / Redémarrage

```bash
docker compose stop     # Arrêter
docker compose start    # Redémarrer
docker compose down     # Arrêter et supprimer conteneurs
docker compose down -v  # + supprimer volumes (PERTE DE DONNÉES)
```

---

## 5. Variables d'environnement

| Variable | Requis | Description | Exemple |
|----------|--------|-------------|---------|
| `SECRET_KEY` | **Oui** | Clé secrète Flask (64 chars hex) | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | **Oui** | Clé Fernet pour chiffrer identifiants | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `FLASK_ENV` | Non | `development` ou `production` | `production` |
| `DATABASE_URL` | Non | URL SQLAlchemy | `sqlite:///instance/app.db` |
| `STORAGE_DIR` | Non | Répertoire PDF | `/data/modes-degrades` |
| `TZ` | Non | Fuseau horaire | `Europe/Paris` |

### Génération des clés

```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 6. Commandes CLI Flask

```bash
# Activer l'environnement (hors Docker)
source venv/bin/activate

# Initialiser la base de données
flask init-db

# Créer un administrateur
flask create-admin --username <nom> --password <mdp>

# Lancer en développement
FLASK_ENV=development flask run

# Lancer les tests
python -m pytest -v
```

---

## 7. Sécurité

### Mesures implémentées

| Mesure | Détail |
|--------|--------|
| **CSRF** | Token Flask-WTF sur tous les formulaires |
| **XSS** | Headers CSP via Flask-Talisman |
| **Sessions** | Cookie sécurisé (Secure, HttpOnly, SameSite=Lax) |
| **Mots de passe** | bcrypt avec salt |
| **Identifiants sources** | Chiffrés Fernet en base |
| **Rate limiting** | Flask-Limiter (login, API) |
| **Host key SSH** | Vérification stricte avec fingerprints BDD |
| **Image Docker** | Base épinglée par hash SHA256 |

### Validations production

Au démarrage en mode `production`, l'application vérifie :
- `SECRET_KEY` est définie
- `ENCRYPTION_KEY` est une clé Fernet valide

---

## 8. Structure du code

```
app/
├── __init__.py          # Factory create_app()
├── extensions.py        # db, csrf, login_manager, limiter
├── utils/
│   └── crypto.py        # Fonctions chiffrer/dechiffrer
├── models/
│   ├── source.py        # Sources de collecte
│   ├── document.py      # Documents PDF
│   ├── journal.py       # Événements d'audit
│   ├── user.py          # Utilisateurs
│   └── ssh_fingerprint.py
├── routes/
│   ├── auth.py          # /auth/*
│   ├── main.py          # / (dashboard)
│   ├── sources.py       # /sources/*
│   ├── documents.py     # /documents/*
│   └── journaux.py      # /journaux/*
├── services/
│   ├── sync_service.py  # Orchestration synchronisation
│   ├── sftp_service.py  # Connecteur SFTP
│   ├── smb_service.py   # Connecteur SMB
│   └── purge_service.py # Purge automatique/manuelle
├── scheduler/
│   └── tasks.py         # Tâches APScheduler
└── templates/           # Templates Jinja2
```
