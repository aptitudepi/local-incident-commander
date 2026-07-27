import { useEffect, useState } from "react";
import type { Stats, SystemHealth } from "../types";
import { Badge } from "./ui/Badge";

function Clock() {
  const [time, setTime] = useState(new Date().toLocaleTimeString("en-GB"));
  useEffect(() => {
    const id = setInterval(() => setTime(new Date().toLocaleTimeString("en-GB")), 1000);
    return () => clearInterval(id);
  }, []);
  return <span className="font-mono text-xs text-dim">{time}</span>;
}

export function Header({ stats, health }: { stats?: Stats | null; health?: SystemHealth | null }) {
  const llmOk = health?.model?.vllm_running;
  return (
    <header className="flex items-center gap-4 rounded-xl border border-line bg-panel px-4 py-3">
      <div className="flex items-center gap-3 min-w-[240px]">
        <div className="flex size-8 items-center justify-center rounded-lg border border-line bg-gradient-to-br from-[#1c2636] to-[#0e1420]">
          <span className="size-3 rounded-full bg-ok shadow-[0_0_10px_rgba(134,194,50,0.6)] animate-pulse" />
        </div>
        <div>
          <h1 className="text-sm font-bold uppercase tracking-widest m-0">Local Incident Commander</h1>
          <span className="block font-mono text-[10px] text-dim tracking-widest">OFFLINE SRE TRIAGE</span>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        <Badge variant="ok"><span className="size-1.5 rounded-full bg-ok shadow-[0_0_6px_rgba(134,194,50,0.8)]" /> LOCAL</Badge>
        <Badge variant="outline">CLOUD CALLS <b className="text-hi font-semibold">0</b></Badge>
        <Badge variant="outline">
          MODEL <b className="text-hi font-semibold">{llmOk ? "vllm" : "local-fallback"}</b>
        </Badge>
        <Badge variant="outline">
          INBOX <b className="text-hi font-semibold">{stats?.inbox_count ?? 0}</b>
        </Badge>
        <Badge variant="outline">
          INCIDENTS <b className="text-hi font-semibold">{stats?.total_incidents ?? 0}</b>
        </Badge>
      </div>

      <div className="ml-auto flex items-center gap-3">
        <Clock />
        <span className="flex items-center gap-1.5 text-[11px] text-dim font-mono">
          <span className="size-1.5 rounded-full bg-ok" />
          auto-refresh 2s
        </span>
      </div>
    </header>
  );
}
