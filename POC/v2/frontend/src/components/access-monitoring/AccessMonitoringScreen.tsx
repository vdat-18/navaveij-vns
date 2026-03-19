"use client";

import React, { useEffect, useState } from "react";
import { clinicalService } from "@/services/api";
import { AuditLogEntry, AuditLogFilters, AnomalyAlert, MappingCode, MasterProgram, MonitoringSnapshot, RbacRole } from "@/types/access-monitoring";
import { LiveMetricsBar } from "./LiveMetricsBar";
import { AnomalyAlertsPanel } from "./AnomalyAlertsPanel";
import { AuditLogSearchPanel } from "./AuditLogSearchPanel";
import { RoleManagementTab } from "./RoleManagementTab";
import { MappingToolTab } from "./MappingToolTab";
import { MasterDataTab } from "./MasterDataTab";

interface AccessMonitoringScreenProps {
  role: "admin" | "dpo";
}

type TabKey = "role" | "mapping" | "master";

export function AccessMonitoringScreen({ role }: AccessMonitoringScreenProps) {
  const [snapshot, setSnapshot] = useState<MonitoringSnapshot | null>(null);
  const [alerts, setAlerts] = useState<AnomalyAlert[]>([]);
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [roles, setRoles] = useState<RbacRole[]>([]);
  const [mappings, setMappings] = useState<MappingCode[]>([]);
  const [programs, setPrograms] = useState<MasterProgram[]>([]);
  const [filters, setFilters] = useState<AuditLogFilters>({});
  const [tab, setTab] = useState<TabKey>("role");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadScreen = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [snapshotData, alertData, auditData, rbacData, mappingData, masterData] = await Promise.all([
        clinicalService.getMonitoringSnapshot(role),
        clinicalService.getAnomalyAlerts(role),
        clinicalService.searchAuditLogs({}, role),
        clinicalService.getRbac(role),
        clinicalService.getMappingCodes(role),
        clinicalService.getMasterPrograms(role),
      ]);
      setSnapshot(snapshotData);
      setAlerts(alertData.alerts);
      setEntries(auditData.entries);
      setTotal(auditData.total);
      setRoles(rbacData.roles);
      setMappings(mappingData.mappings);
      setPrograms(masterData.programs);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to load access monitoring data.";
      setErrorMessage(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    loadScreen();
    const interval = setInterval(() => {
      clinicalService.getMonitoringSnapshot(role).then((data) => {
        if (active) {
          setSnapshot(data);
        }
      }).catch(() => null);
    }, 30000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [role]);

  const runAuditSearch = async () => {
    try {
      setErrorMessage(null);
      const auditData = await clinicalService.searchAuditLogs(filters, role);
      setEntries(auditData.entries);
      setTotal(auditData.total);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to run audit search.";
      setErrorMessage(message);
    }
  };

  return (
    <div className="space-y-6">
      {isLoading && (
        <div className="navavej-card bg-white p-4 border border-navavej-border">
          <p className="text-xs font-black text-navavej-gray-med uppercase">
            Loading access monitoring data...
          </p>
        </div>
      )}
      {errorMessage && (
        <div className="navavej-card bg-[#fff5f5] p-4 border border-navavej-red/30">
          <p className="text-xs font-black text-navavej-red uppercase">
            Data load warning
          </p>
          <p className="text-xs font-bold text-navavej-gray-dark mt-2">{errorMessage}</p>
        </div>
      )}
      <LiveMetricsBar snapshot={snapshot} />
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <AnomalyAlertsPanel alerts={alerts} />
        <AuditLogSearchPanel
          entries={entries}
          total={total}
          filters={filters}
          onFilterChange={setFilters}
          onSearch={runAuditSearch}
        />
      </div>

      <div className="flex gap-2 border-b border-navavej-border">
        <TabButton label="Role Management" active={tab === "role"} onClick={() => setTab("role")} />
        <TabButton label="Mapping Tool" active={tab === "mapping"} onClick={() => setTab("mapping")} />
        <TabButton label="Master Data" active={tab === "master"} onClick={() => setTab("master")} />
      </div>

      {tab === "role" && <RoleManagementTab roles={roles} />}
      {tab === "mapping" && <MappingToolTab mappings={mappings} />}
      {tab === "master" && <MasterDataTab programs={programs} />}
    </div>
  );
}

function TabButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-4 py-2 text-xs font-black uppercase tracking-widest border-b-2 ${
        active ? "text-navavej-teal border-navavej-teal" : "text-navavej-gray-med border-transparent"
      }`}
    >
      {label}
    </button>
  );
}
