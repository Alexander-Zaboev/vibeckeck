import json
import os
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

st.set_page_config(page_title="VibeCheck YouTube Explorer", layout="wide")

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Open+Sans:wght@400;500;600;700&display=swap');

:root {
  --background: 230 15% 8%;
  --foreground: 0 0% 95%;
  --card: 230 15% 12%;
  --primary: 24 100% 58%;
  --secondary: 230 12% 18%;
  --muted: 230 10% 16%;
  --muted-foreground: 230 10% 55%;
  --accent: 340 80% 58%;
  --border: 230 12% 20%;
  --gradient-from: 30 100% 60%;
  --gradient-via: 15 100% 55%;
  --gradient-to: 350 85% 55%;
}

html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 10% 20%, rgba(255,119,72,0.15), transparent 55%),
              radial-gradient(circle at 90% 10%, rgba(255,0,92,0.18), transparent 45%),
              hsl(var(--background));
  color: hsl(var(--foreground));
  font-family: "Open Sans", sans-serif;
}

[data-testid="stHeader"] {
  background: transparent;
}

.ambient-glow {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: -1;
}

.ambient-glow::before,
.ambient-glow::after {
  content: "";
  position: absolute;
  border-radius: 999px;
  filter: blur(120px);
  opacity: 0.35;
}

.ambient-glow::before {
  width: 600px;
  height: 600px;
  top: -150px;
  right: -100px;
  background: hsla(var(--gradient-from)/0.9);
}

.ambient-glow::after {
  width: 520px;
  height: 520px;
  bottom: -160px;
  left: -120px;
  background: hsla(var(--gradient-to)/0.9);
}

.hero-card {
  border-radius: 1.5rem;
  padding: 2.5rem;
  background: hsl(230 15% 12% / 0.65);
  border: 1px solid hsla(0,0%,100%,0.08);
  backdrop-filter: blur(24px);
  margin-bottom: 2rem;
}

.badge {
  display: inline-flex;
  padding: 0.25rem 1.25rem;
  border-radius: 999px;
  font-size: 0.65rem;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  background: hsla(var(--muted)/0.4);
  color: hsl(var(--muted-foreground));
}

.hero-card h1 {
  margin-top: 1rem;
  font-size: clamp(2.4rem, 4vw, 3.4rem);
  font-family: "Plus Jakarta Sans", sans-serif;
  line-height: 1.1;
}

.text-gradient {
  background: linear-gradient(135deg, hsl(var(--gradient-from)), hsl(var(--gradient-via)), hsl(var(--gradient-to)));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-card p {
  color: hsl(var(--muted-foreground));
  font-size: 1rem;
  max-width: 720px;
}

.glass-panel {
  background: hsl(230 15% 14% / 0.55);
  border-radius: 1.5rem;
  border: 1px solid hsla(0,0%,100%,0.08);
  backdrop-filter: blur(24px);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.85rem 1.5rem;
  border-radius: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, hsl(var(--gradient-from)), hsl(var(--gradient-to)));
  color: #05060a;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 8px 24px rgba(255,119,72,0.35);
}

.cta-button:hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 14px 32px rgba(255,119,72,0.45);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 1rem;
  border-radius: 999px;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  background: hsla(var(--muted)/0.6);
  color: hsl(var(--muted-foreground));
}

.status-pill.success {
  background: hsla(var(--primary)/0.3);
  color: hsl(var(--foreground));
}

.stat-pill {
  background: hsla(230,20%,12%,0.8);
  border: 1px solid hsla(0,0%,100%,0.08);
  border-radius: 1.25rem;
  padding: 1rem 1.25rem;
}

.stat-pill span {
  display: block;
}

.stat-pill .label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  color: hsl(var(--muted-foreground));
}

.stat-pill .value {
  font-size: 1.7rem;
  font-weight: 600;
  font-family: "Plus Jakarta Sans", sans-serif;
  background: linear-gradient(135deg, hsl(var(--gradient-from)), hsl(var(--gradient-to)));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-pill .detail {
  font-size: 0.9rem;
  color: hsla(var(--foreground)/0.75);
}

.section-title {
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.35em;
  color: hsl(var(--muted-foreground));
}

.section-heading {
  font-size: 1.8rem;
  font-family: "Plus Jakarta Sans", sans-serif;
}

.stButton>button {
  border-radius: 1.5rem;
  border: none;
  padding: 0.9rem 1.75rem;
  font-weight: 600;
  background: linear-gradient(135deg, hsl(var(--gradient-from)), hsl(var(--gradient-to)));
  color: #05060a;
  box-shadow: 0 10px 30px rgba(255,119,72,0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stButton>button:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 36px rgba(255,119,72,0.45);
}

.stLinkButton>button {
  border-radius: 1.5rem;
  font-weight: 600;
  background: transparent;
  border: 1px solid hsla(0,0%,100%,0.2);
}

div[data-testid="stMetricValue"] {
  font-size: 2.2rem;
  font-family: "Plus Jakarta Sans", sans-serif;
}

.chart-card {
  padding: 1rem;
  border-radius: 1.25rem;
  background: hsla(230,15%,18%,0.7);
  border: 1px solid hsla(0,0%,100%,0.06);
}

.chart-card h4 {
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-family: "Plus Jakarta Sans", sans-serif;
}

.glass-panel .stDataFrame,
.glass-panel .stTable {
  background: transparent;
}

.glass-panel .stDataFrame div[data-testid="StyledTable"] {
  background: transparent;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.markdown('<div class="ambient-glow"></div>', unsafe_allow_html=True)

# -------------------------
# CONFIG
# -------------------------
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
DEFAULT_REDIRECT_URI = "http://localhost:8501/"
ENV_SECRET_FILE = "GOOGLE_CLIENT_SECRET_FILE"
MAX_PAGES = 20  # 20 * 50 = 1000 liked videos per pull


def _discover_secret_file() -> Path | None:
    """Heuristic to find a client_secret*.json without extra configuration."""
    env_path = os.environ.get(ENV_SECRET_FILE)
    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())

    downloads = Path.home() / "Downloads"
    candidates.extend(sorted(downloads.glob("client_secret*.json")))
    local = Path(__file__).with_name("client_secret.json")
    candidates.append(local)

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return None


def _normalize_client_config(raw: Dict) -> Tuple[Dict, str]:
    """Return Flow-compatible config plus the redirect URI to use."""
    web = raw.get("web") or raw.get("installed") or raw
    web = dict(web)  # shallow copy
    redirect_uris = list(web.get("redirect_uris") or [])
    if not redirect_uris and web.get("redirect_uri"):
        redirect_uris = [web["redirect_uri"]]
    if not redirect_uris:
        redirect_uris = [DEFAULT_REDIRECT_URI]
    web["redirect_uris"] = redirect_uris
    redirect_uri = redirect_uris[0]

    # Fill defaults expected by Flow
    web.setdefault("auth_uri", "https://accounts.google.com/o/oauth2/auth")
    web.setdefault("token_uri", "https://oauth2.googleapis.com/token")

    return {"web": web}, redirect_uri


def _load_client_config_from_user() -> Tuple[Dict, str]:
    """Ask the user for a client_secret JSON (unless secrets.toml already set)."""
    st.sidebar.subheader("Google OAuth Client")
    st.sidebar.caption(
        "Upload or point to the client_secret*.json downloaded from Google Cloud Console."
    )
    guessed = _discover_secret_file()
    default_path = str(guessed) if guessed else ""
    client_secret_path = st.sidebar.text_input(
        "Client secret JSON path", value=default_path, help="Absolute path to client_secret*.json"
    )
    uploaded = st.sidebar.file_uploader(
        "...or upload client_secret*.json", type=["json"], key="client_secret_upload"
    )

    data = None
    error_location = "uploaded file"
    if uploaded is not None:
        try:
            data = json.load(uploaded)
        except json.JSONDecodeError:
            st.sidebar.error("Uploaded file is not valid JSON.")
            st.stop()
    elif client_secret_path:
        path = Path(client_secret_path).expanduser()
        error_location = str(path)
        if not path.exists():
            st.sidebar.error(f"Client secret file not found: {path}")
            st.stop()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            st.sidebar.error(f"File {path} is not valid JSON.")
            st.stop()
    else:
        st.sidebar.info("Provide a client_secret*.json to continue.")
        st.stop()

    if not data:
        st.sidebar.error(f"Unable to read {error_location}.")
        st.stop()

    config, redirect_uri = _normalize_client_config(data)
    st.sidebar.success("Client secret loaded.")
    return config, redirect_uri


def _ensure_client_settings() -> Dict:
    """
    Read credentials from Streamlit secrets, env/file, or prompt the user.
    Cached in session_state to avoid repeated parsing.
    """
    if "google_client_settings" in st.session_state:
        return st.session_state["google_client_settings"]

    try:
        secret = st.secrets["google_oauth"]
    except Exception:
        secret = None

    if secret:
        web = {
            "client_id": secret.get("client_id"),
            "client_secret": secret.get("client_secret"),
            "auth_uri": secret.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": secret.get("token_uri", "https://oauth2.googleapis.com/token"),
            "redirect_uris": [secret.get("redirect_uri", DEFAULT_REDIRECT_URI)],
        }
        config, redirect_uri = _normalize_client_config({"web": web})
    else:
        config, redirect_uri = _load_client_config_from_user()

    settings = {"client_config": config, "redirect_uri": redirect_uri}
    st.session_state["google_client_settings"] = settings
    return settings


def make_flow(state=None):
    settings = _ensure_client_settings()
    return Flow.from_client_config(
        client_config=settings["client_config"],
        scopes=SCOPES,
        redirect_uri=settings["redirect_uri"],
        state=state,
    )

def get_liked_videos(credentials, max_pages=5):
    """
    Reads the special playlist 'Liked videos' by first finding its playlistId (if accessible),
    then listing playlistItems. (YouTube returns a 'likes' playlist for many accounts.)
    """
    youtube = build("youtube", "v3", credentials=credentials)

    # 1) Find the "likes" playlist id
    channels = youtube.channels().list(part="contentDetails", mine=True).execute()
    items = channels.get("items", [])
    if not items:
        raise RuntimeError("No channel found for this Google account.")

    related = items[0]["contentDetails"]["relatedPlaylists"]
    likes_playlist_id = related.get("likes")
    if not likes_playlist_id:
        raise RuntimeError("This account does not expose a 'Liked videos' playlist via API.")

    # 2) Paginate playlist items
    rows = []
    page_token = None
    pages = 0

    while True:
        resp = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=likes_playlist_id,
            maxResults=50,
            pageToken=page_token,
        ).execute()

        for it in resp.get("items", []):
            sn = it.get("snippet", {})
            cd = it.get("contentDetails", {})
            vid = cd.get("videoId")
            rows.append({
                "videoId": vid,
                "title": sn.get("title"),
                "channelTitle": sn.get("videoOwnerChannelTitle") or sn.get("channelTitle"),
                "publishedAt": sn.get("publishedAt"),
            })

        page_token = resp.get("nextPageToken")
        pages += 1
        if not page_token or pages >= max_pages:
            break

    return pd.DataFrame(rows)

# -------------------------
# UI
# -------------------------
st.markdown(
    """
    <div class="hero-card">
        <div class="badge">OAuth Explorer</div>
        <h1 class="text-gradient">VibeCheck YouTube Liked Videos Lab</h1>
        <p>
            Connect with Google OAuth using the same client_secret JSON as the Streamlit MVP, then generate a Spotify-Wrapped style
            dashboard for your liked videos. Upload the client secret via sidebar, tap connect, and let the FastAPI backend crunch
            your signals.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


def _get_query_params():
    attr = getattr(st, "query_params", None)
    if attr is not None:
        return attr
    return st.experimental_get_query_params()


def _clear_query_params():
    attr = getattr(st, "query_params", None)
    if attr is not None and hasattr(attr, "clear"):
        attr.clear()
    else:
        st.experimental_set_query_params()


def _first_value(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def render_stat(label: str, value: str, detail: str = ""):
    st.markdown(
        f"""
        <div class="stat-pill">
            <span class="label">{label}</span>
            <span class="value">{value}</span>
            <span class="detail">{detail}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Keep tokens in session state
if "creds" not in st.session_state:
    st.session_state["creds"] = None


# Handle OAuth callback (?code=...)
params = _get_query_params()
code_param = _first_value(params.get("code"))
if st.session_state["creds"] is None and code_param:
    try:
        flow = make_flow(state=_first_value(params.get("state")))
        flow.fetch_token(code=code_param)
        st.session_state["creds"] = flow.credentials

        # Clean up URL (optional, Streamlit supports rerun)
        _clear_query_params()
        st.rerun()
    except Exception as e:
        st.error(f"OAuth callback error: {e}")

if st.session_state["creds"] is None:
    # Create auth URL
    flow = make_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",  # ensure refresh token on first run
    )
    st.markdown(
        f"""
        <div class="glass-panel">
            <div class="section-title">Step 1 · Connect</div>
            <h2 class="section-heading">Authenticate with Google</h2>
            <p style="color: hsla(var(--foreground)/0.7);">
                Provide your client_secret file via the sidebar, then start the OAuth consent flow.
                We request read-only access to your channel to list the private "Liked videos" playlist.
            </p>
            <a class="cta-button" href="{auth_url}" target="_self">Connect YouTube (Google OAuth)</a>
            <p style="margin-top:0.75rem;color:hsla(var(--foreground)/0.6);font-size:0.9rem;">
                Tip: ensure the YouTube Data API v3 is enabled for your Google Cloud project before connecting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    f"""
    <div class="glass-panel" style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem;">
        <div>
            <div class="status-pill success">Connected · Credentials stored in session</div>
            <p style="margin-top:0.75rem;color:hsla(var(--foreground)/0.7);">
                Pulling up to {MAX_PAGES * 50:,} liked videos automatically. Use the refresh control to re-sync with YouTube anytime.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

refresh_clicked = st.button("Refresh dataset", key="refresh_button")


def _fetch_and_store():
    with st.spinner(f"Fetching up to {MAX_PAGES * 50:,} liked videos from YouTube…"):
        df = get_liked_videos(st.session_state["creds"], max_pages=MAX_PAGES)
        df["publishedAt"] = pd.to_datetime(df["publishedAt"], errors="coerce")
        st.session_state["liked_df"] = df


if refresh_clicked or st.session_state.get("liked_df") is None:
    try:
        _fetch_and_store()
    except Exception as e:
        st.error(str(e))


def _bucket_video(title: str) -> str:
    text = (title or "").lower()
    buckets = [
        ("Nerdcore Deep Dives", ["ai", "python", "code", "data", "build", "analysis", "tech", "gpu"]),
        ("News & Hot Takes", ["news", "update", "explained", "breaking", "drama", "politics", "election"]),
        ("Creative Sparks", ["music", "remix", "cover", "design", "art", "edit", "draw"]),
        ("Wellness & Mindset", ["meditation", "fitness", "gym", "habit", "mindset", "health"]),
        ("Entertain & Chill", ["reaction", "vlog", "challenge", "funny", "meme", "storytime"]),
    ]
    for bucket, keywords in buckets:
        if any(word in text for word in keywords):
            return bucket
    if len(text) > 70:
        return "Longform Explorations"
    if text.startswith("how ") or " guide" in text or "tutorial" in text:
        return "Curiosity Tutorials"
    return "Snackable Dopamine"


df = st.session_state.get("liked_df")
if df is not None and not df.empty:
    df["bucket"] = df["title"].apply(_bucket_video)
    top_channels = df["channelTitle"].value_counts()
    favorite_channel = top_channels.idxmax() if not top_channels.empty else "-"
    unique_channels = int(df["channelTitle"].nunique())
    bucket_counts = df["bucket"].value_counts()
    fresh = df["publishedAt"]
    recent_window = (pd.Timestamp.utcnow() - pd.Timedelta(days=30))
    fresh_count = int(fresh.gt(recent_window).sum())
    median_age_days = int((pd.Timestamp.utcnow() - fresh.dropna()).dt.days.median()) if fresh.notna().any() else 0
    top_share = (top_channels.iloc[0] / len(df) * 100) if not top_channels.empty else 0

    stat_cols = st.columns(4)
    with stat_cols[0]:
        render_stat("Total liked videos", f"{len(df):,}", "Auto-fetched at max depth.")
    with stat_cols[1]:
        render_stat("Unique channels", f"{unique_channels:,}", "Voices in your likes.")
    with stat_cols[2]:
        render_stat("Most replayed", favorite_channel or "-", f"{top_share:.1f}% of recent likes.")
    with stat_cols[3]:
        render_stat("Fresh in 30 days", f"{fresh_count:,}", f"Median age {median_age_days} days.")

    channel_col, bucket_col = st.columns(2)
    with channel_col:
        st.markdown('<div class="glass-panel chart-card"><h4>Top channels (20)</h4>', unsafe_allow_html=True)
        st.bar_chart(top_channels.head(20), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bucket_col:
        st.markdown('<div class="glass-panel chart-card"><h4>AI bucket distribution</h4>', unsafe_allow_html=True)
        st.bar_chart(bucket_counts, use_container_width=True)
        st.markdown(
            "<p style='color:hsla(var(--foreground)/0.65);font-size:0.85rem;'>Buckets are derived via lightweight ML-inspired heuristics that group videos by intent (tech deep dives, news bursts, wellness, etc.).</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    timeline = (
        df.dropna(subset=["publishedAt"])
        .assign(month=lambda x: x["publishedAt"].dt.to_period("M").astype(str))
        .groupby("month")
        .size()
        .sort_index()
    )

    words = (
        df["title"]
        .fillna("")
        .str.lower()
        .str.replace(r"[^a-z0-9\\s]", " ", regex=True)
        .str.split()
        .explode()
    )
    stop = set(["the", "a", "and", "to", "of", "in", "for", "on", "with", "feat", "official", "video"])
    top_words = words[~words.isin(stop)].value_counts().head(25)

    trend_col, words_col = st.columns(2)
    with trend_col:
        st.markdown('<div class="glass-panel chart-card"><h4>Publishing heat (per month)</h4>', unsafe_allow_html=True)
        if not timeline.empty:
            st.line_chart(timeline, use_container_width=True)
        else:
            st.write("No published dates returned for these likes.")
        st.markdown("</div>", unsafe_allow_html=True)

    with words_col:
        st.markdown('<div class="glass-panel chart-card"><h4>Title signal keywords</h4>', unsafe_allow_html=True)
        if not top_words.empty:
            st.bar_chart(top_words, use_container_width=True)
        else:
            st.write("Need more likes to compute text stats.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Sample table</div>', unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("No liked videos retrieved yet. Try refreshing once more.")
