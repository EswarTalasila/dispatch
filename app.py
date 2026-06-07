"""Streamlit frontend for browsing matched jobs. Run: streamlit run app.py"""

import streamlit as st

import db

st.set_page_config(page_title="Job Finder", page_icon="briefcase", layout="wide")

jobs = db.load()

st.title("Job Finder")
if not jobs:
    st.info("No jobs yet. Run `python main.py` to fetch and score some.")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("Filters")

query = st.sidebar.text_input("Search (title / company)").lower()

scores = [j["score"] for j in jobs]
min_score = st.sidebar.slider(
    "Minimum score", min_value=int(min(scores)), max_value=int(max(scores)),
    value=int(min(scores)),
)

roles = sorted({j["role_query"] for j in jobs})
picked_roles = st.sidebar.multiselect("Role search", roles, default=roles)

dates = sorted({j["found_date"] for j in jobs}, reverse=True)
picked_dates = st.sidebar.multiselect("Date found", dates, default=dates)

sort_by = st.sidebar.radio("Sort by", ["Priority (location + score)", "Score"])

# --- Apply filters ---
def keep(j):
    if j["score"] < min_score:
        return False
    if j["role_query"] not in picked_roles:
        return False
    if j["found_date"] not in picked_dates:
        return False
    if query and query not in (j["title"] + " " + j["company"]).lower():
        return False
    return True

filtered = [j for j in jobs if keep(j)]
key = "priority" if sort_by.startswith("Priority") else "score"
filtered.sort(key=lambda j: j[key], reverse=True)

st.caption(f"Showing {len(filtered)} of {len(jobs)} jobs")

# --- Render ---
for j in filtered:
    score = int(j["score"])
    if score >= 75:
        color = "#16a34a"
    elif score >= 60:
        color = "#ca8a04"
    else:
        color = "#9ca3af"
    left, right = st.columns([0.08, 0.92])
    with left:
        st.markdown(
            f"<div style='background:{color};color:white;border-radius:8px;"
            f"padding:10px 0;text-align:center;font-size:22px;font-weight:700'>"
            f"{score}</div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(f"**{j['title']}**")
        st.caption(f"{j['company']} - {j['location']} - found {j['found_date']}")
        st.write(j["reason"])
        if j["url"]:
            st.markdown(f"[Apply / view posting]({j['url']})")
    st.divider()
