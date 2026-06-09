# Plan imagegen des figures du rapport

Objectif : refaire toutes les figures du rapport avec des visuels raster propres, lisibles sur une page A4, suffisamment techniques pour appuyer le texte sans transformer chaque figure en tableau illisible.

Principes communs à toutes les images :
- Format paysage 4:3 ou proche, utilisable à `width=100%` dans le rapport.
- Fond clair, contraste fort, palette technique sobre : bleu nuit, cyan, vert hôpital, ambre, rouge d'alerte, gris clair.
- Pas de logo inventé, pas de photoréalisme décoratif, pas de personnages.
- Peu de texte dans l'image : 6 à 12 libellés courts maximum, police sans-serif grande, aucune phrase longue.
- Aucun micro-détail ni texte sous 24 px en sortie.
- Composition aérée : marges externes, trois à cinq zones principales, traits épais, flèches lisibles.
- Style cohérent sur la série : infographie technique semi-vectorielle, isométrie légère seulement quand elle clarifie l'architecture.

## Prompt maître à préfixer

```text
Use case: infographic-diagram
Asset type: technical figure for a French internship report, printed on A4.
Global style: clean technical infographic, white background, subtle light grid, high contrast, large readable French labels, restrained hospital IT palette (deep navy, cyan, clinical green, amber warning, red critical, light gray). Landscape 4:3 composition. Use thick connector lines and generous spacing. No decorative people, no invented logos, no tiny UI text, no long paragraphs, no watermark.
Readability rule: the figure must remain readable when printed at 16 cm width on A4 paper. Use only short labels and large type.
```

## Figure 1 : Avant / après centralisation

Fichier : `images/schema-avant-apres.png`

Prompt :

```text
Primary request: create a before/after architecture figure for StageSarcophage document centralization.
Composition: split screen with a vertical divider.
Left side title: "Avant". Show three separated source islands: "SFTP bloc", "SMB urgences", "Dossier local". Add scattered PDF icons, warning badges, and no central visibility.
Right side title: "Après". Show the same sources feeding into a central application block labeled "StageSarcophage", then one unified access point labeled "Accès web + API". Add clear badges: "Fraîcheur", "Traçabilité", "Sécurité".
Technical details to show visually: SFTP, SMB/CIFS, local storage, PDF collection, centralized lookup.
Avoid: dense text, fake brand logos, decorative hospital imagery.
```

## Figure 2 : Architecture applicative

Fichier : `images/schema-architecture-generale.png`

Prompt :

```text
Primary request: create a layered application architecture diagram for a Flask monolith named StageSarcophage.
Composition: three horizontal zones from top to bottom.
Top zone "Entrées": "Navigateur", "API REST", "Planificateur".
Middle zone "Application Flask": four large modules: "Routes", "Services", "Modèles", "Utils sécurité".
Bottom zone "Persistance": "SQLite WAL", "STORAGE_DIR", "Journaux".
Left external column: "Sources PDF" with "SFTP", "SMB", "Local". Connect it to Services.
Technical details to include as small labels only: Jinja, SQLAlchemy, APScheduler, Docker.
Visual focus: architecture flow and separation of responsibilities.
Avoid: code blocks, tiny endpoint lists.
```

## Figure 3 : Modèle de données

Fichier : `images/schema-modele-donnees.png`

Prompt :

```text
Primary request: create a readable entity relationship diagram for StageSarcophage.
Composition: central pair of entities "Source" and "Document", with thick relationship line "1 -> n".
Surrounding support entities: "Journal", "BackgroundJob", "User", "Role", "APIToken", "Setting".
Show only the most important attributes as short chips:
Source: protocole, seuils, identifiants chiffrés.
Document: hash, statut, date source, chemin local.
User/Role: permissions.
APIToken: hash, portée.
Visual style: database cards with icons and color-coded groups: métier, sécurité, exploitation.
Avoid: full SQL schema, PK/FK columns, tiny cardinality notation.
```

## Figure 4 : Flux de synchronisation

Fichier : `images/schema-flux-synchronisation.png`

Prompt :

```text
Primary request: create a technical pipeline diagram for synchronizing PDF files from external sources.
Composition: left-to-right flow with seven large steps:
"Connecteur" -> "Inventaire *.pdf" -> "Nom sécurisé" -> "Téléchargement temp" -> "SHA-256" -> "Remplacement si changé" -> "Journal".
Add three branch badges under the hash step: "Nouveau", "Inchangé", "Erreur".
Show a safety gate around "Nom sécurisé" with label "realpath + commonpath".
Use PDF file icons moving through the pipeline.
Visual focus: atomic temporary file write, hash-based deduplication, journalization.
Avoid: long pseudocode, microscopic arrows.
```

## Figure 5 : Tableau de bord

Fichier : `images/ui-dashboard.png`

Prompt :

```text
Primary request: create a high-fidelity but simplified dashboard mockup for StageSarcophage.
Composition: web application screenshot style inside a browser frame.
Header: "StageSarcophage".
Top metric cards: "Documents", "Sources actives", "Critiques", "Dernière sync".
Main left panel: source distribution bar chart.
Main right panel: recent activity list with colored status dots.
Bottom panel: document freshness summary with green, amber, red segments.
Visual style: serious hospital internal tool, dense but readable, Bootstrap-like spacing, no marketing hero.
Avoid: fake real patient data, tiny table rows, decorative illustrations.
```

## Figure 6 : Fraîcheur, purge et corbeille

Fichier : `images/schema-purge-corbeille.png`

Prompt :

```text
Primary request: create a document lifecycle diagram for freshness status and purge.
Composition: circular or horizontal lifecycle with five states:
"Collecté" -> "OK" -> "Avertissement" -> "Critique" -> "Corbeille" -> "Purge finale".
Show thresholds as timeline markers labeled "seuil source" and "rétention".
Add a reversible arrow from "Corbeille" to "Restaurer" before final purge.
Use color coding: green OK, amber warning, red critical, gray trash.
Technical detail: include label "CORBEILLE_RETENTION_JOURS" as a visible configuration tag.
Avoid: emotional wording, trash-can cartoon style.
```

## Figure 7 : Sécurité en couches

Fichier : `images/schema-securite-acces.png`

Prompt :

```text
Primary request: create a defense-in-depth security diagram for StageSarcophage.
Composition: central asset "PDF modes dégradés" protected by concentric layers or stacked shields.
Layers labeled: "Session", "CSRF", "RBAC", "Token hashé", "CSP", "Fernet", "Chemins confinés".
Add two entry paths on the left: "Interface web" and "API Bearer".
Add protected assets on the right: "Identifiants sources", "Stockage PDF", "Journaux".
Visual tone: sober cybersecurity diagram for a hospital IT application.
Avoid: hacker silhouettes, padlock clichés dominating the image, unreadable small text.
```

## Figure 8 : Déploiement

Fichier : `images/schema-deploiement.png`

Prompt :

```text
Primary request: create an operational deployment topology diagram for the application.
Composition: left-to-right infrastructure chain:
"Navigateur" -> "Reverse proxy HTTPS" -> "Gunicorn" -> "Flask app".
Below Flask, show persistent volumes: "SQLite app.db", "STORAGE_DIR", ".env", "logs".
Right side, show external source boxes: "SFTP", "SMB", "Local".
Add Docker boundary around Gunicorn, Flask, volumes and entrypoint.
Small operations badges: "backup", "make check", "rotation Fernet".
Avoid: cloud provider logos, Kubernetes, database servers not used in the project.
```

## Figure 9 : Choix technologiques

Fichier : `images/schema-choix-technologiques.png`

Prompt :

```text
Primary request: create a decision matrix infographic comparing selected technologies with rejected alternatives.
Composition: four decision cards in a 2x2 grid:
"Backend: Flask" vs "Django / FastAPI"
"Base: SQLite WAL" vs "PostgreSQL"
"Jobs: ThreadPoolExecutor" vs "Celery / RQ"
"Secrets: Fernet" vs "AES manuel / env seul"
Each card has three short criteria chips: "simple", "déployable", "adapté volume" or equivalent.
Use checkmarks for selected technologies and neutral gray for alternatives.
Visual tone: engineering tradeoff board, not a marketing slide.
Avoid: dense paragraphs, exaggerated winner/loser styling.
```

## Figure 10 : API REST

Fichier : `images/schema-api-rest.png`

Prompt :

```text
Primary request: create a REST API overview diagram for StageSarcophage.
Composition: central vertical API gateway labeled "/api/v1".
Left side: "Client DSI" with Bearer token.
Right side endpoint groups as large boxes:
"Health", "Stats", "Sources", "Sync jobs", "Documents", "Download".
Show HTTP methods as small colored pills: GET, POST.
Add security ribbon: "Bearer token hashé + permissions".
Mention limitation as a small note: "pas de CRUD sources".
Avoid: listing every route path in tiny text.
```

## Figure 11 : Planning prévisionnel / réalisé

Fichier : `images/schema-gantt-prevu-realise.png`

Prompt :

```text
Primary request: create a readable Gantt-style project planning figure for an eight-week internship.
Composition: horizontal timeline with weeks S1 to S8 at the top.
Rows: "Analyse", "Architecture", "Sources", "Synchronisation", "Interface", "Sécurité/API", "Tests", "Docs".
Each row has two bars: planned in light blue, actual in darker blue.
Show "Sécurité/API" taking more time than planned and pushing compression into week S8.
Show "Tests" and "Docs" concentrated in S8.
Add two small callouts: "Sécurité/API prolongée" and "Tests intégration réduits".
Add a small legend: "Prévu" and "Réalisé".
Use wide bars and large week labels for A4 readability.
Avoid: adding an extra week, extremely wide panoramic canvas, tiny task names, detailed daily schedule.
```

## Figure 12 : Pipeline qualité

Fichier : `images/schema-pipeline-qualite.png`

Prompt :

```text
Primary request: create a quality pipeline diagram for the `make check` command.
Composition: six connected blocks from left to right:
"Ruff", "pytest", "Bandit", "pip-audit", "scan secrets", "permissions .env".
Above the flow, title label "make check".
Below each block, use a simple icon-like cue: lint, tests, security, dependencies, secrets, filesystem.
Add final outcome box "Rapport vérifiable".
Visual style: CI pipeline, clear pass/fail gates, technical and compact.
Avoid: too many logs, terminal screenshots, unreadable command output.
```
