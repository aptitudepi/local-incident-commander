import { motion } from "motion/react";
import type { Costs, Stats } from "../types";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card";

function AnimatedNumber({ value, prefix = "", suffix = "" }: { value: number; prefix?: string; suffix?: string }) {
  return (
    <motion.span
      className="font-mono text-2xl font-bold text-hi"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      key={value}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
    >
      {prefix}{value.toLocaleString()}{suffix}
    </motion.span>
  );
}

function MetricCard({ label, value, prefix, suffix, color }: {
  label: string; value: number; prefix?: string; suffix?: string; color: string;
}) {
  return (
    <div className="flex flex-col items-center gap-1 rounded-lg border border-line bg-panel2 p-3 text-center">
      <span className="font-mono text-[10px] uppercase tracking-wider text-dim">{label}</span>
      <AnimatedNumber value={value} prefix={prefix} suffix={suffix} />
    </div>
  );
}

export function CostTracker({ costs, stats }: { costs?: Costs | null; stats?: Stats | null }) {
  const resolved = costs?.total_incidents_resolved ?? stats?.total_incidents ?? 0;
  const saved = costs?.total_saved ?? stats?.total_saved ?? 0;
  const blocked = costs?.total_actions_blocked ?? 0;
  const autoResolved = stats?.triage_count ?? 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cost Tracker</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-2">
          <MetricCard label="Incidents Resolved" value={resolved} color="#4caf50" />
          <MetricCard label="Auto-Triaged" value={autoResolved} color="#4D8DF0" />
          <MetricCard label="Actions Blocked" value={blocked} color="#e94560" />
          <MetricCard label="Total Savings" value={saved} prefix="$" color="#ffc107" />
        </div>
      </CardContent>
    </Card>
  );
}
