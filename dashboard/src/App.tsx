import "./index.css";
import { useIncidents, useReports, useTriages, useCosts, useSystemHealth, useStats, useEvents } from "./hooks/useApi";
import { Header } from "./components/Header";
import { StatusBar } from "./components/StatusBar";
import { IncidentTimeline } from "./components/IncidentTimeline";
import { SeverityDistribution } from "./components/SeverityDistribution";
import { ServiceBreakdown } from "./components/ServiceBreakdown";
import { TriageResults } from "./components/TriageResults";
import { PostIncidentReports } from "./components/PostIncidentReports";
import { CostTracker } from "./components/CostTracker";
import { SavingsChart } from "./components/SavingsChart";
import { SystemHealth } from "./components/SystemHealth";
import { PolicyDenials } from "./components/PolicyDenials";
import { ActivityFeed } from "./components/ActivityFeed";

const POLL_INTERVAL = 2000;

export default function App() {
  const { data: incidents } = useIncidents(POLL_INTERVAL);
  const { data: reports } = useReports(POLL_INTERVAL);
  const { data: triages } = useTriages(POLL_INTERVAL);
  const { data: costs } = useCosts(POLL_INTERVAL);
  const { data: health } = useSystemHealth(POLL_INTERVAL);
  const { data: stats } = useStats(POLL_INTERVAL);
  const { data: events } = useEvents(POLL_INTERVAL);

  return (
    <div className="flex h-full flex-col gap-3 p-3">
      <Header stats={stats} health={health} />

      <div className="flex flex-1 gap-3 min-h-0">
        <aside className="w-56 flex flex-col gap-3 min-h-0">
          <StatusBar stats={stats} />
          <ActivityFeed events={events} />
        </aside>

        <main className="flex-1 grid grid-cols-3 gap-3 min-h-0">
          <div className="col-span-3">
            <IncidentTimeline incidents={incidents} />
          </div>

          <SeverityDistribution incidents={incidents} />
          <ServiceBreakdown incidents={incidents} />
          <CostTracker costs={costs} stats={stats} />

          <div className="col-span-2">
            <TriageResults triages={triages} />
          </div>
          <SystemHealth health={health} />

          <div className="col-span-3">
            <SavingsChart costs={costs} />
          </div>

          <div className="col-span-3">
            <PostIncidentReports reports={reports} />
          </div>

          {costs?.blocked_actions && costs.blocked_actions.length > 0 && (
            <div className="col-span-3">
              <PolicyDenials blockedActions={costs.blocked_actions} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
