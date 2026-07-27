import { useState } from "react";
import { ChevronDown, ChevronRight, FileText } from "lucide-react";
import type { Report } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";
import { SeverityDot } from "./ui/SeverityBadge";

export function PostIncidentReports({ reports }: { reports?: Report[] | null }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const items = (reports || []).slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Post-Incident Reports</CardTitle>
        <CardBadge>{reports?.length ?? 0} reports</CardBadge>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="flex h-16 items-center justify-center text-dim font-mono text-xs">
            No PIRs yet
          </div>
        ) : (
          <div className="flex flex-col gap-1.5">
            {items.map((r) => {
              const id = r.incident_id || "unknown";
              const open = expanded === id;
              return (
                <div key={id} className="rounded-lg border border-line overflow-hidden">
                  <button
                    className="flex w-full items-center gap-2 bg-panel2 p-3 text-left hover:bg-panel transition-colors cursor-pointer"
                    onClick={() => setExpanded(open ? null : id)}
                  >
                    {open ? <ChevronDown size={14} className="text-dim shrink-0" /> : <ChevronRight size={14} className="text-dim shrink-0" />}
                    <FileText size={14} className="text-mid shrink-0" />
                    <span className="flex-1 font-mono text-xs text-hi font-semibold">{id}</span>
                    <SeverityDot severity={r.severity || "low"} />
                    <span className="font-mono text-[10px] text-dim">{r.service || "?"}</span>
                    {r.title && <span className="text-xs text-mid truncate max-w-[200px]">{r.title}</span>}
                  </button>
                  {open && (
                    <div className="border-t border-line bg-panel p-3">
                      {r.probable_root_cause && (
                        <div className="mb-2">
                          <span className="font-mono text-[10px] uppercase tracking-wider text-dim block mb-1">Root Cause</span>
                          <p className="text-xs text-mid">{r.probable_root_cause}</p>
                        </div>
                      )}
                      {r.evidence && r.evidence.length > 0 && (
                        <div className="mb-2">
                          <span className="font-mono text-[10px] uppercase tracking-wider text-dim block mb-1">Evidence</span>
                          <ul className="list-none p-0 m-0">
                            {r.evidence.map((e, i) => (
                              <li key={i} className="font-mono text-[11px] text-mid py-0.5 border-b border-line last:border-0">
                                {e}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {r.recommended_action && (
                        <div>
                          <span className="font-mono text-[10px] uppercase tracking-wider text-dim block mb-1">Recommended Action</span>
                          <code className="block font-mono text-[11px] text-active bg-panel2 rounded px-2 py-1">
                            {r.recommended_action}
                          </code>
                        </div>
                      )}
                    </div>
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
