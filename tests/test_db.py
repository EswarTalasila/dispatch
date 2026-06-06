"""Database: job storage and the résumé library."""

import db


def sample_jobs():
    return [
        {"id": "1", "title": "Software Engineer", "company": "Acme",
         "location": "Charlotte, NC", "score": 80, "priority": 2080,
         "reason": "good", "url": "u1", "role_query": "Software Engineer",
         "description": "desc one"},
        {"id": "2", "title": "ML Engineer", "company": "Beta",
         "location": "Austin, TX", "score": 70, "priority": 1070,
         "reason": "ok", "url": "u2", "role_query": "ML Engineer",
         "description": "desc two"},
    ]


def test_save_and_load():
    db.save(sample_jobs())
    rows = db.load()
    assert {r["id"] for r in rows} == {"1", "2"}


def test_save_ignores_duplicate_ids():
    db.save(sample_jobs())
    db.save(sample_jobs())
    assert len(db.load()) == 2


def test_description_is_stored():
    db.save(sample_jobs())
    row = next(r for r in db.load() if r["id"] == "1")
    assert row["description"] == "desc one"


def test_update_scores():
    db.save(sample_jobs())
    db.update_scores([{"id": "1", "score": 12, "priority": 12, "reason": "changed"}])
    row = next(r for r in db.load() if r["id"] == "1")
    assert row["score"] == 12
    assert row["reason"] == "changed"


def test_resume_add_list_and_active_file():
    rid = db.add_resume("R1", "resume one")
    assert isinstance(rid, int)
    rid2 = db.add_resume("R2", "resume two")
    items = db.list_resumes()
    active = [r for r in items if r["active"]]
    assert len(active) == 1 and active[0]["id"] == rid2
    with open(db.RESUME_FILE) as f:
        assert f.read() == "resume two"  # newest is active and written to file


def test_resume_activate_and_get():
    a = db.add_resume("A", "alpha text")
    db.add_resume("B", "bravo text")
    assert db.activate_resume(a) is True
    with open(db.RESUME_FILE) as f:
        assert f.read() == "alpha text"
    got = db.get_resume(a)
    assert got["name"] == "A" and got["text"] == "alpha text"


def test_resume_delete_active_falls_back():
    db.add_resume("A", "aaa")
    b = db.add_resume("B", "bbb")  # active
    db.delete_resume(b)
    active = [r for r in db.list_resumes() if r["active"]]
    assert len(active) == 1 and active[0]["name"] == "A"
