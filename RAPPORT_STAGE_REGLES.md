# Règles pour le rapport de stage StageSarcophage

Ce fichier fixe les consignes à suivre pour rédiger le rapport de stage. Il sert de source de règles pour un futur skill, mais aucun skill n'est créé maintenant.

Le rapport final doit être un rapport technique dense. Chaque affirmation doit pouvoir être reliée à une source du dépôt, un fichier, une commande, un test, un choix d'architecture, une contrainte du cahier des charges ou une limite constatée. Aucune phrase IA, aucune formule creuse, aucune fonctionnalité inventée.

## Sources de vérité

Ordre de priorité:

1. `cahier_des_charges.md`: besoin officiel fourni par la DSI du CLCC. Il prime sur le reste pour le contexte, le périmètre attendu et les exigences.
2. Documentation actuelle du dépôt, code et tests: vérité sur ce qui est réellement livré. Les fichiers à vérifier en priorité sont `README.md`, `docs/README.md`, `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`, `docs/SECURITY.md`, `docs/OPERATIONS.md`, `docs/TESTING.md`, `docs/IMPLEMENTATION_STATUS.md`, `app/`, `tests/`, `Makefile` et `docker-compose.yml`.
3. `MethodologieRapportUnivMontpellier.pdf`: référence académique Montpellier pour la structure attendue du rapport et des annexes.
4. `RS-Barbero_Lucas (2).pdf`: modèle local pour la logique de page de garde seulement. Ne pas recopier son contenu, son nombre de pages, ses logos, son entreprise ni son ton.
5. Brouillon ODT local: piste de rédaction seulement. Il ne doit jamais contredire le dépôt ni être traité comme preuve si le code, les tests ou les docs ne confirment pas son contenu.

Aucun exemple de bon rapport de stage versionné dans Git n'a été trouvé dans ce dépôt. Le rapport ne doit donc pas inventer une source modèle interne.

## Contraintes de rendu IUT

Le rapport doit viser environ 25 pages pour le corps principal, et ne doit pas dépasser 25 pages hors annexes. Éviter les pages à moitié vides. Les compléments trop longs doivent aller en annexe plutôt que gonfler artificiellement le corps du rapport.

Le rendu numérique doit inclure le scan de la première page signée et tamponnée par l'entreprise. Il doit être remis au plus tard à la date de fin des stages:

- par mail à l'enseignant référent IUT;
- par mail au responsable des stages, M. Erol Acundeger;
- par mail au tuteur en entreprise;
- par mail au président du jury;
- dans la boîte de dépôt Moodle, section "Documents".

Le jour de la soutenance, une version papier doit être remise à l'enseignant référent. Cette version sert notamment à la signature obligatoire et au dépôt possible des meilleurs rapports à la bibliothèque.

Un rendu après la date limite entraîne une pénalité de 2 points sur la note du rapport.

Le résumé du rapport doit exister en français et en anglais. Le résumé anglais, ou `summary`, doit être intitulé `Summary`. Chaque résumé doit faire 15 à 20 lignes. Il décrit le contexte, le projet, la méthode et les principaux résultats. Il ne doit pas parler de vécu personnel, d'apprentissage général ou de ressenti de stage.

## Page de garde

Utiliser `RS-Barbero_Lucas (2).pdf` comme modèle de composition de la première page. La logique à reprendre est:

- logos académiques en haut, à gauche et à droite;
- bloc établissement centré;
- intitulé administratif du rapport;
- titre du projet bien visible au centre;
- nom de l'étudiant;
- logo de l'entreprise au milieu bas;
- coordonnées de l'entreprise et noms des tuteurs en bas;
- emplacement pour signature et tampon si disponible;
- pied de page avec étudiant, stage, entreprise et numéro de page.

Adapter entièrement le contenu à ce stage. Ne jamais garder les anciens noms, l'ancienne entreprise, l'ancien diplôme, l'ancienne année ou les anciens logos.

Contenu attendu pour cette page:

- étudiant: Maxime Giovanelli;
- formation: BUT2 Informatique;
- année universitaire: 2025-2026;
- période de stage: 15 avril au 13 juin;
- établissement académique: Université Côte d'Azur, IUT Nice Côte d'Azur, Département informatique;
- adresse IUT: 41 boulevard Napoléon III, 06206 Nice Cedex 3;
- entreprise: Centre Antoine Lacassagne;
- adresse entreprise: 33 avenue de Valombrose, 06100 Nice;
- maître de stage: Julien Degardin;
- tuteur école: Olivier Pantz.

Titre recommandé pour la page de garde:

```text
Développement d'une application web de centralisation
et de suivi des PDF de modes dégradés
```

Intitulé administratif recommandé:

```text
Rapport de stage pour l'obtention du Bachelor Universitaire de Technologie Informatique
Année universitaire 2025-2026
```

Logos à utiliser:

- logo Université Côte d'Azur;
- logo IUT Nice Côte d'Azur;
- logo Centre Antoine Lacassagne.

Chercher les logos sur les sites officiels avant génération ou intégration. Sources web vérifiées comme points de départ:

- IUT Nice Côte d'Azur: `https://iut.univ-cotedazur.fr/`;
- BUT Informatique Université Côte d'Azur: `https://butinfo.univ-cotedazur.fr/`;
- Centre Antoine Lacassagne: `https://www.centreantoinelacassagne.org/`;
- fiche Unicancer du Centre Antoine Lacassagne: `https://www.unicancer.fr/fr/clcc/centre-antoine-lacassagne/`.

Si un logo officiel téléchargeable n'est pas disponible proprement, générer une image sobre avec imagegen ou recréer un visuel neutre à partir du nom de l'organisation, sans fabriquer de faux tampon officiel.

La page de garde doit rester sobre. Pas de grande illustration décorative. Pas de fond chargé. Pas de promesse marketing. Le modèle Barbero fait 41 pages au total; ne pas reprendre cette longueur. Le rapport StageSarcophage reste limité à 25 pages maximum hors annexes.

## Interdiction d'inventer des fonctionnalités

Ne jamais présenter comme livré ce que le dépôt actuel ne confirme pas.

Fonctionnalités explicitement interdites sans preuve dans le repo:

- FTP;
- WebDAV;
- S3;
- OCR;
- PWA;
- versioning documentaire;
- toute intégration externe non visible dans `requirements*.txt`, `app/`, `docs/` ou `tests/`.

Une fonctionnalité peut être mentionnée seulement si elle est rattachée à une preuve précise. Exemple de preuve acceptable: fichier de service, route, modèle SQLAlchemy, test pytest, documentation projet, commande `make check`, configuration Docker ou exigence du cahier des charges clairement marquée comme exigence et non comme livraison.

Si une exigence existe dans `cahier_des_charges.md` mais n'est pas livrée, l'écrire comme écart, arbitrage, limite ou perspective. Ne pas la décrire comme un résultat.

## Difficultés et narration technique

Le rapport peut raconter les difficultés rencontrées de manière humaine, mais il ne doit pas fabriquer de faux faits. Une difficulté acceptable doit venir d'au moins un indice réel: code complexe, test ajouté, règle de sécurité, contrainte du cahier des charges, correction visible, documentation d'exploitation ou limite constatée.

Quand une difficulté sert à rendre le cheminement compréhensible sans preuve directe d'un incident précis, la formuler comme un problème technique général du projet. Exemple acceptable: `La gestion des chemins a demandé une attention particulière, car le même fichier pouvait être manipulé lors du téléchargement, du ZIP et de la purge.` Exemple interdit: `Une faille critique a été découverte en production`, sauf preuve explicite.

Les obstacles à privilégier sont ceux qui expliquent un choix réel du dépôt: SQLite en mémoire dans les tests, mocks SFTP/SMB/LDAP, permissions web/API, CSRF contre token Bearer, rotation Fernet, path traversal, neutralisation CSV/XLSX, jobs de fond et erreurs publiques génériques.

## Structure Montpellier à respecter

Le rapport doit suivre la logique académique de la méthodologie Montpellier:

- couverture;
- remerciements;
- résumé en français;
- abstract en anglais;
- sommaire;
- table des figures;
- glossaire;
- introduction;
- présentation de l'entreprise ou du contexte d'accueil;
- cahier des charges et analyse du besoin;
- rapport technique;
- manuel d'installation et d'utilisation;
- bilan, perspectives et rapport d'activité;
- conclusion;
- bibliographie et sitographie;
- annexes;
- quatrième de couverture.

Le sommaire doit rester limité à trois niveaux. Les figures doivent être numérotées, titrées et légendées. Le glossaire doit être alphabétique et contenir des renvois vers les premières sections où les termes sont utilisés.

## Contenu attendu par partie

### Résumés français et anglais

Les résumés servent au classement et à l'archivage du rapport. Ils doivent être rédigés comme des notices techniques courtes, pas comme un bilan personnel.

Chaque résumé doit contenir:

- le contexte du stage;
- le projet confié;
- la méthode de travail;
- les principaux choix techniques;
- les résultats obtenus;
- les perspectives directes si elles sont nécessaires pour comprendre l'état final.

Ne pas écrire dans les résumés: "ce stage m'a permis de", "j'ai découvert", "j'ai appris" ou une phrase équivalente. Le résumé doit parler du travail, pas de l'étudiant.

### Introduction

L'introduction doit poser le contexte, la problématique et l'annonce de plan.

Elle doit partir du besoin réel: disposer de PDF de modes dégradés accessibles, suivis et consultables en cas d'indisponibilité des outils métier habituels. Elle doit distinguer clairement:

- le contexte CLCC et DSI;
- le problème opérationnel;
- les objectifs du stage;
- la place du stagiaire dans l'organisation;
- le périmètre livré;
- les limites connues.

L'introduction présente le contenu du rapport. Elle annonce les parties sans formule interchangeable. Elle doit faire comprendre à un lecteur extérieur pourquoi le projet existe, ce qui a été demandé et comment le rapport va expliquer le travail.

### Présentation entreprise et contexte

La présentation de l'entreprise doit rester utile au stage. Ne pas remplir avec un historique général, une communication institutionnelle ou des informations non nécessaires à la compréhension du projet.

Les éléments pertinents sont:

- le rôle de la DSI;
- les contraintes de continuité d'activité;
- la sensibilité des documents de santé;
- le besoin de contrôles, journaux, permissions et sécurité.

### Cahier des charges et analyse

Cette partie doit partir de `cahier_des_charges.md`. Elle doit séparer:

- exigences fonctionnelles;
- exigences non fonctionnelles;
- contraintes de sécurité;
- contraintes de déploiement;
- arbitrages faits pendant le stage;
- écarts entre le besoin initial et l'état livré.

Une exigence non livrée ne doit pas être masquée. Elle doit être classée comme non implémentée, partiellement implémentée, reportée ou hors périmètre, avec justification si le repo permet de la justifier.

Cette partie doit aussi présenter les projets confiés et le planning prévisionnel. Utiliser le cahier des charges demandé au début du stage comme base. Ajouter un diagramme de Gantt ou un schéma équivalent pour montrer l'organisation prévue, puis réutiliser ce planning dans le bilan pour comparer prévu et réalisé.

### Outils, existant et choix techniques

Avant la description technique détaillée, présenter les logiciels, bibliothèques, protocoles et outils utilisés. Même lorsqu'un choix a été imposé par l'entreprise ou par le cahier des charges, expliquer pourquoi il convient au contexte du projet.

Cette partie doit montrer une recherche sur l'existant:

- solutions ou produits concurrents envisagés;
- contraintes qui les rendent adaptés ou non au besoin;
- raison du choix final;
- limites acceptées.

Ne pas inventer de comparatif. Si le dépôt ne contient pas cette recherche, l'écrire comme une section à compléter à partir de sources externes identifiées. Les concurrents et alternatives doivent être réels et cités.

### Rapport technique

Le rapport technique est le cœur du document. Il doit être précis, dense et vérifiable.

Le rapport doit être très centré sur la technique tout en restant compréhensible. Le lecteur doit pouvoir suivre le raisonnement sans connaître le code à l'avance. Couper les paragraphes de remplissage. Garder ce qui explique un besoin, une contrainte, un choix, une difficulté, un test ou une limite.

Points minimums à traiter:

- architecture Flask monolithe côté serveur;
- rendu Jinja et interface Bootstrap;
- API REST v1 et tokens Bearer;
- modèle de données SQLAlchemy et SQLite;
- sources SFTP, SMB/CIFS et locales si confirmées par code et tests;
- synchronisation, hash SHA-256 et copie locale;
- jobs de fond, statuts et exécution testable;
- purge, corbeille et contraintes de stockage;
- authentification locale, LDAP optionnel, rôles et permissions;
- chiffrement Fernet des identifiants de sources;
- protections chemins, exports CSV/XLSX/ZIP et noms de fichiers;
- CSP, headers de sécurité et contraintes HTTPS;
- tests automatisés et gate qualité.

Chaque sous-partie technique doit citer les fichiers ou commandes qui la fondent. Exemple: `app/services/sync_service.py`, `app/models/source.py`, `tests/test_sync_service.py`, `docs/SECURITY.md`, `make check`.

Le lecteur cible est une personne capable de poursuivre le projet. Le texte doit expliquer la logique de la démarche avant d'entrer dans les détails. Les longues séquences de code doivent rester en annexe. Dans le corps du rapport, préférer des extraits courts, des schémas, des tableaux et des explications reliées à une décision technique.

### Manuel d'installation et d'utilisation

Cette partie doit être pratique et reproductible. Elle peut reprendre les commandes du `README.md` et de `docs/OPERATIONS.md`, sans les enjoliver.

Inclure seulement les procédures testables dans le dépôt:

- création de l'environnement;
- installation des dépendances;
- configuration `.env`;
- initialisation de la base;
- création d'un administrateur;
- lancement Flask;
- lancement Docker si documenté;
- exécution des tests;
- parcours utilisateur principal: connexion, création source, test connexion, synchronisation, consultation document, téléchargement, journaux, administration.

### Bilan, perspectives et rapport d'activité

Le bilan doit montrer les étapes du projet, l'état d'achèvement des tâches et les écarts avec le planning prévisionnel. Réutiliser le diagramme de Gantt ou un tableau de suivi pour montrer ce qui a été réalisé, déplacé, abandonné ou reporté.

Si une tâche n'a pas été accomplie, dire pourquoi. Une difficulté doit être décrite concrètement: problème rencontré, cause probable, piste testée, choix retenu, conséquence sur le projet. Le but est de montrer les efforts techniques fournis pour dépasser les obstacles, pas de produire un journal personnel.

Les perspectives sont une partie importante du rapport. Elles doivent proposer des améliorations ou suites possibles en expliquant comment une personne qui reprend le projet pourrait avancer. Elles doivent rester séparées de ce qui est livré. FTP, WebDAV, S3, OCR, PWA ou versioning documentaire ne peuvent être cités ici que comme pistes non livrées.

Éviter `je` et `on` dans tout le rapport, y compris dans cette partie. Si la première personne devient indispensable pour expliquer une décision personnelle, elle doit rester rare, concrète et limitée au bilan. Elle est interdite dans les résumés.

### Conclusion

La conclusion doit revenir sur le besoin initial, l'état livré, les limites et les suites possibles. Elle ne doit pas promettre une application aboutie, fiable ou facile à utiliser sans preuve.

Les perspectives doivent être séparées des livraisons. Si FTP, WebDAV, S3, OCR, PWA ou versioning documentaire sont cités comme idées futures, les marquer explicitement comme non livrés.

La conclusion porte sur le contenu technique et les perspectives, comme si elle s'adressait à une personne qui prendrait le relais. Si elle mentionne le stagiaire, cette partie ne doit pas dépasser 10% de la conclusion.

## Règles de style

Style attendu:

- français direct, humain et précis;
- phrases courtes quand l'information est simple;
- termes techniques conservés quand ils sont exacts;
- orthographe et grammaire relues plusieurs fois;
- pas de langage familier;
- pas de `je`, pas de `on`, sauf exception rare et justifiée dans le bilan;
- règle courte: pas de je, pas de on;
- pas de ton marketing;
- pas de blabla;
- pas de résumé creux;
- pas de promesse sans preuve.

Faire relire le rapport par une tierce personne si possible. Les fautes d'orthographe, de grammaire ou d'accord affaiblissent directement la crédibilité du travail technique.

Formules interdites sans preuve concrète:

- "ce stage m'a permis de";
- "solution robuste";
- "application intuitive";
- "enjeu majeur";
- "expérience enrichissante";
- "solution innovante";
- "outil puissant";
- "en quelques clics";
- "simple et efficace";
- "répond parfaitement aux besoins";
- toute tournure de type "dans un monde où".

Si une phrase pourrait être collée dans n'importe quel rapport de stage informatique, elle doit être supprimée ou remplacée par une observation spécifique à StageSarcophage.

## Règles imagegen pour les figures

Privilégier les schémas et figures pour étayer les explications techniques. Tous les schémas et diagrammes du rapport doivent être générés avec imagegen et ajoutés comme images. Chaque image doit avoir:

- un prompt conservé dans les notes de rédaction;
- un nom de fichier stable, par exemple `schema-architecture.png`;
- une légende claire;
- un numéro de figure;
- une explication dans le texte;
- une source logique, c'est-à-dire les fichiers ou docs qui justifient ce que le schéma montre.

Schémas minimums à produire:

- architecture générale;
- modèle de données;
- flux de synchronisation;
- sécurité et contrôle d'accès;
- jobs de fond;
- déploiement;
- planning prévisionnel et état d'achèvement, sous forme de diagramme de Gantt ou équivalent.

Un schéma ne doit pas ajouter de composant absent du repo. Si une file de messages, un serveur externe, un stockage cloud, une PWA ou un module OCR n'existe pas dans le code, il ne doit pas apparaître dans les images.

## Bibliographie, sitographie et annexes

La bibliographie et la sitographie doivent distinguer:

- sources internes du dépôt;
- cahier des charges;
- documentation Montpellier;
- documentation technique externe réellement utilisée;
- bibliothèques ou frameworks mentionnés dans le projet.

Les annexes doivent contenir uniquement ce qui aide à vérifier ou comprendre:

- extraits de configuration anonymisés;
- schéma de base de données si utile;
- commandes de test;
- listings de programmes ou extraits longs de code;
- aides techniques permettant de reprendre le projet;
- captures d'écran sélectionnées;
- glossaire et tableaux de correspondance si trop longs pour le corps du rapport.

Le nombre de pages des annexes n'est pas limité. Elles ne remplacent pas l'explication dans le corps du rapport: elles servent de preuve, de détail ou de support technique.

## Règles d'action pour l'agent rédacteur

Pour générer ou réviser le rapport, l'agent doit agir comme un rédacteur technique au service d'un lecteur qui pourrait poursuivre le projet.

Règles obligatoires:

- utiliser ce fichier comme source de consignes avant de rédiger;
- utiliser `humanizer` pour supprimer les signes d'écriture IA;
- utiliser un contrôle anti-slop pour repérer les phrases génériques;
- rattacher chaque affirmation technique à une source réelle;
- refuser d'inventer une fonctionnalité, une difficulté, un concurrent, une décision ou un résultat;
- distinguer ce qui est livré, ce qui était demandé, ce qui reste à faire et ce qui relève des perspectives;
- expliquer les obstacles techniques avec des faits: symptôme, cause, essai, correction, test ou limite.

## Contrôle avant rédaction finale

Avant de considérer une section terminée:

1. Vérifier que chaque affirmation importante a une source.
2. Vérifier que les fonctionnalités décrites existent dans le dépôt ou sont marquées comme exigences non livrées.
3. Supprimer les phrases génériques.
4. Vérifier que les figures ont prompt, légende, nom stable et explication.
5. Vérifier que la structure reste compatible avec Montpellier.
6. Vérifier que le rapport respecte environ 25 pages hors annexes.
7. Vérifier que les résumés français et anglais font chacun 15 à 20 lignes.
8. Vérifier que le rendu numérique prévoit le scan de la première page signée et tamponnée.
9. Vérifier que la version papier est prévue pour la soutenance.
10. Vérifier que la page de garde suit la logique de `RS-Barbero_Lucas (2).pdf` sans recopier son contenu.
11. Vérifier que les logos prévus correspondent à l'Université Côte d'Azur, l'IUT Nice Côte d'Azur et au Centre Antoine Lacassagne.
12. Vérifier que le titre, les dates, la formation, l'entreprise et les tuteurs sont ceux de Maxime Giovanelli.
13. Relire contre la règle: rapport technique dense, aucune phrase IA, sources de vérité explicites, interdiction d'inventer des fonctionnalités.

Commandes utiles à citer ou lancer selon le besoin:

```bash
git diff --check
make check
.venv/bin/python -m pytest -q
```
