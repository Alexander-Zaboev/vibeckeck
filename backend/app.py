"""FastAPI backend for VibeCheck algorithm profile."""
from typing import Any, Dict, List, Optional
import math
import time

import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AlgoProfile API")

DB: Dict[str, Dict[str, Any]] = {}


class IngestReq(BaseModel):
    user_id: str
    reddit_username: Optional[str] = None
    youtube_sources: Optional[List[Dict[str, Any]]] = None
    max_reddit_items: int = 80


def fetch_reddit_public(username: str, limit: int = 80) -> List[Dict[str, Any]]:
    headers = {"User-Agent": "AlgoProfileHackathon/0.1"}
    urls = [
        f"https://www.reddit.com/user/{username}/submitted.json?limit={limit}",
        f"https://www.reddit.com/user/{username}/comments.json?limit={limit}",
    ]

    items: List[Dict[str, Any]] = []
    for url in urls:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Reddit fetch failed ({r.status_code}) for {url}")
        data = r.json()
        for ch in data.get("data", {}).get("children", []):
            d = ch.get("data", {})
            text = (d.get("title", "") + "\n" + (d.get("selftext", "") or "")).strip()
            if not text:
                text = (d.get("body", "") or "").strip()

            items.append(
                {
                    "platform": "reddit",
                    "item_type": ch.get("kind", ""),
                    "source": d.get("subreddit", "unknown"),
                    "source_id": d.get("subreddit_id", None),
                    "text": text[:4000],
                    "timestamp": int(d.get("created_utc", time.time())),
                    "engagement": {
                        "score": int(d.get("score", 0)),
                        "num_comments": int(d.get("num_comments", 0))
                        if d.get("num_comments") is not None
                        else 0,
                    },
                    "url": d.get("permalink", None),
                    "raw": {"id": d.get("id"), "name": d.get("name")},
                }
            )

    seen = set()
    dedup = []
    for it in items:
        key = (it["platform"], it["raw"].get("name") or it["raw"].get("id") or it["text"][:80])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(it)
    return dedup[:limit]


def ingest_youtube_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items = []
    now = int(time.time())
    for s in sources[:500]:
        title = (s.get("channelTitle") or s.get("title") or "").strip()
        cid = s.get("channelId") or s.get("id")
        if not title:
            continue
        items.append(
            {
                "platform": "youtube",
                "item_type": "channel_subscription",
                "source": title,
                "source_id": cid,
                "text": f"Subscribed channel: {title}",
                "timestamp": now,
                "engagement": {},
                "url": None,
                "raw": s,
            }
        )
    return items


TOPICS = ["finance", "tech", "sports", "politics", "fitness", "relationships", "gaming", "culture", "news", "other"]
TONES = ["informative", "neutral", "humorous", "outrage", "fear", "positive", "sad", "angry"]


def label_item(item: Dict[str, Any]) -> Dict[str, Any]:
    text = (item.get("text") or "").lower()
    topic = "other"
    if any(k in text for k in ["stock", "bond", "crypto", "interest rate", "inflation", "earnings"]):
        topic = "finance"
    elif any(k in text for k in ["python", "ai", "openai", "gpu", "programming", "cloud"]):
        topic = "tech"
    elif any(k in text for k in ["gym", "protein", "workout", "bench", "cardio"]):
        topic = "fitness"
    elif any(k in text for k in ["election", "government", "policy", "immigration", "ukraine", "israel"]):
        topic = "politics"
    elif any(k in text for k in ["nba", "football", "soccer", "goal", "match"]):
        topic = "sports"

    tone = "neutral"
    if any(k in text for k in ["lol", "lmao", "haha"]):
        tone = "humorous"
    if any(k in text for k in ["shocking", "disgusting", "outrage", "they want you to"]):
        tone = "outrage"

    clickbait = float("!" in item.get("text", "") or item.get("text", "").isupper())
    controversy = 1.0 if topic in ["politics"] else 0.2

    return {
        "topic": topic,
        "tone": tone,
        "clickbait_score": min(1.0, clickbait),
        "controversy_score": float(controversy),
        "confidence": 0.55,
    }


def engagement_score(it: Dict[str, Any]) -> float:
    e = it.get("engagement") or {}
    return float(e.get("score", 0)) + 2.0 * float(e.get("num_comments", 0))


def compute_metrics(items: List[Dict[str, Any]], labels: List[Dict[str, Any]]) -> Dict[str, Any]:
    df = pd.DataFrame(items)
    lab = pd.DataFrame(labels)
    if df.empty or lab.empty:
        return {"error": "no data"}

    df = pd.concat([df.reset_index(drop=True), lab.reset_index(drop=True)], axis=1)
    df["engagement_score"] = df.apply(lambda r: engagement_score(r.to_dict()), axis=1)

    topic_raw = df["topic"].value_counts(normalize=True).to_dict()
    tone_raw = df["tone"].value_counts(normalize=True).to_dict()

    w = df["engagement_score"].clip(lower=0.0)
    wsum = float(w.sum()) if float(w.sum()) > 0 else 1.0
    topic_w = (df.groupby("topic")["engagement_score"].sum() / wsum).sort_values(ascending=False).to_dict()
    tone_w = (df.groupby("tone")["engagement_score"].sum() / wsum).sort_values(ascending=False).to_dict()

    all_topics = set(topic_raw) | set(topic_w)
    lift = {t: float(topic_w.get(t, 0.0) - topic_raw.get(t, 0.0)) for t in all_topics}
    lift = dict(sorted(lift.items(), key=lambda kv: abs(kv[1]), reverse=True))

    def entropy(p: Dict[str, float]) -> float:
        return float(-sum(v * math.log(v + 1e-12) for v in p.values() if v > 0))

    topic_entropy = entropy(topic_raw)

    source_share = df["source"].value_counts(normalize=True)
    top5_source_share = float(source_share.head(5).sum()) if not source_share.empty else 0.0

    df["lift_topic"] = df["topic"].map(lambda t: lift.get(t, 0.0))
    df_sorted = df.sort_values(["engagement_score", "lift_topic"], ascending=[False, False])

    evidence = {
        "most_reinforced": df_sorted.head(10)[["platform", "source", "topic", "tone", "engagement_score", "text"]].to_dict(orient="records"),
        "most_intense": df.sort_values(["controversy_score", "clickbait_score"], ascending=[False, False])
        .head(10)[["platform", "source", "topic", "tone", "controversy_score", "clickbait_score", "text"]]
        .to_dict(orient="records"),
    }

    return {
        "counts": {"items": int(len(df))},
        "topic_raw": topic_raw,
        "topic_weighted": topic_w,
        "tone_raw": tone_raw,
        "tone_weighted": tone_w,
        "lift": lift,
        "diversity": {"topic_entropy": topic_entropy, "top5_source_share": top5_source_share},
        "evidence": evidence,
    }


@app.post("/ingest")
def ingest(req: IngestReq):
    items: List[Dict[str, Any]] = []
    if req.reddit_username:
        items.extend(fetch_reddit_public(req.reddit_username, limit=req.max_reddit_items))
    if req.youtube_sources:
        items.extend(ingest_youtube_sources(req.youtube_sources))

    if not items:
        raise HTTPException(status_code=400, detail="No data ingested. Provide reddit_username and/or youtube_sources.")

    labels = [label_item(it) for it in items]
    metrics = compute_metrics(items, labels)

    DB[req.user_id] = {"items": items, "labels": labels, "metrics": metrics}
    return {"user_id": req.user_id, "items": len(items), "metrics_keys": list(metrics.keys())}


@app.get("/profile/{user_id}")
def profile(user_id: str):
    if user_id not in DB:
        raise HTTPException(status_code=404, detail="Unknown user_id. Ingest first.")
    return DB[user_id]["metrics"]
