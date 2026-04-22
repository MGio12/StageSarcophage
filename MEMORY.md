# MEMORY — Base de connaissances du projet

> Ce fichier est la mémoire vivante du projet. Il est mis à jour à chaque étape significative.
> Il sert de référence pour tous les agents/développeurs travaillant sur ce code.

---

## 1. Contexte projet

- **Commanditaire** : DSI — CLCC (Centre de Lutte Contre le Cancer)
- **Objectif** : Application web de gestion centralisée des documents de modes dégradés (PDF)
- **Sources** : serveurs Windows (SMB/CIFS) et Linux (SFTP/SCP), chemins réseau locaux
- **Version cahier des charges** : 1.0 — 2026-04-22

---

## 2. Stack technologique décidée

| Composant | Technologie | Version |
|---|---|---|
| Backend | Python / Flask | 3.1.x |
| Base de données | SQLite (WAL mode) | via Flask-SQLAlchemy |
| Scheduler | APScheduler | 3.10.x |
| Accès SFTP | paramiko | 3.5.x |
| Accès SMB | smbprotocol | 1.14.x |
| Chiffrement identifiants | cryptography (Fernet) | 44.x |
| Frontend | Jinja2 + Bootstrap 5 | — |
| PDF viewer | `<iframe>` natif + PDF.js (Phase 2) | — |
| Conteneurisation | Docker + docker-compose | — |

---

## 3. Architecture des fichiers

```
stageSarcophage/
├── app/
│   ├── __init__.py          # Factory Flask (create_app)
│   ├── models/              # Modèles SQLAlchemy
│   │   ├── source.py        # Table sources
│   │   ├── document.py      # Table documents
│   │   └── journal.py       # Table journaux
│   ├── routes/              # Blueprints Flask
│   │   ├── main.py          # Dashboard (/)
│   │   ├── sources.py       # CRUD sources (/sources)
│   │   ├── documents.py     # Consultation (/documents)
│   │   └── journaux.py      # Logs (/journaux)
│   ├── services/            # Logique métier (sans dépendance HTTP)
│   │   ├── sync_service.py  # Orchestration synchronisation
│   │   ├── sftp_service.py  # Connecteur SFTP (paramiko)
│   │   ├── smb_service.py   # Connecteur SMB (smbprotocol)
│   │   └── purge_service.py # Logique de purge
│   ├── scheduler/           # Tâches APScheduler
│   │   └── tasks.py
│   ├── static/              # CSS, JS, assets
│   └── templates/           # Jinja2 HTML
├── instance/                # Config locale + app.db (hors git)
├── tests/                   # pytest
├── data/                    # PDF collectés, organisés par source (hors git)
├── logs/                    # Logs applicatifs (hors git)
├── config.py                # Configs Dev / Prod
├── run.py                   # Point d'entrée
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── MEMORY.md
```

---

## 4. Schéma de base de données

### Table `sources`
| Colonne | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| nom | VARCHAR(100) | unique |
| description | TEXT | nullable |
| type_serveur | VARCHAR(10) | `linux` ou `windows` |
| protocole | VARCHAR(10) | `smb`, `sftp`, `local` |
| adresse | VARCHAR(255) | IP ou hostname |
| port | INTEGER | nullable (22 SFTP, 445 SMB) |
| chemin_distant | TEXT | chemin sur le serveur source |
| login | TEXT | **chiffré Fernet** |
| mot_de_passe | TEXT | **chiffré Fernet** |
| filtre_fichiers | VARCHAR(50) | glob pattern, défaut `*.pdf` |
| frequence_sync_minutes | INTEGER | défaut 60 |
| retention_jours | INTEGER | défaut 90 |
| seuil_avertissement_jours | INTEGER | défaut 30 |
| seuil_critique_jours | INTEGER | défaut 60 |
| actif | BOOLEAN | défaut True |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

### Table `documents`
| Colonne | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| source_id | FK → sources | CASCADE DELETE |
| nom_fichier | VARCHAR(255) | |
| chemin_local | TEXT | chemin absolu local |
| hash_sha256 | VARCHAR(64) | pour dédup |
| taille_octets | INTEGER | |
| date_modification_source | DATETIME | date fichier côté serveur |
| date_collecte | DATETIME | date de la dernière copie |
| statut | VARCHAR(15) | `ok`, `avertissement`, `critique`, `purge` |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

### Table `journaux`
| Colonne | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| source_id | FK → sources | nullable |
| type_evenement | VARCHAR(20) | `sync`, `purge`, `erreur`, `connexion`, `acces` |
| message | TEXT | |
| details | TEXT | JSON sérialisé, nullable |
| created_at | DATETIME | auto |

---

## 5. Conventions de code

- **Pattern** : App Factory (`create_app`) + Blueprints par domaine
- **Services** : toute logique métier dans `app/services/`, indépendante des routes
- **Chiffrement** : Fernet (`cryptography`) — JAMAIS stocker un mot de passe en clair
- **Tâches de fond** : APScheduler en mode `BackgroundScheduler`, démarré dans `create_app`
- **Nommage** : snake_case pour Python, kebab-case pour les routes URL
- **Templates** : Jinja2, organisés par blueprint (`templates/sources/`, etc.)
- **Variables d'env** : `.env` local (non versionné), `.env.example` versionné
- **Tests** : pytest, fixtures dans `tests/conftest.py`, base de données de test en mémoire (`:memory:`)
- **Langue** : commentaires et messages UI en français, code (variables, fonctions) en français ou anglais technique

---

## 6. Décisions d'architecture

| Décision | Choix | Raison |
|---|---|---|
| SQLite WAL mode | Activé | Permet lectures concurrentes pendant écritures du scheduler |
| Chiffrement Fernet | Symétrique | Suffisant pour un seul admin ; clé dans variable d'env |
| APScheduler vs Celery | APScheduler | Pas de dépendance Redis/RabbitMQ, volume modéré |
| PDF viewer | iframe natif d'abord | Zéro dépendance JS externe, PDF.js en Phase 2 si besoin |
| Bootstrap 5 | CDN ou local | Interface légère, composants prêts à l'emploi |

---

## 7. État d'avancement

### Phase 1 — MVP

| Tâche | Statut | Commit |
|---|---|---|
| Initialisation structure + Hello World | ✅ Terminé | `chore: initialisation du projet et architecture` |
| Modèles SQLAlchemy (Source, Document, Journal) | ⬜ À faire | — |
| Authentification (session + mot de passe hashé) | ⬜ À faire | — |
| CRUD Sources (routes + formulaires) | ⬜ À faire | — |
| Service SFTP (paramiko) | ⬜ À faire | — |
| Service SMB (smbprotocol) | ⬜ À faire | — |
| Sync manuelle + dédup SHA-256 | ⬜ À faire | — |
| Scheduler (APScheduler) | ⬜ À faire | — |
| Contrôle de fraîcheur + statuts | ⬜ À faire | — |
| Purge automatique + corbeille | ⬜ À faire | — |
| Interface consultation documents | ⬜ À faire | — |
| Journaux + export CSV | ⬜ À faire | — |
| Dashboard tableau de bord | ⬜ À faire | — |
| Docker + docker-compose fonctionnel | ⬜ À faire | — |

---

## 8. Points de vigilance sécurité

- `SECRET_KEY` et `ENCRYPTION_KEY` : **obligatoirement** dans les variables d'environnement en prod
- CSRF : activer Flask-WTF sur tous les formulaires modifiants
- Pas de secrets dans les logs (`details` JSON du journal ne doit jamais contenir de mots de passe)
- Vérifier le hash SHA-256 **avant** toute écriture locale lors de la sync
- Purge : toujours journaliser avant de supprimer physiquement
