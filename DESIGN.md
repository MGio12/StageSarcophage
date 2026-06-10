# Système de design — « Console clinique »

Source de vérité visuelle de **Modes Dégradés** (outil CLCC de surveillance de la
fraîcheur documentaire). Posture : *un instrument de surveillance, pas une app SaaS.*
Dense, précis, lisible ; statuts qui ressortent comme sur un tableau de bord
d'équipement médical. Une seule couleur d'accent, des filets plutôt que des ombres,
toute donnée alignée en chasse fixe.

Implémentation : re-skin par-dessus **Bootstrap 5.3** (grille + JS conservés), tout le
visuel piloté par `app/static/css/style.css`. Aucune dépendance réseau.

## Principes
1. **La donnée en chasse fixe.** Dates, âges, tailles, noms de fichiers, IP, compteurs → IBM Plex Mono. C'est la signature « console » : les colonnes s'alignent au pixel.
2. **Une couleur d'accent.** Pétrole `#0B6E6E` pour les actions primaires, les liens, l'item de nav actif. Le reste est encre / neutre.
3. **Statut = sémantique, pas décor.** Vert / ambre / rouge réservés aux états OK / Attention / Critique. Jamais décoratifs.
4. **Filets, pas ombres.** Bordures 1px `--line`. Les ombres sont réservées aux overlays (modale, menu).
5. **Coins nets** (`--radius: 4px`) et densité maîtrisée.

## Couleurs (tokens `:root`)
| Token | Hex | Usage |
|---|---|---|
| `--ink` | `#0F1B2D` | texte principal, sidebar |
| `--ink-soft` | `#38475A` | texte secondaire |
| `--muted` | `#6B7A8B` | labels, méta |
| `--surface` | `#FFFFFF` | cartes, contenu |
| `--paper` | `#EEF2F5` | fond d'application |
| `--line` | `#D6DEE6` | filets |
| `--petrol` / `--petrol-ink` | `#0B6E6E` / `#0A5F5F` | accent / accent foncé (hover, AA) |
| `--ok` | `#1F7A56` | statut à jour |
| `--attention` | `#B26A00` | statut avertissement (> 30 j) |
| `--critique` | `#B3261E` | statut critique (> 90 j) |
| `--focus` | `#0EA5C4` | anneau de focus |

Les couleurs sémantiques Bootstrap sont remappées (`--bs-primary` → pétrole,
`--bs-success` → ok, `--bs-danger` → critique, `--bs-warning` → attention, etc.),
donc `btn-*`, `badge`, `bg-*`, `text-*`, `alert-*` héritent du système.

## Typographie
- **IBM Plex Sans** 400/500/600 — interface, titres. (`--sans`)
- **IBM Plex Mono** 400/500 — toute donnée tabulaire. (`--mono`, mappée sur `--bs-font-monospace`)
- Auto-hébergées (`app/static/fonts/`, woff2 latin + latin-ext, licence SIL OFL), `font-display: swap`.
- En-têtes de section/colonne : majuscules, `letter-spacing ~.08em`, `--muted`.

## Espacement & rayons
- Échelle : 4 / 8 / 12 / 16 / 24 / 32 px.
- `--radius: 4px` (composants), 6px (modale, login, brand), `999px` (pills).
- Tables : padding `.6rem .85rem`, `tabular-nums` sur les cellules.

## Composants clés
- **App shell** : sidebar encre fixe (`--ink`) + topbar surface. Item de nav actif = fond pétrole translucide + barre d'accent 2px à gauche. Mobile : sidebar en tiroir off-canvas + backdrop (toggle clavier/Échap).
- **Cluster d'instruments** (dashboard) : tuiles blanches à filet, barre d'accent 2px en haut (couleur de statut), gros numéral Plex Mono, label majuscule, pastille de statut.
- **Statut** : `.status` = pastille (`.status-dot`) + label Plex Mono coloré. Badges pleins (`.badge-ok/-avertissement/-critique/-purge`) en réserve.
- **Boutons** : primaire pétrol plein ; `outline-secondary` neutre (filet) ; `outline-danger` rouge discret. Coins nets.
- **Lignes de table par statut** : `tr.statut-avertissement` / `.statut-critique` = teinte légère + barre d'accent gauche `inset`.
- **Alertes (flash)** : fond teinté + barre d'accent gauche 3px selon la catégorie.
- **Login** : carte console centrée, barre d'accent pétrole en haut, glyphe, type Plex.

## Accessibilité
- Focus visible : `outline 3px var(--focus)` partout ; anneau pétrole sur les champs.
- Contraste visé AA ; texte blanc forcé sur tous les badges de couleur pleine.
- `prefers-reduced-motion` respecté (transitions coupées).
- Skip-link, `aria-current` sur la nav, `aria-expanded` sur le toggle mobile.

## Assets & sécurité
- Bootstrap CSS/JS + Bootstrap Icons vendorisés (`app/static/vendor/`), polices en local → **zéro requête externe** pour l'app, fonctionne hors-ligne (cohérent « modes dégradés »).
- Le CSP autorise encore `cdn.jsdelivr.net` **uniquement** pour Swagger UI (`api/docs.html`). Vendoriser Swagger permettrait de le retirer entièrement.

## Fichiers
- `app/static/css/style.css` — design system complet (tokens + override composants + shell).
- `app/templates/base.html` — app shell (sidebar/topbar), assets locaux, JS sidebar mobile.
- `app/templates/main/dashboard.html`, `auth/login.html` — pages vitrines.
- `app/static/fonts/`, `app/static/vendor/` — polices et Bootstrap locaux.
