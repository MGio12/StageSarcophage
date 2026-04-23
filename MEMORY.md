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
│   ├── __init__.py          # Factory Flask (create_app) + WAL pragma + CLI init-db
│   ├── extensions.py        # Instance SQLAlchemy partagée (db)
│   ├── models/              # Modèles SQLAlchemy
│   │   ├── source.py        # Table sources (login/mot_de_passe chiffrés via @property)
│   │   ├── document.py      # Table documents (enum StatutDocument)
│   │   └── journal.py       # Table journaux (details JSON, enum TypeEvenement)
│   ├── routes/              # Blueprints Flask
│   │   ├── main.py          # Dashboard (/)
│   │   ├── sources.py       # CRUD sources (/sources)
│   │   ├── documents.py     # Consultation (/documents)
│   │   └── journaux.py      # Logs (/journaux)
│   ├── services/            # Logique métier (sans dépendance HTTP)
│   │   ├── smb_service.py   # Connecteur SMB — lister_fichiers + telecharger_fichier + tester_connexion
│   │   ├── sftp_service.py  # Connecteur SFTP — lister_fichiers + telecharger_fichier + tester_connexion
│   │   ├── sync_service.py  # Synchronisation : dédup SHA-256, copie locale, journalisation
│   │   └── purge_service.py # Purge : corbeille, statuts ok/avertissement/critique
│   ├── scheduler/           # Tâches APScheduler
│   │   └── tasks.py         # demarrer_scheduler + jobs par source + purge nuit à 2h
│   ├── utils/
│   │   └── crypto.py        # chiffrer() / dechiffrer() via Fernet
│   ├── static/              # CSS, JS, assets
│   └── templates/           # Jinja2 HTML
├── instance/                # Config locale + app.db (hors git)
├── tests/
│   ├── conftest.py          # Fixtures pytest (app, db, client)
│   ├── test_crypto.py       # Tests chiffrement (9 cas)
│   ├── test_models.py       # Tests modèles + tables (17 cas)
│   ├── test_smb_service.py  # Tests connecteur SMB (13 cas, mock smbclient)
│   ├── test_sftp_service.py # Tests connecteur SFTP (13 cas, mock paramiko)
│   ├── test_sync_service.py # Tests synchronisation (10 cas, mock connectors + vrai DB)
│   └── test_purge_service.py # Tests purge + statuts (12 cas, vrai DB + tmp_path)
├── data/                    # PDF collectés, organisés par source (hors git)
├── logs/                    # Logs applicatifs (hors git)
├── config.py                # Configs Dev / Prod / Testing
├── run.py                   # Point d'entrée
├── pytest.ini               # testpaths=tests, python_functions=test_*
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

## 6. Décisions d'architecture clés (sync + purge)

| Décision | Choix | Raison |
|---|---|---|
| Dédup deux niveaux | 1. date+taille → skip sans DL ; 2. hash SHA-256 → skip si inchangé | Évite les téléchargements inutiles tout en garantissant l'intégrité |
| Écriture atomique | `tempfile.mkstemp` → hash → `shutil.move` | Pas de fichier partiel si la copie échoue en cours |
| Corbeille avant suppression | `_corbeille/{source_id}/` dans STORAGE_DIR | Permet récupération manuelle, conforme CDC §2.4 |
| Scheduler non démarré en tests | `if not app.config.get("TESTING")` | Évite les threads de fond pendant pytest |
| Jobs par source | `IntervalTrigger(minutes=source.frequence_sync_minutes)` | Fréquence indépendante par source, conforme CDC §2.2 |
| Purge globale | `CronTrigger(hour=2)` chaque nuit | Faible impact utilisateur |
| `_as_utc()` helper | Normalise naive/aware avant comparaison | SQLite+SQLAlchemy peut retourner des datetimes naïves |

## 7. Décisions d'architecture (base)



| Décision | Choix | Raison |
|---|---|---|
| SQLite WAL mode | Activé via `PRAGMA journal_mode=WAL` sur connect | Lectures concurrentes pendant écritures du scheduler |
| `PRAGMA foreign_keys=ON` | Activé sur chaque connexion | SQLite désactive les FK par défaut |
| Chiffrement | Fernet (AES-128-CBC + HMAC-SHA256) | CDC dit "AES-256 ou équivalent" — Fernet est l'équivalent sécurisé retenu |
| Colonnes chiffrées | `@property` Python sur `_login`/`_mot_de_passe` | Chiffrement transparent, invisible pour le code appelant |
| Enum Python | `StatutDocument`, `TypeEvenement` | Validation des valeurs autorisées au niveau modèle |
| details Journal | Texte JSON sérialisé manuellement | Prévisible sur SQLite, pas de dépendance JSON native |
| ENCRYPTION_KEY en tests | Générée via `Fernet.generate_key()` dans conftest.py | Clé valide + unique par session, jamais hardcodée |
| APScheduler vs Celery | APScheduler | Pas de dépendance Redis/RabbitMQ, volume modéré |
| PDF viewer | iframe natif d'abord | Zéro dépendance JS externe, PDF.js en Phase 2 si besoin |
| Bootstrap 5 | CDN ou local | Interface légère, composants prêts à l'emploi |

---

## 8. État d'avancement

### Phase 1 — MVP

| Tâche | Statut | Commit |
|---|---|---|
| Initialisation structure + Hello World | ✅ Terminé | `chore: initialisation du projet et architecture` |
| Modèles SQLAlchemy (Source, Document, Journal) | ✅ Terminé | `feat: modèles de données et chiffrement` |
| Chiffrement Fernet (crypto.py) + tests | ✅ Terminé | `feat: modèles de données et chiffrement` |
| Authentification (session + mot de passe hashé) | ⬜ À faire | — |
| CRUD Sources (routes + formulaires) | ⬜ À faire | — |
| Connecteurs SFTP + SMB (services + tests mock) | ✅ Terminé | `feat: implémentation des connecteurs SMB et SFTP` |
| Sync service (SHA-256, copie, journal) + Purge service + APScheduler | ✅ Terminé | `feat: logique de synchronisation et purge planifiée` |
| Sync manuelle + dédup SHA-256 | ⬜ À faire | — |
| Scheduler (APScheduler) | ⬜ À faire | — |
| Contrôle de fraîcheur + statuts | ⬜ À faire | — |
| Purge automatique + corbeille | ⬜ À faire | — |
| Interface consultation documents | ⬜ À faire | — |
| Journaux + export CSV | ⬜ À faire | — |
| Dashboard tableau de bord | ⬜ À faire | — |
| Docker + docker-compose fonctionnel | ⬜ À faire | — |

---

## 9. Points de vigilance sécurité

- `SECRET_KEY` et `ENCRYPTION_KEY` : **obligatoirement** dans les variables d'environnement en prod
- CSRF : activer Flask-WTF sur tous les formulaires modifiants
- Pas de secrets dans les logs (`details` JSON du journal ne doit jamais contenir de mots de passe)
- Vérifier le hash SHA-256 **avant** toute écriture locale lors de la sync
- Purge : toujours journaliser avant de supprimer physiquement
