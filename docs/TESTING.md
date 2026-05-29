# Testing

## Lecteur cible

Ce document s'adresse à un développeur qui prépare une modification. Après lecture, il doit pouvoir choisir la bonne commande de vérification.

## Commande Principale

```bash
make check
```

Cette commande exécute:

- Ruff sur les erreurs Python critiques;
- pytest avec couverture;
- Bandit;
- pip-audit;
- le scan de secrets sur les fichiers suivis par Git;
- le controle de permissions du fichier d'environnement local.

## Tests Ciblés

Pendant le développement, exécuter un sous-ensemble:

```bash
.venv/bin/python -m pytest tests/test_api_permissions.py -q
.venv/bin/python -m pytest tests/test_sync_service.py tests/test_purge_service.py -q
.venv/bin/python -m pytest tests/test_template_accessibility.py -q
.venv/bin/python -m pytest tests/test_config_security.py tests/test_encryption_rotation.py -q
.venv/bin/python -m pytest tests/test_migration_service.py tests/test_permissions_check.py -q
```

Revenir à `make check` avant de considérer la branche prête.

## Scénarios Sensibles

Les tests couvrent notamment:

- synchronisation API asynchrone et statut de job;
- permissions API et administration;
- LDAP sans TLS refusé en production;
- secrets requis en production et cle de developpement non hardcodee;
- rotation Fernet des identifiants de sources;
- headers CSP avec nonce et sans dependance a Flask-Talisman;
- validation defensive des identifiants SQL de migration;
- permissions restrictives de `.env`;
- timeouts LDAP et SMB;
- allowlist des sources locales;
- protection purge/corbeille hors stockage;
- neutralisation CSV/XLSX;
- échappement HTML des emails;
- accessibilité de base des templates.

## Données De Test

Les tests utilisent SQLite en mémoire et un stockage temporaire. Ils ne doivent pas dépendre de serveurs SFTP, SMB, LDAP ou SMTP réels.
