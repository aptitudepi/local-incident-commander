import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import type { Incident } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";

export function ServiceBreakdown({ incidents }: { incidents?: Incident[] | null }) {
  const counts: Record<string, number> = {};
  (incidents || []).forEach((i) => {
    const s = i.service || "unknown";
    counts[s] = (counts[s] || 0) + 1;
  });

  const data = Object.entries(counts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Service Breakdown</CardTitle>
        <CardBadge>{data.length} services</CardBadge>
      </CardHeader>
      <CardContent className="h-52">
        {data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-dim font-mono text-xs">
            No data
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, bottom: 5, left: 80 }}>
              <XAxis type="number" tick={{ fill: "#5A6678", fontSize: 10 }} stroke="#232C3D" />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: "#93A0B4", fontSize: 11 }}
                stroke="#232C3D"
                width={80}
              />
              <Tooltip
                contentStyle={{
                  background: "#1A2130",
                  border: "1px solid #232C3D",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "#E8EDF5",
                }}
              />
              <Bar dataKey="value" fill="#e94560" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
