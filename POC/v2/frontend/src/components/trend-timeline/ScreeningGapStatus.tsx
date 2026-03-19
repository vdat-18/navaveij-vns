"use client";

import React from "react";
import { ScreeningGapRow } from "@/types/timeline";

interface ScreeningGapStatusProps {
  screeningGaps: ScreeningGapRow[];
}

const priorityClass = (priority?: string) => {
  if (priority === "Red") return "text-navavej-red";
  if (priority === "Orange") return "text-orange-500";
  return "text-navavej-gray-med";
};

export function ScreeningGapStatus({ screeningGaps }: ScreeningGapStatusProps) {
  return (
    <div className="navavej-card bg-white p-5">
      <h4 className="text-[11px] font-black text-navavej-gray-dark uppercase tracking-widest mb-4">
        Screening Gap Status
      </h4>
      <div className="space-y-3">
        {screeningGaps.map((gap, idx) => (
          <div key={`${gap.label}-${idx}`} className="border border-navavej-border rounded-xl p-3">
            <div className="flex justify-between items-center">
              <p className="text-xs font-black text-navavej-gray-dark">{gap.label}</p>
              <span className={`text-[10px] font-black uppercase ${priorityClass(gap.priority_color)}`}>
                {gap.priority_color || "N/A"}
              </span>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 text-[10px] font-bold text-navavej-gray-med">
              <span>Overdue: {gap.overdue_days ?? "Never"} days</span>
              <span>Last: {gap.last_performed_date || gap.last_administered_date || "Never"}</span>
            </div>
            {gap.note && <p className="text-[10px] text-navavej-gray-med mt-2">{gap.note}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
