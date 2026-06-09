"""Generate all 12 report figures programmatically with matplotlib."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY   = "#0b2d4d"
TEAL   = "#0f766e"
LGRAY  = "#f5f7fa"
MGRAY  = "#e2e8f0"
DGRAY  = "#64748b"
WHITE  = "#ffffff"
GREEN  = "#16a34a"
ORANGE = "#f97316"
RED    = "#dc2626"
YELLOW = "#fbbf24"
PURPLE = "#7c3aed"
BLUE   = "#2563eb"


def box(ax, x, y, w, h, text, bg=LGRAY, fg=NAVY, fontsize=9, bold=False,
        radius=0.015, va="center", ha="center", wrap=False, border=None):
    fc = bg
    ec = border if border else bg
    lw = 1.5 if border else 0.5
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0,rounding_size={radius}",
                           facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3)
    ax.add_patch(patch)
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text, fontsize=fontsize, color=fg,
            ha=ha, va=va, weight=weight, zorder=4,
            wrap=wrap, multialignment="center")


def header_box(ax, x, y, w, h, text, bg=NAVY, fg=WHITE, fontsize=10):
    box(ax, x, y, w, h, text, bg=bg, fg=fg, fontsize=fontsize, bold=True, border=bg)


def arrow(ax, x1, y1, x2, y2, color=DGRAY, lw=1.5, style="-|>", label="", fontsize=7.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw), zorder=5)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my, label, fontsize=fontsize, color=color, ha="center", va="center",
                zorder=6, bbox=dict(fc=WHITE, ec="none", pad=1))


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"  ✓ {name}")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 1 — Avant / Après
# ═══════════════════════════════════════════════════════════════════════════════
def fig_avant_apres():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
    fig.patch.set_facecolor(WHITE)

    # Title
    ax.text(8, 8.6, "StageSarcophage — Avant / Après", fontsize=15, color=NAVY,
            ha="center", va="top", weight="bold")

    # Divider
    ax.plot([8, 8], [0.2, 8.2], ls="--", color=MGRAY, lw=2)
    ax.annotate("", xy=(9, 4.5), xytext=(7, 4.5),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=2.5))
    ax.text(8, 4.1, "Migration", fontsize=9, color=TEAL, ha="center", weight="bold")

    # ── LEFT: Avant ──
    ax.text(3.5, 8.1, "Avant — Situation initiale", fontsize=13, color=RED,
            ha="center", weight="bold")

    servers_l = [
        (1.2, 6.5, "Serveur SFTP\nLinux\n(Bloc opératoire)"),
        (3.3, 6.5, "Partage SMB\nWindows\n(Urgences)"),
        (5.4, 6.5, "Stockage\nlocal\n(Autres services)"),
    ]
    for sx, sy, label in servers_l:
        box(ax, sx - 0.7, sy - 0.1, 1.4, 1.2, label, bg="#fee2e2", fg=NAVY,
            fontsize=8, border=RED)

    # Question marks
    questions = ["Ce document\nest-il à jour ?",
                 "Existe-t-il sur\nle serveur ?",
                 "Quand a-t-il\nété modifié ?"]
    for i, (sx, sy, _) in enumerate(servers_l):
        ax.plot([sx, sx], [sy - 0.1, sy - 1.2], ls=":", color=RED, lw=1.5)
        box(ax, sx - 0.75, sy - 2.0, 1.5, 0.85, questions[i], bg="#fff1f2",
            fg=RED, fontsize=7.5, border=RED)

    # Users bottom left
    for i, role in enumerate(["Médecin", "Infirmier", "Admin"]):
        ux = 1.2 + i * 2.1
        ax.text(ux, 2.2, "👤", fontsize=20, ha="center")
        ax.text(ux, 1.85, role, fontsize=8, ha="center", color=DGRAY)
        ax.annotate("", xy=(servers_l[i][0], servers_l[i][1] - 2.0),
                    xytext=(ux, 2.3),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=1,
                                   connectionstyle="arc3,rad=0.2"))

    ax.text(3.5, 0.5, "❌ Aucune vue centralisée — fraîcheur inconnue", fontsize=9,
            color=RED, ha="center", weight="bold",
            bbox=dict(fc="#fee2e2", ec=RED, pad=4, boxstyle="round"))

    # ── RIGHT: Après ──
    ax.text(11.5, 8.1, "Après — StageSarcophage", fontsize=13, color=GREEN,
            ha="center", weight="bold")

    # Central app box
    box(ax, 9.8, 5.2, 3.4, 1.5,
        "StageSarcophage\n🔍 Recherche  📅 Fraîcheur\n🔒 Sécurité   📋 Journaux",
        bg=NAVY, fg=WHITE, fontsize=8.5, border=TEAL)

    # Sources (same, now with green)
    servers_r = [(9.4, 7.0), (11.1, 7.2), (12.8, 7.0)]
    slabels   = ["SFTP Linux\n✅", "SMB Windows\n✅", "Local\n✅"]
    for (sx, sy), label in zip(servers_r, slabels):
        box(ax, sx - 0.65, sy - 0.1, 1.3, 0.85, label, bg="#dcfce7", fg=NAVY,
            fontsize=8, border=GREEN)
        ax.annotate("", xy=(sx, sy - 0.1), xytext=(11.5, 5.2 + 1.5),
                    arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.5))

    # PDF list mockup
    box(ax, 9.8, 3.2, 3.4, 1.8,
        "📄 proc_urgences.pdf     🟢 OK\n"
        "📄 mode_degradé_RX.pdf   🟡 Avert.\n"
        "📄 fiche_chimio.pdf      🔴 Critique\n"
        "📄 protocole_chir.pdf    🟢 OK",
        bg=LGRAY, fg=NAVY, fontsize=7.5, border=TEAL)
    ax.annotate("", xy=(11.5, 3.2 + 1.8), xytext=(11.5, 5.2),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.5))

    # Users bottom right
    for i, role in enumerate(["Médecin", "Infirmier", "Admin"]):
        ux = 9.8 + i * 1.7
        ax.text(ux, 2.2, "👤", fontsize=20, ha="center")
        ax.text(ux, 1.85, role, fontsize=8, ha="center", color=DGRAY)
        ax.annotate("", xy=(11.5, 3.2), xytext=(ux, 2.3),
                    arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1,
                                   connectionstyle="arc3,rad=0.1"))

    ax.text(11.5, 0.5, "✅ Accès centralisé, sécurisé, traçable — fraîcheur garantie",
            fontsize=9, color=GREEN, ha="center", weight="bold",
            bbox=dict(fc="#dcfce7", ec=GREEN, pad=4, boxstyle="round"))

    save(fig, "schema-avant-apres.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 2 — Architecture Flask en couches
# ═══════════════════════════════════════════════════════════════════════════════
def fig_architecture():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16); ax.set_ylim(0, 12); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(8, 11.7, "Architecture applicative de StageSarcophage", fontsize=14,
            color=NAVY, ha="center", weight="bold")

    layers = [
        # (y_bottom, height, label, bg, items_list)
        (10.2, 0.9,  "Clients",         LGRAY,  ["Navigateur web\n(Jinja2/Bootstrap 5)", "Client API\n(curl/scripts)", "Monitoring DSI"]),
        (9.0,  0.85, "Reverse Proxy",   "#dbeafe", ["nginx / Traefik\n(HTTPS termination)"]),
        (6.5,  2.3,  "Flask / Gunicorn","white",  None),   # special — drawn manually
        (5.2,  1.0,  "Modèles SQLAlchemy","white", None),  # special
        (3.8,  1.1,  "Stockage",        LGRAY,  ["SQLite WAL\n(app.db)", "Système de fichiers\n(STORAGE_DIR)\n_pdfs/ _corbeille/ _temp/"]),
        (2.2,  1.3,  "Sources externes",YELLOW+"33", ["Serveurs SFTP\n(Paramiko)", "Partages SMB\n(smbprotocol)", "Stockage local"]),
    ]

    # Layer backgrounds
    bgs = [LGRAY, "#dbeafe", "#e0f2fe", "#ccfbf1", LGRAY, "#fefce8"]
    labels = ["Clients", "Reverse Proxy", "Application Flask / Gunicorn",
              "Modèles SQLAlchemy (app/models/)", "Stockage", "Sources externes (réseau DSI)"]
    ys     = [10.2, 9.0, 6.5, 5.2, 3.8, 2.2]
    hs     = [0.9,  0.85, 2.3, 1.0, 1.1,  1.3]

    for bg, lbl, y, h in zip(bgs, labels, ys, hs):
        p = FancyBboxPatch((0.3, y), 12.0, h, boxstyle="round,pad=0.05",
                           facecolor=bg, edgecolor=MGRAY, linewidth=1, zorder=1)
        ax.add_patch(p)
        ax.text(0.5, y + h - 0.18, lbl, fontsize=8, color=DGRAY, va="top",
                style="italic", zorder=2)

    # Arrows between layers
    for i in range(len(ys) - 1):
        ax.annotate("", xy=(6.3, ys[i+1] + hs[i+1]),
                    xytext=(6.3, ys[i]),
                    arrowprops=dict(arrowstyle="-|>", color=DGRAY, lw=1.5))

    # Layer 1 — Clients
    for i, txt in enumerate(["Navigateur web\n(Jinja2 / Bootstrap 5)",
                              "Client API\n(curl / scripts)", "Monitoring DSI"]):
        box(ax, 1.2 + i*3.5, 10.3, 3.0, 0.7, txt, bg=WHITE, fg=NAVY,
            fontsize=8, border=BLUE)

    # Layer 2 — Reverse proxy
    box(ax, 3.8, 9.1, 4.8, 0.65, "nginx / Traefik   (HTTPS · SSL termination)",
        bg=WHITE, fg=NAVY, fontsize=9, border=BLUE)

    # Layer 3 — Flask (special: 3 columns)
    for col, (title, items, bg_col) in enumerate([
        ("Routes (app/routes/)",
         ["auth.py", "sources.py", "documents.py", "api.py", "admin.py"], "#eff6ff"),
        ("Services (app/services/)",
         ["sync_service.py", "purge_service.py", "job_service.py",
          "notification_service.py", "ldap_service.py"], "#f0fdf4"),
        ("Utils (app/utils/)",
         ["files.py\n(path confinement)", "crypto.py\n(Fernet)",
          "decorators.py\n(RBAC)", "sanitize.py"], "#fdf4ff"),
    ]):
        cx = 0.6 + col * 4.1
        header_box(ax, cx, 8.5, 3.7, 0.35, title, bg=NAVY if col == 0 else TEAL if col == 1 else PURPLE)
        for j, item in enumerate(items):
            box(ax, cx, 6.6 + (4 - j) * 0.37, 3.7, 0.34, item,
                bg=bg_col, fg=NAVY, fontsize=7)

    # Arrow routes→services, services→utils
    ax.annotate("", xy=(4.65, 7.5), xytext=(4.35, 7.5),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.5))
    ax.annotate("", xy=(8.75, 7.5), xytext=(8.45, 7.5),
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.5))

    # Layer 4 — Models
    models = ["Source", "Document", "User", "Role", "Journal", "BackgroundJob", "APIToken"]
    for i, m in enumerate(models):
        c = NAVY if m in ("Source", "Document") else TEAL if m in ("Journal", "BackgroundJob") else DGRAY
        box(ax, 0.5 + i * 1.68, 5.28, 1.55, 0.75, m, bg=c, fg=WHITE, fontsize=8, bold=True)

    # Layer 5 — Storage
    box(ax, 1.0, 3.9, 3.5, 0.85, "SQLite WAL\n(app.db)", bg=WHITE, fg=NAVY,
        fontsize=8.5, border=NAVY)
    box(ax, 5.3, 3.9, 6.5, 0.85,
        "STORAGE_DIR/     _pdfs/    _corbeille/    _temp/",
        bg=WHITE, fg=NAVY, fontsize=8.5, border=NAVY)

    # Layer 6 — Sources
    for i, (lbl, proto) in enumerate([("Serveurs SFTP\n(Paramiko)", "sftp"),
                                       ("Partages SMB\n(smbprotocol)", "smb"),
                                       ("Stockage local", "local")]):
        box(ax, 0.6 + i * 4.0, 2.3, 3.6, 1.0, lbl, bg=WHITE, fg=NAVY,
            fontsize=8.5, border=ORANGE)

    # Right-side: Docker bracket annotation
    for y, h in [(6.5, 2.3), (5.2, 1.0), (3.8, 1.1)]:
        p = FancyBboxPatch((12.5, y), 0.4, h, boxstyle="round,pad=0.02",
                           facecolor="#dbeafe", edgecolor=BLUE, lw=1.5, zorder=1)
        ax.add_patch(p)
    ax.text(13.1, 8.0, "Docker\ncontainer", fontsize=8, color=BLUE, va="top",
            ha="center", style="italic")
    ax.annotate("", xy=(12.9, 5.5), xytext=(14.0, 5.5),
                arrowprops=dict(arrowstyle="<-", color=BLUE, lw=1))
    ax.text(14.1, 9.5, "APScheduler\n(jobs planifiés)", fontsize=7.5, color=TEAL)
    ax.text(14.1, 8.8, "ThreadPoolExecutor\n(jobs de fond)", fontsize=7.5, color=TEAL)

    save(fig, "schema-architecture-generale.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 3 — Modèle de données ER
# ═══════════════════════════════════════════════════════════════════════════════
def fig_modele_donnees():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16); ax.set_ylim(0, 12); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(8, 11.7, "Modèle de données — Entités SQLAlchemy", fontsize=14,
            color=NAVY, ha="center", weight="bold")

    def entity(x, y, title, fields, color=NAVY):
        row_h = 0.32
        w = 3.2
        h_total = 0.42 + len(fields) * row_h
        header_box(ax, x, y + h_total - 0.42, w, 0.42, title, bg=color)
        for i, f in enumerate(fields):
            bg = LGRAY if i % 2 == 0 else WHITE
            box(ax, x, y + h_total - 0.42 - (i + 1) * row_h, w, row_h,
                f, bg=bg, fg=NAVY, fontsize=7, ha="left",
                border=MGRAY)
            ax.text(x + 0.08, y + h_total - 0.42 - (i + 0.5) * row_h, f,
                    fontsize=7, color=NAVY, va="center")
        return (x + w / 2, y + h_total, x + w / 2, y,
                x, y + h_total / 2, x + w, y + h_total / 2)

    # Source
    source_fields = ["🔑 id", "nom", "protocole (sftp|smb|local)", "hote, port",
                     "chemin_distant", "login_chiffré, mdp_chiffré",
                     "filtre_glob", "frequence_sync",
                     "seuil_avert_jours, seuil_critique_jours",
                     "retention_jours", "actif", "derniere_sync"]
    entity(0.5, 3.5, "Source", source_fields, color=NAVY)

    # Document
    doc_fields = ["🔑 id", "source_id 🔗 Source", "nom_fichier", "chemin_local",
                  "hash_sha256", "date_modification_source",
                  "date_collecte", "taille_octets",
                  "statut (ok|avert.|critique|purge)", "en_corbeille"]
    entity(4.3, 3.8, "Document", doc_fields, color=NAVY)

    # Journal
    jrn_fields = ["🔑 id", "horodatage", "niveau (INFO|WARN|ERROR)",
                  "operation", "source_id 🔗 nullable",
                  "document_id 🔗 nullable", "utilisateur", "message"]
    entity(8.2, 5.0, "Journal", jrn_fields, color=TEAL)

    # BackgroundJob
    bj_fields = ["🔑 id (UUID)", "source_id 🔗 Source",
                 "statut (pending|running|done|failed)",
                 "debut, fin", "message_erreur"]
    entity(8.2, 0.8, "BackgroundJob", bj_fields, color=TEAL)

    # User
    user_fields = ["🔑 id", "username", "email",
                   "password_hash (bcrypt)", "actif", "created_at"]
    entity(0.5, 8.8, "User", user_fields, color=DGRAY)

    # Role
    role_fields = ["🔑 id", "nom", "permissions (JSON)"]
    entity(4.3, 9.5, "Role", role_fields, color=DGRAY)

    # APIToken
    token_fields = ["🔑 id", "user_id 🔗 User", "token_hash",
                    "permissions (JSON)", "created_at", "last_used", "revoked"]
    entity(8.2, 8.5, "APIToken", token_fields, color=DGRAY)

    # Relationship arrows (simplified)
    rels = [
        (3.7, 7.4, 4.3, 7.7, "1:N collecte"),
        (3.7, 5.8, 8.2, 8.2, "1:N concerne"),
        (7.5, 7.5, 8.2, 8.0, "1:N"),
        (3.7, 4.0, 8.2, 4.5, "1:N"),
        (3.7, 9.7, 4.3, 10.1, "N:M roles"),
        (7.5, 10.1, 8.2, 10.3, "1:N tokens"),
    ]
    for x1, y1, x2, y2, lbl in rels:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=MGRAY, lw=1.5))
        ax.text((x1+x2)/2, (y1+y2)/2+0.1, lbl, fontsize=6.5, color=DGRAY, ha="center")

    save(fig, "schema-modele-donnees.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 4 — Flux de synchronisation (swimlane)
# ═══════════════════════════════════════════════════════════════════════════════
def fig_flux_sync():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16); ax.set_ylim(0, 12); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(8, 11.7, "Flux de synchronisation d'un document PDF", fontsize=14,
            color=NAVY, ha="center", weight="bold")

    lanes = ["APScheduler\n/ Déclencheur", "sync_service.py",
             "Connecteur\n(SFTP|SMB|Local)", "app/utils/files.py",
             "Système de\nfichiers local", "SQLite"]
    n = len(lanes)
    lane_h = 11.2 / n
    lane_colors = [LGRAY, "#e0f2fe", "#f0fdf4", "#fdf4ff", "#fef9c3", "#e0f2fe"]
    cx = [1.8 + i * 2.4 for i in range(n)]

    for i, (lane, lc) in enumerate(zip(lanes, lane_colors)):
        y = 11.2 - (i + 1) * lane_h
        p = FancyBboxPatch((1.3 + i * 2.4 - 1.1, 0.3), 2.2, 11.0,
                           boxstyle="round,pad=0.05",
                           facecolor=lc, edgecolor=MGRAY, lw=0.8, zorder=1)
        ax.add_patch(p)
        ax.text(cx[i], 11.4, lane, fontsize=8, color=NAVY, ha="center", va="bottom",
                weight="bold", multialignment="center")

    steps = [
        (0, 10.5, "Déclenchement\nplanifié ou manuel"),
        (1, 9.5,  "_get_connector\n(source.protocole)"),
        (2, 8.5,  "Inventaire fichiers\n(list_files + filtre_glob)"),
        (3, 7.4,  "sanitize_filename()\nrealpath + commonpath"),
        (2, 6.4,  "download_to_tempfile()"),
        (4, 5.4,  "Écriture /tmp/sync_XXXX.pdf"),
        (3, 4.4,  "sha256(temp_file)"),
        (5, 3.4,  "SELECT hash WHERE\nnom_fichier = X"),
        (4, 2.4,  "move(temp → STORAGE_DIR)\n[si hash différent]"),
        (5, 1.4,  "INSERT/UPDATE Document\n+ INSERT Journal"),
    ]
    step_colors = [NAVY]*3 + [PURPLE, TEAL, ORANGE, PURPLE, NAVY, ORANGE, NAVY]

    prev_x, prev_y = None, None
    for i, (lane_idx, y, txt) in enumerate(steps):
        x = cx[lane_idx]
        box(ax, x - 1.0, y - 0.35, 2.0, 0.7, txt, bg=step_colors[i], fg=WHITE,
            fontsize=7.5, border=step_colors[i])
        if prev_x is not None:
            ax.annotate("", xy=(x, y + 0.35), xytext=(prev_x, prev_y - 0.35),
                        arrowprops=dict(arrowstyle="-|>", color=DGRAY, lw=1.5))
        prev_x, prev_y = x, y

    # Error branch
    ax.annotate("", xy=(cx[5], 2.4), xytext=(cx[5], 3.4 - 0.35),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.5,
                                connectionstyle="arc3,rad=0.4"))
    box(ax, cx[5] + 0.8, 2.8, 2.5, 0.6,
        "❌ Erreur réseau\n→ Journal ERREUR\n→ Job statut=failed",
        bg="#fee2e2", fg=RED, fontsize=7, border=RED)

    # Skip branch
    ax.text(cx[5] + 1.1, 3.7, "Hash identique\n→ skip (inchangé)",
            fontsize=7, color=DGRAY,
            bbox=dict(fc="#f1f5f9", ec=MGRAY, pad=2, boxstyle="round"))

    save(fig, "schema-flux-synchronisation.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 5 — UI Dashboard mockup
# ═══════════════════════════════════════════════════════════════════════════════
def fig_dashboard():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")

    # Navbar
    nav = FancyBboxPatch((0, 8.3), 16, 0.7, boxstyle="square,pad=0",
                         facecolor=NAVY, edgecolor=NAVY, zorder=3)
    ax.add_patch(nav)
    ax.text(0.4, 8.65, "StageSarcophage", fontsize=12, color=WHITE, weight="bold", va="center")
    for i, (lbl, active) in enumerate([("Tableau de bord", True), ("Sources", False),
                                        ("Documents", False), ("Journaux", False),
                                        ("Administration", False)]):
        x = 3.5 + i * 2.2
        c = WHITE if active else "#93c5fd"
        ax.text(x, 8.65, lbl, fontsize=8.5, color=c, va="center", ha="center",
                weight="bold" if active else "normal")
        if active:
            ax.plot([x - 0.6, x + 0.6], [8.3, 8.3], color=TEAL, lw=3)
    ax.text(15.5, 8.65, "admin ↗", fontsize=8, color="#93c5fd", va="center", ha="right")

    # Metric cards
    cards = [
        (BLUE,   "📄", "247",  "Documents actifs"),
        (GREEN,  "🔗",  "3",   "Sources actives"),
        (ORANGE, "⚠",   "12",  "À vérifier"),
        (RED,    "🔴",  "2",   "Critiques"),
    ]
    for i, (c, icon, val, lbl) in enumerate(cards):
        x = 0.4 + i * 3.9
        p = FancyBboxPatch((x, 6.8), 3.6, 1.3, boxstyle="round,pad=0.1",
                           facecolor=WHITE, edgecolor=c, linewidth=2, zorder=3)
        ax.add_patch(p)
        ax.text(x + 0.5, 7.55, icon, fontsize=22, va="center")
        ax.text(x + 2.8, 7.6, val, fontsize=22, color=c, va="center", ha="right", weight="bold")
        ax.text(x + 1.8, 7.0, lbl, fontsize=8, color=DGRAY, va="center", ha="center")

    # Activity table
    box(ax, 0.3, 3.8, 9.5, 2.8, "", bg=WHITE, border=MGRAY)
    ax.text(0.6, 6.5, "Activité récente", fontsize=10, color=NAVY, weight="bold")
    header_box(ax, 0.3, 6.25, 9.5, 0.38, "Horodatage          Opération       Source          Statut",
               bg=LGRAY, fg=NAVY, fontsize=8)
    rows = [
        ("09/06 09:24", "SYNC_OK",   "SFTP-Bloc",     "✅ 18 docs sync."),
        ("09/06 09:20", "SYNC_WARN", "SMB-Urgences",  "⚠ 3 docs > seuil"),
        ("09/06 08:15", "PURGE",     "Local-Admin",   "🗑 1 doc corbeille"),
        ("09/06 07:00", "SYNC_OK",   "SFTP-Bloc",     "✅ 0 modification"),
        ("08/06 23:00", "SYNC_ERR",  "SMB-Urgences",  "❌ Connexion refusée"),
    ]
    row_colors = [GREEN, ORANGE, ORANGE, GREEN, RED]
    for i, (ts, op, src, st) in enumerate(rows):
        bg = LGRAY if i % 2 == 0 else WHITE
        y = 5.9 - i * 0.42
        box(ax, 0.3, y, 9.5, 0.42, "", bg=bg)
        ax.text(0.55, y + 0.21, ts, fontsize=7.5, color=NAVY, va="center")
        ax.text(2.7, y + 0.21, op, fontsize=7.5, color=row_colors[i], va="center", weight="bold")
        ax.text(4.9, y + 0.21, src, fontsize=7.5, color=NAVY, va="center")
        ax.text(6.8, y + 0.21, st, fontsize=7.5, color=row_colors[i], va="center")

    # Pie chart (simplified as wedges)
    box(ax, 10.2, 3.8, 5.5, 2.8, "", bg=WHITE, border=MGRAY)
    ax.text(10.5, 6.5, "Répartition par source", fontsize=10, color=NAVY, weight="bold")
    pie_data = [142, 87, 18]
    pie_colors = [NAVY, TEAL, ORANGE]
    pie_labels = ["SFTP-Bloc\n(142 docs)", "SMB-Urgences\n(87 docs)", "Local\n(18 docs)"]
    wedge_ax = fig.add_axes([0.66, 0.44, 0.22, 0.28])
    wedge_ax.pie(pie_data, colors=pie_colors, labels=pie_labels,
                 textprops={"fontsize": 7}, startangle=90,
                 wedgeprops={"edgecolor": WHITE, "linewidth": 2})
    wedge_ax.axis("equal")

    # Freshness bars
    box(ax, 0.3, 1.2, 15.2, 2.4, "", bg=WHITE, border=MGRAY)
    ax.text(0.6, 3.5, "État des sources — Dernière synchronisation", fontsize=10,
            color=NAVY, weight="bold")
    for i, (src, age, color, label) in enumerate([
        ("SFTP-Bloc opératoire",    0.95, GREEN,  "Hier 23:00 — ✅ À jour"),
        ("SMB Windows Urgences",    0.45, ORANGE, "Avant-hier — ⚠ Avertissement"),
        ("Stockage local Admin",    0.15, RED,    "Il y a 3 jours — 🔴 Critique"),
    ]):
        y = 2.8 - i * 0.55
        ax.text(0.6, y, src, fontsize=8.5, color=NAVY, va="center")
        ax.text(5.5, y, label, fontsize=8, color=color, va="center")
        bar = FancyBboxPatch((0.5, y - 0.15), 4.5 * age, 0.3,
                             boxstyle="round,pad=0", facecolor=color, edgecolor="none")
        bg_bar = FancyBboxPatch((0.5, y - 0.15), 4.5, 0.3,
                                boxstyle="round,pad=0", facecolor=MGRAY, edgecolor="none")
        ax.add_patch(bg_bar); ax.add_patch(bar)

    save(fig, "ui-dashboard.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 6 — Cycle de vie document / purge
# ═══════════════════════════════════════════════════════════════════════════════
def fig_purge():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(8, 9.7, "Cycle de vie d'un document PDF — Fraîcheur et purge",
            fontsize=14, color=NAVY, ha="center", weight="bold")

    states = [
        (2.0, 7.0, "COLLECTÉ",     TEAL,   "📅"),
        (6.5, 7.5, "OK",           GREEN,  "✅"),
        (6.5, 5.5, "AVERTISSEMENT",ORANGE, "⚠"),
        (6.5, 3.5, "CRITIQUE",     RED,    "🔴"),
        (11.0, 3.5, "PURGE",       "#7f1d1d", "🗑"),
        (13.5, 1.2, "SUPPRIMÉ",    "#1c1917", "✕"),
    ]
    state_patches = {}
    for x, y, name, color, icon in states:
        p = FancyBboxPatch((x - 1.4, y - 0.42), 2.8, 0.84,
                           boxstyle="round,pad=0.1",
                           facecolor=color, edgecolor=color, lw=2, zorder=3)
        ax.add_patch(p)
        ax.text(x - 0.9, y, icon, fontsize=16, va="center", zorder=4)
        ax.text(x + 0.1, y, name, fontsize=9.5, color=WHITE, va="center",
                weight="bold", zorder=4)
        state_patches[name] = (x, y)

    # Initial marker
    ax.annotate("", xy=(2.0 - 1.4, 7.0), xytext=(0.5, 7.0),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))
    ax.text(0.1, 7.3, "Initial", fontsize=8, color=NAVY)

    transitions = [
        ("COLLECTÉ", "OK",           0.0, "hash différent\nou nouveau fichier", TEAL, "arc3,rad=-0.2"),
        ("OK",       "AVERTISSEMENT",0.0, "âge > seuil_avert_jours\n(ex: 30 j)", ORANGE, "arc3,rad=0"),
        ("AVERTISSEMENT","CRITIQUE", 0.0, "âge > seuil_critique_jours\n(ex: 60 j)", RED, "arc3,rad=0"),
        ("CRITIQUE", "PURGE",        0.0, "âge > retention_jours\n(ex: 90 j)\n→ déplacé _corbeille/", "#7f1d1d", "arc3,rad=0"),
        ("PURGE",    "SUPPRIMÉ",     0.0, "après CORBEILLE_\nRETENTION_JOURS", "#1c1917", "arc3,rad=0"),
        ("PURGE",    "OK",           0.0, "restauration manuelle", TEAL, "arc3,rad=-0.5"),
        ("AVERTISSEMENT","OK",       0.0, "resync (hash modifié)", GREEN, "arc3,rad=0.4"),
        ("CRITIQUE", "OK",           0.0, "resync (hash modifié)", GREEN, "arc3,rad=0.5"),
    ]
    for src, dst, _, lbl, color, cs in transitions:
        sx, sy = state_patches[src]
        dx, dy = state_patches[dst]
        ax.annotate("", xy=(dx - 1.3 if dx > sx else dx + 1.3, dy),
                    xytext=(sx + 1.3 if dx > sx else sx - 1.3, sy),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5,
                                   connectionstyle=cs))
        mx = (sx + dx) / 2
        my = (sy + dy) / 2 + 0.3
        ax.text(mx, my, lbl, fontsize=7, color=color, ha="center",
                bbox=dict(fc=WHITE, ec="none", pad=1))

    # Timeline bar
    ax.text(1.5, 2.1, "Chronologie (paramètres configurables par source):", fontsize=9,
            color=NAVY, weight="bold")
    zones = [(0, 30, GREEN, "OK (0–30 j)"),
             (30, 60, ORANGE, "Avertissement (30–60 j)"),
             (60, 90, RED, "Critique (60–90 j)"),
             (90, 120, "#7f1d1d", "Purge / Corbeille (≥ 90 j)")]
    bar_x0, bar_y, bar_w = 1.5, 1.5, 11.0
    for start, end, color, lbl in zones:
        x = bar_x0 + (start / 120) * bar_w
        w = ((end - start) / 120) * bar_w
        p = FancyBboxPatch((x, bar_y - 0.25), w, 0.5,
                           boxstyle="square,pad=0", facecolor=color, edgecolor="none")
        ax.add_patch(p)
        ax.text(x + w / 2, bar_y + 0.45, lbl, fontsize=7.5, color=color,
                ha="center", weight="bold")
    for d in [0, 30, 60, 90, 120]:
        x = bar_x0 + (d / 120) * bar_w
        ax.plot([x, x], [bar_y - 0.45, bar_y + 0.35], color=WHITE, lw=1.5)
        ax.text(x, bar_y - 0.55, f"{d} j", fontsize=7, color=DGRAY, ha="center")

    # Legend box
    box(ax, 12.0, 5.5, 3.5, 3.0,
        "Paramètres Source :\n"
        "• seuil_avert_jours (déf: 30)\n"
        "• seuil_critique_jours (déf: 60)\n"
        "• retention_jours (déf: 90)\n\n"
        "Global :\n"
        "• CORBEILLE_RETENTION_JOURS",
        bg=LGRAY, fg=NAVY, fontsize=8, border=MGRAY, ha="left")

    save(fig, "schema-purge-corbeille.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 7 — Sécurité en couches (oignon)
# ═══════════════════════════════════════════════════════════════════════════════
def fig_securite():
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.set_xlim(-7, 7); ax.set_ylim(-6.5, 6.5); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.set_aspect("equal")
    ax.text(0, 6.3, "Architecture de sécurité — Défense en profondeur",
            fontsize=13, color=NAVY, ha="center", weight="bold")

    layers_data = [
        (5.8, "#e2e8f0", DGRAY,  "Transport & Infrastructure",
         "HTTPS · HSTS · SESSION_COOKIE_SECURE"),
        (4.8, "#dbeafe", BLUE,   "En-têtes HTTP",
         "X-Content-Type-Options · X-Frame-Options\nCSP nonce · Referrer-Policy"),
        (3.8, "#ffedd5", ORANGE, "Authentification & Sessions",
         "Flask-Login · bcrypt coût 12\nTokens Bearer hachés · Révocation"),
        (2.9, "#fef9c3", "#92400e", "Autorisation RBAC",
         "@require_permission · Rôles→Permissions\nCouverture uniforme web + API"),
        (2.0, "#dcfce7", GREEN,  "Protection CSRF",
         "Flask-WTF · Tous formulaires modifiants"),
        (1.2, "#ccfbf1", TEAL,   "Chiffrement Fernet",
         "AES-128-CBC + HMAC-SHA256\nENCRYPTION_KEY ≠ SECRET_KEY"),
        (0.5, NAVY,     WHITE,  "Confinement des chemins",
         "realpath + commonpath\napp/utils/files.py"),
    ]
    for radius, fc, tc, title, details in layers_data:
        circle = plt.Circle((0, 0), radius, facecolor=fc, edgecolor=WHITE, lw=2, zorder=2)
        ax.add_patch(circle)

    # Labels on layers
    label_angles = [90, 40, 340, 300, 250, 200, 160]
    for i, ((radius, fc, tc, title, details), angle) in enumerate(zip(layers_data, label_angles)):
        r_mid = radius - 0.4
        if i == len(layers_data) - 1:
            r_mid = 0
        rad = np.deg2rad(angle)
        x, y = r_mid * np.cos(rad), r_mid * np.sin(rad)
        fontsize = 7.5 if i < 6 else 8
        ax.text(x, y, f"{title}\n{details}", fontsize=fontsize, color=tc,
                ha="center", va="center", weight="bold" if i == 6 else "normal",
                multialignment="center", zorder=5)

    # Attack vector annotations
    attacks = [
        (6.5, 3.5, "XSS", BLUE, (4.8 * np.cos(np.deg2rad(30)), 4.8 * np.sin(np.deg2rad(30)))),
        (6.5, 0.5, "CSRF", ORANGE, (2.0 * np.cos(np.deg2rad(5)), 2.0 * np.sin(np.deg2rad(5)))),
        (6.5, -2.0, "Path traversal", RED, (0.5 * np.cos(np.deg2rad(-20)), 0.5 * np.sin(np.deg2rad(-20)))),
        (-6.5, 2.0, "Credential theft", TEAL, (-1.2 * np.cos(np.deg2rad(170)), 1.2 * np.sin(np.deg2rad(170)))),
        (-6.5, -1.5, "Privilege esc.", "#92400e", (-2.9 * np.cos(np.deg2rad(200)), -2.9 * np.sin(np.deg2rad(200)))),
    ]
    for ax_x, ax_y, lbl, color, target in attacks:
        ax.text(ax_x, ax_y, f"⚡ {lbl}", fontsize=8, color=color, weight="bold",
                ha="center", va="center",
                bbox=dict(fc=WHITE, ec=color, pad=3, boxstyle="round"))
        ax.annotate("", xy=target, xytext=(ax_x * 0.85, ax_y * 0.85),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))

    ax.text(0, -6.3,
            "Sanitisation exports CSV/XLSX : neutralisation des formules (=, +, -, @)",
            fontsize=8, color=DGRAY, ha="center",
            bbox=dict(fc=LGRAY, ec=MGRAY, pad=4, boxstyle="round"))

    save(fig, "schema-securite-acces.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 8 — Déploiement Docker
# ═══════════════════════════════════════════════════════════════════════════════
def fig_deploiement():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(8, 9.7, "Architecture de déploiement — Docker + Gunicorn",
            fontsize=14, color=NAVY, ha="center", weight="bold")

    # Host box
    host = FancyBboxPatch((0.3, 0.8), 15.4, 8.5, boxstyle="round,pad=0.1",
                          facecolor=LGRAY, edgecolor=MGRAY, lw=2, zorder=1)
    ax.add_patch(host)
    ax.text(0.6, 9.2, "Hôte Linux / Serveur DSI", fontsize=9, color=DGRAY, style="italic")

    # Docker compose area
    compose = FancyBboxPatch((0.6, 1.0), 9.5, 8.0, boxstyle="round,pad=0.1",
                             facecolor="#eff6ff", edgecolor=BLUE, lw=1.5, ls="--", zorder=2)
    ax.add_patch(compose)
    ax.text(0.9, 8.9, "docker-compose.yml", fontsize=8.5, color=BLUE, weight="bold")

    # Reverse proxy
    box(ax, 0.9, 7.4, 4.0, 1.0, "nginx / Traefik\n🔒 Port 80/443 HTTPS · SSL termination",
        bg=WHITE, fg=BLUE, fontsize=9, border=BLUE)

    ax.annotate("", xy=(2.9, 7.4), xytext=(2.9, 6.9),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.5))

    # Container web
    container = FancyBboxPatch((0.9, 2.0), 8.7, 4.8, boxstyle="round,pad=0.1",
                               facecolor="#f0f9ff", edgecolor=BLUE, lw=2, zorder=2)
    ax.add_patch(container)
    ax.text(1.2, 6.7, "Container : web   ·   python:3.11-slim", fontsize=8.5,
            color=BLUE, weight="bold")
    box(ax, 1.2, 5.5, 3.8, 0.9, "Gunicorn\n(4 workers · port 5000)",
        bg=WHITE, fg=NAVY, fontsize=8.5, border=NAVY)
    box(ax, 5.4, 5.5, 3.8, 0.9, "Application Flask\n(run.py)",
        bg=WHITE, fg=NAVY, fontsize=8.5, border=NAVY)
    box(ax, 1.2, 4.3, 3.8, 0.9, "APScheduler\n⏰ Tâches planifiées",
        bg=WHITE, fg=TEAL, fontsize=8.5, border=TEAL)
    box(ax, 5.4, 4.3, 3.8, 0.9, "ThreadPoolExecutor\n⚙ Jobs de fond",
        bg=WHITE, fg=TEAL, fontsize=8.5, border=TEAL)
    box(ax, 1.2, 2.3, 8.0, 1.7,
        "entrypoint.sh :\n  flask init-db && flask create-admin\n  gunicorn --workers 4 --bind 0.0.0.0:5000 run:app",
        bg=LGRAY, fg=NAVY, fontsize=8, border=MGRAY)

    # Volume mounts
    vols = [
        (10.5, 7.5, "./app.db → /app/app.db", ORANGE),
        (10.5, 6.5, "./storage → /app/storage", ORANGE),
        (10.5, 5.5, "./.env → /app/.env  (ro)", RED),
    ]
    box(ax, 10.3, 4.8, 5.3, 3.6, "", bg="#fff7ed", border=ORANGE)
    ax.text(10.6, 8.3, "Volumes persistants", fontsize=9, color=ORANGE, weight="bold")
    for x, y, lbl, c in vols:
        ax.text(x, y, f"📎 {lbl}", fontsize=8.5, color=c, va="center")
        ax.annotate("", xy=(9.6, y), xytext=(x - 0.1, y),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.2))

    # Env vars card
    box(ax, 10.3, 1.0, 5.3, 3.5,
        "Variables requises :\n\n"
        "SECRET_KEY=<32 octets aléatoires>\n"
        "ENCRYPTION_KEY=<clé Fernet>\n"
        "STORAGE_DIR=/app/storage\n"
        "FLASK_ENV=production\n"
        "SESSION_COOKIE_SECURE=true",
        bg=LGRAY, fg=NAVY, fontsize=8, border=MGRAY, ha="left")

    # Sources externes
    box(ax, 0.6, 0.1, 9.5, 0.7, "Sources externes (réseau interne DSI) :   SFTP Linux  ·  SMB Windows  ·  Stockage local",
        bg="#fefce8", fg=NAVY, fontsize=8.5, border=YELLOW)
    ax.annotate("", xy=(5.0, 2.0), xytext=(5.0, 0.8),
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.5))

    save(fig, "schema-deploiement.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 9 — Comparaison technologique (2×2 tables)
# ═══════════════════════════════════════════════════════════════════════════════
def fig_choix_techno():
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor(WHITE)
    fig.suptitle("Choix technologiques — Analyse comparative", fontsize=15,
                 color=NAVY, weight="bold", y=0.98)

    tables = [
        {
            "title": "Backend web",
            "chosen": "Flask ✅",
            "cols": ["Critère", "Flask ✅", "Django", "FastAPI"],
            "rows": [
                ["Légèreté / simplicité",    "✅ Excellent", "⚠ Lourd",        "✅ Bon"],
                ["Rendu HTML SSR natif",     "✅ Jinja2",    "✅ Templates",    "❌ Non natif"],
                ["Adéquation périmètre",     "✅ Parfait",   "❌ Surdim.",      "⚠ Partiel"],
                ["Déploiement Gunicorn",     "✅ Direct",    "✅ Direct",       "✅ Direct"],
            ],
        },
        {
            "title": "Base de données",
            "chosen": "SQLite WAL ✅",
            "cols": ["Critère", "SQLite WAL ✅", "PostgreSQL", "MySQL"],
            "rows": [
                ["Installation requise",     "✅ Aucune",    "❌ Serveur",     "❌ Serveur"],
                ["Sauvegarde",               "✅ cp fichier","⚠ pg_dump",     "⚠ mysqldump"],
                ["Concurrence lecture",      "✅ WAL",       "✅ Excellent",   "✅ Bon"],
                ["Migration SQLAlchemy",     "✅ Possible",  "✅ Possible",    "✅ Possible"],
            ],
        },
        {
            "title": "File de jobs asynchrones",
            "chosen": "ThreadPoolExecutor ✅",
            "cols": ["Critère", "ThreadPoolExec ✅", "Celery+Redis", "RQ+Redis"],
            "rows": [
                ["Dépendances",              "✅ Aucune",    "❌ Redis",       "❌ Redis"],
                ["Persistance jobs",         "⚠ Volatile",  "✅ Persistant",  "✅ Persistant"],
                ["Adéquation volume",        "✅ Suffisant", "❌ Excessif",    "⚠ Acceptable"],
                ["Complexité déploiement",   "✅ Simple",    "❌ Complexe",    "⚠ Modérée"],
            ],
        },
        {
            "title": "Chiffrement des identifiants",
            "chosen": "Fernet ✅",
            "cols": ["Critère", "Fernet ✅", "AES-CBC manuel", "Env vars seules"],
            "rows": [
                ["Authentif. message",       "✅ HMAC-SHA256","❌ À implém.",  "❌ Aucune"],
                ["Risque implémentation",    "✅ Audité",     "❌ IV fixe/noMAC","⚠ Lecture DB"],
                ["Rotation de clé",          "✅ Documentée","⚠ Manuelle",    "N/A"],
                ["Protection si DB volée",   "✅ Oui",        "⚠ Partielle",  "❌ Non"],
            ],
        },
    ]

    icon_color = {"✅": GREEN, "❌": RED, "⚠": ORANGE, "N/A": DGRAY}

    for ax, tbl in zip(axes.flat, tables):
        ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
        ax.set_facecolor(WHITE)

        # Title
        ax.text(5, 6.7, tbl["title"], fontsize=11, color=NAVY,
                ha="center", weight="bold")

        col_w = [3.2, 2.0, 2.0, 2.0]
        col_x = [0.3, 3.7, 5.9, 8.1]
        row_h = 0.85
        header_y = 5.7

        # Column headers
        for j, (cname, cx, cw) in enumerate(zip(tbl["cols"], col_x, col_w)):
            bg = TEAL if j == 1 else NAVY if j == 0 else LGRAY
            fg = WHITE if j <= 1 else DGRAY
            box(ax, cx - 0.1, header_y, cw, 0.75, cname, bg=bg, fg=fg,
                fontsize=8, bold=True, border=bg)

        for i, row in enumerate(tbl["rows"]):
            y = header_y - (i + 1) * row_h
            for j, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
                bg = "#f0fdf4" if j == 1 else (LGRAY if i % 2 == 0 else WHITE)
                # Determine color
                fg = NAVY
                for icon, c in icon_color.items():
                    if cell.startswith(icon):
                        fg = c
                        break
                box(ax, cx - 0.1, y, cw, row_h - 0.05, cell, bg=bg, fg=fg,
                    fontsize=8, border=MGRAY)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    save(fig, "schema-choix-technologiques.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 10 — API REST endpoints
# ═══════════════════════════════════════════════════════════════════════════════
def fig_api():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16); ax.set_ylim(0, 12); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(8, 11.7, "API REST v1 — Vue d'ensemble des endpoints",
            fontsize=14, color=NAVY, ha="center", weight="bold")

    METHOD_C = {"GET": GREEN, "POST": ORANGE, "DELETE": RED}

    groups = [
        ("Santé & Statut", DGRAY, [("GET", "/api/v1/health", "Healthcheck public — aucune authentification requise")]),
        ("Statistiques", BLUE, [("GET", "/api/v1/stats", "Statistiques agrégées : nb docs, sources, espace utilisé")]),
        ("Sources", NAVY, [
            ("GET",  "/api/v1/sources",         "Liste toutes les sources déclarées"),
            ("GET",  "/api/v1/sources/{id}",    "Détail d'une source"),
            ("POST", "/api/v1/sources/{id}/sync","Déclencher une synchronisation → retourne job_id"),
        ]),
        ("Jobs de fond", TEAL, [("GET", "/api/v1/jobs/{job_id}", "Statut d'un job (pending|running|done|failed)")]),
        ("Documents", BLUE, [
            ("GET", "/api/v1/documents",           "Liste tous les documents (filtrable par source, statut)"),
            ("GET", "/api/v1/documents/{id}",      "Détail d'un document"),
            ("GET", "/api/v1/documents/{id}/download","Télécharger le fichier PDF"),
        ]),
    ]

    y = 11.0
    for grp_name, grp_color, endpoints in groups:
        header_box(ax, 0.3, y - 0.38, 10.5, 0.38, grp_name, bg=grp_color)
        y -= 0.38
        for method, path, desc in endpoints:
            mc = METHOD_C.get(method, DGRAY)
            box(ax, 0.3, y - 0.52, 0.85, 0.48, method, bg=mc, fg=WHITE,
                fontsize=8, bold=True, border=mc)
            box(ax, 1.2, y - 0.52, 4.2, 0.48, path, bg=LGRAY, fg=NAVY,
                fontsize=8.5, border=MGRAY)
            ax.text(5.6, y - 0.28, desc, fontsize=8, color=DGRAY, va="center")
            y -= 0.55
        y -= 0.15

    # Auth panel
    box(ax, 11.0, 5.0, 4.7, 6.5,
        "Authentification\n\n"
        "① Session web (Flask-Login)\n"
        "   → Cookie de session\n"
        "   → CSRF requis sur POST\n\n"
        "② Token Bearer\n"
        "   Authorization: Bearer <token>\n"
        "   → Pas de CSRF\n"
        "   → Token haché en base\n"
        "   → Révocation immédiate\n\n"
        "Décorateurs partagés :\n"
        "@require_permission('sources.read')\n"
        "@require_permission('docs.download')\n"
        "→ Contrôle identique\n   session + API",
        bg=LGRAY, fg=NAVY, fontsize=8, border=NAVY, ha="left")

    # Not implemented
    box(ax, 11.0, 0.3, 4.7, 4.5,
        "Hors périmètre v1 :\n\n"
        "❌ POST /api/v1/sources\n   (création)\n\n"
        "❌ PUT /api/v1/sources/{id}\n   (modification)\n\n"
        "❌ DELETE /api/v1/sources/{id}\n   (suppression)\n\n"
        "→ Ces actions passent\n   par l'interface web",
        bg="#fff1f2", fg=RED, fontsize=8, border=RED, ha="left")

    # Curl examples
    box(ax, 0.3, 0.1, 10.5, 2.4,
        "Exemples curl :\n"
        "  curl -H 'Authorization: Bearer <token>' http://host/api/v1/sources\n"
        "  curl -X POST -H 'Authorization: Bearer <token>' http://host/api/v1/sources/1/sync\n"
        "  curl -H 'Authorization: Bearer <token>' http://host/api/v1/jobs/<job-id>",
        bg="#1e1e2e", fg="#cdd6f4", fontsize=8, border="#313244", ha="left")

    save(fig, "schema-api-rest.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 11 — Gantt prévisionnel vs réalisé
# ═══════════════════════════════════════════════════════════════════════════════
def fig_gantt():
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(0, 9.5); ax.set_ylim(-0.5, 11.5); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(4.75, 11.2, "Planning du stage — Prévisionnel vs Réalisé",
            fontsize=14, color=NAVY, ha="center", weight="bold")

    weeks = ["S1\n15-19 avr", "S2\n22-26 avr", "S3\n29 avr\n3 mai",
             "S4\n6-10 mai", "S5\n13-17 mai", "S6\n20-24 mai",
             "S7\n27-31 mai", "S8\n3-7 juin", "S9\n10-13 juin"]
    for i, w in enumerate(weeks):
        ax.text(1.5 + i, 10.8, w, fontsize=7.5, ha="center", va="center",
                color=NAVY, multialignment="center")
        ax.axvline(1.5 + i - 0.5, color=MGRAY, lw=0.8, ymin=0.05, ymax=0.9)
    ax.axvline(1.5 + 9 - 0.5, color=MGRAY, lw=0.8, ymin=0.05, ymax=0.9)

    tasks = [
        # (label, prev_start, prev_end, real_start, real_end, slip)
        ("Analyse CDC & contraintes HDS",          0, 1, 0, 1,    False),
        ("Architecture & modèle de données",       1, 2, 1, 2,    False),
        ("Connecteurs sources (SFTP, SMB, Local)", 2, 3, 2, 3,    False),
        ("Synchronisation & fraîcheur",            3, 4, 3, 4,    False),
        ("Interface web (Jinja2 / Bootstrap)",     4, 5, 4, 5,    False),
        ("Sécurité (CSRF·CSP·Fernet·RBAC)",        5, 6, 5, 7,    True),
        ("API REST & documentation OpenAPI",       6, 7, 6.5, 8,  False),
        ("Tests & couverture (20 fichiers)",       7, 9, 7, 9,    False),
        ("Documentation d'exploitation",           8, 9, 8, 9,    False),
        ("Accompagnement CSU (interventions)",     0, 9, 0, 9,    False),
    ]
    task_y = [9.5, 8.7, 7.9, 7.1, 6.3, 5.5, 4.7, 3.9, 3.1, 1.8]
    x0 = 1.0

    for (label, ps, pe, rs, re, slip), y in zip(tasks, task_y):
        ax.text(0.95, y, label, fontsize=8, ha="right", va="center", color=NAVY)
        # Planned bar
        alpha = 0.35 if label == "Accompagnement CSU (interventions)" else 0.7
        h = 0.15 if label == "Accompagnement CSU (interventions)" else 0.28
        p_bar = FancyBboxPatch((x0 + ps, y - h - 0.04), pe - ps, h * 2,
                               boxstyle="round,pad=0.02",
                               facecolor=NAVY, edgecolor="none",
                               alpha=alpha, zorder=2)
        ax.add_patch(p_bar)
        # Real bar
        r_color = RED if slip else TEAL
        r_bar = FancyBboxPatch((x0 + rs, y - h + 0.01), re - rs, h * 1.8,
                               boxstyle="round,pad=0.02",
                               facecolor=r_color, edgecolor="none",
                               alpha=0.85, zorder=3)
        ax.add_patch(r_bar)
        if slip:
            ax.text(x0 + re + 0.05, y + 0.1, "▲ +1 sem.", fontsize=7.5,
                    color=RED, va="center", weight="bold")

    # Legend
    legend_items = [
        (mpatches.Patch(facecolor=NAVY, alpha=0.7), "Prévu"),
        (mpatches.Patch(facecolor=TEAL, alpha=0.85), "Réalisé"),
        (mpatches.Patch(facecolor=RED, alpha=0.85), "Réalisé (décalage)"),
    ]
    ax.legend(handles=[p for p, _ in legend_items],
              labels=[l for _, l in legend_items],
              loc="lower right", fontsize=9, framealpha=0.9,
              bbox_to_anchor=(9.4, 0.0))

    ax.text(4.75, 0.5,
            "Décalage sécurité (+1 semaine) compensé par réduction du périmètre des tests d'intégration",
            fontsize=8, color=RED, ha="center",
            bbox=dict(fc="#fee2e2", ec=RED, pad=3, boxstyle="round"))

    save(fig, "schema-gantt-prevu-realise.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 12 — Pipeline qualité make check
# ═══════════════════════════════════════════════════════════════════════════════
def fig_pipeline_qualite():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(8, 9.7, "Pipeline de qualité — make check",
            fontsize=14, color=NAVY, ha="center", weight="bold")

    # make check tree (left)
    box(ax, 0.3, 7.8, 2.5, 1.6,
        "make check\n├── lint\n├── test\n├── security\n├── audit\n├── secrets\n└── permissions",
        bg=NAVY, fg=WHITE, fontsize=8.5, ha="left", border=NAVY)

    # Pipeline stages
    stages = [
        (BLUE,   "🔍", "Ruff",           "Linter Python\n--select E9,F63\n,F7,F82"),
        (GREEN,  "🧪", "pytest",         "20 fichiers tests\n--cov=app\ncoverage report"),
        (ORANGE, "🔒", "Bandit",         "Analyse statique\nsécurité OWASP\napp/ + config"),
        (PURPLE, "📦", "pip-audit",      "Audit CVE\nrequirements.txt\n+ dev"),
        (RED,    "🔑", "Scan secrets",   "Secrets suivis\npar Git\n(API keys, tokens)"),
        (DGRAY,  "🛡", "Permissions",   ".env chmod 600\nvérification\ndes droits"),
    ]

    stage_w = 2.1
    x0 = 3.2
    stage_y = 8.3
    for i, (color, icon, name, desc) in enumerate(stages):
        x = x0 + i * (stage_w + 0.2)
        box(ax, x, stage_y - 1.2, stage_w, 1.5, f"{icon}\n{name}\n{desc}",
            bg=color, fg=WHITE, fontsize=7.5, bold=False, border=color)
        if i < len(stages) - 1:
            ax.annotate("", xy=(x + stage_w + 0.2, stage_y - 0.45),
                        xytext=(x + stage_w, stage_y - 0.45),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))

    ax.annotate("", xy=(x0, stage_y - 0.45), xytext=(2.8, stage_y - 0.45),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))

    # Test coverage grid
    box(ax, 0.3, 0.2, 15.4, 6.0, "", bg=LGRAY, border=MGRAY)
    ax.text(0.6, 6.0, "Couverture des tests (20 fichiers)", fontsize=10,
            color=NAVY, weight="bold")

    test_cols = [
        ("Modèles & Core", NAVY, ["test_models.py", "test_sync_service.py",
                                   "test_purge_service.py", "test_sources.py",
                                   "test_documents.py"]),
        ("Sécurité", RED, ["test_security.py", "test_documents_security.py",
                            "test_api_permissions.py"]),
        ("Protocoles réseau", TEAL, ["test_sftp.py", "test_smb.py",
                                      "test_ldap.py"]),
        ("Fonctionnalités", GREEN, ["test_exports.py", "test_notifications.py",
                                     "test_templates.py", "test_jobs.py",
                                     "test_freshness.py"]),
    ]
    col_w = 3.6
    for j, (title, color, files) in enumerate(test_cols):
        cx = 0.5 + j * (col_w + 0.3)
        header_box(ax, cx, 5.4, col_w, 0.38, title, bg=color)
        for k, fname in enumerate(files):
            box(ax, cx, 5.4 - (k + 1) * 0.65, col_w, 0.6, fname,
                bg=WHITE if k % 2 == 0 else LGRAY, fg=NAVY,
                fontsize=8, border=MGRAY)

    # Bottom note
    box(ax, 0.3, 0.2, 15.4, 0.9,
        "SQLite en mémoire + stockage temporaire  ·  "
        "JOBS_RUN_INLINE=true → jobs déterministes  ·  "
        "Mocks : Paramiko, smbprotocol (pas de serveur réel requis)",
        bg=LGRAY, fg=DGRAY, fontsize=8, border=MGRAY)

    # Green success badge
    box(ax, 6.0, 9.0, 4.0, 0.6, "✅ Tous les contrôles passent → Prêt pour livraison",
        bg=GREEN, fg=WHITE, fontsize=9.5, bold=True, border=GREEN)

    save(fig, "schema-pipeline-qualite.png")


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")

    print("Generating report figures...")
    fig_avant_apres()
    fig_architecture()
    fig_modele_donnees()
    fig_flux_sync()
    fig_dashboard()
    fig_purge()
    fig_securite()
    fig_deploiement()
    fig_choix_techno()
    fig_api()
    fig_gantt()
    fig_pipeline_qualite()
    print("Done — 12 figures generated in rapport_stage/images/")
