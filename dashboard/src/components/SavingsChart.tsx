import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { Costs } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";

function buildSavingsData(costs?: Costs | null) {
  const data: { name: string; savings: number }[] = [];
  const blocked = costs?.blocked_actions || [];
  let running = 0;
  for (const b of blocked) {
    running += 1;
    const ts = b.timestamp ? new Date(b.timestamp).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }) : "?";
    data.push({ name: ts, savings: running });
  }
  if (data.length === 0 && costs) {
    data.push({ name: "init", savings: costs.total_saved || 0 });
  }
  return data;
}

export function SavingsChart({ costs }: { costs?: Costs | null }) {
  const data = buildSavingsData(costs);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Savings Over Time</CardTitle>
        <CardBadge>${(costs?.total_saved ?? 0).toFixed(2)} total</CardBadge>
      </CardHeader>
      <CardContent className="h-48">
        {data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-dim font-mono text-xs">
            No savings data yet
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <defs>
                <linearGradient id="savingsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4caf50" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#4caf50" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#232C3D" strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fill: "#5A6678", fontSize: 10 }} stroke="#232C3D" />
              <YAxis tick={{ fill: "#5A6678", fontSize: 10 }} stroke="#232C3D" />
              <Tooltip
                contentStyle={{
                  background: "#1A2130",
                  border: "1px solid #232C3D",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "#E8EDF5",
                }}
              />
              <Area type="monotone" dataKey="savings" stroke="#4caf50" fill="url(#savingsGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
