"""FastAPI backend serving matched jobs from the local SQLite store to the
React frontend. Run: uvicorn server:app --reload"""

import os
import re
import threading

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import config
import db
import main as pipeline
import progress
import resume_intake

app = FastAPI(title="Job Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def location_tier(location):
    low = (location or "").lower()
    for tier, keywords in enumerate(config.LOCATION_TIERS):
        if any(re.search(rf"\b{re.escape(kw)}\b", low) for kw in keywords):
            return tier
    return len(config.LOCATION_TIERS)


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
    sort: str = "priority",
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

    key = "score" if sort == "score" else "priority"
    jobs.sort(key=lambda j: (j.get(key) or 0), reverse=True)
    return jobs


def _run_pipeline():
    try:
        before = len(db.load())
        pipeline.main()
        added = len(db.load()) - before
        progress.finish(f"Done — {added} new job{'s' if added != 1 else ''} added.")
    except Exception as e:
        progress.finish(f"Refresh failed: {e}")


@app.post("/api/refresh")
def refresh():
    if not progress.try_start():
        return {"started": False, "running": True}
    threading.Thread(target=_run_pipeline, daemon=True).start()
    return {"started": True, "running": True}


def _run_rescore():
    try:
        n = pipeline.rescore()
        progress.finish(f"Re-scored {n} job{'s' if n != 1 else ''} against your résumé.")
    except Exception as e:
        progress.finish(f"Re-score failed: {e}")


@app.post("/api/rescore")
def rescore():
    if not progress.try_start():
        return {"started": False, "running": True}
    threading.Thread(target=_run_rescore, daemon=True).start()
    return {"started": True, "running": True}


@app.get("/api/status")
def status():
    return progress.snapshot()


@app.get("/api/resumes")
def list_resumes():
    return {"resumes": db.list_resumes()}


@app.post("/api/resume")
async def upload_resume(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(400, "File too large (max 5 MB).")
    try:
        raw = resume_intake.extract_text(file.filename, data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not raw.strip():
        raise HTTPException(400, "Couldn't read any text from that file.")

    cleaned = resume_intake.clean_with_claude(raw)
    name = os.path.splitext(file.filename or "")[0].strip() or "Résumé"
    new_id = db.add_resume(name, cleaned)
    return {"ok": True, "id": new_id, "name": name, "chars": len(cleaned)}


@app.post("/api/resumes/{resume_id}/activate")
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
