"""FastAPI backend serving matched jobs from the local SQLite store to the
React frontend. Run: uvicorn server:app --reload"""

import os
import threading
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import db
import main as pipeline
import progress
import resume_intake

app = FastAPI(title="Job Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


# Single source of truth for tiering lives in the pipeline; the API reuses it.
location_tier = pipeline.location_rank

TIER_LABELS = {0: "NC", 1: "TX"}


def enrich(job):
    tier = location_tier(job["location"])
    job["tier"] = tier
    job["tier_label"] = TIER_LABELS.get(tier, "OTHER")
    job["score"] = round(job["score"]) if job["score"] is not None else 0
    return job


@app.get("/api/jobs")
def get_jobs(
    q: str = "",
    min_score: int = 0,
    role: str = "",
    date: str = "",
    sort: str = "score",
):
    jobs = [enrich(j) for j in db.load()]

    q = q.lower().strip()
    if q:
        jobs = [j for j in jobs if q in (j["title"] + " " + j["company"]).lower()]
    if min_score:
        jobs = [j for j in jobs if j["score"] >= min_score]
    if role:
        jobs = [j for j in jobs if j["role_query"] == role]
    if date:
        jobs = [j for j in jobs if j["found_date"] == date]

    if sort == "priority":
        jobs.sort(key=lambda j: j.get("priority") or 0, reverse=True)
    elif sort == "new":
        jobs.sort(key=lambda j: (j.get("found_date") or "", j.get("score") or 0), reverse=True)
    elif sort == "company":
        jobs.sort(key=lambda j: ((j.get("company") or "").lower(), -(j.get("score") or 0)))
    else:  # "score"
        jobs.sort(key=lambda j: j.get("score") or 0, reverse=True)
    return jobs


def _plural(n):
    return "" if n == 1 else "s"


def _start_background(worker):
    """Run worker in a daemon thread if no run is in progress."""
    if not progress.try_start():
        return {"started": False, "running": True}
    threading.Thread(target=worker, daemon=True).start()
    return {"started": True, "running": True}


def _run_pipeline():
    try:
        before = len(db.load())
        pipeline.main()
        added = len(db.load()) - before
        progress.finish(f"Done — {added} new job{_plural(added)} added.")
    except progress.Cancelled:
        progress.finish("Cancelled — no changes saved.")
    except Exception as e:
        progress.finish(f"Refresh failed: {e}")


def _run_rescore():
    try:
        n = pipeline.rescore()
        progress.finish(f"Re-scored {n} job{_plural(n)} against your résumé.")
    except progress.Cancelled:
        progress.finish("Cancelled — no changes saved.")
    except Exception as e:
        progress.finish(f"Re-score failed: {e}")


@app.post("/api/refresh")
def refresh():
    return _start_background(_run_pipeline)


@app.post("/api/rescore")
def rescore():
    return _start_background(_run_rescore)


@app.post("/api/cancel")
def cancel():
    return {"cancelled": progress.request_cancel()}


@app.get("/api/status")
def status():
    return progress.snapshot()


@app.get("/api/resumes")
def list_resumes():
    return {"resumes": db.list_resumes()}


@app.post("/api/resume", responses={400: {"description": "Invalid or unreadable file"}})
async def upload_resume(file: Annotated[UploadFile, File()]):
    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(400, "File too large (max 5 MB).")
    try:
        raw = resume_intake.extract_text(file.filename, data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception:
        raise HTTPException(400, "Couldn't parse that file — make sure it's a valid PDF or DOCX.")
    if not raw.strip():
        raise HTTPException(400, "Couldn't read any text from that file.")

    cleaned = resume_intake.clean_with_claude(raw)
    name = os.path.splitext(file.filename or "")[0].strip() or "Résumé"
    new_id = db.add_resume(name, cleaned)
    return {"ok": True, "id": new_id, "name": name, "chars": len(cleaned)}


@app.get("/api/resumes/{resume_id}", responses={404: {"description": "Resume not found"}})
def get_resume(resume_id: int):
    r = db.get_resume(resume_id)
    if not r:
        raise HTTPException(404, "Resume not found.")
    return r


@app.post(
    "/api/resumes/{resume_id}/activate",
    responses={404: {"description": "Resume not found"}},
)
def activate_resume(resume_id: int):
    if not db.activate_resume(resume_id):
        raise HTTPException(404, "Resume not found.")
    return {"ok": True}


@app.delete("/api/resumes/{resume_id}")
def delete_resume(resume_id: int):
    active_id = db.delete_resume(resume_id)
    return {"ok": True, "active_id": active_id}


@app.get("/api/meta")
def get_meta():
    jobs = db.load()
    scores = [j["score"] for j in jobs if j["score"] is not None]
    tiers = [location_tier(j["location"]) for j in jobs]
    roles = sorted({j["role_query"] for j in jobs if j["role_query"]})
    dates = sorted({j["found_date"] for j in jobs if j["found_date"]}, reverse=True)

    return {
        "total": len(jobs),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "top_score": round(max(scores)) if scores else 0,
        "nc_count": tiers.count(0),
        "tx_count": tiers.count(1),
        "roles": roles,
        "dates": dates,
    }
