# Cahier des charges - Application de gestion des documents de modes dégradés

> **⚠️ DOCUMENT DE RÉFÉRENCE - NE PAS MODIFIER ⚠️**
>
> Ce cahier des charges a été fourni par le maître de stage (DSI - CLCC).
> Il constitue le document de référence officiel du projet et ne doit en aucun cas être modifié.
> Toute évolution ou clarification doit être documentée séparément.

---

## Centre de Lutte Contre le Cancer

> **Version** : 1.0
> **Date** : 2026-04-22
> **Auteur** : DSI - CLCC

---

## 1. Contexte et objectifs

### 1.1 Contexte

Dans un CLCC, la continuité de l'activité de soins impose de disposer en permanence de documents de **modes dégradés** : formulaires, fiches réflexes, procédures papier, bons vierges, etc. Ces documents sont générés automatiquement (ou manuellement) sous forme de fichiers PDF, stockés sur différents serveurs de l'établissement (Windows et Linux).

Aujourd'hui, ces fichiers sont dispersés sur plusieurs partages réseau, sans visibilité centralisée sur leur fraîcheur, leur disponibilité ni leur cycle de vie. En cas de panne ou de cyberattaque, l'accès à ces documents peut être compromis ou leur obsolescence non détectée.

### 1.2 Objectifs

Développer une application web permettant de :

1. **Centraliser** la collecte des PDF de modes dégradés depuis des sources hétérogènes (serveurs Windows/Linux)
2. **Automatiser** la récupération périodique et la vérification de la fraîcheur des documents
3. **Alerter** sur les documents obsolètes ou manquants
4. **Purger** automatiquement les fichiers périmés selon une politique paramétrable par source
5. **Consulter** rapidement les documents disponibles via une interface web

---

## 2. Périmètre fonctionnel

### 2.1 Gestion des sources

| Fonctionnalité | Description |
|---|---|
| Ajout d'une source | Nom, description, type de serveur (Linux/Windows), adresse (IP ou hostname), chemin distant, protocole d'accès (SMB/CIFS, SFTP/SCP, partage réseau UNC), identifiants (login/mot de passe), port éventuel |
| Modification d'une source | Mise à jour de tous les paramètres, y compris les identifiants |
| Suppression d'une source | Suppression logique avec archivage des métadonnées, suppression optionnelle des fichiers locaux associés |
| Test de connexion | Vérification à la demande de l'accessibilité d'une source et de la validité des identifiants |
| Paramétrage par source | Fréquence de synchronisation, durée de rétention (en jours), extensions autorisées (PDF par défaut), filtre par nom/pattern de fichier |

### 2.2 Collecte des documents

| Fonctionnalité | Description |
|---|---|
| Synchronisation planifiée | Tâche périodique configurable par source (ex : toutes les heures, une fois par jour, etc.) |
| Synchronisation manuelle | Bouton de déclenchement immédiat par source ou global (toutes les sources) |
| Copie locale | Les fichiers récupérés sont copiés dans un répertoire local dédié, organisé par source |
| Détection de doublons | Comparaison par nom de fichier + hash SHA-256 pour éviter les copies inutiles |
| Journal de collecte | Historique horodaté de chaque opération : fichiers copiés, erreurs, fichiers ignorés (inchangés) |

### 2.3 Contrôle de fraîcheur

| Fonctionnalité | Description |
|---|---|
| Âge des fichiers | Calcul de l'âge de chaque fichier à partir de sa date de dernière modification sur le serveur source |
| Seuils d'alerte | Paramétrage par source d'un seuil d'avertissement (ex : > 30 jours) et d'un seuil critique (ex : > 90 jours) |
| Indicateurs visuels | Code couleur dans l'interface : vert (OK), orange (avertissement), rouge (critique/périmé) |
| Tableau de bord | Vue synthétique : nombre de documents par statut, par source, dernière synchronisation réussie |

### 2.4 Purge automatique

| Fonctionnalité | Description |
|---|---|
| Rétention paramétrable | Durée de conservation en jours, configurable indépendamment par source |
| Purge automatique | Tâche planifiée supprimant les fichiers locaux dont l'âge dépasse la durée de rétention |
| Purge manuelle | Possibilité de déclencher manuellement la purge pour une source donnée |
| Corbeille / grâce | Période de grâce optionnelle avant suppression définitive (ex : fichiers déplacés dans un dossier « corbeille » pendant 7 jours) |
| Journal de purge | Historique horodaté des fichiers supprimés |

### 2.5 Consultation des documents

| Fonctionnalité | Description |
|---|---|
| Liste des documents | Tableau filtrable et triable : nom, source, date de dernière modification, âge, taille, statut de fraîcheur |
| Recherche | Recherche par nom de fichier, par source, par statut |
| Visualisation | Ouverture du PDF directement dans le navigateur (viewer intégré) |
| Téléchargement | Téléchargement unitaire ou par lot (ZIP) |
| Filtres rapides | Par source, par statut (OK / avertissement / critique), par plage de dates |

### 2.6 Administration

| Fonctionnalité | Description |
|---|---|
| Authentification | Accès protégé par mot de passe (ou intégration LDAP/AD future) |
| Gestion des identifiants sources | Stockage chiffré des mots de passe de connexion aux serveurs distants |
| Paramètres globaux | Répertoire de stockage local, fréquence de purge globale, fuseau horaire |
| Journaux d'activité | Consultation des logs de synchronisation, de purge et d'accès |
| Export des logs | Export CSV des journaux pour audit |

---

## 3. Exigences non fonctionnelles

### 3.1 Sécurité

- **Chiffrement des identifiants** : les mots de passe des sources distantes doivent être stockés chiffrés en base (AES-256 ou équivalent), jamais en clair
- **HTTPS** : l'application doit être servie en HTTPS en production
- **Protection CSRF** : toutes les actions modifiantes doivent être protégées contre les attaques CSRF
- **Authentification** : accès restreint par mot de passe au minimum ; prévoir une évolution vers LDAP/Active Directory
- **Cloisonnement réseau** : l'application doit pouvoir fonctionner dans un VLAN dédié avec accès contrôlé aux serveurs sources
- **Conformité HDS** : le stockage local doit être compatible avec les exigences d'hébergement de données de santé si les documents contiennent des données patient

### 3.2 Performance

- La synchronisation d'une source de 500 fichiers PDF (< 10 Mo chacun) doit s'exécuter en moins de 5 minutes sur un réseau local
- L'interface de consultation doit afficher la liste des documents en moins de 2 secondes
- Les tâches de synchronisation et de purge doivent s'exécuter en arrière-plan sans bloquer l'interface

### 3.3 Fiabilité

- En cas d'échec de connexion à une source, l'application doit journaliser l'erreur et réessayer à la prochaine planification, sans impacter les autres sources
- Les fichiers locaux ne doivent jamais être supprimés tant que la copie n'est pas confirmée intègre (vérification de hash)
- La base de données doit être sauvegardée automatiquement (ou sauvegardable facilement)

### 3.4 Compatibilité des sources

| Protocole | Système cible | Usage |
|---|---|---|
| **SMB/CIFS** (smbclient / pysmb) | Windows (partages réseau) | Accès aux partages \\\\serveur\\partage |
| **SFTP/SCP** (paramiko) | Linux | Accès SSH aux répertoires distants |
| **Système de fichiers local / montage réseau** | Windows / Linux | Chemin local ou point de montage déjà existant |

### 3.5 Déploiement

- Application conteneurisée (Docker) pour faciliter le déploiement
- Compatible avec un hébergement sur serveur Linux (Debian/Ubuntu) ou Windows Server
- Configuration par variables d'environnement et/ou fichier de configuration
- Base de données SQLite pour la simplicité (migration possible vers PostgreSQL si nécessaire)

---

## 4. Architecture technique proposée

### 4.1 Stack technologique

| Composant | Technologie | Justification |
|---|---|---|
| Backend | **Python / Flask** | Cohérence avec l'écosystème existant (application BIC), compétences internes |
| Base de données | **SQLite** (WAL mode) | Légèreté, pas de serveur supplémentaire, suffisant pour le volume attendu |
| Tâches planifiées | **APScheduler** ou **Celery** (si montée en charge) | Exécution des synchronisations et purges en arrière-plan |
| Accès SMB | **smbprotocol** / **pysmb** | Connexion native aux partages Windows |
| Accès SFTP | **paramiko** | Connexion SSH/SFTP aux serveurs Linux |
| Frontend | **HTML/CSS/JS** (Jinja2 + Bootstrap ou équivalent) | Interface légère, pas de framework JS lourd |
| Viewer PDF | **PDF.js** (Mozilla) ou `<iframe>` natif | Consultation directe dans le navigateur |
| Conteneurisation | **Docker + docker-compose** | Déploiement reproductible |

### 4.2 Schéma de la base de données (préliminaire)

```
sources
├── id (PK)
├── nom
├── description
├── type_serveur (linux / windows)
├── protocole (smb / sftp / local)
├── adresse
├── port
├── chemin_distant
├── login (chiffré)
├── mot_de_passe (chiffré)
├── filtre_fichiers (pattern glob, ex: *.pdf)
├── frequence_sync_minutes
├── retention_jours
├── seuil_avertissement_jours
├── seuil_critique_jours
├── actif (booléen)
├── created_at
└── updated_at

documents
├── id (PK)
├── source_id (FK → sources)
├── nom_fichier
├── chemin_local
├── hash_sha256
├── taille_octets
├── date_modification_source (date du fichier sur le serveur distant)
├── date_collecte (date de la dernière copie locale)
├── statut (ok / avertissement / critique / purge)
├── created_at
└── updated_at

journaux
├── id (PK)
├── source_id (FK → sources, nullable)
├── type_evenement (sync / purge / erreur / connexion / acces)
├── message
├── details (JSON, optionnel)
├── created_at
```

### 4.3 Organisation du stockage local

```
/data/modes-degrades/
├── source-1-nom/
│   ├── document-a.pdf
│   ├── document-b.pdf
│   └── ...
├── source-2-nom/
│   ├── document-c.pdf
│   └── ...
└── _corbeille/
    ├── source-1-nom/
    │   └── ancien-document.pdf
    └── ...
```

---

## 5. Interface utilisateur (maquette fonctionnelle)

### 5.1 Tableau de bord (page d'accueil)

- **Résumé global** : nombre total de documents, nombre par statut (OK / avertissement / critique)
- **État des sources** : carte ou tableau avec pour chaque source : nom, dernière synchronisation, nombre de documents, état de connexion
- **Alertes** : liste des documents en statut critique ou des sources en erreur
- **Actions rapides** : bouton « Synchroniser tout », accès à l'ajout de source

### 5.2 Page Sources

- Liste des sources avec indicateurs d'état
- Formulaire d'ajout/modification avec test de connexion intégré
- Détail d'une source : paramètres, liste de ses documents, historique de synchronisation

### 5.3 Page Documents

- Tableau avec colonnes : nom, source, date modification, âge, taille, statut
- Filtres : par source, par statut, recherche texte
- Actions : voir (PDF viewer), télécharger, télécharger sélection (ZIP)
- Tri par colonne

### 5.4 Page Journaux

- Liste chronologique des événements
- Filtres par type (sync / purge / erreur), par source, par plage de dates
- Export CSV

---

## 6. Cas d'utilisation principaux

### CU1 - Ajouter une nouvelle source

1. L'utilisateur accède à la page Sources et clique sur « Nouvelle source »
2. Il renseigne les paramètres de connexion (type, adresse, chemin, identifiants, etc.)
3. Il clique sur « Tester la connexion » - l'application vérifie l'accessibilité et liste les fichiers trouvés
4. Il configure la fréquence de synchronisation et la durée de rétention
5. Il valide - la source est créée et une première synchronisation est déclenchée

### CU2 - Synchronisation automatique

1. Le scheduler déclenche la tâche de synchronisation pour une source
2. L'application se connecte au serveur distant avec les identifiants stockés
3. Elle liste les fichiers correspondant au filtre configuré
4. Pour chaque fichier : comparaison du hash avec la copie locale existante
5. Si le fichier est nouveau ou modifié : copie vers le répertoire local
6. Mise à jour de la base de données (métadonnées, date de collecte)
7. Journalisation de l'opération (succès, erreurs, fichiers ignorés)

### CU3 - Consultation d'un document

1. L'utilisateur accède à la page Documents
2. Il filtre par source ou par statut
3. Il clique sur un document - le PDF s'ouvre dans le viewer intégré
4. Il peut télécharger le fichier si nécessaire

### CU4 - Purge automatique

1. Le scheduler déclenche la tâche de purge
2. Pour chaque source : identification des fichiers dont l'âge dépasse la durée de rétention
3. Déplacement des fichiers dans le dossier « corbeille » (si période de grâce configurée) ou suppression directe
4. Mise à jour de la base de données
5. Journalisation

### CU5 - Détection d'un document obsolète

1. Lors de la synchronisation ou via le tableau de bord, un document dépasse le seuil d'avertissement
2. Son statut passe à « avertissement » (orange) puis « critique » (rouge) selon les seuils configurés
3. L'alerte est visible sur le tableau de bord
4. (Évolution future : notification par email)

---

## 7. Contraintes et hypothèses

### 7.1 Contraintes

- L'application doit pouvoir accéder aux serveurs sources depuis le réseau où elle est déployée (règles de pare-feu à prévoir)
- Les identifiants de connexion aux sources doivent être fournis par les administrateurs des serveurs concernés
- Le répertoire de stockage local doit disposer d'un espace disque suffisant (à dimensionner selon le volume de documents)
- Le serveur hébergeant l'application doit avoir accès aux ports SMB (445) et/ou SSH (22) des serveurs sources

### 7.2 Hypothèses

- Les fichiers PDF sont déposés par des applications tierces dans des répertoires connus et stables
- Le volume total de documents est estimé à quelques centaines à quelques milliers de fichiers (< 50 Go)
- Un seul utilisateur administre l'application (pas de gestion multi-utilisateurs avec rôles dans la V1)
- Les documents de modes dégradés ne contiennent pas de données patient nominatives (sinon, conformité HDS requise)

---

## 8. Phasage du développement

### Phase 1 - MVP (Minimum Viable Product)

- Gestion des sources (CRUD + test de connexion)
- Connexion SFTP (Linux) et SMB (Windows)
- Synchronisation manuelle et planifiée
- Stockage local organisé par source
- Interface de consultation avec filtres et viewer PDF
- Contrôle de fraîcheur avec indicateurs visuels
- Purge automatique paramétrable
- Authentification simple par mot de passe
- Journaux de synchronisation et de purge
- Déploiement Docker

### Phase 2 - Améliorations

- Notifications par email (documents obsolètes, erreurs de connexion)
- Authentification LDAP / Active Directory
- Gestion de rôles (administrateur / consultation seule)
- Export des rapports de conformité (liste des documents avec statut)
- API REST pour intégration avec d'autres outils internes

### Phase 3 - Évolutions

- Support de sources supplémentaires (FTP, WebDAV, S3)
- OCR sur les PDF pour recherche plein texte
- Versioning des documents (conservation des anciennes versions)
- Tableau de bord avec graphiques d'évolution dans le temps
- Application mobile (PWA) pour consultation hors réseau

---

## 9. Livrables attendus

| Livrable | Description |
|---|---|
| Code source | Application Python/Flask, versionné sous Git |
| Dockerfile + docker-compose.yml | Déploiement conteneurisé |
| Documentation technique | Architecture, schéma BDD, API interne, guide de déploiement |
| Documentation utilisateur | Guide d'utilisation de l'interface |
| Jeux de tests | Tests unitaires et d'intégration |
| Script d'initialisation | Création de la BDD, configuration initiale |

---

## 10. Critères de recette

- [ ] Ajout, modification et suppression d'une source fonctionnels
- [ ] Test de connexion opérationnel pour SMB et SFTP
- [ ] Synchronisation manuelle d'une source : fichiers copiés localement
- [ ] Synchronisation planifiée : exécution automatique selon la fréquence configurée
- [ ] Détection correcte des doublons (pas de recopie si fichier inchangé)
- [ ] Indicateurs de fraîcheur corrects (vert/orange/rouge selon les seuils)
- [ ] Purge automatique : fichiers supprimés après expiration de la rétention
- [ ] Interface de consultation : liste, filtres, recherche, viewer PDF fonctionnels
- [ ] Téléchargement unitaire et par lot (ZIP)
- [ ] Journaux consultables et exportables en CSV
- [ ] Identifiants des sources stockés chiffrés en base
- [ ] Application fonctionnelle via Docker
- [ ] Temps de réponse de l'interface < 2 secondes

---

## 11. Glossaire

| Terme | Définition |
|---|---|
| **CLCC** | Centre de Lutte Contre le Cancer |
| **Mode dégradé** | Fonctionnement de secours lorsqu'un système informatique est indisponible, basé sur des procédures et formulaires papier |
| **Source** | Serveur distant (Linux ou Windows) hébergeant des fichiers PDF de modes dégradés |
| **Synchronisation** | Opération de récupération des fichiers depuis une source distante vers le stockage local |
| **Rétention** | Durée maximale de conservation d'un fichier local avant purge automatique |
| **Fraîcheur** | Indicateur de l'âge d'un document par rapport à sa dernière modification |
| **SMB/CIFS** | Protocole de partage de fichiers Windows (Server Message Block) |
| **SFTP** | Protocole de transfert de fichiers sécurisé via SSH |
| **HDS** | Hébergement de Données de Santé - certification obligatoire pour le stockage de données de santé en France |

