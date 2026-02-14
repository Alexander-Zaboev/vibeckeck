import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Upload } from "lucide-react";
import { fetchProfile, ingestProfile, persistProfile } from "@/lib/api";

interface ChannelSource {
  channelTitle: string;
  channelId?: string | null;
  [key: string]: unknown;
}

const CSV_TITLE_KEYS = ["channelTitle", "channel title", "Title", "Channel Title"];
const CSV_ID_KEYS = ["channelId", "channel id", "Channel Id", "Channel ID", "Id", "ID"];

function parseCsv(text: string): ChannelSource[] {
  const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
  if (lines.length < 2) throw new Error("CSV must include a header row and at least one data row.");
  const headers = lines[0].split(",").map((h) => h.trim());
  const rows: ChannelSource[] = [];
  for (const line of lines.slice(1)) {
    const values = line.split(",");
    const row: Record<string, string> = {};
    headers.forEach((header, idx) => {
      row[header] = values[idx]?.trim() ?? "";
    });
    const title = CSV_TITLE_KEYS.map((key) => row[key]).find((v) => v);
    if (!title) continue;
    const channelId = CSV_ID_KEYS.map((key) => row[key]).find((v) => v);
    rows.push({ channelTitle: title, channelId: channelId || undefined, raw: row });
  }
  if (!rows.length) {
    throw new Error("CSV did not include recognizable channelTitle/channelId columns.");
  }
  return rows;
}

async function parseYoutubeFile(file: File): Promise<ChannelSource[]> {
  const text = await file.text();
  const isJson = file.name.toLowerCase().endsWith(".json") || file.type.includes("json");
  if (isJson) {
    const data = JSON.parse(text);
    if (!Array.isArray(data)) {
      throw new Error("YouTube JSON export must be a list of channel objects.");
    }
    return data as ChannelSource[];
  }
  return parseCsv(text);
}

export default function LoginPage() {
  const [userId, setUserId] = useState("demo_user");
  const [redditUsername, setRedditUsername] = useState("spez");
  const [maxItems, setMaxItems] = useState(80);
  const [ytSources, setYtSources] = useState<ChannelSource[] | null>(null);
  const [uploadLabel, setUploadLabel] = useState("No file selected");
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      setError("");
      setStatus("Parsing YouTube export…");
      const parsed = await parseYoutubeFile(file);
      setYtSources(parsed);
      setUploadLabel(`${file.name} (${parsed.length} channels)`);
      setStatus("YouTube subscriptions ready.");
    } catch (err) {
      setYtSources(null);
      setUploadLabel("No file selected");
      setError(err instanceof Error ? err.message : "Unable to parse file.");
    } finally {
      setTimeout(() => setStatus(""), 1500);
    }
  };

  const handleGenerate = async (event: FormEvent) => {
    event.preventDefault();
    if (!redditUsername && !ytSources?.length) {
      setError("Provide a Reddit username and/or attach a YouTube subscriptions export.");
      return;
    }
    setError("");
    setLoading(true);
    setStatus("Calling FastAPI /ingest…");
    try {
      await ingestProfile({
        userId,
        redditUsername: redditUsername || undefined,
        youtubeSources: ytSources ?? undefined,
        maxRedditItems: maxItems,
      });
      setStatus("Fetching computed metrics…");
      const profile = await fetchProfile(userId);
      persistProfile(userId, profile);
      navigate("/wrapped", { state: { from: "ingest" } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingestion failed.");
    } finally {
      setLoading(false);
      setTimeout(() => setStatus(""), 2000);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <motion.form
        onSubmit={handleGenerate}
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className="glass-card w-full max-w-4xl p-10 space-y-10"
      >
        <div className="flex flex-col gap-4 text-center">
          <span className="px-4 py-1 text-xs uppercase tracking-[0.4em] bg-muted/40 rounded-full self-center">
            Powered by FastAPI + Streamlit ingestion
          </span>
          <h1 className="text-4xl font-heading text-gradient-sunset">VibeCheck Wrapped</h1>
          <p className="text-muted-foreground">
            This UI talks directly to your FastAPI backend (`Snippet.py`). Provide the same inputs as the Streamlit MVP—Reddit username
            and/or YouTube subscriptions export—and we will hit `/ingest` then `/profile` to build your slides + dashboard.
          </p>
        </div>

        <div className="grid gap-6">
          <label className="text-xs uppercase tracking-[0.3em] text-muted-foreground">User ID</label>
          <input
            className="rounded-2xl bg-secondary/50 border border-border px-4 py-3"
            value={userId}
            onChange={(e) => setUserId(e.target.value.trim())}
            placeholder="demo_user"
            required
          />

          <label className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Reddit username (public)</label>
          <input
            className="rounded-2xl bg-secondary/50 border border-border px-4 py-3"
            value={redditUsername}
            onChange={(e) => setRedditUsername(e.target.value)}
            placeholder="u/username"
          />

          <div className="grid gap-2">
            <label className="text-xs uppercase tracking-[0.3em] text-muted-foreground">YouTube subscriptions export (JSON or CSV)</label>
            <label className="rounded-2xl border border-dashed border-border px-4 py-6 flex flex-col items-center gap-2 text-sm text-muted-foreground cursor-pointer hover:bg-secondary/40">
              <Upload size={18} />
              <span>{uploadLabel}</span>
              <input type="file" accept=".json,.csv" onChange={handleFileChange} className="hidden" />
            </label>
            <p className="text-xs text-muted-foreground">
              Export your subscriptions from YouTube (Settings → Privacy → Download data). We send the parsed list to `/ingest` exactly like the Streamlit app.
            </p>
          </div>

          <div className="grid gap-2">
            <label className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Max Reddit items</label>
            <input
              type="range"
              min={20}
              max={200}
              step={10}
              value={maxItems}
              onChange={(e) => setMaxItems(Number(e.target.value))}
            />
            <div className="text-sm text-muted-foreground">{maxItems} posts/comments will be fetched.</div>
          </div>
        </div>

        {status && <div className="text-sm text-primary">{status}</div>}
        {error && <div className="text-sm text-red-400">{error}</div>}

        <button
          type="submit"
          disabled={loading}
          className="bg-gradient-sunset text-background rounded-2xl px-6 py-3 font-semibold flex items-center justify-center gap-2 hover:scale-105 active:scale-95 transition"
        >
          {loading ? "Generating" : "Generate My Wrapped"}
          <ArrowRight size={18} />
        </button>

        <p className="text-center text-sm text-muted-foreground">
          Need to debug liked videos?{" "}
          <button
            type="button"
            onClick={() => navigate("/youtube-explorer")}
            className="text-primary underline underline-offset-4"
          >
            Open the explorer
          </button>
        </p>
      </motion.form>
    </div>
  );
}
