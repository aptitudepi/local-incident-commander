import type { SystemHealth as Health } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";
import { Badge } from "./ui/Badge";

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block size-2 rounded-full ${ok ? "bg-ok shadow-[0_0_6px_rgba(134,194,50,0.6)]" : "bg-crit shadow-[0_0_6px_rgba(233,69,96,0.4)]"}`}
    />
  );
}

function StatRow({ label, ok, detail }: { label: string; ok: boolean; detail?: string }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-line last:border-0">
      <span className="text-xs text-mid">{label}</span>
      <div className="flex items-center gap-2">
        {detail && <span className="font-mono text-[11px] text-dim">{detail}</span>}
        <StatusDot ok={ok} />
      </div>
    </div>
  );
}

export function SystemHealth({ health }: { health?: Health | null }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health</CardTitle>
        <Badge variant={health?.model?.vllm_running ? "ok" : "crit"}>
          {health?.model?.vllm_running ? "ONLINE" : "DEGRADED"}
        </Badge>
      </CardHeader>
      <CardContent>
        <StatRow label="Watcher" ok={health?.pipeline?.watcher === "active"} detail={health?.pipeline?.watcher} />
        <StatRow label="Correlator" ok={health?.pipeline?.correlator === "active"} detail={health?.pipeline?.correlator} />
        <StatRow label="LLM Endpoint" ok={!!health?.model?.vllm_running} detail={health?.model?.vllm_running ? "running" : "down"} />
        <StatRow label="Model Loaded" ok={!!health?.model?.model_loaded} />
        <StatRow label="Inbox Queue" ok={(health?.queue?.inbox_count ?? 0) < 100} detail={`${health?.queue?.inbox_count ?? 0} items`} />
        <StatRow label="Fallback Available" ok={!!health?.model?.fallback_available} />
      </CardContent>
    </Card>
  );
}
