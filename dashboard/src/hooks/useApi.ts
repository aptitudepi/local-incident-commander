import { useState, useEffect, useCallback, useRef } from "react";
import type { Incident, Report, Triage, Costs, SystemHealth, Stats, InboxEvent } from "../types";

const API_BASE = "/api";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

export function usePolling<T>(url: string, intervalMs: number = 2000): { data: T | null; loading: boolean } {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const mountedRef = useRef(true);

  const fetch_ = useCallback(async () => {
    try {
      const result = await fetchJson<T>(url);
      if (mountedRef.current) {
        setData(result);
        setLoading(false);
      }
    } catch {
      if (mountedRef.current) setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    mountedRef.current = true;
    fetch_();
    const id = setInterval(fetch_, intervalMs);
    return () => {
      mountedRef.current = false;
      clearInterval(id);
    };
  }, [fetch_, intervalMs]);

  return { data, loading };
}

export function useIncidents(intervalMs?: number) {
  return usePolling<Incident[]>(`${API_BASE}/incidents`, intervalMs);
}

export function useReports(intervalMs?: number) {
  return usePolling<Report[]>(`${API_BASE}/reports`, intervalMs);
}

export function useTriages(intervalMs?: number) {
  return usePolling<Triage[]>(`${API_BASE}/triages`, intervalMs);
}

export function useCosts(intervalMs?: number) {
  return usePolling<Costs>(`${API_BASE}/costs`, intervalMs);
}

export function useSystemHealth(intervalMs?: number) {
  return usePolling<SystemHealth>(`${API_BASE}/health/system`, intervalMs);
}

export function useStats(intervalMs?: number) {
  return usePolling<Stats>(`${API_BASE}/stats`, intervalMs);
}

export function useEvents(intervalMs?: number) {
  return usePolling<InboxEvent[]>(`${API_BASE}/events`, intervalMs);
}
