import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { Incident } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";
import { SeverityDot } from "./ui/SeverityBadge";

const sevColorMap: Record<string, string> = {
  critical: "#e94560",
  high: "#ff6b35",
  medium: "#ffc107",
  low: "#4caf50",
};

const sevOrder: Record<string, number> = { critical: 4, high: 3, medium: 2, low: 1 };

export function IncidentTimeline({ incidents }: { incidents?: Incident[] | null }) {
  const data = (incidents || [])
    .filter((i) => i.timestamp)
    .map((i) => ({
      id: i.incident_id || "",
      service: i.service || "",
      severity: (i.severity || "low").toLowerCase(),
      y: sevOrder[(i.severity || "low").toLowerCase()] || 1,
      x: new Date(i.timestamp).getTime(),
    }))
    .sort((a, b) => a.x - b.x);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Incident Timeline</CardTitle>
        <CardBadge>{data.length} incidents</CardBadge>
      </CardHeader>
      <CardContent className="h-52">
        {data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-dim font-mono text-xs">
            No incidents yet
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 40 }}>
              <CartesianGrid stroke="#232C3D" strokeDasharray="3 3" />
              <XAxis
                dataKey="x"
                type="number"
                domain={["dataMin - 60000", "dataMax + 60000"]}
                tick={{ fill: "#5A6678", fontSize: 10 }}
                tickFormatter={(v) => new Date(v).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}
                stroke="#232C3D"
              />
              <YAxis
                dataKey="y"
                type="number"
                domain={[0.5, 4.5]}
                ticks={[1, 2, 3, 4]}
                tick={{ fill: "#5A6678", fontSize: 10 }}
                tickFormatter={(v) => ({ 4: "Critical", 3: "High", 2: "Medium", 1: "Low" })[v] || ""}
                stroke="#232C3D"
              />
              <Tooltip
                contentStyle={{
                  background: "#1A2130",
                  border: "1px solid #232C3D",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "#E8EDF5",
                }}
                labelFormatter={(v) => new Date(v).toLocaleTimeString("en-GB")}
                formatter={(_: unknown, __: unknown, props: { payload: { severity: string; service: string; id: string } }) => [
                  `${props.payload.service} - ${props.payload.id}`,
                  props.payload.severity.toUpperCase(),
                ]}
              />
              <Legend
                formatter={(value: string) => <span style={{ color: "#93A0B4", fontSize: 11 }}>{value}</span>}
              />
              {["critical", "high", "medium", "low"].map((sev) => {
                const d = data.filter((i) => i.severity === sev);
                if (d.length === 0) return null;
                return (
                  <Scatter
                    key={sev}
                    name={sev.charAt(0).toUpperCase() + sev.slice(1)}
                    data={d}
                    fill={sevColorMap[sev]}
                    fillOpacity={0.8}
                    stroke="none"
                    shape={(props: { cx: number; cy: number }) => (
                      <circle cx={props.cx} cy={props.cy} r={6} fill={sevColorMap[sev]} />
                    )}
                  />
                );
              })}
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
