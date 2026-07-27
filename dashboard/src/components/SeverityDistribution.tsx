import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import type { Incident } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";

const COLORS = ["#e94560", "#ff6b35", "#ffc107", "#4caf50"];
const LABELS = ["Critical", "High", "Medium", "Low"];

export function SeverityDistribution({ incidents }: { incidents?: Incident[] | null }) {
  const counts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
  (incidents || []).forEach((i) => {
    const s = (i.severity || "low").toLowerCase();
    if (s in counts) counts[s as keyof typeof counts]++;
  });

  const data = LABELS.map((label, i) => ({
    name: label,
    value: Object.values(counts)[i],
    color: COLORS[i],
  })).filter((d) => d.value > 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Severity Distribution</CardTitle>
        <CardBadge>{data.reduce((a, b) => a + b.value, 0)} total</CardBadge>
      </CardHeader>
      <CardContent className="h-52 flex items-center justify-center">
        {data.length === 0 ? (
          <span className="text-dim font-mono text-xs">No data</span>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={70}
                paddingAngle={3}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={index} fill={entry.color} stroke="none" />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#1A2130",
                  border: "1px solid #232C3D",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "#E8EDF5",
                }}
                formatter={(value: number, name: string) => [value, name]}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
      <div className="flex justify-center gap-4 pb-3">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5 text-[11px] text-mid">
            <span className="inline-block size-2 rounded-full" style={{ backgroundColor: d.color }} />
            {d.name}: {d.value}
          </div>
        ))}
      </div>
    </Card>
  );
}
