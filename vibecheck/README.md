# VibeCheck UI

Apple-inspired Wrapped + dashboard built with React 18, TypeScript, Vite, Tailwind, Framer Motion, and Recharts. This front end now reads real metrics from the FastAPI backend defined in `Snippet.py`, matching the same Reddit + YouTube ingestion pipeline the Streamlit MVP uses.

## Getting Started

1. **Backend**
   - Install backend deps from `Snippet.py` instructions: `pip install fastapi uvicorn pandas requests streamlit`.
   - Run the API: `uvicorn Snippet:app --reload` (or use your preferred host). Keep it accessible at `http://127.0.0.1:8000` or set `VITE_API_BASE` accordingly.
   - For YouTube data, upload the subscriptions export (JSON/CSV) inside the UI; FastAPI will synthesize signals via `ingest_youtube_sources`.

2. **Frontend**
   ```bash
   cd vibecheck
   npm install
   npm run dev
   ```
   Optionally set `VITE_API_BASE` in a `.env` file if the backend runs elsewhere.

3. **Workflow**
   - Visit `/` and provide a `user_id`, Reddit username (optional), and/or YouTube export; this triggers POST `/ingest` and GET `/profile/{user_id}`.
   - Wrapped + Dashboard pages visualize the returned `compute_metrics` payload.
   - `/youtube-explorer` filters `evidence` down to YouTube-only items and can refresh by calling `/profile` again.

## Project Highlights
- Glassmorphism aesthetic with semantic color tokens + ambient glows from the original brief.
- Tap-to-advance Wrapped slideshow sourced from FastAPI metrics instead of placeholder data.
- Dashboard showing topic/tone mixes, lift, and evidence tables computed server-side.
- Explorer page aligned with the Streamlit OAuth flow (YouTube export → FastAPI ingest).
