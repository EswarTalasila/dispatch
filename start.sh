#!/usr/bin/env bash
# Starts the FastAPI backend and the React frontend together.
# Backend on :8000, frontend on :5173. Ctrl+C stops both.
set -e
cd "$(dirname "$0")"

./venv/bin/uvicorn server:app --port 8000 &
API_PID=$!
trap "kill $API_PID 2>/dev/null" EXIT

cd frontend
npm run dev
