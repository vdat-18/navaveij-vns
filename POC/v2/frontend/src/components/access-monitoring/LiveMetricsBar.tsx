"use client";

import React from "react";
import { MonitoringSnapshot } from "@/types/access-monitoring";

interface LiveMetricsBarProps {
  snapshot: MonitoringSnapshot | null;
}

export function LiveMetricsBar({ snapshot }: LiveMetricsBarProps) {
  if (!snapshot) {
    return <div className="navavej-card p-6 text-xs font-bold text-navavej-gray-med">Loading snapshot...</div>;
  }

  return (
    <div className="navavej-card p-6 space-y-4">
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        <MetricCard label="Active Users" value={snapshot.active_users_now} />
        <MetricCard label="Sessions Today" value={snapshot.sessions_today} />
        <MetricCard label="Records Today" value={snapshot.patient_records_accessed_today} />
        <MetricCard
          label="Alerts"
          value={`${snapshot.alert_counts.critical}/${snapshot.alert_counts.high}/${snapshot.alert_counts.medium}/${snapshot.alert_counts.low}`}
        />
      </div>
      <div className="flex flex-wrap gap-4 text-[11px] font-bold text-navavej-gray-med">
        <span>AI Recommendations Today: {snapshot.ai_recommendations_generated_today}</span>
        <span>Safety Validator Failures: {snapshot.safety_validator_failures_today}</span>
        <span>Snapshot: {new Date(snapshot.snapshot_at).toLocaleString()}</span>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-navavej-border bg-white p-4">
      <p className="text-[10px] uppercase tracking-widest font-black text-navavej-gray-med">{label}</p>
      <p className="text-2xl font-black text-navavej-gray-dark mt-2">{value}</p>
    </div>
  );
}
