# Dispatch

A personal job board that finds roles worth your time. Dispatch pulls fresh
listings, has Claude score each one against your résumé and preferences, and
serves the good matches in a clean web app — sorted by fit and location, split
into New / This week / All.

It's a manual, on-demand tool: hit **Fetch new jobs** whenever you want a fresh
batch. No spam, no senior roles you don't qualify for, no listings you've
already seen.

## How it works

```
Adzuna API ─► filters (seniority, company, dedupe) ─► Claude scores fit
   ─► SQLite (+ optional Notion) ─► FastAPI ─► React web app
```

1. **Fetch** — queries Adzuna for your configured roles across the US.
2. **Filter** — drops senior/staff/lead titles, blocklisted companies, and
   anything already seen.
3. **Score** — Claude rates each job 0-100 on how well it fits *and* whether you
   realistically qualify, with a one-line reason. Your résumé is sent as a cached
   prompt so repeat runs stay cheap.
4. **Rank** — sorts by score plus a location bonus (configurable tiers).
5. **Browse** — the React app shows matches with live filters and freshness tabs.

## Stack

- **Backend / pipeline:** Python, FastAPI, SQLite, Anthropic Claude
- **Frontend:** React, Vite, Tailwind CSS, Framer Motion
- **Source:** Adzuna jobs API · optional Notion mirror
- **Tooling:** Docker Compose, [Task](https://taskfile.dev)

## Getting started

### Prerequisites
- Docker Desktop
- [Task](https://taskfile.dev) (`brew install go-task`)
- An [Adzuna API](https://developer.adzuna.com) key (free) and an
  [Anthropic API](https://console.anthropic.com) key. Notion is optional.

### Setup
```bash
git clone https://github.com/EswarTalasila/dispatch.git
cd dispatch

cp .env.example .env                       # add your API keys
cp resume.example.txt resume.txt           # paste your résumé
cp preferences.example.txt preferences.txt # describe what you want
```
Edit `config.py` to set the roles, locations, and filters you care about.

Instead of editing `resume.txt` by hand, you can drag a PDF or DOCX résumé into
the app once it's running — Claude extracts and structures it for you. Uploading
a new résumé automatically re-scores your existing jobs against it, so the
rankings update right away (no re-fetch needed).

### Run
```bash
task up        # build + start; web on :5173, api on :8000
```
Open http://localhost:5173 and click **Fetch new jobs**.

### Commands
```bash
task           # list everything
task up        # start the app
task down      # stop
task fetch     # run the pipeline once from the CLI
task logs      # tail logs
task clean     # stop and wipe the data volume
```
`resume.txt`, `preferences.txt`, and `config.py` are mounted into the container,
so edits take effect without a rebuild. Data persists in a Docker volume.

## Run without Docker
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys
python main.py         # run the pipeline
./start.sh             # serve the web app (api + frontend)
```
There's also a Streamlit view: `streamlit run app.py`.

## Optional: Notion
Set `NOTION_TOKEN` and `NOTION_DATABASE_ID` in `.env` to also mirror matches to a
Notion database (columns: Title, Company, Location, Score, Priority, Why, Role,
Link). Leave them blank to skip Notion entirely.

## License
MIT
