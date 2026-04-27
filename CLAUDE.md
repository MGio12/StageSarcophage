# Modes Dégradés — CLCC

Application Flask de collecte et archivage de documents PDF depuis des sources distantes (SFTP/SMB), avec suivi de fraîcheur et alertes.

## État du projet

- **Phase 1** : MVP terminé (collecte, purge, interface web, Docker)
- **Phase 2** : Terminée (notifications, LDAP, rôles, API REST, rapports)
- **Phase 3** : À définir

## Stack technique

- Python 3.12 / Flask
- SQLite + SQLAlchemy ORM
- APScheduler (tâches planifiées)
- Bootstrap 5 (UI)
- Docker / Gunicorn (production)

## Commandes essentielles

```bash
source venv/bin/activate
python -m pytest -v          # Tests (92 tests)
flask init-db                # Initialiser la BDD
flask create-admin           # Créer un admin
STORAGE_DIR=./data flask run # Lancer en dev
```

## Structure clé

```
app/
├── models/       # Source, Document, User, Role, Setting, etc.
├── routes/       # auth, main, sources, documents, journaux, admin, api
├── services/     # sync, purge, sftp, smb, ldap, email, notification, export
├── scheduler/    # Tâches APScheduler
└── templates/    # Jinja2 + Bootstrap
```

## Documentation

- `docs/TECHNIQUE.md` — Architecture, API, déploiement
- `docs/UTILISATEUR.md` — Guide utilisateur
- `PLAN_PHASE2.md` — Plan de travail Phase 2 (terminé)

## Points d'attention

- Les identifiants des sources sont chiffrés (Fernet) — `ENCRYPTION_KEY` requis
- Authentification : locale (bcrypt) ou LDAP/AD
- API REST : `/api/v1/*` avec tokens Bearer — doc Swagger sur `/api/v1/docs`
- Corbeille : fichiers purgés conservés 30j avant suppression définitive
