# Implementation Status

## Lecteur cible

Ce document s'adresse à un mainteneur qui veut savoir ce qui a été livré dans la vague qualité. Après lecture, il doit savoir quelles garanties existent et quels points restent à surveiller.

## Backend

Livré:

- gate qualité avec Makefile, CI, Ruff, pytest-cov, Bandit, pip-audit et scan de secrets suivis;
- controle de permissions du fichier d'environnement local dans le gate qualite;
- validation des secrets requis en production et cle de developpement generee a l'execution;
- commande interne de rotation Fernet pour les identifiants de sources;
- headers de securite et CSP geres par middleware interne avec nonce;
- migrations SQLite durcies par validation et quotage des identifiants;
- durcissement LDAP/SMB: TLS LDAP obligatoire en production, timeouts explicites, erreurs publiques sanitizées;
- sources locales protégées par allowlist et permission `sources.local`;
- purge et restauration contraintes au stockage applicatif;
- neutralisation des formules CSV/XLSX et noms d'onglets XLSX valides;
- échappement HTML des notifications;
- jobs de fond pour synchronisation et purge déclenchées par l'interface ou l'API;
- endpoint API de statut de job;
- contrat commun des connecteurs;
- permissions `admin.*` sur les routes d'administration;
- app factory découpée et OpenAPI déplacé hors des routes.

## Frontend

Livré:

- tokens CSS sobres, focus visible, lien d'évitement et cible `main`;
- macros Jinja partagées pour badges, boutons icône, états vides et pagination;
- labels explicites, scopes de tables et noms accessibles sur les actions principales;
- login et Swagger alignés sur le layout partagé;
- template racine mort supprimé.

## Documentation

Livré:

- architecture;
- index documentaire;
- securite;
- modèle de données;
- exploitation;
- stratégie de test;
- statut d'implémentation.

Le cahier des charges reste le document de référence et n'a pas été modifié.
