# Documentation

## Lecteur cible

Ce point d'entrée s'adresse a une personne qui arrive sur le projet et doit
trouver rapidement la bonne information. Apres lecture, elle doit savoir quel
document ouvrir pour installer, exploiter, securiser, tester ou faire evoluer
StageSarcophage.

## Trouver La Bonne Page

| Besoin | Lire |
| --- | --- |
| Installer et lancer en local | [README projet](../README.md) |
| Comprendre les couches applicatives | [Architecture](ARCHITECTURE.md) |
| Comprendre les entites metier | [Modele de donnees](DATA_MODEL.md) |
| Exploiter, initialiser ou depanner | [Exploitation](OPERATIONS.md) |
| Gerer secrets, headers, permissions et audits | [Securite](SECURITY.md) |
| Choisir une commande de verification | [Tests et qualite](TESTING.md) |
| Connaitre ce qui a ete livre dans la vague qualite | [Statut d'implementation](IMPLEMENTATION_STATUS.md) |
| Relire les exigences initiales | [Cahier des charges](../cahier_des_charges.md) |

## Parcours Rapides

### Nouveau developpeur

1. Lire le README projet pour installer l'environnement.
2. Lire Architecture pour situer les routes, services et modeles.
3. Lire Modele de donnees avant de modifier une regle metier.
4. Lire Tests et qualite avant d'ouvrir une branche prete a relire.

### Exploitant ou astreinte

1. Lire Exploitation pour les commandes de base, sauvegardes et depannage.
2. Lire Securite pour les secrets, la rotation Fernet et les permissions.
3. Utiliser le healthcheck et `make check` pour confirmer l'etat applicatif.

### Revue securite

1. Lire Securite de bout en bout.
2. Verifier que les secrets de production sont presents hors Git.
3. Executer les commandes de verification de Tests et qualite.
4. Controler les changements de dependances et de migrations.

## Invariants A Ne Pas Perdre

- Les secrets reels restent hors Git et le fichier d'environnement local n'est
  lisible que par son proprietaire.
- Les identifiants de sources sont chiffres avec Fernet et necessitent une
  rotation controlee avant tout changement de cle.
- Les documents lus, copies, purges ou servis restent sous le stockage controle.
- Les migrations SQLite n'acceptent que l'allowlist interne de tables et
  colonnes.
- Les routes d'administration et l'API verifient des permissions explicites.
- Le gate qualite complet reste `make check`.
