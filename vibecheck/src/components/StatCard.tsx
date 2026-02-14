import { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: ReactNode;
  detail?: ReactNode;
}

export default function StatCard({ label, value, detail }: StatCardProps) {
  return (
    <div className="glass-card p-6 flex flex-col gap-2">
      <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground font-heading">{label}</span>
      <span className="text-gradient-sunset text-3xl font-bold">{value}</span>
      {detail && <span className="text-sm text-muted-foreground">{detail}</span>}
    </div>
  );
}
