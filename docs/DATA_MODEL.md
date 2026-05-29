# Data Model

## Lecteur cible

Ce document s'adresse à un développeur qui doit modifier une règle métier ou diagnostiquer une donnée incohérente. Après lecture, il doit savoir quelle entité porte quelle responsabilité.

## Entités Principales

`User` représente un utilisateur local ou LDAP. Un utilisateur local possède un mot de passe bcrypt. Un utilisateur LDAP possède un mot de passe local inutilisable et s'authentifie via l'annuaire.

`Role` regroupe les permissions applicatives. Les permissions sont stockées sous forme JSON. Le rôle administrateur conserve le joker `*`, mais les routes vérifient des permissions explicites.

`APIToken` représente un token Bearer haché en base. Le secret du token n'est visible qu'à la création. Le token est lié à un utilisateur, donc ses permissions viennent du rôle de cet utilisateur.

`Source` décrit une origine documentaire. Les protocoles pris en charge sont SFTP, SMB et local. Les identifiants source sont chiffrés avec Fernet.

`Document` représente un PDF collecté. Il porte son nom, son chemin local, sa taille, son hash, ses dates de collecte et de modification source, ainsi que son statut métier.

`Journal` trace les événements: synchronisation, purge, erreur, connexion et accès documentaire. Les détails structurés sont sérialisés en JSON.

`BackgroundJob` suit les opérations longues: type d'opération, statut, payload, résultat, erreur et horodatages.

## Statuts Document

Un document peut être:

- `ok`: document récent.
- `avertissement`: âge supérieur au seuil d'avertissement de sa source.
- `critique`: âge supérieur au seuil critique de sa source.
- `purge`: document déplacé en corbeille ou considéré expiré.

## Corbeille

La purge ne supprime pas immédiatement les fichiers. Elle déplace les fichiers expirés dans une corbeille sous le stockage contrôlé, marque les documents en `purge`, puis laisse le nettoyage définitif appliquer la rétention de corbeille.

## Paramètres

`Setting` porte les paramètres applicatifs modifiables depuis l'administration. Les variables d'environnement gardent la priorité pour les secrets, la sécurité de transport, le stockage et les jobs.
