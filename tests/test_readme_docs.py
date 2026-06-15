from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documente_configuration_smtp():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Configuration SMTP" in readme
    for variable in (
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "SMTP_FROM",
        "SMTP_USE_TLS",
    ):
        assert variable in readme
    assert "relais interne sans authentification" in readme
    assert "SMTP authentifié avec STARTTLS" in readme
    assert "docker compose up -d --force-recreate web" in readme
    assert "Administration > Notifications" in readme
    assert "465" in readme
