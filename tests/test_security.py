"""Tests de sécurité : sanitization des noms de fichiers, path traversal."""
import os
import pytest
from app.services.sync_service import _safe_filename, _verifier_chemin_storage


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
