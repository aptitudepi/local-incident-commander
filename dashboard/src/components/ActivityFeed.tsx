import { motion, AnimatePresence } from "motion/react";
import type { InboxEvent } from "../types";
import { Card, CardHeader, CardTitle, CardBadge, CardContent } from "./ui/Card";
import { SeverityDot } from "./ui/SeverityBadge";

const eventIcons: Record<string, string> = {
  alert: "⚠",
  deploy: "⟳",
  log: "□",
  webhook: "↗",
};

export function ActivityFeed({ events }: { events?: InboxEvent[] | null }) {
  const items = (events || []).slice(0, 20);
  return (
    <Card className="flex-1 min-h-0">
      <CardHeader>
        <CardTitle>Activity Feed</CardTitle>
        <CardBadge>{events?.length ?? 0} events</CardBadge>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="flex h-full items-center justify-center text-dim font-mono text-xs">
            Watching inbox...
          </div>
        ) : (
          <div className="flex flex-col gap-1">
            <AnimatePresence initial={false}>
              {items.map((ev, i) => (
                <motion.div
                  key={`${ev.timestamp}-${i}`}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: i * 0.03 }}
                  className="flex items-start gap-2 rounded-lg border border-line bg-panel2 p-2"
                >
                  <span className="text-xs mt-0.5">{eventIcons[ev.event_type] || "□"}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className="font-mono text-[11px] text-hi font-semibold truncate">{ev.service || "?"}</span>
                      <SeverityDot severity={ev.severity || "low"} />
                    </div>
                    <div className="font-mono text-[10px] text-dim truncate">
                      {ev.event_type || "event"}
                      {ev.timestamp && ` · ${new Date(ev.timestamp).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
