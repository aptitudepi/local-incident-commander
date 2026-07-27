import { ShieldOff } from "lucide-react";
import type { BlockedAction } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";

export function PolicyDenials({ blockedActions }: { blockedActions: BlockedAction[] }) {
  const items = blockedActions.slice(-10).reverse();
  return (
    <Card>
      <CardHeader>
        <CardTitle>Policy Denials</CardTitle>
        <CardBadge>{blockedActions.length} blocked</CardBadge>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-1.5">
          {items.map((b, i) => (
            <div
              key={i}
              className="rounded-lg border border-crit/30 bg-[#2d1b1b] p-3 border-l-2 border-l-crit"
            >
              <div className="flex items-center gap-2 mb-1">
                <ShieldOff size={14} className="text-crit shrink-0" />
                <span className="font-mono text-[11px] font-bold text-crit uppercase">Denied</span>
                {b.timestamp && (
                  <span className="font-mono text-[10px] text-dim ml-auto">
                    {new Date(b.timestamp).toLocaleTimeString("en-GB")}
                  </span>
                )}
              </div>
              <code className="block font-mono text-[11px] text-hi mb-1">{b.action}</code>
              <p className="text-[11px] text-mid mb-1">{b.reason}</p>
              <span className="font-mono text-[10px] text-dim">Policy: {b.policy_id}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
