"""Résumé text extraction from uploaded files."""

import io

import docx
import pytest

import resume_intake


def _docx_bytes(lines):
    document = docx.Document()
    for line in lines:
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def test_extract_docx():
    data = _docx_bytes(["Jane Tester", "Software Engineer", "Skills: Python"])
    text = resume_intake.extract_text("resume.docx", data)
    assert "Jane Tester" in text
    assert "Python" in text


def test_unsupported_type_raises():
    with pytest.raises(ValueError):
        resume_intake.extract_text("resume.txt", b"plain text")
