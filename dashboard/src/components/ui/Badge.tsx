import { cn } from "../../lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "crit" | "high" | "med" | "low" | "outline" | "ok";
  className?: string;
}

const variants: Record<string, string> = {
  default: "bg-active text-white",
  crit: "bg-crit/10 text-crit border-crit/30",
  high: "bg-high/10 text-high border-high/30",
  med: "bg-med/10 text-med border-med/30",
  low: "bg-low/10 text-low border-low/30",
  outline: "bg-transparent border-line text-mid",
  ok: "bg-ok/10 text-ok border-ok/30",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium font-mono uppercase tracking-wider",
        variants[variant] || variants.default,
        className
      )}
    >
      {children}
    </span>
  );
}
