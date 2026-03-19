import axios from "axios";
import { AuditLogEntry, AuditLogFilters, AnomalyAlert, MappingCode, MasterProgram, MonitoringSnapshot, RbacRole } from "@/types/access-monitoring";
import { TimelinePayload } from "@/types/timeline";

const API_BASE_URL_V1 = process.env.NEXT_PUBLIC_API_URL_V1 || "http://localhost:8000/api/v1";
const API_BASE_URL_V3 = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const AUTH_USER_ID = process.env.NEXT_PUBLIC_AUTH_USER_ID || "usr-admin-00001";
const AUTH_ROLE = (process.env.NEXT_PUBLIC_AUTH_ROLE || "admin").toLowerCase();
const AUTH_SCOPES = process.env.NEXT_PUBLIC_AUTH_SCOPES || "recommendation:read,recommendation:write,monitoring:read";

const apiV1 = axios.create({
    baseURL: API_BASE_URL_V1,
    headers: {
        "Content-Type": "application/json",
    },
});

const apiV3 = axios.create({
    baseURL: API_BASE_URL_V3,
    headers: {
        "Content-Type": "application/json",
    },
});

const mergeScopes = (...scopeGroups: string[]): string => {
    const merged = new Set<string>();
    for (const group of scopeGroups) {
        for (const scope of group.split(",").map((item) => item.trim().toLowerCase()).filter(Boolean)) {
            merged.add(scope);
        }
    }
    return Array.from(merged).join(",");
};

const buildAuthHeaders = (roleOverride?: string, scopeOverride?: string) => {
    const role = (roleOverride || AUTH_ROLE).toLowerCase();
    return {
        "X-Auth-User-Id": AUTH_USER_ID,
        "X-Auth-Role": role,
        "X-Auth-Scopes": mergeScopes(AUTH_SCOPES, scopeOverride || ""),
    };
};

export const patientService = {
    getAll: async () => {
        const response = await apiV1.get("/patients", { headers: buildAuthHeaders() });
        return response.data;
    },
    getDetails: async (id: string) => {
        const response = await apiV1.get(`/patients/${id}`, { headers: buildAuthHeaders() });
        return response.data;
    },
};

export const clinicalService = {
    getRecommendation: async (patientToken: string, forceRuleBased: boolean = false) => {
        const response = await apiV3.post(
            "/recommend",
            {
                patient_token: patientToken,
                force_rule_based: forceRuleBased
            },
            { headers: buildAuthHeaders(undefined, "recommendation:read") }
        );
        return response.data;
    },
    recordDecision: async (patientId: string, recommendationHash: string, decision: "Approve" | "Reject", notes: string = "") => {
        const response = await apiV1.post(
            "/clinical/approve",
            {
                patient_id: patientId,
                recommendation_hash: recommendationHash,
                decision: decision,
                physician_id: "dr-admin-001",
                notes: notes
            },
            { headers: buildAuthHeaders(undefined, "recommendation:write") }
        );
        return response.data;
    },
    getAuditLogs: async () => {
        const response = await apiV1.get("/clinical/audit", { headers: buildAuthHeaders(undefined, "recommendation:read") });
        return response.data;
    },
    getTimeline: async (patientToken: string): Promise<TimelinePayload> => {
        const response = await apiV3.get(`/timeline/${patientToken}`, { headers: buildAuthHeaders(undefined, "recommendation:read") });
        return response.data;
    },
    getBiomarkerTrends: async (patientToken: string) => {
        const response = await apiV3.get(`/biomarker-trends/${patientToken}`, { headers: buildAuthHeaders(undefined, "recommendation:read") });
        return response.data;
    },
    getScreeningGaps: async (patientToken: string) => {
        const response = await apiV3.get(`/screening-gaps/${patientToken}`, { headers: buildAuthHeaders(undefined, "recommendation:read") });
        return response.data;
    },
    getMonitoringSnapshot: async (role: "admin" | "dpo" = "admin"): Promise<MonitoringSnapshot> => {
        const response = await apiV3.get("/monitoring-snapshot", {
            headers: buildAuthHeaders(role, "monitoring:read")
        });
        return response.data;
    },
    getAnomalyAlerts: async (role: "admin" | "dpo" = "admin"): Promise<{ alerts: AnomalyAlert[] }> => {
        const response = await apiV3.get("/anomaly-alerts", {
            headers: buildAuthHeaders(role, "monitoring:read")
        });
        return response.data;
    },
    searchAuditLogs: async (
        filters: AuditLogFilters,
        role: "admin" | "dpo" = "admin"
    ): Promise<{ total: number; entries: AuditLogEntry[] }> => {
        const response = await apiV3.get("/audit-logs", {
            params: filters,
            headers: buildAuthHeaders(role, "monitoring:read")
        });
        return response.data;
    },
    getRbac: async (role: "admin" | "dpo" = "admin"): Promise<{ roles: RbacRole[] }> => {
        const response = await apiV3.get("/rbac", {
            headers: buildAuthHeaders(role, "monitoring:read")
        });
        return response.data;
    },
    getMappingCodes: async (role: "admin" | "dpo" = "admin"): Promise<{ mappings: MappingCode[] }> => {
        const response = await apiV3.get("/mapping-codes", {
            headers: buildAuthHeaders(role, "monitoring:read")
        });
        return response.data;
    },
    getMasterPrograms: async (role: "admin" | "dpo" = "admin"): Promise<{ programs: MasterProgram[] }> => {
        const response = await apiV3.get("/master-programs", {
            headers: buildAuthHeaders(role, "monitoring:read")
        });
        return response.data;
    }
};
