import { cn } from "../../lib/utils";

const sevConfig: Record<string, { color: string; bg: string; border: string; shadow?: string }> = {
  critical: { color: "text-crit", bg: "bg-crit/8", border: "border-crit", shadow: "shadow-[0_0_10px_rgba(233,69,96,0.3)]" },
  high: { color: "text-high", bg: "bg-high/8", border: "border-high" },
  medium: { color: "text-med", bg: "bg-med/7", border: "border-med" },
  low: { color: "text-low", bg: "bg-low/8", border: "border-low" },
};

const sevColors: Record<string, string> = {
  critical: "#e94560",
  high: "#ff6b35",
  medium: "#ffc107",
  low: "#4caf50",
};

export function SeverityBadge({ severity, className }: { severity: string; className?: string }) {
  const s = (severity || "low").toLowerCase();
  const cfg = sevConfig[s] || sevConfig.low;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 font-mono text-[13px] font-bold uppercase tracking-wider",
        cfg.color, cfg.bg, cfg.border, cfg.shadow, className
      )}
    >
      <span
        className="inline-block size-[11px] rounded-sm"
        style={{ backgroundColor: sevColors[s] || sevColors.low, boxShadow: s === "critical" ? `0 0 10px ${sevColors.critical}` : undefined }}
      />
      {severity || "Low"}
    </span>
  );
}

export function SeverityDot({ severity, className }: { severity: string; className?: string }) {
  const s = (severity || "low").toLowerCase();
  return (
    <span
      className={cn("inline-block size-2 rounded-full", className)}
      style={{ backgroundColor: sevColors[s] || sevColors.low }}
    />
  );
}
