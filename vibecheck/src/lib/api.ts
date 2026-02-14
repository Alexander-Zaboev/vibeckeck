import type { AlgoProfile, IngestPayload, IngestResponse } from "@/types/vibe";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
const PROFILE_KEY = "algo-profile";
const USER_KEY = "algo-profile-user";

export function persistProfile(userId: string, profile: AlgoProfile) {
  sessionStorage.setItem(USER_KEY, userId);
  sessionStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function readProfile(): { userId: string; profile: AlgoProfile } | null {
  const userId = sessionStorage.getItem(USER_KEY);
  const payload = sessionStorage.getItem(PROFILE_KEY);
  if (!userId || !payload) return null;
  try {
    return { userId, profile: JSON.parse(payload) as AlgoProfile };
  } catch {
    return null;
  }
}

export function clearProfile() {
  sessionStorage.removeItem(USER_KEY);
  sessionStorage.removeItem(PROFILE_KEY);
}

async function handleResponse<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || resp.statusText);
  }
  return resp.json() as Promise<T>;
}

export async function ingestProfile(payload: IngestPayload): Promise<IngestResponse> {
  const body = {
    user_id: payload.userId,
    reddit_username: payload.redditUsername || null,
    youtube_sources: payload.youtubeSources ?? null,
    max_reddit_items: payload.maxRedditItems ?? 80,
  };
  const resp = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<IngestResponse>(resp);
}

export async function fetchProfile(userId: string): Promise<AlgoProfile> {
  const resp = await fetch(`${API_BASE}/profile/${encodeURIComponent(userId)}`);
  return handleResponse<AlgoProfile>(resp);
}
