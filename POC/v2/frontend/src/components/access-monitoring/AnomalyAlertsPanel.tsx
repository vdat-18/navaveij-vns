"use client";

import React, { useMemo, useState } from "react";
import { AnomalyAlert } from "@/types/access-monitoring";

interface AnomalyAlertsPanelProps {
  alerts: AnomalyAlert[];
}

export function AnomalyAlertsPanel({ alerts }: AnomalyAlertsPanelProps) {
  const [statusMap, setStatusMap] = useState<Record<string, AnomalyAlert["status"]>>({});

  const normalized = useMemo(
    () =>
      alerts.map((alert) => ({
        ...alert,
        status: statusMap[alert.alert_id] || alert.status,
      })),
    [alerts, statusMap]
  );

  return (
    <div className="navavej-card p-6 space-y-3">
      <h3 className="text-sm font-black uppercase tracking-widest text-navavej-gray-dark">Anomaly Alerts</h3>
      <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
        {normalized.map((alert) => (
          <div key={alert.alert_id} className="rounded-xl border border-navavej-border p-4 bg-white">
            <div className="flex items-center justify-between gap-3">
              <p className="text-xs font-black text-navavej-gray-dark">{alert.user_display_name}</p>
              <span className="text-[10px] font-black uppercase tracking-widest text-navavej-teal">{alert.severity}</span>
            </div>
            <p className="text-[11px] mt-1 text-navavej-gray-med font-bold">{alert.alert_type} • {alert.department}</p>
            <p className="text-[11px] text-navavej-gray-med mt-1">Triggered: {new Date(alert.triggered_at).toLocaleString()}</p>
            <div className="mt-3 flex items-center gap-2">
              <button
                type="button"
                onClick={() => setStatusMap((prev) => ({ ...prev, [alert.alert_id]: "Acknowledged" }))}
                className="px-3 py-1 rounded-lg border border-navavej-border text-[10px] font-black uppercase"
              >
                Acknowledge
              </button>
              <button
                type="button"
                onClick={() => setStatusMap((prev) => ({ ...prev, [alert.alert_id]: "Resolved" }))}
                className="px-3 py-1 rounded-lg bg-navavej-teal text-white text-[10px] font-black uppercase"
              >
                Resolve
              </button>
              <span className="ml-auto text-[10px] font-black uppercase tracking-widest text-navavej-gray-med">
                {statusMap[alert.alert_id] || alert.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
