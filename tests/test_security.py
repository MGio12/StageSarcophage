"""Tests de sécurité : sanitization des noms de fichiers, path traversal."""
import os
import builtins
import inspect
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet

from app import create_app
from app.routes import api as api_routes
from app.services.sync_service import _safe_filename, _verifier_chemin_storage


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PROJECT_ROOT / "app" / "templates"


class TestSafeFilename:
    def test_nom_simple_inchange(self):
        assert _safe_filename("document.pdf") == "document.pdf"

    def test_supprime_chemin_relatif(self):
        assert _safe_filename("../../../etc/passwd") == "passwd"

    def test_supprime_chemin_absolu(self):
        assert _safe_filename("/etc/passwd") == "passwd"

    def test_supprime_chemin_windows(self):
        assert _safe_filename("..\\..\\windows\\system32\\config") == "config"

    def test_supprime_caractere_nul(self):
        assert _safe_filename("doc\x00ument.pdf") == "document.pdf"

    def test_refuse_fichier_cache(self):
        with pytest.raises(ValueError, match="invalide"):
            _safe_filename(".hidden")

    def test_refuse_nom_vide(self):
        with pytest.raises(ValueError, match="invalide"):
            _safe_filename("")

    def test_refuse_seulement_points(self):
        with pytest.raises(ValueError, match="invalide"):
            _safe_filename("...")


class TestVerifierCheminStorage:
    def test_chemin_valide(self, tmp_path):
        storage = str(tmp_path / "storage")
        os.makedirs(storage)
        chemin = os.path.join(storage, "doc.pdf")
        # Ne doit pas lever d'exception
        _verifier_chemin_storage(chemin, storage)

    def test_path_traversal_detecte(self, tmp_path):
        storage = str(tmp_path / "storage")
        os.makedirs(storage)
        chemin = os.path.join(storage, "..", "outside.pdf")
        with pytest.raises(ValueError, match="path traversal"):
            _verifier_chemin_storage(chemin, storage)

    def test_chemin_absolu_hors_storage(self, tmp_path):
        storage = str(tmp_path / "storage")
        os.makedirs(storage)
        with pytest.raises(ValueError, match="path traversal"):
            _verifier_chemin_storage("/etc/passwd", storage)


def test_api_docs_utilise_template_dedie_pas_render_template_string():
    source = inspect.getsource(api_routes)

    assert "render_template_string" not in source


def test_templates_evitent_sinks_dom_xss_et_handlers_inline():
    patterns = ("innerHTML", "insertAdjacentHTML", "outerHTML", "document.write")
    violations = []

    for path in TEMPLATES_DIR.rglob("*.html"):
        contenu = path.read_text(encoding="utf-8")
        rel_path = path.relative_to(PROJECT_ROOT)
        for pattern in patterns:
            if pattern in contenu:
                violations.append(f"{rel_path}: {pattern}")
        for match in re.finditer(r"\son[a-z]+\s*=", contenu):
            violations.append(f"{rel_path}: inline handler {match.group().strip()}")

    assert violations == []


def test_entetes_securite_production_utilisent_csp_nonce(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    monkeypatch.delenv("FORCE_HTTPS", raising=False)
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)

    with patch("app.scheduler.tasks.demarrer_scheduler"):
        production_app = create_app("production")

    response = production_app.test_client().get(
        "/api/v1/health",
        base_url="https://example.test",
    )
    csp = response.headers["Content-Security-Policy"]
    script_src = next(
        directive for directive in csp.split("; ") if directive.startswith("script-src ")
    )

    assert response.status_code == 200
    assert production_app.config["SESSION_COOKIE_SECURE"] is True
    assert production_app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert production_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert "'unsafe-inline'" not in script_src
    assert "https://cdn.jsdelivr.net" in script_src
    assert re.search(r"'nonce-[^']+'", script_src)
    assert "object-src 'none'" in csp
    assert "base-uri 'self'" in csp
    assert "form-action 'self'" in csp
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_entetes_securite_ne_dependent_pas_de_flask_talisman(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    monkeypatch.delenv("FORCE_HTTPS", raising=False)
    real_import = builtins.__import__

    def block_talisman(name, *args, **kwargs):
        if name == "flask_talisman":
            raise ImportError("flask_talisman unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_talisman)
    with patch("app.scheduler.tasks.demarrer_scheduler"):
        production_app = create_app("production")

    response = production_app.test_client().get(
        "/api/v1/health",
        base_url="https://example.test",
    )

    assert response.status_code == 200
    assert "Content-Security-Policy" in response.headers
