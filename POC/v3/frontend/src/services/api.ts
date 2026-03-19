import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

export const patientService = {
    getAll: async () => {
        const response = await api.get("/patients");
        return response.data;
    },
    getDetails: async (id: string) => {
        const response = await api.get(`/patients/${id}`);
        return response.data;
    },
};

export const clinicalService = {
    getRecommendation: async (patientId: string, forceRuleBased: boolean = false) => {
        const response = await api.post("/clinical/recommend", {
            patient_id: patientId,
            force_rule_based: forceRuleBased
        });
        return response.data;
    },
    recordDecision: async (
        patientId: string,
        recommendationHash: string,
        decision: "Approve" | "Reject" | "Modify",
        notes: string = "",
        modifiedTier?: string,
        rating?: number,
        feedbackComment?: string
    ) => {
        const response = await api.post("/clinical/approve", {
            patient_id: patientId,
            recommendation_hash: recommendationHash,
            decision: decision,
            physician_id: "dr-admin-001",
            notes: notes,
            modified_tier: modifiedTier,
            rating: rating,
            feedback_comment: feedbackComment
        });
        return response.data;
    },
    getAuditLogs: async () => {
        const response = await api.get("/clinical/audit");
        return response.data;
    }
};
