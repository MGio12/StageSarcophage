# Architecture

## Lecteur cible

Ce document s'adresse à un ingénieur qui doit faire évoluer StageSarcophage sans connaître l'historique du projet. Après lecture, il doit pouvoir situer une nouvelle fonctionnalité dans la bonne couche et préserver les invariants de sécurité.

## Vue d'ensemble

StageSarcophage est une application Flask monolithe côté serveur. Les pages sont rendues en Jinja avec Bootstrap, et l'API REST v1 expose les intégrations internes avec authentification par token.

Le cœur applicatif est organisé en couches:

- Routes HTTP: pages web, API REST, authentification et administration.
- Services: synchronisation, purge, exports, notifications, jobs de fond, LDAP et connecteurs.
- Modèles: tables SQLAlchemy persistées en SQLite.
- Utilitaires: chiffrement, validation de chemins et neutralisation des sorties.

Les routes doivent rester minces: elles valident l'accès, récupèrent les entrées HTTP, appellent un service, puis rendent une réponse. Les règles qui touchent le stockage, les connecteurs, les exports ou les notifications appartiennent aux services.

## Flux De Synchronisation

Une source active peut être SFTP, SMB ou locale. Les connecteurs exposent le même contrat: lister des fichiers distants puis télécharger un fichier vers un chemin local contrôlé. La synchronisation copie d'abord vers un fichier temporaire, calcule le hash SHA-256, puis remplace le fichier final si le contenu a changé.

Les sources locales sont soumises à une allowlist de racines. Une source locale qui sort de ces racines est refusée avant lecture ou copie.

## Jobs De Fond

Les opérations longues sont représentées par des jobs de fond. L'API de synchronisation crée un job et répond avec `202 Accepted`. En production, les jobs s'exécutent dans un pool de threads Flask configuré par `JOB_WORKERS`. En test, `JOBS_RUN_INLINE` permet de rendre l'exécution déterministe.

Chaque job expose un statut, un résultat sérialisable et une erreur générique si l'exécution échoue. Les messages d'erreur publics ne doivent pas contenir de chemin interne, secret ou détail de stack trace.

## Sécurité

Les invariants principaux:

- Les documents servis ou déplacés doivent rester sous le répertoire de stockage.
- Les noms utilisés en ZIP, corbeille, XLSX ou CSV sont normalisés ou neutralisés.
- LDAP exige TLS en production quand l'authentification LDAP est activée.
- Les opérations d'administration sont protégées par permissions `admin.*`, pas par simple nom de rôle.
- L'API REST exige un token Bearer et vérifie les permissions de l'utilisateur attaché au token.

## Interface Web

L'interface reste Flask/Jinja/Bootstrap. Le design vise une console opérationnelle sobre: densité raisonnable, tables lisibles, focus clavier visible, liens de saut, macros Jinja partagées pour badges, états vides et pagination.
