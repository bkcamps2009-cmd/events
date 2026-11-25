# CampusPulse

CampusPulse serves the browser frontend and Flask API from one app. The `frontend/` folder is the source for the student, event manager, and authority dashboards; the API reads and writes Supabase data.

## Run locally

1. Install the packages in `requirements.txt`.
2. Set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `.env` (see `.env.example`).
3. Run `python app.py` and open `http://127.0.0.1:5000`.

## Deploy to Render

This repository's Render Blueprint is in `render.yaml`. In Render, create a new Blueprint from the repository root. It creates a Flask/Gunicorn backend and a static frontend. Set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` for the backend when prompted. The frontend build uses `API_BASE_URL` to connect to the backend; it defaults to `https://campuspulse-backend.onrender.com`, so update it in the frontend service's Environment settings if Render assigns your backend a different URL, then redeploy the frontend. The backend's `/healthz` endpoint is used for deploy health checks.

## Deploy to Vercel

Import this repository into Vercel with the repository root as the project root. Add `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` to the Vercel project's Preview and Production environment variables. Vercel uses the root Flask application and runs the build step in `pyproject.toml`, which copies the browser assets into `public/` for CDN delivery.

The API currently supports event listing and details, registration creation, a user's registrations, and event attendee lists. It does not provide authentication, event creation/editing, check-in, approvals, budgets, or venue schedules; those dashboard areas are marked accordingly.
