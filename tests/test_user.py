"""Tests du modèle User et de l'authentification."""
import pytest
from app.models.user import User


class TestModeleUser:
    def test_creation_user(self, db):
        user = User(username="testuser")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.is_active is True

    def test_password_hash_different_du_clair(self, db):
        user = User(username="testuser2")
        mot_de_passe_test = "monmotdepasse"  # pragma: allowlist secret
        user.set_password(mot_de_passe_test)
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != mot_de_passe_test
        assert mot_de_passe_test not in user.password_hash

    def test_check_password_correct(self, db):
        user = User(username="testuser3")
        user.set_password("correct")
        db.session.add(user)
        db.session.commit()

        assert user.check_password("correct") is True

    def test_check_password_incorrect(self, db):
        user = User(username="testuser4")
        user.set_password("correct")
        db.session.add(user)
        db.session.commit()

        assert user.check_password("incorrect") is False

    def test_unicite_username(self, db):
        from sqlalchemy.exc import IntegrityError

        user1 = User(username="duplicate")
        user1.set_password("pass1")
        db.session.add(user1)
        db.session.commit()

        user2 = User(username="duplicate")
        user2.set_password("pass2")
        db.session.add(user2)
        with pytest.raises(IntegrityError):
            db.session.commit()
