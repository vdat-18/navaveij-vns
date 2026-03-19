"use client";

import React from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { BiomarkerSeries } from "@/types/timeline";

interface BiomarkerTrendGridProps {
  series: BiomarkerSeries[];
}

const TrendTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-navavej-border rounded-xl px-3 py-2 shadow-lg">
      <p className="text-[10px] font-black text-navavej-gray-med uppercase tracking-wider">{label}</p>
      <p className="text-xs font-black text-navavej-gray-dark mt-1">{payload[0].value}</p>
    </div>
  );
};

export function BiomarkerTrendGrid({ series }: BiomarkerTrendGridProps) {
  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
      {series.map((item) => (
        <div key={`${item.label}-${item.loinc_code}`} className="navavej-card bg-white p-5">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h4 className="text-[11px] font-black text-navavej-gray-dark uppercase tracking-widest">{item.label}</h4>
              <p className="text-[10px] font-bold text-navavej-gray-med mt-1">LOINC {item.loinc_code}</p>
            </div>
            <span className="text-[9px] font-black text-navavej-teal uppercase">{item.trend_direction}</span>
          </div>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={item.history}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E9ECEF" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 9, fontWeight: 700, fill: "#666" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 9, fontWeight: 700, fill: "#666" }} />
                <Tooltip content={<TrendTooltip />} />
                {typeof item.reference === "number" && (
                  <ReferenceLine y={item.reference} stroke="#9D0A31" strokeDasharray="4 4" />
                )}
                <Line
                  name={item.label}
                  type="monotone"
                  dataKey="value"
                  stroke="#00ABC7"
                  strokeWidth={3}
                  dot={{ r: 3.5, fill: "#00ABC7", strokeWidth: 2, stroke: "#fff" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-[10px] font-bold text-navavej-gray-med">
            <span>Now: {item.current} {item.unit}</span>
            <span>Ref: {typeof item.reference === "number" ? item.reference : "N/A"}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
