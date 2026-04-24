# Plan de travail — Finalisation MVP Phase 1

> **⚠️ CE FICHIER DOIT ÊTRE SUPPRIMÉ UNE FOIS TOUTES LES TÂCHES TERMINÉES ⚠️**

> **Créé le** : 2026-04-24
> **Objectif** : Finaliser le MVP selon le cahier des charges et corriger les écarts identifiés

---

## Instructions pour Claude

À chaque nouvelle conversation, pointe vers ce fichier :
```
Lis /home/user1/Documents/SarcophageStage/StageSarcophage/PLAN_TRAVAIL.md et continue les tâches non terminées.
```

Après chaque tâche terminée, mets à jour ce fichier en cochant la case `[x]`.

---

## Phase A — Corrections sécurité Priorité 3

*(SECURITE_TODO.md supprimé car toutes les corrections sont terminées)*

- [x] **A1. Pin Docker base image** ✅
  - Fichier : `Dockerfile`
  - Fait : `python@sha256:520153e2deb359602c9cffd84e491e3431d76e7bf95a3255c9ce9433b76ab99a`

- [x] **A2. Streaming ZIP gros fichiers** ✅
  - Fichier : `app/routes/documents.py`
  - Fait : `tempfile.NamedTemporaryFile` + `@after_this_request` pour cleanup

- [x] **A3. Audit trail user_id** ✅
  - Fichiers modifiés : `app/models/journal.py`, `app/routes/documents.py`, `app/routes/journaux.py`, `app/templates/journaux/index.html`
  - Fait :
    - Colonne `user_id` FK vers users ajoutée
    - Routes documents passent `current_user.id`
    - Template journaux affiche la colonne Utilisateur
    - Export CSV inclut l'utilisateur

- [x] **A4. Host key verification stricte SFTP** ✅
  - Fichiers créés/modifiés : `app/models/ssh_fingerprint.py`, `app/services/sftp_service.py`, `app/routes/sources.py`
  - Fait :
    - Modèle `SSHFingerprint` pour stocker les empreintes
    - `StrictHostKeyPolicy` personnalisée avec vérification BDD
    - Exceptions `HostKeyMismatchError` et `HostKeyNewError`
    - Route `/sources/<id>/accepter-fingerprint` pour accepter manuellement
    - Test de connexion retourne les infos de fingerprint si nouveau

---

## Phase B — Écarts avec le cahier des charges

- [x] **B1. Suppression logique des sources** ✅
  - Fichiers modifiés : `app/models/source.py`, `app/routes/sources.py`
  - Fait :
    - Champ `deleted_at` ajouté au modèle Source
    - Propriété `est_supprimee` ajoutée
    - Route `/supprimer` fait maintenant une suppression logique
    - Route `/restaurer` ajoutée pour restaurer une source archivée
    - Requêtes filtrées pour exclure les sources supprimées

- [x] **B2. Purge manuelle par source** ✅
  - Fichiers modifiés : `app/routes/sources.py`, `app/templates/sources/detail.html`
  - Fait : Route `/sources/<id>/purger` + bouton "Purger" avec confirmation

- [x] **B3. Filtre par plage de dates sur documents** ✅
  - Fichiers modifiés : `app/routes/documents.py`, `app/templates/documents/index.html`
  - Fait : Filtres `depuis` et `jusqua` ajoutés

- [ ] **B4. Page paramètres globaux** (~1h) — *Optionnel*
  - CDC §2.6 : "Répertoire de stockage local, fréquence de purge globale, fuseau horaire"
  - Note : Actuellement via variables d'environnement, acceptable pour MVP
  - Si implémenté : créer table `settings` et page `/admin/parametres`

---

## Phase C — Documentation

- [x] **C1. Documentation technique** ✅
  - Créé `docs/TECHNIQUE.md`
  - Contenu : architecture, schéma BDD, routes API, déploiement Docker, variables d'env, commandes CLI

- [x] **C2. Documentation utilisateur** ✅
  - Créé `docs/UTILISATEUR.md`
  - Contenu : connexion, gestion sources, documents, téléchargements, journaux, FAQ

---

## Phase D — Finalisation

- [x] **D1. Mettre à jour MEMORY.md** ✅
  - Authentification et Docker marqués comme terminés

- [x] **D2. Supprimer SECURITE_TODO.md** ✅

- [ ] **D3. Commit final**
  - Committer tous les fichiers non suivis (auth.py, user.py, tests, etc.)
  - Message : `feat: finalisation MVP Phase 1 avec corrections sécurité`

- [ ] **D4. Vérification des critères de recette**
  - Passer en revue la checklist de la section 10 du CDC
  - Tester manuellement chaque fonctionnalité

---

## État actuel des tests

```bash
# Lancer les tests
source venv/bin/activate && python -m pytest -v

# Résultat attendu : 92 tests passent (avant ajouts Phase A/B)
```

---

## Fichiers clés à connaître

| Fichier | Description |
|---------|-------------|
| `cahier_des_charges.md` | CDC officiel (NE PAS MODIFIER) |
| `MEMORY.md` | Base de connaissances projet |
| `app/__init__.py` | Factory Flask |
| `app/routes/` | Blueprints (auth, main, sources, documents, journaux) |
| `app/services/` | Logique métier (sync, purge, sftp, smb) |
| `app/models/` | Modèles SQLAlchemy |
| `config.py` | Configuration Dev/Prod/Testing |

---

## Commandes utiles

```bash
# Activer l'environnement
source venv/bin/activate

# Lancer l'app en dev
STORAGE_DIR="$(pwd)/data" ENCRYPTION_KEY="..." SECRET_KEY="..." flask run

# Lancer les tests
python -m pytest -v

# Créer un admin
flask create-admin --username admin --password <motdepasse>

# Docker
docker compose build && docker compose up -d
```
