"""Tests unitaires du connecteur SFTP - sans serveur réel (mock paramiko)."""
from __future__ import annotations

import base64
import hashlib
import stat as stat_module
from dataclasses import dataclass
from datetime import timezone
from unittest.mock import MagicMock, patch

import paramiko
import pytest

from app.services.sftp_service import (
    FichierDistant,
    HostKeyMismatchError,
    ResultatConnexion,
    StrictHostKeyPolicy,
    _calculer_fingerprint,
    lister_fichiers,
    tester_connexion,
)


@dataclass
class _Source:
    adresse: str = "192.168.1.50"
    port: int | None = None
    login: str = "sftp_user"
    mot_de_passe: str = "MotDePasse123"
    chemin_distant: str = "/data/modes-degrades"
    filtre_fichiers: str = "*.pdf"


def _mock_attr(
    filename: str,
    is_regular: bool = True,
    size: int = 1024,
    mtime: float = 1_700_000_000.0,
) -> MagicMock:
    attr = MagicMock()
    attr.filename = filename
    attr.st_mode = 0o100644 if is_regular else 0o040755
    attr.st_size = size
    attr.st_mtime = mtime
    return attr


def _build_ssh_mock(attrs: list) -> MagicMock:
    """Construit un SSHClient mocké avec un SFTP retournant *attrs*."""
    mock_sftp = MagicMock()
    mock_sftp.listdir_attr.return_value = attrs

    mock_ssh = MagicMock()
    mock_ssh.open_sftp.return_value = mock_sftp
    return mock_ssh


class _FakeKey:
    def __init__(self, payload: bytes = b"public-key"):
        self.payload = payload

    def asbytes(self) -> bytes:
        return self.payload

    def get_name(self) -> str:
        return "ssh-ed25519"


class TestFingerprintSFTP:
    def test_fingerprint_utilise_format_openssh_sha256(self):
        payload = b"server-public-key"
        attendu = base64.b64encode(hashlib.sha256(payload).digest()).decode("ascii").rstrip("=")

        fingerprint = _calculer_fingerprint(_FakeKey(payload))

        assert fingerprint == f"SHA256:{attendu}"
        assert "=" not in fingerprint

    def test_fingerprint_legacy_hex_reste_accepte(self):
        payload = b"server-public-key"
        legacy_hex = hashlib.sha256(payload).hexdigest()
        transport = MagicMock()
        transport.getpeername.return_value = ("sftp", 22)
        client = MagicMock()
        client.get_transport.return_value = transport

        with patch(
            "app.services.sftp_service._get_stored_fingerprint",
            return_value=(legacy_hex, "ssh-ed25519"),
        ), patch("app.services.sftp_service._save_fingerprint") as save_fingerprint:
            StrictHostKeyPolicy(source_id=42).missing_host_key(client, "sftp", _FakeKey(payload))

        save_fingerprint.assert_called_once()
        assert save_fingerprint.call_args.args[0:3] == (42, "sftp", 22)
        assert save_fingerprint.call_args.args[3].startswith("SHA256:")


class TestListerFichiersSFTP:
    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_liste_uniquement_les_pdf(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([
            _mock_attr("rapport.pdf"),
            _mock_attr("archive.zip"),
            _mock_attr("notice.pdf"),
            _mock_attr("sous-dossier", is_regular=False),
        ])
        result = lister_fichiers(_Source())
        noms = [f.nom for f in result]
        assert "rapport.pdf" in noms
        assert "notice.pdf" in noms
        assert "archive.zip" not in noms
        assert "sous-dossier" not in noms

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_retourne_metadonnees_correctes(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([
            _mock_attr("doc.pdf", size=4096, mtime=1_700_000_000.0),
        ])
        fichiers = lister_fichiers(_Source())
        assert len(fichiers) == 1
        f = fichiers[0]
        assert f.nom == "doc.pdf"
        assert f.taille == 4096
        assert f.date_modification.tzinfo is timezone.utc

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_chemin_fichier_construit_correctement(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([_mock_attr("proc.pdf")])
        src = _Source(chemin_distant="/data/docs/")
        fichiers = lister_fichiers(src)
        assert fichiers[0].chemin == "/data/docs/proc.pdf"

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_retourne_liste_vide_si_aucun_match(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([_mock_attr("fichier.docx")])
        assert lister_fichiers(_Source()) == []

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_port_par_defaut_22(self, mock_ssh_class):
        mock_ssh = _build_ssh_mock([])
        mock_ssh_class.return_value = mock_ssh
        lister_fichiers(_Source(port=None))
        _, kwargs = mock_ssh.connect.call_args
        assert kwargs.get("port") == 22

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_connexion_sans_agent_ni_cles(self, mock_ssh_class):
        mock_ssh = _build_ssh_mock([])
        mock_ssh_class.return_value = mock_ssh
        lister_fichiers(_Source())
        _, kwargs = mock_ssh.connect.call_args
        assert kwargs.get("allow_agent") is False
        assert kwargs.get("look_for_keys") is False

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_ignore_les_repertoires(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([
            _mock_attr("dossier", is_regular=False),
            _mock_attr("fiche.pdf", is_regular=True),
        ])
        result = lister_fichiers(_Source())
        assert len(result) == 1
        assert result[0].nom == "fiche.pdf"

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_ignore_les_noms_distants_dangereux(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([
            _mock_attr("../secret.pdf"),
            _mock_attr("..\\secret.pdf"),
            _mock_attr("fiche.pdf"),
        ])
        result = lister_fichiers(_Source())
        assert [f.nom for f in result] == ["fiche.pdf"]


class TestTesterConnexionSFTP:
    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_succes(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([_mock_attr("proc.pdf")])
        result = tester_connexion(_Source())
        assert result.succes is True
        assert result.nb_fichiers == 1
        assert "réussie" in result.message

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_succes_retourne_liste_fichiers(self, mock_ssh_class):
        mock_ssh_class.return_value = _build_ssh_mock([
            _mock_attr("a.pdf"),
            _mock_attr("b.pdf"),
        ])
        result = tester_connexion(_Source())
        assert len(result.fichiers) == 2
        assert all(isinstance(f, FichierDistant) for f in result.fichiers)

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_echec_authentification(self, mock_ssh_class):
        mock_ssh = MagicMock()
        mock_ssh.connect.side_effect = paramiko.AuthenticationException("Mot de passe incorrect")
        mock_ssh_class.return_value = mock_ssh
        result = tester_connexion(_Source())
        assert result.succes is False
        assert "Authentification refusée" in result.message
        assert result.nb_fichiers == 0

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_echec_ssh_exception(self, mock_ssh_class):
        mock_ssh = MagicMock()
        mock_ssh.connect.side_effect = paramiko.SSHException("Négociation SSH échouée")
        mock_ssh_class.return_value = mock_ssh
        result = tester_connexion(_Source())
        assert result.succes is False
        assert result.message == "Connexion SFTP impossible."

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_echec_hote_inaccessible(self, mock_ssh_class):
        mock_ssh = MagicMock()
        mock_ssh.connect.side_effect = OSError("Network unreachable")
        mock_ssh_class.return_value = mock_ssh
        result = tester_connexion(_Source())
        assert result.succes is False
        assert result.message == "Hôte SFTP inaccessible."

    @patch("app.services.sftp_service.paramiko.SSHClient")
    def test_echec_listdir_attr(self, mock_ssh_class):
        mock_sftp = MagicMock()
        mock_sftp.listdir_attr.side_effect = OSError("Permission denied")
        mock_ssh = MagicMock()
        mock_ssh.open_sftp.return_value = mock_sftp
        mock_ssh_class.return_value = mock_ssh
        result = tester_connexion(_Source())
        assert result.succes is False
        assert result.fichiers == []

    def test_echec_fingerprint_modifie_retourne_empreintes(self):
        with patch(
            "app.services.sftp_service.lister_fichiers",
            side_effect=HostKeyMismatchError("SHA256:ancienne", "SHA256:nouvelle"),
        ):
            result = tester_connexion(_Source())

        assert result.succes is False
        assert result.fingerprint_attendu == "SHA256:ancienne"
        assert result.fingerprint_recu == "SHA256:nouvelle"
