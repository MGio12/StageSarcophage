# Plan de travail — Phase 2 : Améliorations

> **Créé le** : 2026-04-24
> **Objectif** : Implémenter les fonctionnalités Phase 2 du cahier des charges (section 8.2)
> **Prérequis** : Phase 1 MVP terminée et fonctionnelle

---

## Instructions pour Claude

À chaque nouvelle conversation :
```
Lis /home/user1/Documents/SarcophageStage/StageSarcophage/PLAN_PHASE2.md et continue les tâches non terminées.
```

Après chaque tâche terminée, mets à jour ce fichier en cochant la case `[x]`.

---

## A — Notifications par email

> CDC §8.2 : "Notifications par email (documents obsolètes, erreurs de connexion)"

- [ ] **A1. Configuration SMTP** (~1h)
  - Ajouter variables d'environnement : `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
  - Créer `app/services/email_service.py` avec fonction `envoyer_email(destinataire, sujet, corps)`
  - Gérer TLS/SSL

- [ ] **A2. Table destinataires** (~30min)
  - Créer modèle `NotificationConfig` : user_id, email, notif_erreurs (bool), notif_critiques (bool)
  - Migration

- [ ] **A3. Notifications documents critiques** (~1h)
  - Après chaque sync, si documents passent en statut critique → email
  - Regrouper les alertes (1 email par sync, pas 1 par document)

- [ ] **A4. Notifications erreurs connexion** (~1h)
  - Si une source échoue X fois consécutives → email d'alerte
  - Ajouter compteur `echecs_consecutifs` sur Source

- [ ] **A5. Interface paramétrage notifications** (~1h)
  - Page `/admin/notifications` pour configurer les destinataires
  - Bouton "Envoyer un email test"

---

## B — Authentification LDAP / Active Directory

> CDC §8.2 : "Authentification LDAP / Active Directory"

- [ ] **B1. Dépendance python-ldap** (~30min)
  - Ajouter `python-ldap` ou `ldap3` à requirements.txt
  - Configurer dans Dockerfile (libs système nécessaires)

- [ ] **B2. Configuration LDAP** (~1h)
  - Variables : `LDAP_HOST`, `LDAP_PORT`, `LDAP_BASE_DN`, `LDAP_BIND_DN`, `LDAP_BIND_PASSWORD`
  - `LDAP_USER_FILTER`, `LDAP_GROUP_FILTER` (optionnel)

- [ ] **B3. Service LDAP** (~2h)
  - Créer `app/services/ldap_service.py`
  - Fonction `authentifier_ldap(username, password) -> bool`
  - Fonction `recuperer_infos_utilisateur(username) -> dict`

- [ ] **B4. Intégration login** (~1h)
  - Modifier `routes/auth.py` : tenter LDAP d'abord, fallback sur BDD locale
  - Créer utilisateur local à la première connexion LDAP réussie

- [ ] **B5. Synchronisation groupes AD** (~2h) — *Optionnel*
  - Mapper groupes AD vers rôles applicatifs
  - Sync périodique des appartenances

---

## C — Gestion des rôles

> CDC §8.2 : "Gestion de rôles (administrateur / consultation seule)"

- [ ] **C1. Modèle Role** (~30min)
  - Créer table `roles` : id, nom, permissions (JSON)
  - Ajouter `role_id` FK sur User
  - Rôles initiaux : `admin`, `lecteur`

- [ ] **C2. Décorateur permissions** (~1h)
  - Créer `@require_role('admin')` ou `@require_permission('sources.edit')`
  - Appliquer sur routes sensibles (création/modif sources, purge, etc.)

- [ ] **C3. Interface gestion utilisateurs** (~2h)
  - Page `/admin/utilisateurs` : liste, création, modification, désactivation
  - Assignation des rôles

- [ ] **C4. Permissions granulaires** (~1h) — *Optionnel*
  - Permissions par action : `sources.view`, `sources.edit`, `sources.delete`, `documents.download`, etc.
  - Interface d'édition des permissions par rôle

---

## D — Export rapports de conformité

> CDC §8.2 : "Export des rapports de conformité (liste des documents avec statut)"

- [ ] **D1. Rapport PDF** (~2h)
  - Installer `weasyprint` ou `reportlab`
  - Générer PDF : liste documents par source, statuts, dates, statistiques

- [ ] **D2. Rapport Excel** (~1h)
  - Installer `openpyxl`
  - Export XLSX avec feuilles par source + feuille récapitulative

- [ ] **D3. Planification rapports** (~1h) — *Optionnel*
  - Génération automatique hebdomadaire/mensuelle
  - Envoi par email aux destinataires configurés

---

## E — API REST

> CDC §8.2 : "API REST pour intégration avec d'autres outils internes"

- [ ] **E1. Blueprint API** (~30min)
  - Créer `app/routes/api.py` avec préfixe `/api/v1`
  - Authentification par token (header `Authorization: Bearer <token>`)

- [ ] **E2. Gestion tokens API** (~1h)
  - Table `api_tokens` : id, user_id, token (hash), nom, created_at, expires_at
  - Interface génération/révocation tokens

- [ ] **E3. Endpoints sources** (~1h)
  - `GET /api/v1/sources` — liste des sources
  - `GET /api/v1/sources/<id>` — détail source
  - `POST /api/v1/sources/<id>/sync` — déclencher sync
  - `GET /api/v1/sources/<id>/status` — état connexion

- [ ] **E4. Endpoints documents** (~1h)
  - `GET /api/v1/documents` — liste paginée avec filtres
  - `GET /api/v1/documents/<id>` — métadonnées document
  - `GET /api/v1/documents/<id>/download` — télécharger fichier

- [ ] **E5. Endpoints monitoring** (~30min)
  - `GET /api/v1/health` — état de l'application
  - `GET /api/v1/stats` — statistiques globales (nb docs, alertes, etc.)

- [ ] **E6. Documentation OpenAPI** (~1h) — *Optionnel*
  - Installer `flask-openapi3` ou documenter manuellement
  - Swagger UI sur `/api/docs`

---

## F — Améliorations diverses (hors CDC mais utiles)

- [ ] **F1. Page paramètres globaux** (~1h)
  - Interface web pour modifier : répertoire stockage, fuseau horaire, fréquence purge globale
  - Table `settings` clé/valeur

- [ ] **F2. Corbeille avec période de grâce** (~1h)
  - CDC §2.4 mentionne une corbeille optionnelle
  - Déplacer vers `_corbeille/` au lieu de supprimer directement
  - Purge définitive après X jours

- [ ] **F3. Recherche texte** (~30min)
  - Recherche par nom de fichier (LIKE ou FTS SQLite)

---

## Ordre de priorité suggéré

1. **C (Rôles)** — Sécurité, bloque les autres fonctionnalités admin
2. **E (API REST)** — Intégration avec outils internes
3. **A (Notifications)** — Alertes proactives
4. **D (Rapports)** — Conformité
5. **B (LDAP)** — Peut être complexe selon l'infra AD

---

## Commandes utiles

```bash
# Activer l'environnement
source venv/bin/activate

# Lancer l'app en dev
flask run

# Lancer les tests
python -m pytest -v

# Docker
docker compose build && docker compose up -d
```

---

## Fichiers clés Phase 1 (référence)

| Fichier | Description |
|---------|-------------|
| `app/__init__.py` | Factory Flask |
| `app/routes/` | Blueprints existants |
| `app/services/` | Logique métier |
| `app/models/` | Modèles SQLAlchemy |
| `docs/TECHNIQUE.md` | Documentation technique |
| `docs/UTILISATEUR.md` | Documentation utilisateur |
