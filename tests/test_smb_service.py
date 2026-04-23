"""Tests unitaires du connecteur SMB — sans serveur réel (mock smbclient)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone
from unittest.mock import MagicMock, patch

import pytest

from app.services.smb_service import (
    FichierDistant,
    ResultatConnexion,
    _construire_chemin_unc,
    lister_fichiers,
    tester_connexion,
)


@dataclass
class _Source:
    adresse: str = "192.168.1.100"
    port: int | None = None
    login: str = "domaine\\utilisateur"
    mot_de_passe: str = "MotDePasse123"
    chemin_distant: str = "\\\\192.168.1.100\\docs"
    filtre_fichiers: str = "*.pdf"


def _mock_entry(
    name: str,
    is_file: bool = True,
    size: int = 1024,
    mtime: float = 1_700_000_000.0,
) -> MagicMock:
    entry = MagicMock()
    entry.name = name
    entry.is_file.return_value = is_file
    entry.stat.return_value = MagicMock(st_size=size, st_mtime=mtime)
    return entry


class TestConstruireCheminUnc:
    def test_chemin_unc_complet_passe_tel_quel(self):
        src = _Source(chemin_distant="\\\\serveur\\partage\\docs")
        assert _construire_chemin_unc(src) == "\\\\serveur\\partage\\docs"

    def test_chemin_relatif_combine_avec_adresse(self):
        src = _Source(adresse="10.0.0.1", chemin_distant="partage\\docs")
        assert _construire_chemin_unc(src) == "\\\\10.0.0.1\\partage\\docs"

    def test_chemin_avec_slash_unix_utilise_adresse(self):
        src = _Source(adresse="10.0.0.1", chemin_distant="partage/docs")
        resultat = _construire_chemin_unc(src)
        assert resultat.startswith("\\\\10.0.0.1\\")


class TestListerFichiersSMB:
    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_liste_uniquement_les_pdf(self, mock_register, mock_scandir, mock_reset):
        entries = [
            _mock_entry("rapport.pdf"),
            _mock_entry("archive.zip"),
            _mock_entry("notice.pdf"),
            _mock_entry("dossier", is_file=False),
        ]
        mock_scandir.return_value = iter(entries)
        result = lister_fichiers(_Source())
        noms = [f.nom for f in result]
        assert "rapport.pdf" in noms
        assert "notice.pdf" in noms
        assert "archive.zip" not in noms
        assert "dossier" not in noms

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_retourne_metadonnees_correctes(self, mock_register, mock_scandir, mock_reset):
        mock_scandir.return_value = iter([_mock_entry("doc.pdf", size=2048, mtime=1_700_000_000.0)])
        fichiers = lister_fichiers(_Source())
        assert len(fichiers) == 1
        f = fichiers[0]
        assert f.nom == "doc.pdf"
        assert f.taille == 2048
        assert f.date_modification.tzinfo is timezone.utc

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_chemin_fichier_construit_correctement(self, mock_register, mock_scandir, mock_reset):
        mock_scandir.return_value = iter([_mock_entry("proc.pdf")])
        src = _Source(chemin_distant="\\\\srv\\share")
        fichiers = lister_fichiers(src)
        assert fichiers[0].chemin == "\\\\srv\\share\\proc.pdf"

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_retourne_liste_vide_si_aucun_match(self, mock_register, mock_scandir, mock_reset):
        mock_scandir.return_value = iter([_mock_entry("fichier.docx")])
        assert lister_fichiers(_Source()) == []

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_port_par_defaut_445(self, mock_register, mock_scandir, mock_reset):
        mock_scandir.return_value = iter([])
        lister_fichiers(_Source(port=None))
        _, kwargs = mock_register.call_args
        assert kwargs.get("port") == 445


class TestTesterConnexionSMB:
    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_succes(self, mock_register, mock_scandir, mock_reset):
        mock_scandir.return_value = iter([_mock_entry("proc.pdf")])
        result = tester_connexion(_Source())
        assert result.succes is True
        assert result.nb_fichiers == 1
        assert "réussie" in result.message

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_succes_retourne_liste_fichiers(self, mock_register, mock_scandir, mock_reset):
        mock_scandir.return_value = iter([
            _mock_entry("a.pdf"),
            _mock_entry("b.pdf"),
        ])
        result = tester_connexion(_Source())
        assert len(result.fichiers) == 2
        assert all(isinstance(f, FichierDistant) for f in result.fichiers)

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_echec_smb_exception(self, mock_register, mock_reset):
        from smbprotocol.exceptions import SMBException
        mock_register.side_effect = SMBException("Accès refusé")
        result = tester_connexion(_Source())
        assert result.succes is False
        assert "Accès refusé" in result.message
        assert result.nb_fichiers == 0

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_echec_hote_inaccessible(self, mock_register, mock_reset):
        mock_register.side_effect = OSError("Hôte inaccessible")
        result = tester_connexion(_Source())
        assert result.succes is False
        assert "Hôte inaccessible" in result.message

    @patch("app.services.smb_service.smbclient.reset_connection_cache")
    @patch("app.services.smb_service.smbclient.scandir")
    @patch("app.services.smb_service.smbclient.register_session")
    def test_echec_scandir_smb_exception(self, mock_register, mock_scandir, mock_reset):
        from smbprotocol.exceptions import SMBException
        mock_scandir.side_effect = SMBException("Partage introuvable")
        result = tester_connexion(_Source())
        assert result.succes is False
        assert result.fichiers == []
