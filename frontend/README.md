# CampusPulse frontend

The responsive dashboard is a dependency-free browser app. It contains student, event manager, and authority views based on the designs in `design/`.

## Run locally

From the repository root, install `requirements.txt` and run `python app.py`. Open `http://127.0.0.1:5000`. Flask serves this frontend and its `/api/*` routes from the same origin.

To host the frontend separately, serve this folder with `python -m http.server 8080 --directory frontend` and open `http://127.0.0.1:8080`. The API defaults to the page's origin; set `?api=http://your-api-host` when the backend is hosted elsewhere.

## Deploy to Vercel

Create a Vercel project from the repository and leave the Root Directory set to the repository root. The root Flask entry point, Python dependencies, and Vercel configuration route requests to the backend; the build step copies `frontend/index.html`, `frontend/styles.css`, and `frontend/app.js` into `public/` for CDN delivery.

In the Vercel project settings, add `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` under Environment Variables for Preview and Production. Use the Supabase publishable key expected by the backend; do not use a secret/service-role key in the frontend. Deploy from the Vercel dashboard or CLI. The app and `/api/*` endpoints then share one Vercel origin.

Enter a UUID for an existing row in the backend `users` table to load that user's registrations or register for an event. The API currently supports event listing, event details, registration creation, a user's registrations, and event attendee lists. Event creation/editing, authentication, check-in, approvals, venue schedules, and budget data are not implemented by the backend, so the matching dashboard sections are identified as unavailable rather than filled with mock data.
