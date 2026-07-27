import { motion } from "motion/react";
import type { Stats } from "../types";
import { Card } from "./ui/Card";

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div className="flex flex-col items-center gap-1 rounded-lg border border-line bg-panel2 p-3 text-center">
      <span className="font-mono text-[10px] uppercase tracking-wider text-dim">{label}</span>
      <motion.span
        className="font-mono text-xl font-bold"
        style={{ color }}
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {value}
      </motion.span>
    </div>
  );
}

export function StatusBar({ stats }: { stats?: Stats | null }) {
  return (
    <Card className="shrink-0">
      <div className="grid grid-cols-2 gap-2 p-3">
        <StatCard label="Total" value={stats?.total_incidents ?? 0} color="#93A0B4" />
        <StatCard label="Critical" value={stats?.critical_count ?? 0} color="#e94560" />
        <StatCard label="High" value={stats?.high_count ?? 0} color="#ff6b35" />
        <StatCard label="Saved" value={`$${(stats?.total_saved ?? 0).toLocaleString()}`} color="#4caf50" />
      </div>
    </Card>
  );
}
