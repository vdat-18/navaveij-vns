"use client";

import React, { useMemo } from "react";
import { TimelinePayload } from "@/types/timeline";

interface ClinicalEventTimelineProps {
  timeline: TimelinePayload | null;
  startYear: number;
}

export function ClinicalEventTimeline({ timeline, startYear }: ClinicalEventTimelineProps) {
  const rows = useMemo(() => {
    if (!timeline) return [];
    const timelineRows: Array<{ date: string; type: string; title: string; detail: string; terminology: string }> = [];
    for (const item of timeline.diagnoses) {
      const terminology = [item.icd10_code ? `ICD10 ${item.icd10_code}` : "", item.snomed_code ? `SNOMED ${item.snomed_code}` : ""]
        .filter(Boolean)
        .join(" • ");
      timelineRows.push({
        date: item.date,
        type: "Diagnosis",
        title: item.label,
        detail: item.clinical_status || "active",
        terminology: terminology || "N/A",
      });
    }
    for (const item of timeline.significant_lab_events) {
      timelineRows.push({
        date: item.date,
        type: "Lab",
        title: item.label,
        detail: `${item.value} ${item.unit}`,
        terminology: item.loinc_code ? `LOINC ${item.loinc_code}` : "N/A",
      });
    }
    for (const item of timeline.screening_procedure_history) {
      const terminology = [item.cpt_code ? `CPT ${item.cpt_code}` : "", item.snomed_code ? `SNOMED ${item.snomed_code}` : ""]
        .filter(Boolean)
        .join(" • ");
      timelineRows.push({
        date: item.date,
        type: "Screening",
        title: item.label,
        detail: item.result_summary,
        terminology: terminology || (item.procedure_code ? `Code ${item.procedure_code}` : "N/A"),
      });
    }
    for (const item of timeline.medication_changes) {
      timelineRows.push({
        date: item.date,
        type: "Medication",
        title: item.drug_name,
        detail: item.change_type,
        terminology: "N/A",
      });
    }
    return timelineRows
      .filter((item) => Number(item.date.slice(0, 4)) >= startYear)
      .sort((a, b) => (a.date < b.date ? -1 : 1));
  }, [timeline, startYear]);

  return (
    <div className="navavej-card bg-white p-5">
      <h4 className="text-[11px] font-black text-navavej-gray-dark uppercase tracking-widest mb-4">
        Clinical Event Timeline
      </h4>
      <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
        {rows.map((row, idx) => (
          <div key={`${row.date}-${row.type}-${idx}`} className="border border-navavej-border rounded-xl p-3">
            <div className="flex justify-between items-center mb-1">
              <span className="text-[10px] font-black text-navavej-teal uppercase">{row.type}</span>
              <span className="text-[10px] font-bold text-navavej-gray-med">{row.date}</span>
            </div>
            <p className="text-xs font-black text-navavej-gray-dark">{row.title}</p>
            <p className="text-[10px] font-bold text-navavej-gray-med mt-1">{row.detail}</p>
            <p className="text-[10px] font-bold text-navavej-teal mt-1">{row.terminology}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
