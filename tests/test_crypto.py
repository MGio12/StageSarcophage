"""Tests unitaires du module de chiffrement (app/utils/crypto.py)."""

import pytest
from cryptography.fernet import Fernet
from app.utils.crypto import chiffrer, dechiffrer


class TestChiffrement:
    def test_chiffrer_produit_valeur_differente(self, app):
        with app.app_context():
            resultat = chiffrer("mot_de_passe_secret")
            assert resultat != "mot_de_passe_secret"

    def test_chiffrer_est_encodage_ascii(self, app):
        with app.app_context():
            resultat = chiffrer("test")
            # Fernet produit du base64 URL-safe, donc ASCII pur
            resultat.encode("ascii")

    def test_dechiffrer_inverse_chiffrer(self, app):
        with app.app_context():
            original = "P@ssw0rd!très-sécurisé"
            assert dechiffrer(chiffrer(original)) == original

    def test_chiffrer_chaine_vide_retourne_vide(self, app):
        with app.app_context():
            assert chiffrer("") == ""

    def test_dechiffrer_chaine_vide_retourne_vide(self, app):
        with app.app_context():
            assert dechiffrer("") == ""

    def test_chiffrement_non_deterministe(self, app):
        """Deux chiffrements du même texte produisent des tokens différents (IV aléatoire)."""
        with app.app_context():
            a = chiffrer("secret")
            b = chiffrer("secret")
            assert a != b
            # Mais les deux se déchiffrent en la même valeur
            assert dechiffrer(a) == dechiffrer(b) == "secret"

    def test_dechiffrer_mauvaise_cle_leve_valeur_error(self, app):
        with app.app_context():
            token = chiffrer("secret")

        # Nouvelle app avec une clé différente
        autre_app = app.test_client().application.__class__(
            app.import_name, instance_relative_config=True
        )
        # On crée un contexte isolé avec une clé différente
        from app import create_app
        app2 = create_app("testing")
        app2.config["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

        with app2.app_context():
            with pytest.raises(ValueError, match="Déchiffrement impossible"):
                dechiffrer(token)

    def test_dechiffrer_donnees_corrompues_leve_valeur_error(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="Déchiffrement impossible"):
                dechiffrer("donnees-corrompues-invalides")

    def test_encryption_key_absente_leve_runtime_error(self):
        from app import create_app
        app_sans_cle = create_app("testing")
        app_sans_cle.config["ENCRYPTION_KEY"] = ""

        with app_sans_cle.app_context():
            with pytest.raises(RuntimeError, match="ENCRYPTION_KEY"):
                chiffrer("test")
