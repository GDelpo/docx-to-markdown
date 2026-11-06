"""Regression tests for the upload endpoint: the client-supplied filename must never pick the write path."""
import io
import zipfile

import pytest
from docx import Document
from fastapi.testclient import TestClient

from webapp import main
from webapp.main import app

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def docx_bytes() -> bytes:
    document = Document()
    document.add_paragraph("Hello")
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def post(client: TestClient, filename: str, content: bytes | None = None):
    payload = docx_bytes() if content is None else content
    return client.post("/convertir/", files={"docx": (filename, payload, DOCX_MIME)})


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "RESULTADOS_DIR", tmp_path / "resultados")
    main.RESULTADOS_DIR.mkdir()
    return TestClient(app)


def test_absolute_filename_does_not_write_outside(client, tmp_path):
    target = tmp_path / "planted.docx"
    response = post(client, target.as_posix())
    assert not target.exists()
    assert response.status_code == 200


@pytest.mark.parametrize("prefix", ["../", "..\\", "../../", "a/../../"])
def test_traversal_filename_does_not_write_outside(client, tmp_path, monkeypatch, prefix):
    work = tmp_path / "x" / "y"
    work.mkdir(parents=True)
    monkeypatch.setattr("tempfile.tempdir", str(work))
    response = post(client, f"{prefix}planted.docx")
    assert response.status_code == 200
    assert list(tmp_path.rglob("planted*")) == []


def test_valid_upload_returns_zip_with_markdown(client):
    before = set(main.RESULTADOS_DIR.iterdir())
    response = post(client, "mi informe.docx")
    assert response.status_code == 200
    assert "mi_informe_resultado.zip" in response.text
    created = set(main.RESULTADOS_DIR.iterdir()) - before
    assert len(created) == 1
    with zipfile.ZipFile(created.pop()) as archive:
        assert "mi_informe.md" in archive.namelist()
        assert "Hello" in archive.read("mi_informe.md").decode("utf-8")


@pytest.mark.parametrize("filename", ["notes.txt", "noextension", "evil.docx.exe"])
def test_rejects_non_docx_filename(client, filename):
    assert post(client, filename).status_code == 400


def test_invalid_docx_content_is_not_a_success(client):
    assert post(client, "broken.docx", b"not a docx").status_code != 200
