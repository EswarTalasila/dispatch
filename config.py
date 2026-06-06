"""Tweak these to change what gets searched and how strict filtering is."""

# Roles to search for. Each becomes a separate Adzuna query.
SEARCH_ROLES = [
    "AI Engineer",
    "Machine Learning Engineer",
    "LLM Engineer",
    "Software Engineer",
    "Software Developer",
    "Backend Engineer",
    "Full Stack Developer",
    "Python Developer",
    "Data Engineer",
    "Generative AI Engineer",
]

# Country code for Adzuna (us, gb, etc.) and an optional hard location filter.
# Leave LOCATION empty so we search the whole country, then rank by preference.
COUNTRY = "us"
LOCATION = ""

# Adzuna returns up to 50 results per page. Pull this many pages per role.
RESULTS_PER_PAGE = 50
PAGES_PER_ROLE = 2

# Location preference tiers. Jobs matching tier 1 sort first, then tier 2,
# then everywhere else. Matching is a simple case-insensitive substring check.
LOCATION_TIERS = [
    ["north carolina", "nc", "raleigh", "charlotte", "durham", "cary", "research triangle"],
    ["texas", "tx", "austin", "dallas", "houston", "san antonio", "fort worth"],
]

# Drop any listing whose title contains one of these words before it ever
# reaches Claude. Cheap, deterministic seniority filter.
EXCLUDE_TITLE_KEYWORDS = [
    "senior", "sr.", "sr ", "staff", "principal", "lead", "architect",
    "manager", "director", "head of", "vp", "iii", "iv",
]

# Skip listings from these companies entirely (case-insensitive substring).
# SynergisticIT is a known resume-harvesting staffing firm.
EXCLUDE_COMPANIES = [
    "synergisticit",
]

# Only keep jobs Claude scores at or above this (0-100).
MIN_SCORE = 55

# Claude model used for ranking. Haiku is cheap and good enough here.
MODEL = "claude-haiku-4-5-20251001"
