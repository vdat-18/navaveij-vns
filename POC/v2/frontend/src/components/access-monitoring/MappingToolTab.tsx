"use client";

import React from "react";
import { MappingCode } from "@/types/access-monitoring";

interface MappingToolTabProps {
  mappings: MappingCode[];
}

export function MappingToolTab({ mappings }: MappingToolTabProps) {
  return (
    <div className="navavej-card p-6 overflow-auto">
      <h3 className="text-sm font-black uppercase tracking-widest text-navavej-gray-dark mb-4">Mapping Tool</h3>
      <table className="w-full text-left min-w-[760px]">
        <thead>
          <tr className="bg-navavej-gray-light/40">
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Local</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Local System</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Target</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Target System</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Target Label</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Map Type</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Status</th>
          </tr>
        </thead>
        <tbody>
          {mappings.map((mapping) => (
            <tr key={mapping.mapping_id} className="border-t border-navavej-border">
              <td className="px-3 py-2 text-xs font-black">{mapping.local_code}</td>
              <td className="px-3 py-2 text-xs font-bold">{mapping.local_system}</td>
              <td className="px-3 py-2 text-xs font-bold">{mapping.target_code}</td>
              <td className="px-3 py-2 text-xs font-bold">{mapping.target_system}</td>
              <td className="px-3 py-2 text-xs font-bold">{mapping.target_label}</td>
              <td className="px-3 py-2 text-xs font-bold">{mapping.mapping_type}</td>
              <td className="px-3 py-2 text-xs font-bold">{mapping.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
