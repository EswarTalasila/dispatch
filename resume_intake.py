"""Extracts text from an uploaded resume (PDF/DOCX) and cleans it with Claude."""

import io
import os

from anthropic import Anthropic

import config

CLEAN_PROMPT = """The text below was extracted from a resume file and may have \
messy spacing, broken columns, or odd ordering. Reformat it into a clean, \
well-structured plain-text resume that's good for matching against job \
descriptions. Keep ALL real content (experience, skills, education, projects, \
dates) and do not invent anything. Output ONLY the resume text, no commentary.

RAW RESUME TEXT:
"""


def extract_text(filename, data):
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if name.endswith(".docx"):
        import docx

        document = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs)
    raise ValueError("Unsupported file type — upload a PDF or DOCX.")


def clean_with_claude(raw_text):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=config.MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": CLEAN_PROMPT + raw_text}],
    )
    return msg.content[0].text.strip()
