---
lang: fr-FR
---

```{=html}
<section class="cover">
  <div class="cover-logos">
    <img src="assets/logo-uca.png" alt="Université Côte d'Azur">
    <img src="assets/logo-iut.png" alt="IUT Nice Côte d'Azur">
  </div>
  <div class="cover-center">
    <div class="cover-school">
      Université Côte d'Azur<br>
      IUT Nice Côte d'Azur<br>
      Département informatique<br>
      41 boulevard Napoléon III, 06206 Nice Cedex 3
    </div>
    <div class="cover-label">
      Rapport de stage pour l'obtention du Bachelor Universitaire de Technologie Informatique<br>
      Année universitaire 2025-2026
    </div>
    <div class="cover-title">
      Développement d'une application web de centralisation<br>
      et de suivi des PDF de modes dégradés
    </div>
    <div class="cover-author">
      Présenté par <strong>Maxime Giovanelli</strong><br>
      BUT2 Informatique
    </div>
    <div class="cover-company">
      <img src="assets/logo-lacassagne.png" alt="Centre Antoine Lacassagne">
    </div>
  </div>
  <div class="cover-bottom">
    <div class="cover-meta">
      <strong>Entreprise d'accueil</strong><br>
      Centre Antoine Lacassagne<br>
      33 avenue de Valombrose, 06100 Nice<br><br>
      <strong>Période</strong><br>
      Du 15 avril au 13 juin 2026<br><br>
      <strong>Encadrement</strong><br>
      Maître de stage : Julien Degardin<br>
      Tuteur école : Olivier Pantz
    </div>
    <div class="stamp-box">
      Signature et tampon de l'entreprise<br><br>
      Scan à intégrer dans la version numérique finale
    </div>
  </div>
  <div class="cover-footer">
    Maxime Giovanelli - Stage BUT2 Informatique - Centre Antoine Lacassagne - 2025-2026
  </div>
</section>
```

<div class="page-break"></div>

# Remerciements

Je tiens à remercier Julien Degardin, responsable au sein de la DSI du Centre Antoine Lacassagne, pour la qualité de son encadrement tout au long de ces neuf semaines. Ses retours techniques précis et sa capacité à formuler le besoin métier dès le début du projet ont permis de maintenir le développement dans un périmètre cohérent avec les contraintes réelles d'exploitation hospitalière.

Mes remerciements vont également à Olivier Pantz, tuteur pédagogique à l'IUT Nice Côte d'Azur, pour le suivi régulier du stage et les conseils méthodologiques. Je remercie enfin l'équipe de la DSI du Centre Antoine Lacassagne pour son accueil et sa disponibilité lors des échanges nécessaires à la compréhension du contexte informatique de l'établissement.

<div class="page-break"></div>

# Résumé

Le présent rapport rend compte d'un stage de neuf semaines effectué au Centre Antoine Lacassagne, centre de lutte contre le cancer situé à Nice, au sein de son service informatique (DSI).

Le besoin à l'origine du projet portait sur la continuité d'activité : lorsque des outils métier deviennent indisponibles, les équipes soignantes et administratives doivent pouvoir accéder à des documents PDF de modes dégradés (formulaires, procédures, fiches réflexes). Ces documents sont dispersés sur plusieurs serveurs hétérogènes (SFTP, SMB/CIFS, stockage local) et aucun outil ne permettait de contrôler leur fraîcheur ni d'en centraliser l'accès.

La problématique du stage était donc la suivante : comment centraliser et fiabiliser l'accès à ces documents critiques, tout en garantissant leur fraîcheur, leur traçabilité et la sécurité des accès dans un environnement hospitalier soumis à des exigences HDS ?

La méthode adoptée a suivi quatre grandes phases : analyse du cahier des charges et des contraintes HDS ; conception de l'architecture Flask/SQLite ; développement itératif des fonctionnalités (sources, synchronisation, interface, sécurité, API, tests) ; rédaction de la documentation d'exploitation.

L'application livrée, nommée StageSarcophage, repose sur Flask, Jinja, SQLAlchemy, SQLite, APScheduler et Docker. Elle centralise la collecte des PDF depuis trois types de sources, calcule un état de fraîcheur par document, propose une interface web de consultation avec viewer PDF, gère une purge progressive avec corbeille, expose une API REST et journalise toutes les opérations. Les contrôles de sécurité couvrent les sessions, les tokens Bearer, le CSRF, la CSP, le chiffrement Fernet des identifiants et la confinement des chemins.

Le résultat est une base applicative documentée, testée et conteneurisable, prête pour une validation en environnement réel par la DSI.

# Summary

This report covers a nine-week internship at Centre Antoine Lacassagne, a cancer treatment center in Nice, within its IT department (DSI).

The project originated from a business continuity need: when standard tools become unavailable, medical and administrative staff must access degraded-mode PDF documents (forms, procedures, reference sheets). These documents are scattered across heterogeneous servers (SFTP, SMB/CIFS, local storage) with no centralized tool to track their freshness or availability.

The core research question was: how to centralize and secure access to these critical documents while ensuring freshness tracking, auditability, and access security in a healthcare environment subject to HDS requirements?

The methodology followed four phases: requirements and HDS constraints analysis; Flask/SQLite architecture design; iterative development (sources, synchronization, interface, security, API, tests); and operational documentation.

The delivered application, named StageSarcophage, uses Flask, Jinja, SQLAlchemy, SQLite, APScheduler and Docker. It centralizes PDF collection from three source types, computes per-document freshness status, provides a web interface with integrated PDF viewer, manages progressive purge with a trash bin, exposes a REST API, and logs all operations. Security controls cover sessions, Bearer tokens, CSRF, CSP, Fernet credential encryption, and path confinement.

The result is a documented, tested, and containerizable application base ready for production validation by the DSI.

<div class="page-break"></div>

# Sommaire

1. Remerciements
2. Résumé et Summary
3. Table des illustrations et glossaire
4. Introduction
5. Partie I : Analyse de la situation
   - I.1 Présentation du Centre Antoine Lacassagne
   - I.2 Service DSI et contraintes HDS
   - I.3 Analyse des besoins
   - I.4 Cahier des charges et matrice des exigences
6. Partie II : Conception et réalisation
   - II.1 Choix technologiques et argumentation
   - II.2 Architecture applicative
   - II.3 Sources et synchronisation
   - II.4 Fraîcheur, purge et corbeille
   - II.5 Interface web et parcours utilisateur
   - II.6 API REST
   - II.7 Sécurité
   - II.8 Tests et qualité
   - II.9 Déploiement et exploitation
7. Partie III : Bilan et perspectives
   - III.1 Résultats obtenus
   - III.2 Perspectives et évolutions
8. Accompagnement du CSU lors des interventions
   - Types d'interventions
   - Notions abordées
   - Environnement informatique hospitalier
   - Continuité de service en milieu hospitalier
   - Relation avec les utilisateurs hospitaliers
9. Difficultés rencontrées
10. Conclusion
11. Bibliographie et sitographie
12. Annexes
13. Table des illustrations

# Table des illustrations

1. Situation avant et après StageSarcophage
2. Architecture applicative (couches Flask)
3. Modèle de données : entités et relations
4. Flux de synchronisation d'un document PDF
5. Interface : tableau de bord

# Glossaire

**API REST** — Interface HTTP exposée sous `/api/v1`, utilisant des tokens Bearer pour l'authentification.

**APScheduler** — Bibliothèque Python de planification de tâches périodiques, utilisée pour déclencher les synchronisations automatiques.

**Bearer token** — Jeton transmis dans l'en-tête `Authorization`, permettant l'accès programmatique à l'API sans session web.

**CSRF** — Cross-Site Request Forgery : attaque forçant un navigateur authentifié à envoyer une requête non voulue. Les formulaires modifiants sont protégés par un jeton CSRF.

**CSP** — Content Security Policy : en-tête HTTP limitant les ressources chargées par le navigateur, réduisant la surface d'attaque XSS.

**DSI** — Direction des Systèmes d'Information du Centre Antoine Lacassagne.

**Fernet** — Schéma de chiffrement symétrique authentifié (AES-128-CBC + HMAC-SHA256), utilisé pour chiffrer les identifiants des sources en base.

**GED** — Gestion Électronique de Documents : système dédié au cycle de vie documentaire complet. StageSarcophage n'est pas une GED ; il cible uniquement la collecte et la consultation des PDF de modes dégradés.

**HDS** — Hébergeur de Données de Santé : certification française encadrant l'hébergement de données médicales.

**Mode dégradé** — Procédure ou document utilisé lorsque le fonctionnement normal d'un outil métier n'est plus disponible.

**RBAC** — Role-Based Access Control : les droits sont attribués à des rôles, eux-mêmes assignés aux utilisateurs.

**SHA-256** — Fonction de hachage cryptographique, utilisée pour détecter les fichiers inchangés et éviter les copies inutiles.

**SFTP** — SSH File Transfer Protocol : transfert de fichiers sécurisé via SSH, utilisé pour les sources Linux.

**SMB/CIFS** — Server Message Block / Common Internet File System : protocole d'accès aux partages de fichiers Windows.

**SQLite WAL** — Write-Ahead Logging : mode d'écriture de SQLite améliorant les performances en lecture concurrente.

<div class="page-break"></div>

# Introduction

Le Centre Antoine Lacassagne repose sur un ensemble d'outils informatiques pour la gestion des soins, des patients et des procédures administratives. Lorsque l'un de ces outils devient indisponible (panne réseau, mise à jour bloquante, incident serveur), le personnel doit pouvoir continuer à travailler. C'est le rôle des **modes dégradés** : des procédures et formulaires papier ou PDF qui prennent le relais des outils numériques habituels.

Ces documents existent dans l'établissement. Le problème est leur gestion : stockés sur plusieurs serveurs hétérogènes (un serveur SFTP Linux pour le bloc opératoire, un partage SMB Windows pour le service des urgences, un dossier local pour d'autres services), ils ne font l'objet d'aucune vue centralisée. Personne ne peut répondre facilement aux questions opérationnelles : ce document est-il encore à jour ? Existe-t-il bien sur le serveur ? Quand a-t-il été modifié la dernière fois ?

Résoudre ce problème exige de traiter plusieurs contraintes simultanément : fédérer des protocoles hétérogènes dans un seul point d'accès ; calculer et exposer un état de fraîcheur documentaire sans saturer le réseau ; protéger les identifiants de connexion aux serveurs tout en maintenant une administration simple ; déployer une application robuste sur une infrastructure hospitalière sans introduire de composants lourds. C'est dans ce cadre que la DSI a défini la mission de ce stage : concevoir et développer une application web interne répondant à ces contraintes.

StageSarcophage est l'application développée au cours de ces neuf semaines. Elle collecte les PDF depuis les sources déclarées, en conserve une copie locale avec déduplication, calcule un état de fraîcheur par document, propose une interface web de consultation rapide et journalise toutes les opérations. La figure 1 illustre le changement apporté : d'une dispersion sur serveurs hétérogènes sans visibilité, à un accès centralisé, sécurisé et traçable.

![Figure 1 : Situation avant et après StageSarcophage — dispersion des sources vs accès centralisé.](images/schema-avant-apres.png)

Ce rapport est organisé en trois parties. La première décrit l'analyse de la situation : présentation de l'établissement et de son service informatique, contraintes réglementaires HDS, formulation des besoins et hiérarchisation des exigences. La deuxième présente la conception et la réalisation technique : pour chaque composant développé, les choix d'implémentation sont argumentés par comparaison avec les alternatives disponibles. La troisième dresse un bilan : résultats obtenus par rapport aux exigences initiales, difficultés rencontrées et solutions apportées, perspectives prioritaires pour une reprise du projet par la DSI.

<div class="page-break"></div>

# Partie I : Analyse de la situation

## I.1 Présentation du Centre Antoine Lacassagne

Le Centre Antoine Lacassagne (CAL) est un Centre de Lutte Contre le Cancer (CLCC) situé au 33 avenue de Valombrose à Nice. Fondé en 1947, il fait partie des vingt établissements du réseau Unicancer entièrement dédiés à la prise en charge du cancer. L'établissement accueille chaque année plus de 15 000 patients et emploie environ 800 personnes. Il couvre les trois missions des CLCC : soins (oncologie médicale, radiothérapie, chirurgie), recherche clinique et formation.

Sur le plan informatique, le Centre dispose d'une DSI qui gère l'infrastructure réseau, les serveurs, les applications métier (dossier patient informatisé, système d'information radiologique, outils administratifs) et la sécurité des systèmes. L'établissement traite des données de santé au sens de la réglementation française, ce qui soumet son système d'information à des exigences strictes de sécurité, de traçabilité et de confidentialité.

## I.2 Service DSI et contraintes HDS

La DSI du CAL intervient sur un périmètre large : gestion des accès, exploitation des serveurs, déploiement d'applications internes, sauvegardes et continuité de service. Le contexte hospitalier impose des contraintes spécifiques que l'on ne retrouve pas dans une entreprise standard :

**Exigences HDS** : L'hébergement de données de santé est encadré en France par la certification HDS (Hébergeur de Données de Santé). Elle impose des mesures de sécurité documentées, une traçabilité des accès, des procédures de sauvegarde et une gestion formalisée des incidents. Les choix applicables à StageSarcophage (chiffrement des identifiants, journaux d'opérations, contrôle des accès par rôle, gestion des secrets) s'alignent sur ces exigences dans le périmètre d'une application interne.

**Continuité d'activité** : Un établissement de santé ne peut pas s'arrêter lors d'une panne informatique. Des procédures de mode dégradé existent pour chaque situation critique : panne du dossier patient, indisponibilité du système de prescription, coupure réseau. Ces procédures reposent sur des documents PDF qui doivent être accessibles même quand l'outil principal ne l'est plus.

**Contraintes de déploiement** : La DSI ne peut pas maintenir une infrastructure complexe pour une application interne de portée limitée. Le cahier des charges précise explicitement : SQLite acceptable, pas de serveur de base de données externe requis, déploiement par conteneur Docker, configuration par variables d'environnement.

## I.3 Analyse des besoins

L'analyse des besoins a structuré la demande en trois niveaux :

**Besoins fonctionnels primaires** (cœur du système) :
- Déclarer des sources (SFTP, SMB, local), tester leur connexion, configurer leur fréquence de synchronisation.
- Synchroniser automatiquement les PDF depuis ces sources, en conservant une copie locale.
- Suivre la fraîcheur de chaque document (date de dernière modification source, statut ok/avertissement/critique).
- Permettre la consultation, la recherche, le filtrage et le téléchargement des documents depuis une interface web.
- Conserver un journal de toutes les opérations (synchronisations, purges, connexions, erreurs).

**Besoins fonctionnels secondaires** (qualité d'exploitation) :
- Gestion des utilisateurs, des rôles et des permissions (RBAC).
- API REST pour permettre des intégrations futures (monitoring, outils DSI).
- Purge automatique des documents dépassant leur durée de rétention, avec passage par une corbeille.
- Notifications par email en cas d'erreur ou de documents critiques.

**Contraintes non fonctionnelles** :
- Sécurité : chiffrement des identifiants, protection des sessions, headers HTTP, contrôle des chemins.
- Déployabilité : Docker + Gunicorn, configuration par variables d'environnement, SQLite.
- Maintenabilité : code structuré en couches, tests automatisés, documentation d'exploitation.

## I.4 Cahier des charges et matrice des exigences

Le document `cahier_des_charges.md` fourni par la DSI liste les exigences détaillées. Voici l'état de livraison en fin de stage.

Livré et validé par les tests : sources SFTP, SMB/CIFS et locales ; test de connexion par source ; synchronisation manuelle et planifiée ; déduplication SHA-256 ; statuts de fraîcheur ; interface web avec viewer PDF, téléchargement et export ZIP ; RBAC ; chiffrement Fernet des identifiants ; journaux d'opérations.

Partiel : la purge est opérationnelle mais certains paramètres avancés n'ont pas été démontrés en recette ; l'API REST couvre la lecture, les stats, le déclenchement de sync et les jobs, mais pas le CRUD sur les sources.

Non entièrement résolu : LDAP est configurable mais non validé sur annuaire réel ; HTTPS est assuré par le reverse proxy, pas par Flask directement ; le benchmark "500 PDF en moins de 5 minutes" n'a pas été prouvé ; la sauvegarde automatique n'a pas été livrée.

La planification du projet a couvert neuf semaines : analyse (S1), architecture et modèle de données (S2), connecteurs et sources (S3), synchronisation et fraîcheur (S4), interface web (S5), sécurité et API (S6-S7), tests et documentation (S8-S9).

Le planning réalisé a globalement suivi le planning prévisionnel, avec un décalage d'une semaine sur la partie sécurité, compensé en réduisant le périmètre des tests d'intégration.

<div class="page-break"></div>

# Partie II : Conception et réalisation

## II.1 Choix technologiques et argumentation

Les choix techniques ont été contraints par le cahier des charges et validés après analyse des alternatives disponibles.

### Backend : Flask

Flask est explicitement référencé dans le cahier des charges. Il est léger, son rendu HTML côté serveur via Jinja est natif, et son déploiement derrière Gunicorn est direct. Django apporte davantage de fonctionnalités intégrées mais reste surdimensionné pour une application interne de cette portée. FastAPI est adapté aux API asynchrones mais pas au rendu HTML complet côté serveur.

### Base de données : SQLite via SQLAlchemy

SQLite en mode WAL est explicitement autorisé par le cahier des charges. Il est embarqué dans Python, ne nécessite aucune installation, et sa sauvegarde se résume à une copie de fichier. Les accès concurrents en écriture sont limités, mais suffisants pour le volume attendu. Une migration vers PostgreSQL reste possible via SQLAlchemy si les besoins évoluent.

### File de jobs : ThreadPoolExecutor

Le volume attendu est de quelques dizaines de synchronisations par jour. Le `ThreadPoolExecutor` interne ne demande aucune dépendance supplémentaire et aucune infrastructure. Celery ou RQ offriraient une meilleure persistance des jobs et une résistance aux redémarrages, mais imposent Redis et un worker séparé, ce qui est disproportionné pour ce contexte. La perte des jobs en cours lors d'un arrêt du conteneur est documentée comme limitation connue.

### Chiffrement des identifiants : Fernet

Fernet est correct par construction : l'authentification du message par HMAC-SHA256 est intégrée, la bibliothèque est auditée publiquement, et la rotation de clé est documentée. Implémenter AES-CBC manuellement expose à des erreurs classiques comme un IV fixe ou l'absence de MAC. Stocker les identifiants en variables d'environnement seules ne protège pas contre la lecture directe de la base de données.

## II.2 Architecture applicative

StageSarcophage est un monolithe Flask organisé en couches distinctes. Cette organisation évite le mélange des responsabilités qui fragilise les applications web internes sur le long terme.

Comme illustré en figure 2, l'architecture positionne StageSarcophage entre les sources hétérogènes, les utilisateurs web et les clients API.

![Figure 2 : Architecture applicative de StageSarcophage : couches Flask, services et stockage.](images/schema-architecture-generale.png)

Les routes HTTP (`app/routes/`) gèrent uniquement l'authentification, la lecture des paramètres, la délégation aux services et le rendu. Les services (`app/services/`) portent la logique métier : synchronisation, purge, jobs de fond, notifications, LDAP, connecteurs. Les modèles SQLAlchemy (`app/models/`) définissent le schéma de données et les invariants. Les utilitaires (`app/utils/`) fournissent des fonctions transverses : sécurité des chemins, chiffrement, sanitisation, décorateurs de permissions.

Comme illustré en figure 3, le modèle de données place `Source` et `Document` au centre du flux. Les autres entités (`Journal`, `BackgroundJob`, `User`, `Role`, `APIToken`) servent l'exploitation et la sécurité.

![Figure 3 : Modèle de données : entités SQLAlchemy et leurs relations.](images/schema-modele-donnees.png)

## II.3 Sources et synchronisation

Une source représente l'origine des PDF : protocole (`sftp`, `smb`, `local`), adresse réseau, chemin distant, identifiants chiffrés, filtres, seuils de fraîcheur et durée de rétention. Les identifiants sont accessibles via les propriétés Python `login` et `mot_de_passe` de `Source` ; les colonnes physiques en base contiennent les valeurs chiffrées Fernet.

Le service `app/services/sync_service.py` applique la même logique à tous les protocoles :

1. Sélection du connecteur selon le protocole (`_get_connector`).
2. Inventaire des fichiers distants correspondant au filtre glob.
3. Pour chaque fichier : nettoyage du nom, téléchargement vers un fichier temporaire, calcul du hash SHA-256.
4. Comparaison avec le hash stocké en base : remplacement du fichier final uniquement si le contenu a changé.
5. Journalisation du résultat (succès, inchangé, erreur).

L'écriture via fichier temporaire est importante : elle évite qu'une erreur réseau en milieu de transfert ne produise un fichier PDF partiellement écrit qui serait servi à l'utilisateur.

Comme illustré en figure 4, la synchronisation suit une chaîne : inventaire, hash de contrôle, filtrage de doublon, écriture contrôlée, journalisation.

![Figure 4 : Flux de synchronisation d'un document PDF : de la détection à l'écriture atomique.](images/schema-flux-synchronisation.png)

La difficulté principale de cette partie concerne les noms de fichiers. Un nom distant ne peut pas être utilisé tel quel : un fichier nommé `../secret.pdf` sur un serveur SFTP doit être refusé avant tout stockage local. Cette contrainte est traitée dans `app/utils/files.py` (confinement par `realpath`/`commonpath`) et s'applique à la synchronisation, au téléchargement, au ZIP, à la purge et à la restauration depuis la corbeille.

## II.4 Fraîcheur, purge et corbeille

Chaque document porte un statut calculé à partir de son âge (différence entre la date de collecte et aujourd'hui) et des seuils configurés sur sa source : `ok`, `avertissement`, `critique`, `purge`. Ces seuils sont paramétrables par source, ce qui permet d'appliquer des politiques différentes selon la criticité des documents.

La purge ne supprime pas immédiatement. Quand un document dépasse son seuil de rétention, il est déplacé vers `_corbeille` et son statut passe à `PURGE`. Un nettoyage définitif supprime les fichiers de la corbeille après la durée `CORBEILLE_RETENTION_JOURS`. Cette approche à deux étapes limite le risque d'erreur irréversible.

## II.5 Interface web et parcours utilisateur

L'interface est rendue côté serveur avec Jinja2 et Bootstrap 5. Ce choix évite un frontend JavaScript complexe pour des écrans de gestion interne. L'interface couvre : connexion, tableau de bord, gestion des sources, synchronisation, consultation des documents, journaux et administration.

Comme illustré en figure 5, le tableau de bord présente les indicateurs clés en temps réel : nombre de documents, sources actives, dernière synchronisation, espace utilisé, activité récente et répartition par source.

![Figure 5 : Tableau de bord : indicateurs clés et activité récente.](images/ui-dashboard.png)

L'export ZIP est limité à 100 documents et 500 Mo. Ce plafond évite une réponse HTTP de taille excessive générée depuis l'interface, ce qui pourrait saturer la mémoire du serveur ou la connexion de l'utilisateur.

## II.6 API REST

L'API v1 est définie dans `app/routes/api.py` et documentée via OpenAPI dans `app/api/openapi.py`. Elle expose : un healthcheck public, des statistiques agrégées, la liste et le détail des sources, le déclenchement d'une synchronisation, le statut d'un job de fond, la liste et le détail des documents, et le téléchargement d'un document.

L'API n'est pas un CRUD complet : la création et suppression de sources passent par l'interface web. Les décorateurs dans `app/utils/decorators.py` et les tests dans `tests/test_api_permissions.py` garantissent que les deux chemins (session web et token Bearer) aboutissent aux mêmes contrôles de permissions.

Un exemple de requête API :

```bash
# Lister les sources (token Bearer)
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/v1/sources

# Déclencher une synchronisation
curl -X POST -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/v1/sources/1/sync

# Vérifier le statut du job
curl -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/v1/jobs/<job-id>
```

## II.7 Sécurité

La sécurité de StageSarcophage est construite par couches. Aucune mesure seule n'est suffisante ; leur combinaison réduit la surface d'attaque de façon significative.

**Authentification et sessions** : L'interface web utilise Flask-Login avec sessions côté serveur. Les mots de passe sont hachés avec bcrypt (coût 12). Les routes protégées vérifient les permissions via des décorateurs (`@require_permission`) : un utilisateur peut avoir le rôle "Opérateur" sans avoir la permission de supprimer des sources.

**Tokens API** : Les tokens Bearer sont stockés hachés en base (pas en clair). Leur révocation est immédiate. Chaque token peut porter des permissions restreintes.

**Protection des formulaires** : Flask-WTF fournit des jetons CSRF sur tous les formulaires modifiants. Un attaquant qui trompe un utilisateur en visitant une URL ne peut pas déclencher une action depuis un autre site.

**Headers HTTP** : `app/__init__.py` pose les en-têtes `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, une politique de referrer, une permissions policy et une Content Security Policy (CSP) avec nonce dynamique sur les scripts. Ces en-têtes limitent les vecteurs d'attaque XSS et de clickjacking.

**Chiffrement des identifiants** : Les identifiants des sources (login, mot de passe) sont chiffrés avec Fernet avant stockage. La clé de chiffrement (`ENCRYPTION_KEY`) est séparée de la clé de session (`SECRET_KEY`) et doit rester dans le fichier `.env` avec permissions restrictives (`chmod 600`).

**Confinement des chemins** : `app/utils/files.py` utilise `os.path.realpath` et `os.path.commonpath` pour vérifier que tout chemin demandé reste bien sous le répertoire de stockage autorisé. Cette vérification est plus robuste qu'un simple remplacement de `../`, car elle résout les liens symboliques et gère les chemins absolus.

**Sanitisation des exports** : Les exports CSV/XLSX neutralisent les valeurs commençant par `=`, `+`, `-` ou `@` pour éviter les injections de formules tableur. Les notifications et rapports HTML échappent systématiquement les contenus insérés.

## II.8 Tests et qualité

La commande `make check` orchestre : Ruff (linter Python), pytest avec couverture, Bandit (analyse statique de sécurité), `pip-audit` (vulnérabilités des dépendances), un scan de secrets suivis par Git et une vérification des permissions du fichier `.env`.

Les vingt fichiers de tests couvrent les modèles, la synchronisation, la purge, les sources, les permissions API et web, la sécurité (traversée de chemin, injections), LDAP, SFTP, SMB, les exports, les notifications et les templates.

Les tests utilisent SQLite en mémoire et un stockage temporaire. Cette stratégie maintient des tests rapides et reproductibles en CI, au prix d'une couverture qui ne prouve pas la compatibilité avec tous les comportements de serveurs réels.

Le mode `JOBS_RUN_INLINE=true` exécute les jobs de fond de façon synchrone pendant les tests, rendant les assertions sur les états finaux déterministes.

## II.9 Déploiement et exploitation

Le dépôt fournit un `Dockerfile`, un `docker-compose.yml`, un `entrypoint.sh` et les commandes Flask pour initialiser la base.

Variables minimales requises en production :

```bash
SECRET_KEY=<valeur aléatoire 32 octets>
ENCRYPTION_KEY=<clé Fernet générée>
STORAGE_DIR=/chemin/vers/stockage
FLASK_ENV=production
```

L'application peut être lancée localement ou via Docker :

```bash
# Local
.venv/bin/flask --app run.py init-db
.venv/bin/flask --app run.py create-admin --username admin --password <mot_de_passe>
.venv/bin/flask --app run.py run --host 0.0.0.0 --port 5000

# Docker
docker compose build && docker compose up -d
docker compose exec web flask init-db
docker compose exec web flask create-admin --username admin --password <mot_de_passe>
```

Les jobs de fond s'exécutent dans un `ThreadPoolExecutor` interne. Un redémarrage du processus pendant une synchronisation peut nécessiter un déclenchement manuel. L'exploitant doit être informé de cette limite.

<div class="page-break"></div>

# Partie III : Bilan et perspectives

## III.1 Résultats obtenus

StageSarcophage répond au cœur du cahier des charges : une application web interne, conteneurisable, qui collecte des PDF depuis des sources SFTP, SMB et locales, calcule leur fraîcheur, permet leur consultation et trace les opérations.

Les fonctionnalités livrées couvrent : gestion des sources, synchronisation avec déduplication SHA-256, consultation (interface web, viewer PDF, export ZIP), sécurité (CSRF, CSP, Fernet, RBAC, confinement de chemins) et API REST. LDAP et SMTP sont configurables mais non validés sur infrastructure réelle ; le benchmark 500 PDF reste à prouver. Le résultat est documenté et prêt à une reprise par la DSI.

## III.2 Perspectives et évolutions

Priorité haute : valider les connecteurs sur infrastructure réelle (SFTP, SMB, LDAP, SMTP) et prouver le benchmark 500 PDF en moins de 5 minutes avec un jeu de fichiers représentatif.

Priorité moyenne : implémenter le CRUD sources via l'API REST (politique d'autorisation à affiner) ; mettre en place une sauvegarde automatique de la base SQLite, du stockage PDF et du fichier `.env`.

Priorité basse : envisager une migration PostgreSQL si le volume d'accès concurrents le justifie ; faire réaliser un audit de sécurité externe une fois le périmètre de production figé.

<div class="page-break"></div>

# Accompagnement du CSU lors des interventions

En parallèle du développement de l'application StageSarcophage, j'ai eu l'opportunité d'accompagner des membres de la Cellule de Support aux Utilisateurs (CSU) du Centre Antoine Lacassagne lors de leurs interventions au sein des différents services de l'établissement. Cette expérience, complémentaire à la mission de développement, m'a permis de découvrir le quotidien du support informatique dans un environnement hospitalier et d'appréhender concrètement les enjeux de continuité de service que le projet StageSarcophage cherche précisément à adresser.

Les interventions du CSU se décomposaient en deux types distincts :

- **Les interventions sur site** : déplacements physiques dans les différents services de l'établissement (bloc opératoire, service des urgences, unités d'hospitalisation, services administratifs) pour résoudre des incidents nécessitant une présence sur place, qu'il s'agisse de problèmes matériels, de configuration ou de pannes logicielles complexes,
- **Les interventions à distance** : assistance téléphonique ou via prise en main à distance permettant de guider le personnel soignant ou administratif dans la résolution de leur problème sans déplacement physique, ce type d'intervention permettant de traiter rapidement les cas les moins complexes et de libérer des ressources pour les situations plus critiques.

L'ensemble des interventions pouvaient concerner aussi bien le personnel soignant que les équipes administratives de l'établissement.

## Notions abordées

Au cours de ces accompagnements, de nombreux concepts techniques et organisationnels ont été abordés. Cette partie du stage s'est révélée être un apprentissage complémentaire très précieux, me confrontant à des réalités concrètes que le seul développement logiciel n'aurait pas permis d'appréhender.

### Environnement informatique hospitalier

Le parc informatique du Centre Antoine Lacassagne présente des spécificités importantes par rapport à un environnement d'entreprise classique. Les postes de travail sont partagés entre plusieurs utilisateurs, soumis à des politiques de sécurité strictes, et doivent répondre à des exigences de disponibilité permanente. J'ai pu observer et participer à plusieurs types d'opérations :

- La configuration et le dépannage de postes de travail soumis à des politiques de sécurité strictes, notamment la gestion des sessions utilisateur sur des postes partagés entre plusieurs membres du personnel soignant ou administratif,
- La gestion des droits d'accès aux ressources réseau et aux applications métier, en particulier le dossier patient informatisé (DPI) et les outils de prescription médicale, dont les accès sont finement contrôlés par profil et par service,
- Le paramétrage et la résolution d'incidents liés aux imprimantes et périphériques dans les unités de soins, équipements particulièrement sollicités dans le contexte hospitalier,
- La vérification et le rétablissement de la connectivité réseau dans les services, un incident réseau pouvant bloquer simultanément l'accès à l'ensemble des outils numériques d'un service.

Ces interventions m'ont permis de comprendre la complexité inhérente d'un parc informatique hospitalier : des contraintes de sécurité très fortes coexistent avec une exigence de simplicité d'utilisation pour des personnels dont l'informatique n'est pas le cœur de métier, et dont le moindre blocage a un impact direct sur la prise en charge des patients.

### Continuité de service en milieu hospitalier

La particularité fondamentale du contexte hospitalier réside dans l'exigence absolue de continuité de service. Contrairement à un environnement d'entreprise standard, une panne informatique dans un service de soins peut avoir des répercussions directes sur la prise en charge des patients. Cette réalité confère aux interventions du CSU une dimension d'urgence et de responsabilité que l'on ne retrouve pas nécessairement dans d'autres contextes.

Ces accompagnements ont considérablement renforcé ma compréhension de la problématique au cœur du projet StageSarcophage : les modes dégradés ne sont pas un luxe organisationnel mais une nécessité opérationnelle absolue. Lorsqu'un outil numérique devient indisponible — qu'il s'agisse d'une panne du dossier patient, d'une indisponibilité du système de prescription ou d'une coupure réseau — le personnel soignant doit pouvoir basculer immédiatement vers des procédures alternatives sans perdre de temps. J'ai pu constater lors d'une intervention qu'une indisponibilité temporaire des outils de prescription avait conduit une unité à recourir à ses formulaires papier : c'est exactement ce scénario que l'application développée cherche à sécuriser, en garantissant un accès fiable, centralisé et toujours à jour aux documents de modes dégradés.

### Relation avec les utilisateurs hospitaliers

Les interventions du CSU m'ont également sensibilisé à la dimension relationnelle et humaine du support informatique. Le personnel hospitalier — médecins, cadres de santé, infirmiers, aides-soignants, secrétaires médicales, agents administratifs — présente des niveaux d'aisance informatique très variables. La communication doit constamment s'adapter à l'interlocuteur : vulgariser les termes techniques, reformuler les explications de façon concrète, et adopter une posture rassurante face à des utilisateurs parfois sous pression du fait de leur environnement de travail particulièrement exigeant.

J'ai pu observer que la qualité perçue d'une intervention tient autant à la résolution effective du problème qu'à la qualité de l'échange avec l'utilisateur. Expliquer clairement ce qui s'est passé, rassurer sur la sécurité des données du patient, et indiquer les précautions à prendre pour éviter la récurrence de l'incident contribue à établir un climat de confiance durable entre le CSU et les équipes soignantes ou administratives qu'il accompagne.

Cette expérience m'a conforté dans l'importance de concevoir des interfaces simples et des messages d'état compréhensibles dans StageSarcophage : une application destinée à du personnel non-informaticien, utilisée précisément dans des moments de panne et de stress, doit être pensée avant tout pour celui qui l'utilise dans la difficulté.

<div class="page-break"></div>

# Difficultés rencontrées

La principale difficulté à laquelle j'ai dû faire face est la gestion du temps et l'équilibre entre les différentes dimensions du stage. N'étant pas exclusivement dédié au développement, les accompagnements du CSU ont occupé une part non négligeable du temps disponible, ce qui a conduit à ajuster le périmètre de certaines fonctionnalités en cours de projet.

**Difficulté 1 : Séparation des responsabilités entre routes et services**

Au début du projet, les premières routes Flask mélangeaient logique d'accès réseau, règles de stockage et rendu HTML. Cette organisation fragile a été corrigée dès la deuxième semaine en introduisant une couche de services (`app/services/`) strictement séparée des routes. Cette décision a simplifié considérablement les tests et la lecture du code par la suite.

**Difficulté 2 : Tests de protocoles sans infrastructure**

SFTP, SMB, LDAP et SMTP ne peuvent pas être testés contre de vrais serveurs dans un pipeline d'intégration continue standard. La solution retenue est l'utilisation de mocks (`unittest.mock`) qui simulent les bibliothèques sous-jacentes (Paramiko, smbprotocol). Cette approche permet de tester tous les scénarios (succès, erreurs réseau, timeouts, entrées dangereuses) de façon reproductible. La contrepartie est claire : une recette sur infrastructure réelle reste nécessaire avant déploiement.

**Difficulté 3 : Sécurité des noms de fichiers issus de sources externes**

Un nom de fichier provenant d'un serveur SFTP ou SMB est une entrée non fiable. Le cas `../secret.pdf` est le plus évident, mais des chemins absolus ou des caractères de contrôle peuvent également poser problème. La solution (vérification par `realpath`/`commonpath` dans `app/utils/files.py`) s'est avérée plus robuste qu'un simple filtrage de chaînes et a dû être appliquée de façon cohérente à tous les points du code qui manipulent des chemins de fichiers (sync, téléchargement, ZIP, purge, corbeille).

**Difficulté 4 : Double modèle d'accès : sessions web et tokens API**

L'interface web utilise des sessions avec CSRF ; l'API utilise des tokens Bearer sans CSRF. Ces deux chemins doivent aboutir aux mêmes règles de permissions métier. Le risque était de sécuriser l'interface en oubliant l'API. La solution est de centraliser les contrôles de permissions dans des décorateurs réutilisables (`app/utils/decorators.py`) appliqués uniformément, et de couvrir ce point avec des tests dédiés (`tests/test_api_permissions.py`).

L'apprentissage des concepts de sécurité propres à un contexte hospitalier (HDS, chiffrement des identifiants, contrôle des chemins) a également nécessité un temps d'appropriation important, ce qui a décalé d'une semaine la partie sécurité, compensé en réduisant le périmètre des tests d'intégration. Ces difficultés ont cependant été une source d'apprentissage considérable et se révèlent être parmi les aspects les plus enrichissants du stage.

<div class="page-break"></div>

# Conclusion

StageSarcophage répond au besoin posé en début de stage : les PDF de modes dégradés, dispersés sur des serveurs hétérogènes sans visibilité, sont désormais collectés, dédupliqués, datés et accessibles depuis un point d'accès unique, sécurisé et traçable.

Les choix techniques (Flask, SQLite, APScheduler, Fernet, ThreadPoolExecutor, Docker) ont été guidés par les contraintes du cahier des charges (simplicité de déploiement, environnement hospitalier, adéquation au volume attendu) et non par une recherche de sophistication technique. Chaque choix a fait l'objet d'une comparaison avec les alternatives disponibles, et ses limites sont documentées.

Le travail de sécurité a été plus long que prévu : la liste des points à traiter (confinement des chemins, sanitisation des exports tableur, CSRF, CSP, rotation Fernet, double modèle d'accès session/token) révèle qu'une application de collecte de fichiers comporte des angles d'attaque nombreux dès qu'elle manipule des entrées externes dans un contexte hospitalier.

La prochaine étape est une recette par la DSI sur l'infrastructure réelle du Centre Antoine Lacassagne, pour valider les connecteurs et ajuster les paramètres de rétention avant une mise en service opérationnelle.

# Bibliographie et sitographie

## Documentation technique

- Pallets, *Flask Documentation v3.x*, https://flask.palletsprojects.com/
- SQLAlchemy Authors, *SQLAlchemy 2.0 Documentation*, https://docs.sqlalchemy.org/
- Jeff Forcier et al., *Paramiko Documentation*, https://www.paramiko.org/
- Alex Grönholm, *APScheduler Documentation*, https://apscheduler.readthedocs.io/
- Python Cryptographic Authority, *cryptography : Fernet*, https://cryptography.io/en/latest/fernet/
- Jordan Doyle et al., *smbprotocol Documentation*, https://github.com/jborean93/smbprotocol

## Sources institutionnelles

- Centre Antoine Lacassagne, site officiel : https://www.centreantoinelacassagne.org/
- Unicancer, fiche établissement CAL : https://www.unicancer.fr/fr/clcc/centre-antoine-lacassagne/
- Université Côte d'Azur, logos officiels : https://univ-cotedazur.fr/universite/communication-et-marque/nos-logos
- IUT Nice Côte d'Azur : https://iut.univ-cotedazur.fr/
- Département BUT Informatique : https://butinfo.univ-cotedazur.fr/
- ANSSI, *Guide des bonnes pratiques de l'informatique*, https://www.ssi.gouv.fr/guide/bonnes-pratiques-de-linformatique/
- ANS (Agence du Numérique en Santé), *Certification HDS*, https://esante.gouv.fr/labels-certifications/hds

<div class="page-break"></div>

# Annexes

## Annexe A : Commandes de vérification et de qualité

```bash
# Suite complète (lint + tests + sécurité + audit + permissions)
make check

# Tests seuls avec couverture
make test

# Analyse de sécurité statique (Bandit)
make security

# Audit des dépendances (pip-audit)
make audit

# Scan des secrets suivis par Git
make secrets

# Vérification des permissions du .env
make permissions

# Tests ciblés (plus rapide pendant le développement)
.venv/bin/python -m pytest tests/test_api_permissions.py -v
.venv/bin/python -m pytest tests/test_sync_service.py tests/test_purge_service.py -v
.venv/bin/python -m pytest tests/test_security.py tests/test_documents_security.py -v
```

## Annexe B : Checklist de mise en production

Avant déploiement en environnement réel, vérifier les points suivants :

**Configuration** :
- [ ] `SECRET_KEY` est une valeur aléatoire de 32 octets minimum (non la valeur par défaut de développement)
- [ ] `ENCRYPTION_KEY` est une clé Fernet valide, distincte de `SECRET_KEY`
- [ ] `FLASK_ENV=production` est bien défini
- [ ] Le fichier `.env` a les permissions `chmod 600`
- [ ] `STORAGE_DIR` pointe vers un volume persistant (pas un répertoire temporaire)

**Infrastructure** :
- [ ] Un reverse proxy HTTPS (nginx, Traefik) est configuré devant Gunicorn
- [ ] Les variables `FORCE_HTTPS=true`, `TRUST_PROXY=true`, `SESSION_COOKIE_SECURE=true` sont activées
- [ ] Une sauvegarde planifiée du fichier SQLite, du dossier `STORAGE_DIR` et du fichier `.env` est en place

**Tests d'acceptation** :
- [ ] Connexion réussie à un serveur SFTP réel de l'établissement
- [ ] Connexion réussie à un partage SMB réel de l'établissement
- [ ] Synchronisation d'un lot de documents réels sans erreur
- [ ] Consultation et téléchargement de documents depuis l'interface web
- [ ] Vérification des journaux après chaque opération
- [ ] Test de révocation d'un token API

**Sécurité** :
- [ ] `make check` passe sans erreur sur la version finale
- [ ] Headers HTTP vérifiés avec un outil comme securityheaders.com
- [ ] Aucune clé secrète ne figure dans les variables d'environnement Docker en texte clair dans les logs

<div class="page-break"></div>

# Table des illustrations

Figure 1 : Situation avant et après StageSarcophage — dispersion des sources vs accès centralisé ........................ Introduction

Figure 2 : Architecture applicative de StageSarcophage : couches Flask, services et stockage ................................ Partie II — II.2

Figure 3 : Modèle de données : entités SQLAlchemy et leurs relations ................................................................... Partie II — II.2

Figure 4 : Flux de synchronisation d'un document PDF : de la détection à l'écriture atomique .............................. Partie II — II.3

Figure 5 : Tableau de bord : indicateurs clés et activité récente ............................................................................... Partie II — II.5

