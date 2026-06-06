"""Test setup: point storage at throwaway temp files before importing modules."""

import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="dispatch-test-")
os.environ["JOBS_DB"] = os.path.join(_tmp, "jobs.db")
os.environ["RESUME_FILE"] = os.path.join(_tmp, "resume.txt")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

import pytest


@pytest.fixture(autouse=True)
def fresh_state():
    """Wipe the temp DB and resume file before each test for isolation."""
    for path in (os.environ["JOBS_DB"], os.environ["RESUME_FILE"]):
        if os.path.exists(path):
            os.remove(path)
    yield
