"""Scores each job against your resume + preferences using Claude.

Jobs are scored in batches to amortize the system prompt across many listings.
(A cache_control block is set on the resume/preferences, but note it only takes
effect once that prefix exceeds the model's caching minimum.)
"""

import json
import os

from anthropic import Anthropic

import config

BATCH_SIZE = config.SCORE_BATCH_SIZE  # jobs per Claude call

SYSTEM_INSTRUCTIONS = """You are a job-matching assistant. Given a candidate's \
resume and preferences, score how well each job fits and how realistic the \
candidate's chances are.

Score 0-100:
- 85-100: strong fit, clearly within reach
- 65-84: good fit, realistic shot
- 40-64: partial fit or a stretch
- 0-39: poor fit or out of reach (e.g. needs far more experience)

Weigh BOTH relevance to their background AND whether they realistically \
qualify. Be STRICT about seniority: if a role is senior/staff/principal/lead/\
architect/manager level, or requires more years than the candidate has, cap \
the score at 35 NO MATTER how well the topic matches. Do not call such roles \
a "stretch" and round up. Only score 65+ when the candidate clearly qualifies \
on experience level, not just topic.

Return ONLY a JSON array, one object per job, in the same order. Keep each \
reason to one short sentence under 20 words:
[{"index": 0, "score": 87, "reason": "short reason"}]"""


def _read(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as f:
        return f.read().strip()


def score_jobs(jobs, progress_cb=None, cancel_check=None):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resume = _read("resume.txt")
    preferences = _read("preferences.txt")
    total_batches = (len(jobs) + BATCH_SIZE - 1) // BATCH_SIZE

    system = [
        {"type": "text", "text": SYSTEM_INSTRUCTIONS},
        {
            "type": "text",
            "text": f"CANDIDATE RESUME:\n{resume}\n\nCANDIDATE PREFERENCES:\n{preferences}",
            "cache_control": {"type": "ephemeral"},
        },
    ]

    scored = []
    usage = {"input": 0, "output": 0, "cache_read": 0}
    for start in range(0, len(jobs), BATCH_SIZE):
        if cancel_check:
            cancel_check()
        batch = jobs[start:start + BATCH_SIZE]
        listing_text = "\n\n".join(
            f"[{i}] {j['title']} at {j['company']} ({j['location']})\n"
            f"{j['description'][:1500]}"
            for i, j in enumerate(batch)
        )
        msg = client.messages.create(
            model=config.MODEL,
            max_tokens=4096,
            system=system,
            messages=[{
                "role": "user",
                "content": f"Score these {len(batch)} jobs:\n\n{listing_text}",
            }],
        )
        usage["input"] += msg.usage.input_tokens
        usage["output"] += msg.usage.output_tokens
        usage["cache_read"] += getattr(msg.usage, "cache_read_input_tokens", 0) or 0
        try:
            results = _parse(msg.content[0].text)
        except (json.JSONDecodeError, IndexError) as e:
            print(f"  skipped a batch of {len(batch)} (parse error: {e})")
            continue
        for r in results:
            idx = r.get("index")
            if idx is None or idx >= len(batch):
                continue
            job = dict(batch[idx])
            job["score"] = r.get("score", 0)
            job["reason"] = r.get("reason", "")
            scored.append(job)

        if progress_cb:
            progress_cb(start // BATCH_SIZE + 1, total_batches)

    print(
        f"  tokens: {usage['input']} in / {usage['output']} out"
        f" / {usage['cache_read']} cache-read across {total_batches} batches"
    )
    return scored


def _parse(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
