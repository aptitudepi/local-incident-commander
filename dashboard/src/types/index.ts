export interface Incident {
  incident_id: string;
  service: string;
  severity: string;
  timestamp: string;
  summary?: string;
  status?: string;
  events?: unknown[];
  event_count?: number;
  probable_root_cause?: string;
  evidence?: string[];
  recommended_action?: string;
  requires_human_approval?: boolean;
}

export interface Report {
  incident_id: string;
  service: string;
  severity: string;
  status: string;
  timestamp: string;
  title?: string;
  probable_root_cause?: string;
  evidence?: string[];
  recommended_action?: string;
}

export interface Triage {
  service: string;
  severity: string;
  root_cause: string;
  suggested_fix: string;
  incident_id?: string;
  timestamp?: string;
}

export interface Costs {
  total_events_processed?: number;
  total_incidents_resolved?: number;
  total_actions_blocked?: number;
  total_saved?: number;
  cloud_api_calls_avoided?: number;
  splunk_cost_saved?: number;
  pagerduty_cost_saved?: number;
  cloud_api_cost_saved?: number;
  blocked_actions?: BlockedAction[];
}

export interface BlockedAction {
  action: string;
  policy_id: string;
  reason: string;
  timestamp: string;
}

export interface SystemHealth {
  timestamp?: string;
  pipeline?: {
    watcher: string;
    correlator: string;
    llm_endpoint: string;
    last_event_time: string;
  };
  model?: {
    vllm_running: boolean;
    model_loaded: boolean;
    fallback_available: boolean;
  };
  queue?: {
    inbox_count: number;
    unprocessed_events: number;
  };
  performance?: {
    fix_success_rate: number;
    total_fixes_attempted: number;
    total_fixes_succeeded: number;
    incidents_resolved_today: number;
  };
  system?: {
    uptime: number;
    disk_usage: { total_gb: number; used_gb: number; free_gb: number; percent: number };
    memory_available: { total_mb: number; available_mb: number; free_mb: number };
  };
}

export interface Stats {
  total_incidents: number;
  critical_count: number;
  high_count: number;
  total_saved: number;
  inbox_count: number;
  report_count: number;
  triage_count: number;
  report_count_detail: number;
}

export interface InboxEvent {
  service: string;
  event_type: string;
  severity?: string;
  timestamp: string;
  payload?: Record<string, unknown>;
  _source?: string;
}
