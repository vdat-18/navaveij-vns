"use client";

import React, { useMemo, useState } from "react";
import { AuditLogEntry, AuditLogFilters } from "@/types/access-monitoring";

interface AuditLogSearchPanelProps {
  entries: AuditLogEntry[];
  total: number;
  filters: AuditLogFilters;
  onFilterChange: (next: AuditLogFilters) => void;
  onSearch: () => Promise<void>;
}

export function AuditLogSearchPanel({
  entries,
  total,
  filters,
  onFilterChange,
  onSearch,
}: AuditLogSearchPanelProps) {
  const [selectedEntry, setSelectedEntry] = useState<AuditLogEntry | null>(null);
  const [verifyResult, setVerifyResult] = useState<"idle" | "pass" | "fail">("idle");

  const actionOptions = useMemo(
    () => ["", "View", "Export", "Generate", "Decision", "AdminUpdate"],
    []
  );

  const verifyHash = async (entry: AuditLogEntry) => {
    const payload = {
      prev_entry_hash: entry.prev_entry_hash,
      who: entry.who,
      when: entry.when,
      where: entry.where,
      what: entry.what,
      why: entry.why,
      retention_expiry: entry.retention_expiry,
    };
    const input = stableStringify(payload);
    const encoded = new TextEncoder().encode(input);
    const digest = await crypto.subtle.digest("SHA-256", encoded);
    const hash = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    setVerifyResult(hash === entry.sha256_hash ? "pass" : "fail");
  };

  return (
    <div className="navavej-card p-6 space-y-4">
      <h3 className="text-sm font-black uppercase tracking-widest text-navavej-gray-dark">Audit Log Search</h3>
      <div className="grid grid-cols-2 xl:grid-cols-3 gap-2">
        <input
          placeholder="user_id"
          value={filters.user_id || ""}
          onChange={(e) => onFilterChange({ ...filters, user_id: e.target.value })}
          className="rounded-lg border border-navavej-border px-3 py-2 text-xs font-bold"
        />
        <input
          placeholder="patient token prefix"
          value={filters.patient_token_prefix || ""}
          onChange={(e) => onFilterChange({ ...filters, patient_token_prefix: e.target.value })}
          className="rounded-lg border border-navavej-border px-3 py-2 text-xs font-bold"
        />
        <select
          value={filters.action_type || ""}
          onChange={(e) => onFilterChange({ ...filters, action_type: e.target.value })}
          className="rounded-lg border border-navavej-border px-3 py-2 text-xs font-bold"
        >
          {actionOptions.map((option) => (
            <option key={option || "all"} value={option}>
              {option || "All actions"}
            </option>
          ))}
        </select>
      </div>
      <button
        type="button"
        onClick={onSearch}
        className="px-4 py-2 rounded-lg bg-navavej-teal text-white text-xs font-black uppercase tracking-widest"
      >
        Search ({total})
      </button>

      <div className="max-h-[320px] overflow-y-auto border border-navavej-border rounded-xl">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-navavej-gray-light/50">
              <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">When</th>
              <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Who</th>
              <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">What</th>
              <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Patient</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr
                key={entry.entry_id}
                onClick={() => {
                  setSelectedEntry(entry);
                  setVerifyResult("idle");
                }}
                className="border-t border-navavej-border hover:bg-navavej-gray-light/30 cursor-pointer"
              >
                <td className="px-3 py-2 text-[11px] font-bold">{new Date(entry.when.iso_timestamp_utc).toLocaleString()}</td>
                <td className="px-3 py-2 text-[11px] font-bold">{entry.who.user_id}</td>
                <td className="px-3 py-2 text-[11px] font-bold">{entry.what.action_type}</td>
                <td className="px-3 py-2 text-[11px] font-bold">{entry.what.patient_token_masked || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedEntry && (
        <div className="rounded-xl border border-navavej-border p-4 bg-white space-y-2">
          <p className="text-[10px] font-black uppercase tracking-widest text-navavej-gray-med">Who / When / Where / What / Why</p>
          <p className="text-xs font-bold">{selectedEntry.who.user_display_name} ({selectedEntry.who.user_role})</p>
          <p className="text-xs font-bold">{selectedEntry.when.iso_timestamp_utc}</p>
          <p className="text-xs font-bold">{selectedEntry.where.service_id}</p>
          <p className="text-xs font-bold">{selectedEntry.what.action_type} • {selectedEntry.what.resource_type}</p>
          <p className="text-xs font-bold">{selectedEntry.why.request_context}</p>
          <p className="text-xs font-mono break-all">{selectedEntry.sha256_hash}</p>
          <p className="text-xs font-mono break-all">{selectedEntry.prev_entry_hash}</p>
          <button
            type="button"
            onClick={() => verifyHash(selectedEntry)}
            className="px-3 py-1 rounded-lg border border-navavej-border text-[10px] font-black uppercase"
          >
            Verify Hash
          </button>
          {verifyResult === "pass" && <p className="text-xs font-black text-green-600">Hash verification passed</p>}
          {verifyResult === "fail" && <p className="text-xs font-black text-red-600">Hash verification failed</p>}
        </div>
      )}
    </div>
  );
}

function stableStringify(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  const objectValue = value as Record<string, unknown>;
  const keys = Object.keys(objectValue).sort();
  return `{${keys
    .map((key) => `${JSON.stringify(key)}:${stableStringify(objectValue[key])}`)
    .join(",")}}`;
}
