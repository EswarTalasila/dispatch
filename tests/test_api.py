"""API endpoints via FastAPI's TestClient (no network)."""

import io
import time

import docx
from fastapi.testclient import TestClient

import db
import server

client = TestClient(server.app)


def seed():
    db.save([
        {"id": "1", "title": "Senior Engineer", "company": "Zeta",
         "location": "Charlotte, NC", "score": 60, "priority": 2060,
         "reason": "r", "url": "u", "role_query": "Software Engineer", "description": "d"},
        {"id": "2", "title": "AI Engineer", "company": "Acme",
         "location": "Austin, TX", "score": 90, "priority": 1090,
         "reason": "r", "url": "u", "role_query": "AI Engineer", "description": "d"},
        {"id": "3", "title": "Data Engineer", "company": "Mid",
         "location": "Remote, US", "score": 75, "priority": 75,
         "reason": "r", "url": "u", "role_query": "Data Engineer", "description": "d"},
    ])


def test_sort_by_score():
    seed()
    data = client.get("/api/jobs?sort=score").json()
    scores = [j["score"] for j in data]
    assert scores == sorted(scores, reverse=True)
    assert data[0]["score"] == 90


def test_sort_by_priority_puts_nc_first():
    seed()
    data = client.get("/api/jobs?sort=priority").json()
    assert data[0]["id"] == "1"


def test_sort_by_company_alphabetical():
    seed()
    data = client.get("/api/jobs?sort=company").json()
    companies = [j["company"].lower() for j in data]
    assert companies == sorted(companies)


def test_filter_min_score():
    seed()
    data = client.get("/api/jobs?min_score=80").json()
    assert len(data) == 1 and data[0]["score"] >= 80


def test_filter_query_and_role():
    seed()
    assert len(client.get("/api/jobs?q=acme").json()) == 1
    role = client.get("/api/jobs?role=AI Engineer").json()
    assert len(role) == 1 and role[0]["id"] == "2"


def test_meta_counts():
    seed()
    m = client.get("/api/meta").json()
    assert m["total"] == 3
    assert m["nc_count"] == 1
    assert m["tx_count"] == 1
    assert m["top_score"] == 90


def test_enrich_tier_label():
    seed()
    data = client.get("/api/jobs?sort=priority").json()
    assert next(j for j in data if j["id"] == "1")["tier_label"] == "NC"


def test_resume_endpoints():
    db.add_resume("Mine", "my resume text")
    listing = client.get("/api/resumes").json()["resumes"]
    assert any(r["name"] == "Mine" for r in listing)
    rid = listing[0]["id"]
    assert client.get(f"/api/resumes/{rid}").json()["text"] == "my resume text"
    assert client.post(f"/api/resumes/{rid}/activate").json()["ok"] is True
    assert client.get("/api/resumes/999999").status_code == 404


def test_resume_upload(monkeypatch):
    monkeypatch.setattr(
        server.resume_intake, "clean_with_claude", lambda raw: "CLEANED " + raw[:10]
    )
    document = docx.Document()
    document.add_paragraph("Hello World Resume")
    buf = io.BytesIO()
    document.save(buf)
    resp = client.post(
        "/api/resume",
        files={"file": ("me.docx", buf.getvalue(),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "me"
    assert any(r["name"] == "me" for r in client.get("/api/resumes").json()["resumes"])


def test_refresh_runs_to_completion(monkeypatch):
    monkeypatch.setattr(server.pipeline, "main", lambda: None)
    assert client.post("/api/refresh").json()["started"] is True
    status = {}
    for _ in range(50):
        status = client.get("/api/status").json()
        if not status["running"]:
            break
        time.sleep(0.1)
    assert status["running"] is False
