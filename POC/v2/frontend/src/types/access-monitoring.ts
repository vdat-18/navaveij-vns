export interface AlertCounts {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface MonitoringSnapshot {
  snapshot_at: string;
  refresh_interval_seconds: number;
  active_users_now: number;
  sessions_today: number;
  patient_records_accessed_today: number;
  ai_recommendations_generated_today: number;
  alert_counts: AlertCounts;
  safety_validator_failures_today: number;
  top_active_departments: Array<{ department: string; active_users: number }>;
}

export interface AnomalyAlert {
  alert_id: string;
  user_id: string;
  user_display_name: string;
  department: string;
  alert_type: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  triggered_at: string;
  detail: Record<string, unknown>;
  status: "Open" | "Acknowledged" | "Resolved";
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  resolution_note: string | null;
}

export interface AuditLogFilters {
  user_id?: string;
  patient_token_prefix?: string;
  action_type?: string;
  resource_type?: string;
  start_date?: string;
  end_date?: string;
}

export interface AuditLogEntry {
  entry_id: string;
  sha256_hash: string;
  prev_entry_hash: string;
  who: {
    user_id: string;
    user_display_name: string;
    user_role: string;
    department: string;
  };
  when: {
    iso_timestamp_utc: string;
    local_timestamp_ict: string;
  };
  where: {
    service_id: string;
    source_ip_hash: string;
    request_id: string;
    user_agent_class: string;
  };
  what: {
    action_type: string;
    resource_type: string;
    patient_token: string | null;
    patient_token_masked: string | null;
    model_id: string | null;
    template_version: string | null;
    latency_ms: number | null;
    safety_validator_result: string | null;
    recommendation_source: string | null;
  };
  why: {
    request_context: string;
    indication_code: string;
  };
  retention_expiry: string;
}

export interface RbacRole {
  role_id: string;
  label: string;
  permissions: Record<string, string[]>;
}

export interface MappingCode {
  mapping_id: string;
  local_code: string;
  local_system: string;
  local_label: string;
  target_code: string;
  target_system: string;
  target_label: string;
  mapping_type: string;
  status: string;
  validated_by_user_id: string;
  validated_at: string;
  last_updated_by_user_id: string;
  last_updated_at: string;
  notes: string;
  standard_code?: string;
  standard_system?: string;
  display?: string;
}

export interface MasterProgram {
  program_code: string;
  program_name: string;
  price_thb: number;
  target_ages: string;
  gender: string;
  status: string;
}
