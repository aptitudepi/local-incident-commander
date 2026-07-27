import type { Triage } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";
import { SeverityDot } from "./ui/SeverityBadge";

const sevBorder: Record<string, string> = {
  critical: "border-l-crit",
  high: "border-l-high",
  medium: "border-l-med",
  low: "border-l-low",
};

export function TriageResults({ triages }: { triages?: Triage[] | null }) {
  const items = (triages || []).slice(0, 5);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Triage Results</CardTitle>
        <CardBadge>{triages?.length ?? 0} total</CardBadge>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="flex h-24 items-center justify-center text-dim font-mono text-xs">
            No triage results yet
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {items.map((t, i) => {
              const sev = (t.severity || "low").toLowerCase();
              return (
                <div
                  key={i}
                  className={`rounded-lg border border-line bg-panel2 p-3 border-l-2 ${sevBorder[sev] || "border-l-low"}`}
                >
                  <div className="flex items-center gap-2 mb-1.5">
                    <SeverityDot severity={sev} />
                    <span className="font-mono text-xs text-hi font-semibold">{t.service || "unknown"}</span>
                    <span className="font-mono text-[10px] text-dim uppercase">{t.severity || "Low"}</span>
                  </div>
                  <p className="text-xs text-mid mb-1">{t.root_cause || "No root cause identified"}</p>
                  {t.suggested_fix && (
                    <code className="block font-mono text-[11px] text-active bg-panel rounded px-2 py-1">
                      {t.suggested_fix}
                    </code>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
