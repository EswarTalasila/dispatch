"""Writes matched jobs as rows in a Notion database.

Your Notion database must have these properties (column names matter):
  Title      -> type: Title
  Company    -> type: Text
  Location   -> type: Text
  Score      -> type: Number
  Priority   -> type: Number   (location-weighted sort key; sort view by this)
  Why        -> type: Text
  Role       -> type: Text
  Link       -> type: URL
"""

import os
import requests

NOTION_VERSION = "2022-06-28"


def add_job(job):
    token = os.environ["NOTION_TOKEN"]
    db_id = os.environ["NOTION_DATABASE_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Title": {"title": [{"text": {"content": f"[{job['score']}] {job['title']}"[:200]}}]},
            "Company": {"rich_text": [{"text": {"content": job["company"][:200]}}]},
            "Location": {"rich_text": [{"text": {"content": job["location"][:200]}}]},
            "Score": {"number": job["score"]},
            "Priority": {"number": job.get("priority", job["score"])},
            "Why": {"rich_text": [{"text": {"content": job["reason"][:500]}}]},
            "Role": {"rich_text": [{"text": {"content": job["role_query"][:100]}}]},
            "Link": {"url": job["url"] or None},
        },
    }
    resp = requests.post(
        "https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=30
    )
    resp.raise_for_status()


def add_jobs(jobs):
    for job in jobs:
        add_job(job)
