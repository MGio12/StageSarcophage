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
| **ldap3** | Authentification LDAP / Active Directory |
| **openpyxl** | Export rapports Excel |
| **reportlab** | Export rapports PDF |

---

## 2. Schéma de base de données

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     roles       │       │     users       │       │   api_tokens    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ role_id (FK)    │◄──────│ user_id (FK)    │
│ nom             │       │ id (PK)         │       │ id (PK)         │
│ permissions JSON│       │ username        │       │ token_hash      │
│ description     │       │ password_hash   │       │ nom             │
│ created_at      │       │ is_active       │       │ created_at      │
└─────────────────┘       │ created_at      │       │ expires_at      │
                          │ last_login      │       │ last_used_at    │
                          └────────┬────────┘       │ is_active       │
                                   │                └─────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│notification_conf│     │     sources     │     │  ssh_fingerprints│
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │◄────│ source_id (FK)  │
│ user_id (FK)    │     │ nom             │     │ hostname        │
│ email           │     │ protocole       │     │ fingerprint     │
│ notif_erreurs   │     │ adresse         │     └─────────────────┘
│ notif_critiques │     │ echecs_consec.  │
│ actif           │     │ ...             │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
             ┌─────────────────┐       ┌─────────────────┐
             │   documents     │       │    journaux     │
             ├─────────────────┤       ├─────────────────┤
             │ id (PK)         │       │ id (PK)         │
             │ source_id (FK)  │       │ source_id (FK)  │
             │ nom_fichier     │       │ user_id (FK)    │
             │ statut          │       │ type_evenement  │
             │ ...             │       │ ...             │
             └─────────────────┘       └─────────────────┘
```

### Tables Phase 2

| Table | Description |
|-------|-------------|
| **roles** | Rôles utilisateurs (`admin`, `operateur`, `lecteur`) avec permissions JSON |
| **api_tokens** | Tokens d'authentification API |
| **notification_configs** | Destinataires des alertes email |
| **settings** | Paramètres globaux (clé/valeur) |

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

### Administration (`/admin`) — Phase 2

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/utilisateurs` | Liste des utilisateurs |
| GET/POST | `/admin/utilisateurs/nouveau` | Créer utilisateur |
| GET/POST | `/admin/utilisateurs/<id>/modifier` | Modifier utilisateur |
| POST | `/admin/utilisateurs/<id>/activer` | Activer utilisateur |
| POST | `/admin/utilisateurs/<id>/desactiver` | Désactiver utilisateur |
| GET | `/admin/roles` | Liste des rôles |
| GET/POST | `/admin/roles/nouveau` | Créer rôle |
| GET/POST | `/admin/roles/<id>/modifier` | Modifier rôle (permissions) |
| POST | `/admin/roles/<id>/supprimer` | Supprimer rôle |
| GET | `/admin/tokens` | Liste des tokens API |
| GET/POST | `/admin/tokens/nouveau` | Créer token |
| POST | `/admin/tokens/<id>/revoquer` | Révoquer token |
| GET | `/admin/notifications` | Destinataires notifications |
| GET/POST | `/admin/notifications/nouveau` | Ajouter destinataire |
| POST | `/admin/notifications/test` | Envoyer email test |
| GET | `/admin/parametres` | Paramètres globaux |
| POST | `/admin/parametres/modifier` | Modifier paramètres |
| GET | `/admin/ldap` | Configuration LDAP |
| POST | `/admin/ldap/test` | Tester connexion LDAP |
| POST | `/admin/ldap/sync-groupes` | Synchroniser groupes AD |

### Rapports (`/`) — Phase 2

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/rapport.xlsx` | Export Excel conformité |
| GET | `/rapport.pdf` | Export PDF conformité |

### API REST (`/api/v1`) — Phase 2

Authentification : Header `Authorization: Bearer <token>`

**Documentation interactive** : `/api/v1/docs` (Swagger UI)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/health` | État de l'application (public) |
| GET | `/api/v1/stats` | Statistiques globales |
| GET | `/api/v1/sources` | Liste des sources |
| GET | `/api/v1/sources/<id>` | Détail source |
| POST | `/api/v1/sources/<id>/sync` | Déclencher sync |
| GET | `/api/v1/sources/<id>/status` | État connexion |
| GET | `/api/v1/documents` | Liste paginée (filtres: source_id, statut) |
| GET | `/api/v1/documents/<id>` | Métadonnées document |
| GET | `/api/v1/documents/<id>/download` | Télécharger fichier |
| GET | `/api/v1/openapi.json` | Spécification OpenAPI 3.0 |
| GET | `/api/v1/docs` | Interface Swagger UI |

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

### Variables principales

| Variable | Requis | Description | Exemple |
|----------|--------|-------------|---------|
| `SECRET_KEY` | **Oui** | Clé secrète Flask (64 chars hex) | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | **Oui** | Clé Fernet pour chiffrer identifiants | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `FLASK_ENV` | Non | `development` ou `production` | `production` |
| `DATABASE_URL` | Non | URL SQLAlchemy | `sqlite:///instance/app.db` |
| `STORAGE_DIR` | Non | Répertoire PDF | `/data/modes-degrades` |
| `TZ` | Non | Fuseau horaire | `Europe/Paris` |

### Variables SMTP (notifications) — Phase 2

| Variable | Requis | Description | Exemple |
|----------|--------|-------------|---------|
| `SMTP_HOST` | Non | Serveur SMTP | `smtp.example.com` |
| `SMTP_PORT` | Non | Port SMTP (défaut: 587) | `587` |
| `SMTP_USER` | Non | Utilisateur SMTP | `notifications@example.com` |
| `SMTP_PASSWORD` | Non | Mot de passe SMTP | |
| `SMTP_FROM` | Non | Adresse expéditeur | `noreply@example.com` |
| `SMTP_USE_TLS` | Non | Utiliser STARTTLS (défaut: true) | `true` |

### Variables LDAP (authentification AD) — Phase 2

| Variable | Requis | Description | Exemple |
|----------|--------|-------------|---------|
| `LDAP_ENABLED` | Non | Activer LDAP (défaut: false) | `true` |
| `LDAP_HOST` | Non | Serveur LDAP/AD | `dc01.example.local` |
| `LDAP_PORT` | Non | Port LDAP (défaut: 389) | `389` |
| `LDAP_USE_SSL` | Non | LDAPS (défaut: false) | `false` |
| `LDAP_BASE_DN` | Non | Base DN pour recherche | `DC=example,DC=local` |
| `LDAP_BIND_DN` | Non | DN du compte de service | `CN=svc_app,OU=Services,DC=example,DC=local` |
| `LDAP_BIND_PASSWORD` | Non | Mot de passe du compte de service | |
| `LDAP_USER_FILTER` | Non | Filtre de recherche utilisateur | `(sAMAccountName={username})` |
| `LDAP_DEFAULT_ROLE` | Non | Rôle par défaut (défaut: lecteur) | `lecteur` |
| `LDAP_SYNC_GROUPS` | Non | Activer sync groupes (défaut: false) | `true` |
| `LDAP_GROUP_MAPPING` | Non | Mapping groupes AD → rôles | `CN=Admins,DC=...:admin;CN=Users,DC=...:lecteur` |

### Variables corbeille

| Variable | Requis | Description | Exemple |
|----------|--------|-------------|---------|
| `CORBEILLE_RETENTION_JOURS` | Non | Jours avant suppression définitive (défaut: 30) | `30` |

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
│   ├── crypto.py        # Fonctions chiffrer/dechiffrer
│   └── decorators.py    # @require_role, @require_permission (Phase 2)
├── models/
│   ├── source.py        # Sources de collecte
│   ├── document.py      # Documents PDF
│   ├── journal.py       # Événements d'audit
│   ├── user.py          # Utilisateurs
│   ├── role.py          # Rôles et permissions (Phase 2)
│   ├── api_token.py     # Tokens API (Phase 2)
│   ├── notification_config.py  # Config notifications (Phase 2)
│   ├── setting.py       # Paramètres globaux (Phase 2)
│   └── ssh_fingerprint.py
├── routes/
│   ├── auth.py          # /auth/* (+ LDAP Phase 2)
│   ├── main.py          # / (dashboard, rapports)
│   ├── sources.py       # /sources/*
│   ├── documents.py     # /documents/*
│   ├── journaux.py      # /journaux/*
│   ├── admin.py         # /admin/* (Phase 2)
│   └── api.py           # /api/v1/* (Phase 2)
├── services/
│   ├── sync_service.py  # Orchestration synchronisation
│   ├── sftp_service.py  # Connecteur SFTP
│   ├── smb_service.py   # Connecteur SMB
│   ├── purge_service.py # Purge automatique/manuelle + corbeille
│   ├── email_service.py # Envoi emails SMTP (Phase 2)
│   ├── notification_service.py  # Alertes (Phase 2)
│   ├── ldap_service.py  # Authentification LDAP + sync groupes (Phase 2)
│   ├── export_service.py  # Rapports PDF/Excel (Phase 2)
│   └── report_service.py  # Envoi automatique rapports (Phase 2)
├── scheduler/
│   └── tasks.py         # Tâches APScheduler
└── templates/           # Templates Jinja2
```
