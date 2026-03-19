"use client";

import React from "react";
import { MasterProgram } from "@/types/access-monitoring";

interface MasterDataTabProps {
  programs: MasterProgram[];
}

export function MasterDataTab({ programs }: MasterDataTabProps) {
  return (
    <div className="navavej-card p-6 overflow-auto">
      <h3 className="text-sm font-black uppercase tracking-widest text-navavej-gray-dark mb-4">Master Data</h3>
      <table className="w-full text-left min-w-[760px]">
        <thead>
          <tr className="bg-navavej-gray-light/40">
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Code</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Program</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Price THB</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Target Ages</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Gender</th>
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Status</th>
          </tr>
        </thead>
        <tbody>
          {programs.map((program) => (
            <tr key={program.program_code} className="border-t border-navavej-border">
              <td className="px-3 py-2 text-xs font-black">{program.program_code}</td>
              <td className="px-3 py-2 text-xs font-bold">{program.program_name}</td>
              <td className="px-3 py-2 text-xs font-bold">{program.price_thb.toLocaleString()}</td>
              <td className="px-3 py-2 text-xs font-bold">{program.target_ages}</td>
              <td className="px-3 py-2 text-xs font-bold">{program.gender}</td>
              <td className="px-3 py-2 text-xs font-bold">{program.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
