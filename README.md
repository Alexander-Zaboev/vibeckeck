# VibeCheck Streamlit + FastAPI

Two-part project: a FastAPI backend (`backend/`) that ingests Reddit/YouTube signals and a Streamlit experience (`streamlit/`) that focuses on YouTube OAuth liked-video analytics with the VibeCheck design.

## Repository layout
- `backend/app.py` – FastAPI app exposing `/ingest` + `/profile` endpoints
- `backend/requirements.txt` – backend deps
- `streamlit/app.py` – YouTube-only Streamlit UI (Streamlit Cloud ready)
- `streamlit/dashboard.py` – optional Streamlit dashboard that talks to FastAPI
- `streamlit/requirements.txt` – Streamlit deps for `pip install -r`
- `secrets/` – instructions + example secrets template for OAuth credentials

## Running locally
```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```
Then in another shell:
```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```
Provide the Google OAuth `client_secret*.json` via sidebar or by setting `GOOGLE_CLIENT_SECRET_FILE`/`.streamlit/secrets.toml`.

## Deploying to Streamlit Cloud
1. Create a new GitHub repo with this layout and push it.
2. In Streamlit Cloud, point the app to `streamlit/app.py` and set secrets (copy from `secrets/secrets.example.toml`).
3. Update your Google Cloud OAuth client so `https://<your-app>.streamlit.app/` is an authorized redirect URI (keep `http://localhost:8501/` for dev).
4. Ensure the YouTube Data API v3 is enabled for that project.

## Deploying the backend
Host `backend/app.py` anywhere that can run FastAPI (Railway, Render, Fly.io, etc.). Set `API_BASE` env var in Streamlit Cloud if you serve it somewhere other than `http://127.0.0.1:8000`.

Happy building!
