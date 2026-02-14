import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import StatCard from "@/components/StatCard";
import { fetchProfile, persistProfile, readProfile } from "@/lib/api";
import type { AlgoProfile } from "@/types/vibe";

export default function YouTubeExplorerPage() {
  const stored = readProfile();
  const [profile, setProfile] = useState<AlgoProfile | null>(stored?.profile ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const youtubeReinforced = useMemo(
    () => profile?.evidence.most_reinforced.filter((item) => item.platform === "youtube") ?? [],
    [profile]
  );
  const youtubeIntense = useMemo(
    () => profile?.evidence.most_intense.filter((item) => item.platform === "youtube") ?? [],
    [profile]
  );

  const refresh = async () => {
    if (!stored) {
      navigate("/");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const latest = await fetchProfile(stored.userId);
      persistProfile(stored.userId, latest);
      setProfile(latest);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh profile.");
    } finally {
      setLoading(false);
    }
  };

  if (!stored) {
    navigate("/");
    return null;
  }

  return (
    <div className="min-h-screen px-4 py-24 max-w-5xl mx-auto space-y-10">
      <motion.div className="glass-card p-8 space-y-6" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-heading text-gradient-sunset">YouTube Explorer</h1>
        <p className="text-muted-foreground">
          This page filters the FastAPI metrics down to the synthetic YouTube items you ingested (via subscriptions export). Use it to inspect reinforcement + intensity patterns, then hop back to `/` to re-run ingest with a new file.
        </p>
        <div className="flex flex-wrap gap-4">
          <button
            className="bg-gradient-sunset text-background rounded-2xl px-6 py-3 font-semibold hover:scale-105 transition"
            onClick={refresh}
            disabled={loading}
          >
            {loading ? "Refreshing" : "Refresh from FastAPI"}
          </button>
          <button
            className="rounded-2xl border border-border px-6 py-3 hover:bg-secondary/40"
            onClick={() => navigate("/")}
          >
            Re-run ingest
          </button>
        </div>
        {error && <div className="text-sm text-red-400">{error}</div>}
      </motion.div>

      {profile && (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <StatCard label="YouTube sources" value={youtubeReinforced.length} detail="Ways the algo reinforces you." />
            <StatCard label="Intensity signals" value={youtubeIntense.length} detail="High clickbait/controversy moments." />
            <StatCard label="Total items" value={profile.counts.items} detail="Across Reddit + YouTube." />
          </div>

          <div className="glass-card p-6 space-y-4">
            <h2 className="text-lg font-heading">Most reinforced YouTube sources</h2>
            <div className="space-y-4 max-h-96 overflow-auto pr-2">
              {youtubeReinforced.map((item, idx) => (
                <div key={`${item.source}-${idx}`} className="border border-white/5 rounded-2xl p-4">
                  <p className="text-sm text-muted-foreground">{item.topic} • {item.tone}</p>
                  <p className="font-semibold">{item.source}</p>
                  <p className="text-sm text-muted-foreground">{item.text}</p>
                </div>
              ))}
              {!youtubeReinforced.length && <p className="text-sm text-muted-foreground">No YouTube sources found in the latest ingest.</p>}
            </div>
          </div>

          <div className="glass-card p-6 space-y-4">
            <h2 className="text-lg font-heading">Most intense (controversy/clickbait)</h2>
            <div className="space-y-4 max-h-96 overflow-auto pr-2">
              {youtubeIntense.map((item, idx) => (
                <div key={`${item.source}-${idx}`} className="border border-white/5 rounded-2xl p-4">
                  <p className="text-sm text-muted-foreground">{item.topic} • {item.tone}</p>
                  <p className="font-semibold">{item.source}</p>
                  <p className="text-sm text-muted-foreground">
                    clickbait {item.clickbait_score?.toFixed(2) ?? "0"} • controversy {item.controversy_score?.toFixed(2) ?? "0"}
                  </p>
                  <p className="text-sm text-muted-foreground">{item.text}</p>
                </div>
              ))}
              {!youtubeIntense.length && <p className="text-sm text-muted-foreground">No intense signals flagged yet.</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
