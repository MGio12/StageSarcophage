from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = PROJECT_ROOT / "app" / "templates"


def _read(path: str) -> str:
    return (TEMPLATES / path).read_text(encoding="utf-8")


def test_base_layout_expose_skip_link_and_main_target():
    base = _read("base.html")

    assert 'href="#main-content"' in base
    assert 'id="main-content"' in base
    assert "skip-link" in base


def test_shared_macros_exist_for_repeated_ui_patterns():
    macros = _read("_macros.html")

    assert "macro status_badge" in macros
    assert "macro icon_button" in macros
    assert "macro empty_state" in macros
    assert "macro pagination_nav" in macros


def test_document_filters_have_explicit_labels_and_row_selection_names():
    documents = _read("documents/index.html")

    for control_id in (
        "filter-source",
        "filter-statut",
        "filter-q",
        "filter-depuis",
        "filter-jusqua",
    ):
        assert f'for="{control_id}"' in documents
        assert f'id="{control_id}"' in documents
    assert "selectionner-doc-" in documents


def test_dead_root_template_removed():
    assert not (TEMPLATES / "index.html").exists()
