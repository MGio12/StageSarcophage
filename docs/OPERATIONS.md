# Operations

## Lecteur cible

Ce document s'adresse à un exploitant ou ingénieur d'astreinte. Après lecture, il doit pouvoir lancer, contrôler et dépanner l'application.

## Configuration Requise

Voir aussi [Securite](SECURITY.md) pour la rotation des secrets, les headers
HTTP et les permissions locales.

Variables minimales en production:

```text
SECRET_KEY=...
ENCRYPTION_KEY=...
STORAGE_DIR=...
FLASK_ENV=production
```

Variables importantes:

- `JOB_WORKERS`: nombre de workers de jobs de fond.
- `JOBS_RUN_INLINE`: exécute les jobs inline, réservé aux tests ou diagnostics locaux.
- `LOCAL_SOURCE_ALLOWED_ROOTS`: racines autorisées pour les sources locales, séparées par le séparateur de chemins du système.
- `LDAP_REQUIRE_TLS`: impose TLS pour LDAP. Activé par défaut en production.
- `LDAP_USE_SSL`: active LDAPS.
- `LDAP_TIMEOUT_SECONDS`: timeout de connexion LDAP.
- `FORCE_HTTPS`, `SESSION_COOKIE_SECURE`, `TRUST_PROXY`: réglages de terminaison TLS et reverse proxy.

## Initialisation

Créer ou mettre à jour la base:

```bash
.venv/bin/flask --app run.py init-db
```

Créer un administrateur:

```bash
.venv/bin/flask --app run.py create-admin --username admin --password 'mot-de-passe-long'
```

Appliquer seulement les migrations idempotentes:

```bash
.venv/bin/flask --app run.py upgrade-db
```

Les migrations SQLite utilisent une allowlist interne de tables, colonnes et DDL
connus par l'application. Les identifiants sont validés puis quotés avant
construction du `ALTER TABLE`; aucune entrée utilisateur ne doit être ajoutée à
cette allowlist.

## Rotation De La Cle De Chiffrement

Le runbook securite contient la checklist complete de rotation. Cette section
resume la commande operationnelle.

La rotation de `ENCRYPTION_KEY` doit ré-encrypter les identifiants stockés dans
`Source.login` et `Source.mot_de_passe` avant le changement définitif du fichier
d'environnement:

```bash
OLD_ENCRYPTION_KEY=... NEW_ENCRYPTION_KEY=... .venv/bin/flask --app run.py rotate-encryption-key
```

Après succès seulement, remplacer `ENCRYPTION_KEY` dans `.env`, redémarrer
l'application, puis vérifier la lecture des sources configurées. La commande ne
journalise jamais les valeurs déchiffrées.

## Vérifications

Healthcheck:

```bash
curl http://127.0.0.1:5000/api/v1/health
```

Gate qualité:

```bash
make check
```

Contrôle ciblé des permissions locales:

```bash
make permissions
```

Le fichier `.env` doit être en `0600` ou plus restrictif.

## Sauvegardes

Sauvegarder régulièrement:

- la base SQLite;
- le stockage documentaire;
- le fichier d'environnement;
- les logs si l'historique technique est requis.

## Sources Locales

Les sources locales doivent être placées sous une racine explicitement autorisée. Ne pas configurer une racine trop large comme `/` ou un dossier personnel complet. Préférer un dossier dédié, monté en lecture seule si possible.

## Jobs De Fond

Une synchronisation API répond avec un identifiant de job. Consulter le statut via l'URL retournée par la réponse. Un job en échec expose une erreur générique; consulter les journaux applicatifs pour le détail technique.

## Dépannage

Si LDAP échoue en production, vérifier d'abord `LDAP_USE_SSL`, le port LDAPS et le certificat côté serveur. L'application refuse LDAP sans TLS lorsque l'exigence TLS est active.

Si une source locale échoue, vérifier que le chemin configuré appartient à `LOCAL_SOURCE_ALLOWED_ROOTS`.

Si un export tableur affiche une apostrophe devant une cellule, c'est volontaire: la valeur a été neutralisée pour empêcher l'interprétation en formule.
