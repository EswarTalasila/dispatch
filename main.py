"""Pipeline: fetch -> dedupe -> score with Claude -> store (SQLite + optional Notion)."""

import os
import re

from dotenv import load_dotenv

import config
import sources
import storage
import filter as job_filter
import notion_sink
import db
import progress

load_dotenv()


def location_rank(location):
    """Lower rank = higher priority. Tier 0, then 1, then everything else.

    Matches whole words only so "nc" doesn't match inside "Cincinnati".
    """
    low = (location or "").lower()
    for tier, keywords in enumerate(config.LOCATION_TIERS):
        if any(re.search(rf"\b{re.escape(kw)}\b", low) for kw in keywords):
            return tier
    return len(config.LOCATION_TIERS)


def main():
    seen = storage.load_seen()

    progress.update(stage="Searching Adzuna…", percent=5)
    all_jobs = sources.fetch_all(
        progress_cb=lambda done, total: progress.update(
            stage=f"Searching Adzuna… ({done}/{total} roles)",
            percent=5 + int(done / total * 6),
        )
    )
    print(f"Fetched {len(all_jobs)} listings.")

    new_jobs = storage.filter_new(all_jobs, seen)
    print(f"{len(new_jobs)} are new since last run.")
    if not new_jobs:
        progress.update(stage="No new listings", percent=90)
        return

    progress.update(stage=f"Scoring {len(new_jobs)} new jobs…", percent=12)
    scored = job_filter.score_jobs(
        new_jobs,
        progress_cb=lambda done, total: progress.update(
            stage=f"Scoring with Claude… ({done}/{total})",
            percent=12 + int(done / total * 78),
        ),
    )
    matches = [j for j in scored if j["score"] >= config.MIN_SCORE]
    # Priority = match score plus a location bonus so NC, then TX, then
    # everywhere else sort to the top. Used as the Notion sort key.
    for j in matches:
        bonus = (len(config.LOCATION_TIERS) - location_rank(j["location"])) * 1000
        j["priority"] = j["score"] + bonus
    matches.sort(key=lambda j: -j["priority"])
    print(f"{len(matches)} jobs scored >= {config.MIN_SCORE}.")

    if matches:
        progress.update(stage="Saving matches…", percent=95)
        db.save(matches)
        if os.environ.get("NOTION_TOKEN") and os.environ.get("NOTION_DATABASE_ID"):
            notion_sink.add_jobs(matches)
            print(f"Added {len(matches)} jobs to local DB and Notion.")
        else:
            print(f"Added {len(matches)} jobs to local DB.")

    # Mark everything we fetched as seen, even low scorers, so we don't
    # re-score them tomorrow.
    seen.update(j["id"] for j in all_jobs)
    storage.save_seen(seen)


if __name__ == "__main__":
    main()
