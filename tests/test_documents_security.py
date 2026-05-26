from app.models.document import Document, StatutDocument
from app.models.role import Role
from app.models.source import Source
from app.models.user import User


def _login(client, db, permissions):
    role = Role(nom="documents-role", permissions=permissions)
    user = User(username="documents-user", role=role)
    user.set_password("secret123")
    db.session.add_all([role, user])
    db.session.commit()
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True
    return user


def _source(db):
    src = Source(
        nom="Documents source",
        type_serveur="linux",
        protocole="local",
        chemin_distant="/tmp",
    )
    db.session.add(src)
    db.session.flush()
    return src


def test_zip_refuse_document_hors_storage(client, db, app, tmp_path):
    _login(client, db, {"documents.view": True, "documents.download": True})
    storage = tmp_path / "storage"
    storage.mkdir()
    outside = tmp_path / "storage_evil" / "doc.pdf"
    outside.parent.mkdir()
    outside.write_bytes(b"%PDF")
    app.config["STORAGE_DIR"] = str(storage)
    src = _source(db)
    doc = Document(
        source_id=src.id,
        nom_fichier="doc.pdf",
        chemin_local=str(outside),
    )
    db.session.add(doc)
    db.session.commit()

    response = client.post("/documents/telecharger-zip", data={"doc_ids": [doc.id]})

    assert response.status_code == 403


def test_telechargement_refuse_document_purge(client, db, app, tmp_path):
    _login(client, db, {"documents.download": True})
    app.config["STORAGE_DIR"] = str(tmp_path)
    fichier = tmp_path / "doc.pdf"
    fichier.write_bytes(b"%PDF")
    src = _source(db)
    doc = Document(
        source_id=src.id,
        nom_fichier="doc.pdf",
        chemin_local=str(fichier),
        statut=StatutDocument.PURGE,
    )
    db.session.add(doc)
    db.session.commit()

    response = client.get(f"/documents/{doc.id}/telecharger")

    assert response.status_code == 404


def test_pdf_inline_refuse_document_purge(client, db, app, tmp_path):
    _login(client, db, {"documents.view": True})
    app.config["STORAGE_DIR"] = str(tmp_path)
    fichier = tmp_path / "doc.pdf"
    fichier.write_bytes(b"%PDF")
    src = _source(db)
    doc = Document(
        source_id=src.id,
        nom_fichier="doc.pdf",
        chemin_local=str(fichier),
        statut=StatutDocument.PURGE,
    )
    db.session.add(doc)
    db.session.commit()

    response = client.get(f"/documents/pdf/{doc.id}")

    assert response.status_code == 404
