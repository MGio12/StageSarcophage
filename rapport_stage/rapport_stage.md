---
lang: fr-FR
title: "Développement d'une application web de centralisation et de suivi des PDF de modes dégradés"
subtitle: "Rapport de stage - Bachelor Universitaire de Technologie Informatique - Année 2025-2026"
author: "Maxime Giovanelli"
date: "15 avril - 13 juin 2026"
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

Je remercie Julien Degardin, responsable au sein de la DSI du Centre Antoine Lacassagne, pour son encadrement pendant ces huit semaines. Ses retours techniques et sa formulation claire du besoin métier ont aidé à garder un périmètre compatible avec les contraintes réelles d'exploitation hospitalière.

Je remercie également Olivier Pantz, tuteur pédagogique à l'IUT Nice Côte d'Azur, pour le suivi du stage et les conseils méthodologiques, ainsi que l'ensemble de l'équipe de la DSI pour son accueil et pour les échanges qui m'ont permis de comprendre le fonctionnement informatique de l'établissement.

<div class="page-break"></div>

# Résumé

Ce rapport présente un stage de huit semaines réalisé au Centre Antoine Lacassagne, centre de lutte contre le cancer situé à Nice, au sein de la Direction des Systèmes d'Information (DSI).

Le besoin portait sur la continuité d'activité. Quand un outil métier devient indisponible, les équipes soignantes et administratives doivent retrouver rapidement des documents PDF de modes dégradés : formulaires, procédures et fiches réflexes. Avant le projet, ces documents étaient répartis sur plusieurs stockages hétérogènes (SFTP, SMB/CIFS, dossier local). Or, aucun outil ne donnait à la DSI une vue centralisée ni un contrôle simple de leur fraîcheur.

La problématique du stage était donc la suivante : comment centraliser et fiabiliser l'accès à ces documents critiques, tout en répondant à des exigences parfois contradictoires — fraîcheur documentaire garantie, traçabilité complète des accès, et sécurité adaptée à un environnement HDS ?

L'application livrée, nommée StageSarcophage, utilise Flask, Jinja, SQLAlchemy, SQLite, APScheduler et Docker. Elle collecte les PDF depuis trois types de sources, calcule un état de fraîcheur par document, fournit une interface web avec viewer PDF, gère une purge progressive avec corbeille et expose une API REST. Les opérations sont journalisées ; les contrôles de sécurité couvrent les sessions, les tokens Bearer, le CSRF, la CSP, le chiffrement Fernet des identifiants et le confinement des chemins — autant d'exigences directement issues du contexte HDS.

Le livrable est une base applicative documentée, testée et conteneurisable. Il reste à la valider sur l'infrastructure réelle de la DSI.

# Summary

This report presents an eight-week internship at Centre Antoine Lacassagne, a cancer treatment center in Nice, within its IT department (DSI).

The project came from a business continuity need. When standard tools become unavailable, medical and administrative staff need quick access to degraded-mode PDF documents: forms, procedures and reference sheets. Before the project, these documents were spread across heterogeneous servers (SFTP, SMB/CIFS, local storage), with no central tool to track freshness or availability.

The main question was: how can access to these critical documents be centralized and secured while keeping freshness tracking, auditability and access control compatible with HDS requirements?

The delivered application, StageSarcophage, uses Flask, Jinja, SQLAlchemy, SQLite, APScheduler and Docker. It collects PDFs from three source types, computes a freshness status for each document, provides a web interface with an integrated PDF viewer, manages progressive purge with a trash bin, exposes a REST API and logs operations. Security controls cover sessions, Bearer tokens, CSRF, CSP, Fernet credential encryption and path confinement.

The result is a documented, tested and containerizable application base. The DSI still has to validate it on real infrastructure before production use.

<div class="page-break"></div>

# Sommaire

1. Remerciements
2. Résumé et Summary
3. Glossaire
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
   - III.3 Accompagnement du CSU lors des interventions
8. Difficultés rencontrées
9. Conclusion
10. Bibliographie et sitographie
11. Annexes
12. Table des illustrations

# Glossaire

**CSRF** : Cross-Site Request Forgery : attaque forçant un navigateur authentifié à envoyer une requête non voulue. Les formulaires modifiants sont protégés par un jeton CSRF.

**CSP** : Content Security Policy : en-tête HTTP limitant les ressources chargées par le navigateur, ce qui réduit la surface d'attaque XSS.

**Fernet** : schéma de chiffrement symétrique authentifié (AES-128-CBC + HMAC-SHA256), utilisé pour chiffrer les identifiants des sources en base.

**HDS** : Hébergeur de Données de Santé : certification française encadrant l'hébergement de données médicales.

**Mode dégradé** : procédure ou document utilisé lorsque le fonctionnement normal d'un outil métier n'est plus disponible.

**RBAC** : Role-Based Access Control : les droits sont attribués à des rôles, eux-mêmes assignés aux utilisateurs.

**SFTP** : SSH File Transfer Protocol : transfert de fichiers sécurisé via SSH, utilisé pour les sources Linux.

**SMB/CIFS** : Server Message Block / Common Internet File System : protocole d'accès aux partages de fichiers Windows.

**SQLite WAL** : Write-Ahead Logging : mode d'écriture de SQLite améliorant les performances en lecture concurrente.

<div class="page-break"></div>

# Introduction

Le Centre Antoine Lacassagne utilise plusieurs outils informatiques pour les soins, le suivi des patients et les procédures administratives. Lorsqu'un de ces outils devient indisponible (panne réseau, mise à jour bloquante, incident serveur), le personnel doit continuer à travailler. Les **modes dégradés** répondent à ce besoin avec des procédures et formulaires papier ou PDF qui remplacent temporairement les outils numériques habituels.

Ces documents existent dans l'établissement, mais leur gestion reste dispersée : un serveur SFTP Linux pour le bloc opératoire, un partage SMB Windows pour le service des urgences, un dossier local pour d'autres services. Cette fragmentation créait un vide opérationnel : il n'existait pas de vue centralisée pour répondre à des questions simples comme « ce document est-il encore à jour ? », « existe-t-il toujours sur le serveur source ? » ou « quand a-t-il été modifié pour la dernière fois ? ».

La mission confiée par la DSI était de concevoir et développer une application web interne pour combler ce vide. Concrètement, cela impliquait de résoudre quatre contraintes simultanées : fédérer des protocoles hétérogènes dans un point d'accès unique ; calculer un état de fraîcheur documentaire sans saturer le réseau ; protéger les identifiants de connexion aux serveurs tout en gardant une administration simple ; et déployer l'application sur une infrastructure hospitalière sans ajouter de composants lourds.

J'ai conçu et développé StageSarcophage pour répondre à ce besoin. L'application collecte les PDF depuis les sources déclarées, conserve une copie locale avec déduplication, calcule un état de fraîcheur par document, fournit une interface web de consultation et journalise les opérations. La figure 1 montre le passage d'un accès dispersé sur plusieurs serveurs à un accès centralisé, sécurisé et traçable.

![Figure 1 : Situation avant et après StageSarcophage : dispersion des sources et accès centralisé.](images/schema-avant-apres.png){width=100%}

Le rapport suit trois parties, construites sur un plan problème/solution. La première analyse la situation : l'établissement, la DSI, les contraintes HDS et les besoins qui ont délimité le périmètre. La deuxième retrace la conception et la réalisation dans l'ordre où les problèmes se sont réellement posés : pour chaque sous-système, j'expose la difficulté rencontrée, les solutions envisagées et celle que j'ai retenue — y compris mes premières versions imparfaites, car ce sont souvent elles qui m'ont le plus appris. La troisième dresse le bilan : ce qui est livré, ce qui reste à valider, et les priorités pour une reprise par la DSI.

<div class="page-break"></div>

# Partie I : Analyse de la situation

## I.1 Présentation du Centre Antoine Lacassagne

Le Centre Antoine Lacassagne (CAL) est un Centre de Lutte Contre le Cancer (CLCC) situé au 33 avenue de Valombrose à Nice. Fondé en 1947, il fait partie des vingt établissements du réseau Unicancer entièrement dédiés à la prise en charge du cancer, et accueille chaque année plus de 15 000 patients pour environ 800 personnes employées. Il couvre les trois missions des CLCC : soins (oncologie médicale, radiothérapie, chirurgie), recherche clinique et formation.

Ce qui rend le CAL particulier pour un projet informatique, c'est la nature des données qu'il traite. Son système d'information porte des données de santé au sens de la réglementation française — dossiers patients, prescriptions, imagerie médicale — ce qui impose des exigences fortes de sécurité, de traçabilité et de confidentialité. La DSI gère l'infrastructure réseau, les serveurs, les applications métier et la sécurité des systèmes dans ce cadre contraint.

## I.2 Service DSI et contraintes HDS

La DSI du CAL intervient sur un périmètre large : gestion des accès, exploitation des serveurs, déploiement d'applications internes, sauvegardes et continuité de service. Le contexte hospitalier impose plusieurs contraintes spécifiques.

**Exigences HDS** : la certification HDS (Hébergeur de Données de Santé) encadre en France l'hébergement de données médicales. Elle repose sur trois piliers : documenter les mesures de sécurité, tracer tous les accès, et formaliser les procédures de sauvegarde et de gestion des incidents. Pour StageSarcophage, ces exigences se sont traduites concrètement par le chiffrement des identifiants, les journaux d'opérations, le contrôle des accès par rôle et la gestion séparée des secrets.

**Continuité d'activité** : un établissement de santé doit continuer à fonctionner lors d'une panne informatique. Des procédures de mode dégradé existent pour les situations critiques : panne du dossier patient, indisponibilité du système de prescription, coupure réseau. Ces procédures reposent sur des documents PDF qui doivent rester accessibles même lorsque l'outil principal ne l'est plus.

**Contraintes de déploiement** : la DSI ne souhaitait pas maintenir une infrastructure complexe pour une application interne de portée limitée. Le cahier des charges précisait donc : SQLite acceptable, pas de serveur de base de données externe requis, déploiement par conteneur Docker, configuration par variables d'environnement.

## I.3 Analyse des besoins

L'analyse des besoins a structuré la demande en trois niveaux, du plus critique au plus opérationnel.

**Besoins fonctionnels primaires** — le cœur du système, sans lequel rien d'autre n'a de sens :

- Déclarer des sources (SFTP, SMB, local), tester leur connexion, configurer leur fréquence de synchronisation.
- Synchroniser automatiquement les PDF depuis ces sources, en conservant une copie locale.
- Suivre la fraîcheur de chaque document (date de dernière modification source, statut ok/avertissement/critique).
- Permettre la consultation, la recherche, le filtrage et le téléchargement des documents depuis une interface web.
- Conserver un journal de toutes les opérations (synchronisations, purges, connexions, erreurs).

**Besoins fonctionnels secondaires** — la qualité d'exploitation, qui conditionne l'adoption par la DSI :

- Gestion des utilisateurs, des rôles et des permissions (RBAC).
- API REST pour permettre des intégrations futures (monitoring, outils DSI).
- Purge automatique des documents dépassant leur durée de rétention, avec passage par une corbeille.
- Notifications par email en cas d'erreur ou de documents critiques.

**Contraintes non fonctionnelles** — les conditions sine qua non d'un déploiement hospitalier :

- Sécurité : chiffrement des identifiants, protection des sessions, headers HTTP, contrôle des chemins.
- Déployabilité : Docker + Gunicorn, configuration par variables d'environnement, SQLite.
- Maintenabilité : code structuré en couches, tests automatisés, documentation d'exploitation.

## I.4 Cahier des charges et matrice des exigences

Le document `cahier_des_charges.md` fourni par la DSI liste les exigences détaillées : gestion des sources et connecteurs, synchronisation et déduplication, suivi de fraîcheur, consultation web, sécurité, API et exploitation. L'état de livraison, exigence par exigence, est dressé dans le bilan (partie III.1).

Le projet a été planifié sur huit semaines : analyse (S1), architecture et modèle de données (S2), connecteurs et sources (S3), synchronisation et fraîcheur (S4), interface web (S5), sécurité et API (S6-S7), tests et documentation (S8).

Le planning réalisé a suivi le planning prévisionnel dans ses grandes lignes. La partie sécurité et API a pris plus de temps que prévu : plus on développe de fonctionnalités manipulant des fichiers et des identifiants, plus les points à sécuriser s'accumulent. Ce décalage a été absorbé en concentrant les tests et la documentation sur la dernière semaine.

<div class="page-break"></div>

# Partie II : Conception et réalisation

## II.1 Choix technologiques et argumentation

Les choix techniques partent du cahier des charges et des contraintes d'exploitation. Chaque composant a été choisi après comparaison avec des alternatives plus lourdes ou moins adaptées au besoin.

### Backend : Flask

Le besoin était une application web interne à maintenir par une DSI, pas un service haute disponibilité. Flask correspondait : léger, rendu HTML côté serveur via Jinja natif, déploiement derrière Gunicorn simple. Django aurait apporté plus — administration, ORM, structure imposée — mais précisément ce surplus était un coût sans contrepartie pour ce périmètre. FastAPI aurait été pertinent pour une API principalement asynchrone ; moins pour une application dont l'interface web reste le cas d'usage principal.

### Base de données : SQLite via SQLAlchemy

SQLite en mode WAL est embarqué dans Python, ne nécessite aucune installation et se sauvegarde par simple copie de fichier — trois avantages concrets pour un déploiement hospitalier sans DBA dédié. Ses limites d'écritures concurrentes ne sont pas un problème ici : le volume attendu reste faible (quelques synchronisations planifiées, des consultations web, des opérations d'administration). Et si ce volume devait croître, SQLAlchemy laisse ouverte la migration vers PostgreSQL sans réécrire la couche de données.

### File de jobs : ThreadPoolExecutor

Un `ThreadPoolExecutor` interne suffit pour quelques dizaines de synchronisations par jour — sans dépendance supplémentaire. Celery ou RQ offriraient une meilleure persistance des jobs et une reprise propre après redémarrage, mais au prix de Redis et d'un worker séparé à opérer. Ce coût n'était pas justifié pour ce périmètre. La contrepartie est assumée et documentée : si le conteneur s'arrête pendant une synchronisation, le job est perdu et doit être relancé manuellement.

### Chiffrement des identifiants : Fernet

Fernet fournit un chiffrement symétrique authentifié avec HMAC-SHA256 intégré. La bibliothèque est maintenue, documentée et évite d'implémenter soi-même AES-CBC, ce qui réduirait la marge d'erreur sur des points sensibles comme l'IV ou le MAC. Stocker uniquement les identifiants dans des variables d'environnement n'aurait pas protégé la base si quelqu'un obtenait une copie du fichier SQLite.

## II.2 Architecture applicative

StageSarcophage est un monolithe Flask organisé en couches distinctes. Ce choix n'est pas anodin : au départ, les premières routes mélangeaient logique d'accès réseau, règles de stockage et rendu HTML — ce qui rendait les tests impossibles et les bugs difficiles à isoler. Séparer les couches a été la première décision structurelle du projet.

La figure 2 positionne StageSarcophage entre les sources hétérogènes, les utilisateurs web et les clients API.

![Figure 2 : Architecture applicative de StageSarcophage : couches Flask, services et stockage.](images/schema-architecture-generale.png){width=100%}

Les routes HTTP (`app/routes/`) se limitent à l'authentification, à la lecture des paramètres, à la délégation aux services et au rendu. Les services (`app/services/`) portent la logique métier : synchronisation, purge, jobs de fond, notifications, LDAP, connecteurs. Les modèles SQLAlchemy (`app/models/`) définissent le schéma de données et les invariants. Les utilitaires (`app/utils/`) fournissent les fonctions transverses : sécurité des chemins, chiffrement, sanitisation, décorateurs de permissions.

Le modèle de données place `Source` et `Document` au centre du flux, liés par une relation un-à-plusieurs. Les autres entités (`Journal`, `BackgroundJob`, `User`, `Role`, `APIToken`) couvrent l'exploitation, le suivi des jobs et la sécurité.

### Les jobs planifiés : trois leçons sur la concurrence

Cette architecture a été mise à l'épreuve par les jobs planifiés. APScheduler exécute chaque tâche périodique — synchronisation par source, purge à 2 h, nettoyage de la corbeille à 3 h, rapport de conformité à 8 h — dans un thread séparé du processus Flask. Cette cohabitation entre threads de fond et requêtes web m'a confronté à trois problèmes successifs.

Le premier est apparu dès le premier essai : `RuntimeError: Working outside of application context`. Le même code de service fonctionnait parfaitement appelé depuis une route web, et plantait systématiquement appelé par le scheduler. En lisant la documentation de Flask, j'ai compris que la configuration et la session de base de données sont attachées à un *contexte d'application* que les requêtes web reçoivent automatiquement — mais pas les threads créés par APScheduler. La correction consiste à envelopper le corps de chaque job dans `with app.app_context():` (`app/scheduler/tasks.py`). Une ligne, mais elle m'a obligé à comprendre comment Flask isole réellement ses requêtes, ce que l'usage habituel du framework masque complètement.

Le deuxième problème était un chevauchement. En testant avec une fréquence de synchronisation volontairement courte (une minute) et une source lente, le job suivant démarrait avant la fin du précédent : deux threads synchronisaient la même source en parallèle, avec des écritures concurrentes sur les mêmes lignes en base. APScheduler fournit exactement les garde-fous nécessaires : `max_instances=1` interdit deux exécutions simultanées du même job, et `misfire_grace_time=60` autorise un déclenchement en retard plutôt qu'une exécution de rattrapage en rafale. J'ai aussi ajouté une garde `if _scheduler.running: return` au démarrage, après avoir constaté en développement que le rechargeur automatique de Flask créait deux processus — et donc deux schedulers exécutant chaque synchronisation en double.

Le troisième touchait SQLite. Lors des premiers tests avec une synchronisation planifiée active et l'interface ouverte en parallèle, certaines requêtes échouaient avec `sqlite3.OperationalError: database is locked` : le thread du scheduler écrivait pendant qu'une requête web lisait. Plutôt que de remettre en cause le choix de SQLite (section II.1), j'ai activé le mode WAL à l'ouverture de chaque connexion (`PRAGMA journal_mode=WAL` dans `app/__init__.py`). Dans ce mode, l'écriture se fait dans un journal séparé et ne bloque plus les lectures — ce qui correspond exactement à notre profil d'usage : des écritures occasionnelles (les jobs), des lectures fréquentes (l'interface).

Ces fondations posées — couches séparées, jobs maîtrisés, base fiabilisée —, le cœur fonctionnel restait à construire : la collecte des documents elle-même.

## II.3 Sources et synchronisation

Une source décrit l'origine des PDF : protocole (`sftp`, `smb`, `local`), adresse réseau, chemin distant, identifiants chiffrés, filtres, seuils de fraîcheur et durée de rétention. Dans le code, les identifiants sont manipulés via les propriétés Python `login` et `mot_de_passe` de `Source` ; les colonnes physiques en base stockent les valeurs chiffrées par Fernet.

Le service `app/services/sync_service.py` applique la même logique à tous les protocoles : seul le connecteur (inventaire et téléchargement) change. Cette partie est celle qui a connu le plus d'itérations pendant le stage, et c'est en la racontant dans l'ordre qu'on comprend le mieux sa forme finale.

**Première version : correcte mais inutilisable.** Ma première implémentation était directe : télécharger chaque fichier distant, calculer son hash SHA-256, le comparer à celui stocké en base, et ne remplacer la copie locale que si le contenu avait changé. Fonctionnellement, rien à redire. Mais en testant avec une source d'une centaine de PDF, chaque synchronisation re-téléchargeait l'intégralité des fichiers — y compris ceux inchangés depuis des semaines — car il faut posséder un fichier pour le hacher. La déduplication arrivait trop tard dans la chaîne. Face à l'objectif du cahier des charges (500 PDF en moins de 5 minutes) et à des sources accessibles via le réseau hospitalier, cette approche ne tenait pas.

**Deuxième version : déduplication à deux niveaux.** La solution a été d'exploiter les métadonnées que les protocoles SFTP et SMB fournissent gratuitement à l'inventaire, avant tout téléchargement : la taille et la date de modification. Si les deux correspondent à ce qui est enregistré en base, le fichier est ignoré d'emblée. Le hash SHA-256 ne sert plus qu'en confirmation après téléchargement, pour éviter une écriture inutile quand un fichier a été re-daté sans être modifié (ce qui arrive, par exemple, après une copie de dossier côté serveur). Le coût réseau d'une synchronisation devient ainsi proportionnel à ce qui a *changé*, et non à la taille totale de la source.

**Le bug des deux secondes.** Ce pré-filtre a immédiatement fait apparaître un bug déroutant : certains fichiers — toujours les mêmes — étaient re-téléchargés à chaque synchronisation alors qu'ils n'avaient pas changé. En journalisant les dates comparées, j'ai constaté des écarts d'une seconde entre la date stockée en base et la date annoncée par le serveur. L'explication m'a demandé quelques recherches : plusieurs systèmes de fichiers et serveurs SMB stockent les dates de modification avec une granularité de deux secondes ; la date est arrondie, et l'arrondi peut différer entre ce que le serveur annonce et ce que l'on a enregistré. Ma comparaison stricte échouait donc en permanence pour ces fichiers. La correction tient en une condition : tolérer un écart inférieur à deux secondes.

```python
# sync_service.py — pré-filtre avant téléchargement (simplifié)
if doc and doc.taille_octets == f_distant.taille:
    doc_mtime = _as_utc(doc.date_modification_source)
    if doc_mtime:
        ecart = abs((doc_mtime - f_distant.date_modification).total_seconds())
        if ecart < 2:  # tolérance : granularité des dates SMB/FAT
            return "ignore"  # métadonnées identiques : pas de téléchargement
```

**Les fuseaux horaires.** En branchant le connecteur SFTP, la comparaison ci-dessus a levé une erreur que je ne connaissais pas : `TypeError: can't subtract offset-naive and offset-aware datetimes`. Paramiko renvoie des dates « naïves » (sans information de fuseau horaire), alors que l'application travaille avec des dates UTC « aware » ; Python refuse de soustraire les deux, et c'est une bonne chose — le résultat serait ambigu. J'ai adopté une règle simple pour tout le projet : toutes les dates sont stockées et comparées en UTC, la conversion vers l'heure locale n'intervient qu'à l'affichage. Un petit utilitaire normalise les dates entrantes :

```python
def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
```

**Écriture contrôlée.** Le téléchargement passe par un fichier temporaire créé dans le dossier cible, déplacé vers son nom définitif seulement une fois complet, et supprimé en cas d'exception. Sans cette précaution, une coupure réseau en milieu de transfert laisserait un PDF tronqué qui serait servi tel quel à l'utilisateur — précisément le genre de défaillance silencieuse qu'un outil de continuité d'activité ne peut pas se permettre. Le calcul du hash lui-même lit le fichier par blocs de 64 Ko plutôt qu'en une fois : certains PDF de procédures sont des scans de plusieurs dizaines de mégaoctets, et `sha256(f.read())` aurait chargé chacun intégralement en mémoire.

La figure 3 résume la chaîne complète : inventaire, sécurisation du nom, les deux niveaux de déduplication, écriture contrôlée et journalisation de chaque issue (copié, ignoré, erreur).

![Figure 3 : Flux de synchronisation d'un document PDF : déduplication à deux niveaux et écriture contrôlée.](images/schema-flux-synchronisation.png){width=100%}

**Les noms de fichiers, une entrée comme une autre.** Le point le plus sensible de cette chaîne concerne les noms de fichiers distants. Un nom ne peut pas être utilisé tel quel : un fichier nommé `../secret.pdf` sur un serveur compromis doit être refusé avant tout stockage local. Ma première protection s'appuyait sur `os.path.basename()` pour ne conserver que le nom — jusqu'à ce qu'un test m'apprenne que sous Linux, `basename` ne coupe que sur les `/` : un nom contenant des antislashs Windows (`..\..\fichier.pdf`), tout à fait plausible venant d'un serveur SMB, traversait le filtre intact. La fonction `nom_fichier_sur()` (`app/utils/files.py`) normalise donc d'abord les `\` en `/` avant d'extraire le nom, et le confinement par `realpath` + `commonpath` vérifie en seconde ligne de défense que le chemin final reste bien sous le répertoire de stockage. Cette double vérification s'applique partout où un chemin est manipulé : synchronisation, téléchargement, ZIP, purge et restauration depuis la corbeille.

La synchronisation répond à la question « comment collecter efficacement ». Restait la question symétrique, tout aussi importante pour la DSI : que deviennent les documents qui vieillissent ?

## II.4 Fraîcheur, purge et corbeille

Chaque document porte un statut calculé à partir de son âge et des seuils configurés sur sa source. La progression est intentionnellement graduelle : `ok` (document récent), `avertissement` (à surveiller), `critique` (action requise), puis `purge` (rétention dépassée). Cette dégradation laisse du temps pour réagir avant qu'un document ne disparaisse. Les seuils sont paramétrables par source, ce qui permet d'appliquer des politiques différentes selon la criticité des procédures concernées.

La suppression elle-même n'est jamais immédiate. Quand un document dépasse son seuil de rétention, il est déplacé vers `_corbeille` et son statut passe à `PURGE`. Un nettoyage définitif intervient ensuite après la durée `CORBEILLE_RETENTION_JOURS`. Ce fonctionnement en deux temps limite le risque d'erreur irréversible en cas de mauvais paramétrage. La figure 4 illustre l'ensemble de ce cycle de vie et les seuils de transition.

![Figure 4 : Cycle de vie d'un document PDF : états de fraîcheur, transitions et chronologie de purge.](images/schema-purge-corbeille.png){width=100%}

Ces mécanismes tournent en arrière-plan ; pour l'utilisateur, ils se résument à un badge de couleur sur chaque document. C'est l'interface web qui rend ce travail visible.

## II.5 Interface web et parcours utilisateur

L'interface est rendue côté serveur avec Jinja2 et Bootstrap 5. Ce choix a une raison pratique : un développeur Python de la DSI doit pouvoir maintenir l'interface sans maîtriser un framework JavaScript. Les écrans de gestion interne n'exigent pas de réactivité temps réel. L'interface couvre la connexion, le tableau de bord, la gestion des sources, la synchronisation, la consultation des documents, les journaux et l'administration.

Le tableau de bord affiche les indicateurs utiles à l'exploitation : nombre de documents, sources actives, dernière synchronisation, espace utilisé, activité récente et répartition par source.

L'export ZIP est limité à 100 documents et 500 Mo. Ce plafond évite de générer depuis l'interface une réponse HTTP trop volumineuse, qui pourrait saturer la mémoire du serveur ou la connexion de l'utilisateur.

L'interface couvre l'usage humain. Pour les usages programmatiques — supervision par les outils de la DSI, scripts d'exploitation —, l'application expose une API REST.

## II.6 API REST

L'API v1 est définie dans `app/routes/api.py` et documentée via OpenAPI dans `app/api/openapi.py`. Elle expose un healthcheck public, des statistiques agrégées, la liste et le détail des sources, le déclenchement d'une synchronisation, le statut d'un job de fond, la liste et le détail des documents, ainsi que le téléchargement d'un document.

L'API n'est pas un CRUD complet — et c'est un choix délibéré. La création et la suppression de sources sont des opérations rares, réalisées par des administrateurs qui bénéficient des confirmations visuelles de l'interface web. L'API se concentre sur la consultation et le suivi, les vrais cas d'usage fréquents pour un outil de monitoring externe. Les décorateurs dans `app/utils/decorators.py` et les tests dans `tests/test_api_permissions.py` garantissent que les deux modes d'accès (session web et token Bearer) appliquent les mêmes règles de permissions, sans divergence silencieuse.

Un exemple d'usage typique — déclencher une synchronisation puis suivre son job :

```bash
curl -X POST -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/v1/sources/1/sync
curl -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/v1/jobs/<job-id>
```

## II.7 Sécurité

La sécurité de StageSarcophage repose sur plusieurs contrôles complémentaires. Aucun d'eux ne suffit seul ; l'objectif est de limiter la surface d'attaque sur les accès web, l'API, les fichiers et les exports. Les contrôles peuvent être regroupés par type de menace.

**Contre l'usurpation d'identité** : Flask-Login gère les sessions côté serveur, avec mots de passe hachés en bcrypt (coût 12) et décorateurs `@require_permission` sur les routes sensibles. Les tokens Bearer sont stockés hachés en base, révocables immédiatement, et peuvent porter des permissions restreintes. Un utilisateur peut avoir le rôle "Opérateur" sans avoir la permission de supprimer des sources.

**Contre les attaques par le navigateur** : Flask-WTF pose des jetons CSRF sur tous les formulaires modifiants, ce qui empêche un attaquant de déclencher une action en s'appuyant sur la session ouverte d'un utilisateur. Les en-têtes HTTP (`X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, CSP avec nonce dynamique sur les scripts) réduisent les vecteurs XSS et clickjacking.

La mise en place de la CSP a d'ailleurs été instructive : en l'activant, l'interface a cessé de fonctionner. Les quelques scripts inline des templates étaient bloqués exactement comme l'aurait été un script injecté par un attaquant — comportement attendu, puisque la CSP ne distingue pas le code légitime du code injecté : elle exige que le code légitime soit identifiable. Chaque réponse génère donc un nonce aléatoire, placé à la fois dans l'en-tête CSP et dans les balises `<script>` des templates ; un script dépourvu du nonce de la requête en cours est refusé par le navigateur.

**Contre les attaques par le système de fichiers** : les identifiants des sources sont chiffrés avec Fernet avant stockage — la clé (`ENCRYPTION_KEY`) reste séparée de la clé de session et protégée avec `chmod 600`. Le confinement des chemins dans `app/utils/files.py` utilise `os.path.realpath` et `os.path.commonpath` pour garantir que tout chemin demandé reste sous le répertoire autorisé, y compris face aux liens symboliques ou aux chemins absolus injectés.

**Contre les injections de formules** : les exports CSV/XLSX neutralisent les valeurs commençant par `=`, `+`, `-` ou `@`. Les notifications et rapports HTML échappent systématiquement les contenus insérés.

## II.8 Tests et qualité

La stratégie de test a privilégié la rapidité et la reproductibilité. Les tests utilisent SQLite en mémoire et un stockage temporaire ; le mode `JOBS_RUN_INLINE=true` exécute les jobs de fond de façon synchrone. Ce mode est né d'un problème concret : mes premiers tests de synchronisation échouaient par intermittence, selon que le thread du job avait terminé ou non au moment de l'assertion. Plutôt que d'ajouter des attentes arbitraires (`sleep`) qui ralentissent la suite sans vraiment la fiabiliser, j'ai introduit ce mode qui exécute les jobs en ligne pendant les tests : les assertions deviennent déterministes. Résultat : une suite qui tourne en quelques secondes en CI, sur les vingt fichiers couvrant les modèles, la synchronisation, la purge, les sources, les permissions API et web, la sécurité (traversée de chemin, injections), LDAP, SFTP, SMB, les exports, les notifications et les templates.

La contrepartie est connue : ces tests ne prouvent pas la compatibilité avec les comportements réels de serveurs SFTP, SMB, LDAP ou SMTP. Une recette sur infrastructure réelle reste indispensable avant tout déploiement.

La commande `make check` orchestre l'ensemble : Ruff (linter Python), pytest avec couverture, Bandit (analyse statique de sécurité), `pip-audit` (vulnérabilités des dépendances), un scan de secrets suivis par Git et une vérification des permissions du fichier `.env`.

## II.9 Déploiement et exploitation

Le dépôt contient un `Dockerfile`, un `docker-compose.yml`, un `entrypoint.sh` et les commandes Flask nécessaires à l'initialisation de la base.

Variables minimales requises en production :

```bash
SECRET_KEY=<valeur aléatoire 32 octets>
ENCRYPTION_KEY=<clé Fernet générée>
STORAGE_DIR=/chemin/vers/stockage
FLASK_ENV=production
```

Le déploiement cible passe par Docker (le lancement local hors conteneur est décrit dans le README) :

```bash
docker compose build && docker compose up -d
docker compose exec web flask init-db
docker compose exec web flask create-admin --username admin --password <mot_de_passe>
```

Les jobs de fond s'exécutent dans un `ThreadPoolExecutor` interne. Un redémarrage du processus pendant une synchronisation peut laisser un job inachevé ; dans ce cas, un déclenchement manuel est nécessaire. C'est une limite connue et documentée — l'exploitant doit en être informé lors de la prise en main.

<div class="page-break"></div>

# Partie III : Bilan et perspectives

## III.1 Résultats obtenus

StageSarcophage couvre le périmètre principal du cahier des charges : une application web interne, conteneurisable, qui collecte des PDF depuis des sources SFTP, SMB et locales, calcule leur fraîcheur, permet leur consultation et trace les opérations.

Sur les exigences du cahier des charges, l'essentiel est livré et validé par les tests : gestion des sources, synchronisation avec déduplication SHA-256, consultation (interface web, viewer PDF, export ZIP), sécurité (CSRF, CSP, Fernet, RBAC, confinement de chemins) et API REST. Deux points restent partiels : la purge est fonctionnelle mais certains paramètres avancés n'ont pas été démontrés en recette ; l'API ne couvre pas le CRUD des sources. Trois points restent à valider sur infrastructure réelle : LDAP, SMTP, et le benchmark de performance à 500 PDF. Le projet est documenté pour permettre une reprise par la DSI sans dépendre de ma présence.

## III.2 Perspectives et évolutions

**Priorité haute** : valider les connecteurs sur infrastructure réelle (SFTP, SMB, LDAP, SMTP) et mesurer le benchmark 500 PDF en moins de 5 minutes avec un jeu de fichiers représentatif. C'est le prérequis à toute mise en service.

**Priorité moyenne** : ajouter le CRUD des sources dans l'API REST (avec une politique d'autorisation à préciser) ; mettre en place une sauvegarde automatique de la base SQLite, du stockage PDF et du fichier `.env`.

**Priorité basse** : envisager une migration PostgreSQL si les accès concurrents l'exigent ; faire réaliser un audit de sécurité externe une fois le périmètre de production figé.

## III.3 Accompagnement du CSU lors des interventions

En plus du développement de StageSarcophage, j'ai accompagné des membres de la Cellule de Support aux Utilisateurs (CSU) lors d'interventions dans plusieurs services — sur site (bloc opératoire, urgences, unités d'hospitalisation, services administratifs) quand une présence physique était nécessaire, à distance pour les incidents simples. Cette seconde mission m'a donné une vision directe du terrain que l'application devait servir.

Le parc informatique hospitalier diffère d'un environnement d'entreprise classique : postes partagés entre plusieurs utilisateurs, politiques de sécurité strictes, accès aux applications métier (dossier patient informatisé, outils de prescription) contrôlés par profil et par service. J'ai participé à des dépannages de postes, des gestions de droits d'accès, des incidents d'impression et des rétablissements de connectivité réseau. La tension y est permanente : la sécurité doit rester stricte, mais l'usage doit rester simple pour des personnels dont l'informatique n'est pas le métier — un blocage banal sur un poste ou une imprimante peut désorganiser un service entier.

### Continuité de service en milieu hospitalier

Le contexte hospitalier se distingue surtout par la continuité de service : une panne informatique dans un service de soins peut perturber directement la prise en charge des patients, et les interventions du CSU prennent souvent un caractère urgent. Ces accompagnements ont rendu le besoin de StageSarcophage très concret. Les modes dégradés ne sont pas une formalité documentaire : lors d'une intervention, j'ai vu une unité revenir aux formulaires papier à cause d'une indisponibilité temporaire des outils de prescription. C'est exactement le scénario que l'application sécurise, en garantissant un accès fiable, centralisé et à jour aux documents de modes dégradés.

### Relation avec les utilisateurs hospitaliers

Le personnel hospitalier (médecins, cadres de santé, infirmiers, secrétaires médicales, agents administratifs) a des niveaux d'aisance informatique très variables : il faut adapter le vocabulaire, reformuler concrètement et tenir compte de la pression du service. La qualité perçue d'une intervention tient autant à l'explication donnée qu'à la résolution technique. Cette observation a directement influencé la conception de StageSarcophage : une application utilisée par du personnel non informaticien, souvent en contexte de panne, doit afficher des messages d'état compréhensibles et éviter les parcours inutiles.

<div class="page-break"></div>

# Difficultés rencontrées

Les difficultés techniques ponctuelles — séparation des routes et des services, contexte applicatif des threads, chevauchement des jobs, verrouillage SQLite, granularité des dates SMB, fuseaux horaires, traversée de chemin — ont été racontées dans la partie II, au plus près des choix qu'elles ont provoqués. Cette section revient sur les difficultés transversales : celles qui ne se corrigent pas par un commit, mais qui ont structuré le déroulement du stage.

**Mener deux missions de front.** Le stage ne se limitait pas au développement : les accompagnements du CSU occupaient une partie du temps, par nature imprévisible puisque dictée par les incidents. Il a fallu apprendre à protéger des plages de développement continues — une fonctionnalité comme la synchronisation supporte mal le morcellement — tout en restant disponible pour les interventions. Concrètement, cela a imposé des arbitrages : certaines fonctionnalités avancées ont été documentées plutôt que finalisées, et les tests d'intégration ont été concentrés sur la dernière semaine.

**Changer de posture sur la sécurité.** La difficulté la plus formatrice n'a pas été d'apprendre tel ou tel mécanisme (CSRF, CSP, Fernet), mais de changer de question : ne plus me demander « est-ce que ça marche ? » mais « comment cela peut-il être détourné ? ». Une application qui collecte des fichiers manipule en permanence des entrées non fiables — noms de fichiers distants, contenus exportés vers un tableur, chemins de téléchargement, tokens d'API. Chaque fonctionnalité ajoutée rouvrait la question pour un périmètre nouveau. C'est ce qui explique le débordement de la phase sécurité sur le planning prévisionnel : la charge de sécurisation croît avec le nombre de fonctionnalités, et je l'avais sous-estimée en début de stage.

**Garantir les mêmes règles sur deux chemins d'accès.** Un cas particulier de cette vigilance mérite d'être isolé : l'interface web utilise des sessions avec CSRF, l'API des tokens Bearer sans CSRF, et ces deux chemins doivent appliquer exactement les mêmes permissions métier. Le risque insidieux était de durcir l'interface tout en laissant l'API contourner silencieusement certains contrôles. J'ai centralisé les vérifications dans des décorateurs réutilisables (`app/utils/decorators.py`) appliqués aux deux chemins, et verrouillé cette propriété par des tests dédiés (`tests/test_api_permissions.py`) — si quelqu'un fait diverger les deux chemins à l'avenir, un test échouera.

**Tester sans l'infrastructure cible.** SFTP, SMB, LDAP et SMTP ne pouvaient pas être testés contre les vrais serveurs de l'établissement depuis mon environnement de développement. J'ai simulé les bibliothèques sous-jacentes (Paramiko, `smbprotocol`) avec `unittest.mock`, ce qui permet de tester de façon reproductible les succès, les erreurs réseau, les timeouts et les entrées dangereuses. La limite est connue et assumée : ces tests valident ma logique, pas la compatibilité réelle avec les serveurs de la DSI — c'est pourquoi la recette sur infrastructure réelle figure en tête des perspectives.

**Estimer son propre travail.** Enfin, ce stage m'a confronté à la difficulté d'estimer. Le planning prévisionnel s'est avéré juste dans ses grandes lignes, mais systématiquement optimiste sur les finitions : un connecteur « qui marche » et un connecteur testé, sécurisé et journalisé ne représentent pas le même volume de travail. J'en retiens une règle pratique pour la suite : le dernier quart d'une fonctionnalité coûte aussi cher que les trois premiers.

<div class="page-break"></div>

# Conclusion

StageSarcophage centralise ce qui était dispersé : les PDF de modes dégradés, auparavant éparpillés sur des serveurs hétérogènes, sont maintenant collectés, dédupliqués et accessibles depuis un point d'accès unique. Trois attributs non négociables en contexte HDS : sécurisé (Fernet, CSRF, confinement des chemins), traçable (journaux de toutes les opérations), fiable (copies locales disponibles même si la source est inaccessible).

Les choix techniques — Flask, SQLite, APScheduler, Fernet, ThreadPoolExecutor, Docker — ont été guidés par le cahier des charges : simplicité de déploiement, environnement hospitalier, volume attendu limité. L'objectif n'était pas de multiplier les composants, mais de livrer une base maintenable. Chaque choix a été comparé aux alternatives disponibles et ses limites sont documentées.

Le travail de sécurité a été plus long que prévu, et c'est compréhensible : une application de collecte de fichiers manipule rapidement des entrées non fiables — noms de fichiers distants, exports tableur, formulaires web, tokens API, chemins de téléchargement. Le confinement des chemins, la sanitisation des exports, le CSRF, la CSP et le double modèle d'accès session/token ont donc pris une place importante dans le projet.

Sur le plan personnel, ce stage m'a davantage appris par ses problèmes que par ce qui a fonctionné du premier coup : un `TypeError` sur des fuseaux horaires, une base verrouillée par un thread ou un job exécuté en double obligent à comprendre ce que les frameworks font réellement sous la surface, là où l'usage ordinaire permet de l'ignorer. C'est cette compréhension — plus que la liste des fonctionnalités livrées — qui me semble constituer l'acquis principal de ces huit semaines.

La prochaine étape est une recette par la DSI sur l'infrastructure réelle du Centre Antoine Lacassagne. Elle permettra de valider les connecteurs, de mesurer les performances sur des fichiers représentatifs et d'ajuster les paramètres de rétention avant une mise en service opérationnelle — ce que ce stage n'a pas pu faire, mais a préparé.

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
- ANSSI, *Guide des bonnes pratiques de l'informatique*, https://www.ssi.gouv.fr/guide/bonnes-pratiques-de-linformatique/
- ANS (Agence du Numérique en Santé), *Certification HDS*, https://esante.gouv.fr/labels-certifications/hds

<div class="page-break"></div>

# Annexes

## Annexe A : Commandes de vérification et de qualité

```bash
# Suite complète (lint + tests + sécurité + audit + permissions)
make check

# Tests ciblés (plus rapide pendant le développement)
.venv/bin/python -m pytest tests/test_api_permissions.py tests/test_security.py -v
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

Figure 1 : Situation avant et après StageSarcophage : dispersion des sources vs accès centralisé ........................ Introduction

Figure 2 : Architecture applicative de StageSarcophage : couches Flask, services et stockage ............................. Partie II : II.2

Figure 3 : Flux de synchronisation d'un document PDF : déduplication à deux niveaux et écriture contrôlée ...... Partie II : II.3

Figure 4 : Cycle de vie d'un document PDF : états de fraîcheur, transitions et chronologie de purge .................... Partie II : II.4
