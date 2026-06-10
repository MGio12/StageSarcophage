# Plan imagegen des figures du rapport

Objectif : 4 figures **simples** et techniques, lisibles sur A4, qui montrent comment l'application fonctionne et le lien entre les technos. Pas d'infographie dense.

Principes communs (non négociables) :
- SIMPLE avant tout : 3 à 4 zones maximum, 8 à 10 libellés courts maximum par figure.
- Gros blocs, gros traits, grosses polices sans-serif. Aucun texte petit.
- Fond blanc, palette sobre : bleu nuit, cyan, vert, ambre, rouge. Pas d'icônes décoratives, pas de personnages, pas de logos.
- Format paysage proche de 4:3, utilisable à `width=100%`.

## Prompt maître à préfixer

```text
Use case: simple technical diagram
Asset type: figure for a French internship report, printed on A4.
Global style: MINIMAL technical diagram, white background, large French labels in a clean sans-serif font, restrained palette (deep navy, cyan, green, amber, red), thick connector arrows, generous white space. Landscape 4:3.
HARD CONSTRAINTS: this is NOT a dense infographic. Maximum 10 short labels total. Maximum 4 visual zones. No decorative icons, no people, no logos, no small text, no long sentences, no watermark. Every label must stay readable when printed at 16 cm width.
```

## Figure 1 : Avant / après centralisation

Fichier : `images/schema-avant-apres.png`

```text
Primary request: a simple before/after diagram, two panels separated by a vertical divider.
Left panel titled "Avant": three disconnected boxes "SFTP", "SMB", "Local" with a red question mark below them and the label "Fraîcheur inconnue".
Right panel titled "Après": the same three boxes feeding with arrows into ONE central box "StageSarcophage", which points to ONE box "Accès web + API". Green check label "Fraîcheur suivie".
Nothing else. No users, no file icons, no sub-labels.
```

## Figure 2 : Architecture applicative

Fichier : `images/schema-architecture-generale.png`

```text
Primary request: a simple layered architecture diagram of a Flask application.
Three horizontal layers, top to bottom, connected by thick vertical arrows:
1. "Entrées" containing: "Navigateur", "API REST", "APScheduler".
2. "Application Flask" containing: "Routes", "Services", "Modèles SQLAlchemy".
3. "Stockage" containing: "SQLite", "Fichiers PDF".
On the left, one separate column "Sources : SFTP · SMB · Local" with a single arrow pointing to "Services".
Nothing else. No file paths, no module lists, no Docker box, no reverse proxy.
```

## Figure 3 : Flux de synchronisation

Fichier : `images/schema-flux-synchronisation.png`

```text
Primary request: a simple left-to-right pipeline diagram for PDF synchronization with two decision gates.
Main flow, 6 boxes connected by thick arrows:
"Inventaire" -> diamond "Taille + date ?" -> "Téléchargement" -> diamond "SHA-256 ?" -> "Remplacement" -> "Journal".
From each diamond, one short arrow going up labeled "identique : ignoré".
Color the first diamond amber and the second cyan.
Nothing else. No swimlanes, no error branches, no shield icons, no code.
```

## Figure 4 : Cycle de vie d'un document

Fichier : `images/schema-purge-corbeille.png`

```text
Primary request: a simple horizontal timeline of a document lifecycle with five states.
Five boxes left to right connected by arrows:
"OK" (green) -> "Avertissement" (amber) -> "Critique" (red) -> "Corbeille" (gray) -> "Suppression" (dark gray).
One curved arrow going back from "Corbeille" to "OK" labeled "restauration".
Below the timeline, one thin axis labeled "âge du document" with the word "seuils configurables par source".
Nothing else. No transitions details, no parameter names, no legend box.
```
