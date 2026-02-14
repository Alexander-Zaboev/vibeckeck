# ========================= dashboard.py (Streamlit UI) =========================
"""
streamlit run dashboard.py
"""


def run_dashboard(api_url: str = "http://127.0.0.1:8000") -> None:
    import csv
    import io
    import json

    import pandas as pd
    import requests
    import streamlit as st

    st.title("Your Algorithm Profile (Reddit + YouTube)")

    user_id = st.text_input("User ID", value="demo_user")
    reddit_username = st.text_input("Reddit username (public)", value="")
    yt_file = st.file_uploader(
        "YouTube subscriptions export (JSON or CSV) -- hackathon shortcut", type=["json", "csv"]
    )

    def _load_youtube_sources(uploaded):
        name = (uploaded.name or "").lower()
        raw = uploaded.read()
        uploaded.seek(0)
        if not raw:
            raise ValueError("YouTube file is empty.")

        is_csv = name.endswith(".csv") or uploaded.type == "text/csv"
        text = raw.decode("utf-8-sig")

        if is_csv:
            reader = csv.DictReader(io.StringIO(text))
            title_keys = ["channelTitle", "channel title", "Title", "Channel Title"]
            id_keys = ["channelId", "channel id", "Channel Id", "Channel ID", "Id", "ID"]
            parsed = []
            for row in reader:
                title = next((row.get(k) for k in title_keys if row.get(k)), "").strip()
                cid = next((row.get(k) for k in id_keys if row.get(k)), "").strip() or None
                if not title:
                    continue
                parsed.append({"channelTitle": title, "channelId": cid})
            if not parsed:
                raise ValueError(
                    "CSV must include headers such as channelTitle/channelId with at least one populated row."
                )
            return parsed

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Could not parse JSON: invalid format.") from exc
        if not isinstance(data, list):
            raise ValueError("YouTube file must be a JSON list of objects.")
        return data

    youtube_sources = None
    if yt_file:
        try:
            youtube_sources = _load_youtube_sources(yt_file)
        except ValueError as e:
            st.error(str(e))
            youtube_sources = None
        except Exception as e:
            st.error(f"Could not parse file: {e}")
            youtube_sources = None

    if st.button("Generate Profile"):
        payload = {
            "user_id": user_id,
            "reddit_username": reddit_username or None,
            "youtube_sources": youtube_sources,
            "max_reddit_items": 80,
        }
        r = requests.post(f"{api_url}/ingest", json=payload, timeout=60)
        if r.status_code != 200:
            st.error(r.text)
        else:
            st.success("Ingested. Loading profile...")
            prof = requests.get(f"{api_url}/profile/{user_id}", timeout=60).json()

            st.subheader("Summary")
            st.write(prof.get("counts", {}))
            div = prof.get("diversity", {})
            st.metric("Topic entropy (diversity)", round(div.get("topic_entropy", 0.0), 3))
            st.metric("Top-5 source concentration", f"{div.get('top5_source_share', 0.0)*100:.1f}%")

            st.subheader("Topic Mix")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Raw share")
                st.bar_chart(pd.Series(prof.get("topic_raw", {})))
            with col2:
                st.caption("Engagement-weighted share")
                st.bar_chart(pd.Series(prof.get("topic_weighted", {})))

            st.subheader("Tone Mix")
            col3, col4 = st.columns(2)
            with col3:
                st.caption("Raw share")
                st.bar_chart(pd.Series(prof.get("tone_raw", {})))
            with col4:
                st.caption("Engagement-weighted share")
                st.bar_chart(pd.Series(prof.get("tone_weighted", {})))

            st.subheader("Reinforcement (Lift = weighted - raw)")
            st.bar_chart(pd.Series(prof.get("lift", {})))

            st.subheader("Evidence")
            ev = prof.get("evidence", {})
            st.caption("Most reinforced (high engagement + reinforced topics)")
            st.dataframe(pd.DataFrame(ev.get("most_reinforced", [])))

            st.caption("Most intense (controversy/clickbait)")
            st.dataframe(pd.DataFrame(ev.get("most_intense", [])))


if __name__ == "__main__":
    run_dashboard()
