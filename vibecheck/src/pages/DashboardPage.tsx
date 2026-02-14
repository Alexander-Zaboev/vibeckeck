import { useMemo } from "react";
import { Navigate } from "react-router-dom";
import DashboardNav from "@/components/DashboardNav";
import StatCard from "@/components/StatCard";
import { readProfile } from "@/lib/api";
import type { AlgoProfile } from "@/types/vibe";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function mapRecord(record?: Record<string, number>) {
  if (!record) return [];
  return Object.entries(record).map(([key, value]) => ({ name: key, value: Number(value) }));
}

export default function DashboardPage() {
  const stored = readProfile();
  const profile: AlgoProfile | null = stored?.profile ?? null;

  const topicRaw = useMemo(() => mapRecord(profile?.topic_raw), [profile]);
  const toneRaw = useMemo(() => mapRecord(profile?.tone_raw), [profile]);
  const lift = useMemo(() => mapRecord(profile?.lift), [profile]);

  if (!profile) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="pb-32">
      <DashboardNav username={stored?.userId ?? "guest"} />
      <main className="max-w-6xl mx-auto px-4 pt-32 space-y-12">
        <section className="space-y-6">
          <header className="flex flex-col gap-2">
            <p className="text-sm uppercase tracking-[0.4em] text-muted-foreground">Overview</p>
            <h2 className="text-3xl font-heading text-gradient-sunset">Algorithm profile</h2>
            <p className="text-xs text-muted-foreground">
              Metrics computed by the FastAPI backend (Reddit public JSON + YouTube subscription upload) and cached in memory.
            </p>
          </header>
          <div className="grid gap-4 md:grid-cols-3">
            <StatCard label="Items processed" value={profile.counts.items.toLocaleString()} detail="Posts, comments, and synthetic YouTube sources." />
            <StatCard label="Topic entropy" value={profile.diversity.topic_entropy.toFixed(2)} detail="Higher = more diverse attention." />
            <StatCard label="Top-5 source share" value={`${(profile.diversity.top5_source_share * 100).toFixed(1)}%`} detail="Concentration of inputs." />
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <div className="glass-card p-6 space-y-4">
            <h3 className="font-heading">Topic mix (raw)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topicRaw}>
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" tick={{ fontSize: 11 }} />
                  <YAxis stroke="hsl(var(--muted-foreground))" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                  <Tooltip contentStyle={{ background: "hsl(var(--card))", borderRadius: "1rem" }} formatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
                  <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="glass-card p-6 space-y-4">
            <h3 className="font-heading">Tone mix</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={toneRaw}>
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" tick={{ fontSize: 11 }} />
                  <YAxis stroke="hsl(var(--muted-foreground))" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                  <Tooltip contentStyle={{ background: "hsl(var(--card))", borderRadius: "1rem" }} formatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
                  <Bar dataKey="value" fill="hsl(var(--accent))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="glass-card p-6 space-y-4">
          <h3 className="font-heading">Reinforcement (lift)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={lift}>
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" tick={{ fontSize: 11 }} />
                <YAxis stroke="hsl(var(--muted-foreground))" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip contentStyle={{ background: "hsl(var(--card))", borderRadius: "1rem" }} formatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
                <Bar dataKey="value" fill="hsl(var(--reddit-orange))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <div className="glass-card p-6 space-y-4">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Most reinforced</p>
              <h3 className="text-xl font-heading">High engagement + topic lift</h3>
            </div>
            <div className="space-y-4 max-h-96 overflow-auto pr-2">
              {profile.evidence.most_reinforced.map((item, idx) => (
                <div key={`${item.source}-${idx}`} className="border border-white/5 rounded-2xl p-4">
                  <p className="text-sm text-muted-foreground">{item.platform} • {item.topic} • {item.tone}</p>
                  <p className="font-semibold">{item.source}</p>
                  <p className="text-sm text-muted-foreground">{item.text}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="glass-card p-6 space-y-4">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Most intense</p>
              <h3 className="text-xl font-heading">Clickbait + controversy watchlist</h3>
            </div>
            <div className="space-y-4 max-h-96 overflow-auto pr-2">
              {profile.evidence.most_intense.map((item, idx) => (
                <div key={`${item.source}-${idx}`} className="border border-white/5 rounded-2xl p-4">
                  <p className="text-sm text-muted-foreground">{item.platform} • {item.topic} • {item.tone}</p>
                  <p className="font-semibold">{item.source}</p>
                  <p className="text-sm text-muted-foreground">
                    clickbait {item.clickbait_score?.toFixed(2) ?? "0"} • controversy {item.controversy_score?.toFixed(2) ?? "0"}
                  </p>
                  <p className="text-sm text-muted-foreground">{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
