"""Remembers which jobs we've already sent so you don't get repeats."""

import json
import os

SEEN_FILE = os.environ.get(
    "SEEN_FILE", os.path.join(os.path.dirname(__file__), "seen.json")
)


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE) as f:
        return set(json.load(f))


def save_seen(ids):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(ids), f)


def filter_new(jobs, seen):
    return [j for j in jobs if j["id"] not in seen]
