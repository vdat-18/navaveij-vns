export interface TimelineSpan {
  earliest_event_date: string;
  latest_event_date: string;
  total_years_covered: number;
}

export interface TimelineDiagnosisEvent {
  event_id: string;
  date: string;
  onset_year?: number;
  onset_type?: string;
  icd10_code: string;
  snomed_code?: string;
  label: string;
  clinical_status?: string;
  fhir_condition_id?: string;
}

export interface TimelineLabEvent {
  event_id: string;
  date: string;
  loinc_code: string;
  label: string;
  value: number;
  unit: string;
  interpretation: string;
  threshold_crossed: string;
}

export interface TimelineProcedureEvent {
  event_id: string;
  date: string;
  days_ago?: number;
  procedure_code?: string;
  cpt_code?: string;
  snomed_code?: string;
  label: string;
  status: string;
  result_summary: string;
  fhir_procedure_id?: string;
}

export interface TimelineMedicationEvent {
  event_id: string;
  date: string;
  drug_name: string;
  change_type: string;
  dose: string;
}

export interface TimelinePayload {
  patient_token: string;
  timeline_span: TimelineSpan;
  diagnoses: TimelineDiagnosisEvent[];
  hospitalizations: Record<string, unknown>[];
  significant_lab_events: TimelineLabEvent[];
  screening_procedure_history: TimelineProcedureEvent[];
  medication_changes: TimelineMedicationEvent[];
  pipeline_run_id: string;
  computed_at: string;
}

export interface BiomarkerHistoryEntry {
  date: string;
  value?: number;
  sbp?: number;
  dbp?: number;
}

export interface BiomarkerSeries {
  label: string;
  loinc_code: string;
  unit: string;
  trend_direction: string;
  slope_per_year: number | null;
  reference?: number;
  current: number;
  history: BiomarkerHistoryEntry[];
}

export interface ScreeningGapRow {
  screening_id?: string;
  vaccine_id?: string;
  label: string;
  overdue_days?: number | null;
  priority_color?: string;
  last_performed_date?: string | null;
  last_administered_date?: string | null;
  note?: string;
}
