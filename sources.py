"""Pulls job listings from the Adzuna API."""

import os
import requests

import config

BASE = "https://api.adzuna.com/v1/api/jobs"


def fetch_role(role):
    app_id = os.environ["ADZUNA_APP_ID"]
    app_key = os.environ["ADZUNA_APP_KEY"]

    jobs = []
    for page in range(1, config.PAGES_PER_ROLE + 1):
        url = f"{BASE}/{config.COUNTRY}/search/{page}"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": role,
            "results_per_page": config.RESULTS_PER_PAGE,
            "content-type": "application/json",
            "max_days_old": 3,
            "sort_by": "date",
        }
        if config.LOCATION:
            params["where"] = config.LOCATION

        # Don't use raise_for_status(): its message embeds the full URL, which
        # includes app_id/app_key. Raise a clean error so keys never leak into
        # logs or the /api/status message.
        try:
            resp = requests.get(url, params=params, timeout=30)
        except requests.RequestException:
            raise RuntimeError("Adzuna request failed (network error)")
        if resp.status_code != 200:
            raise RuntimeError(f"Adzuna request failed (HTTP {resp.status_code})")

        results = resp.json().get("results", [])
        if not results:
            break
        for item in results:
            jobs.append({
                "id": str(item.get("id")),
                "title": item.get("title", "").strip(),
                "company": (item.get("company") or {}).get("display_name", "").strip(),
                "location": (item.get("location") or {}).get("display_name", "").strip(),
                "description": item.get("description", "").strip(),
                "url": item.get("redirect_url", ""),
                "role_query": role,
            })
    return jobs


def _excluded_by_title(title):
    low = title.lower()
    return any(kw in low for kw in config.EXCLUDE_TITLE_KEYWORDS)


def _excluded_by_company(company):
    low = company.lower()
    return any(c in low for c in config.EXCLUDE_COMPANIES)


def fetch_all(progress_cb=None):
    """Fetch every configured role, deduped by job id and seniority-filtered."""
    seen_ids = set()
    out = []
    total = len(config.SEARCH_ROLES)
    for i, role in enumerate(config.SEARCH_ROLES):
        for job in fetch_role(role):
            if not job["id"] or job["id"] in seen_ids:
                continue
            if _excluded_by_title(job["title"]):
                continue
            if _excluded_by_company(job["company"]):
                continue
            seen_ids.add(job["id"])
            out.append(job)
        if progress_cb:
            progress_cb(i + 1, total)
    return out
