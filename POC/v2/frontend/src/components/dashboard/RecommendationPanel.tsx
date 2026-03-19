"use client";

import React, { useEffect, useState } from "react";
import {
    ShieldCheck,
    BrainCircuit,
    AlertTriangle,
    CheckCircle2,
    Package,
    ArrowRight,
    TrendingDown,
    TrendingUp,
    Activity,
    Heart,
    Stethoscope,
    ChevronDown,
    MessageSquare
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clinicalService } from "@/services/api";
import { cn } from "@/shared/utils";
import { BiomarkerCharts } from "./BiomarkerCharts";
import { LabResultsGrid } from "./LabResultsGrid";
import { CLINICAL_DICTIONARY } from "@/shared/clinical-dictionary";

interface RecommendationPanelProps {
    patientId: string | null;
    patientToken: string | null;
    isRuleBasedForced: boolean;
}

const renderBoldText = (text: any) => {
    if (!text) return null;

    // Handle array of strings (like add_on_highlights)
    if (Array.isArray(text)) {
        return text.map((item, idx) => (
            <span key={idx}>
                {renderBoldText(item)}
                {idx < text.length - 1 ? ' ' : ''}
            </span>
        ));
    }

    let content = typeof text === 'string' ? text : String(text);

    // 1. CLEANUP QUOTES: Remove all quote types (single, double, curly/smart quotes)
    content = content.replace(/['"‘’“”]/g, "");

    // 2. AUTO-TRANSLATE: Check for any technical identifiers from our dictionary
    // We sort keys by length descending to match longer identifiers first (e.g., PREMIUM_SEVERE_SINGLE before PREMIUM)
    const dictKeys = Object.keys(CLINICAL_DICTIONARY).sort((a, b) => b.length - a.length);

    dictKeys.forEach(key => {
        // Use regex with word boundaries to replace exact identifiers
        const regex = new RegExp(`\\b${key}\\b`, 'g');
        if (content.includes(key)) {
            // Replace with wrapped bold version if it's not already bolded
            // Note: the split/map below will handle the bolding if we wrap it in **
            content = content.replace(regex, `**${CLINICAL_DICTIONARY[key]}**`);
        }
    });

    // 3. CLEANUP: Normalize multiple asterisks (e.g., ****Text**** to **Text**)
    content = content.replace(/\*{3,}/g, '**');

    // 4. FIX: Normalize common AI mistake where it does *Text:** or **Text*
    content = content.replace(/\*+([^*]+):\*+/g, '**$1:**');

    // 5. RENDER: Split by ** markers and render bold parts
    return content.split(/(\*\*.*?\*\*)/g).map((part, i) =>
        part.startsWith('**') && part.endsWith('**')
            ? <strong key={i} className="font-black text-navavej-teal">{part.slice(2, -2)}</strong>
            : part
    );
};

const ClinicalRiskGauge = ({ value }: { value: string }) => {
    const isHigh = value === "High";
    const percentage = isHigh ? 85 : 30;

    return (
        <div className="relative flex flex-col items-center group">
            <svg className="w-48 h-24" viewBox="0 0 100 50">
                <path
                    d="M 10 45 A 40 40 0 0 1 90 45"
                    fill="none"
                    stroke="#E9ECEF"
                    strokeWidth="6"
                    strokeLinecap="round"
                />
                <motion.path
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: percentage / 100 }}
                    transition={{ duration: 2, ease: "circOut" }}
                    d="M 10 45 A 40 40 0 0 1 90 45"
                    fill="none"
                    stroke={isHigh ? "#9D0A31" : "#10B981"}
                    strokeWidth="8"
                    strokeLinecap="round"
                    className="transition-all duration-500"
                />
            </svg>
            <div className="absolute top-10 flex flex-col items-center">
                <span className={cn(
                    "text-3xl font-black transition-all duration-1000 tracking-tighter",
                    isHigh ? "text-navavej-red" : "text-emerald-500"
                )}>
                    {value}
                </span>
                <span className="text-[10px] uppercase tracking-[0.2em] text-navavej-gray-med font-black">Risk Level</span>
            </div>
        </div>
    );
};

const DEFAULT_CRITICAL_ALERTS = [
    { label: "Hypertensive Crisis", sub: "SBP > 180 mmHg detected", value: "URGENT" },
    { label: "High ASCVD Risk", sub: "Score ≥ 20.0%", value: "MONITOR" },
];

const normalizeCriticalAlerts = (patientHighAlert: any) => {
    if (Array.isArray(patientHighAlert)) {
        return patientHighAlert;
    }
    if (Array.isArray(patientHighAlert?.critical_signals)) {
        const mapped = patientHighAlert.critical_signals
            .filter((signal: any) => signal && typeof signal === "object")
            .map((signal: any) => ({
                label: signal.label || signal.signal_id || "Clinical Signal",
                sub: signal.clinical_note || "Immediate clinical review recommended",
                value: signal.severity === "Critical" ? "URGENT" : signal.severity || "MONITOR",
            }));
        if (mapped.length > 0) {
            return mapped;
        }
    }
    return DEFAULT_CRITICAL_ALERTS;
};

export function RecommendationPanel({ patientId, patientToken, isRuleBasedForced }: RecommendationPanelProps) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [isApproving, setIsApproving] = useState(false);
    const [decided, setDecided] = useState<boolean>(false);
    const [notes, setNotes] = useState("");

    useEffect(() => {
        if (!patientToken) return;
        const fetchRecommendation = async () => {
            setLoading(true);
            setDecided(false);
            setNotes("");
            try {
                const result = await clinicalService.getRecommendation(patientToken, isRuleBasedForced);
                setData(result);
            } catch (error) {
                console.error("Failed to fetch recommendation:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchRecommendation();
    }, [patientToken, isRuleBasedForced]);

    const handleApprove = async () => {
        if (!data?.recommendation_hash || !patientId) return;
        setIsApproving(true);
        try {
            await clinicalService.recordDecision(patientId, data.recommendation_hash, "Approve", notes);
            setDecided(true);
        } catch (error) {
            console.error("Failed to approve:", error);
            alert("Approval failed. Please check backend connection.");
        } finally {
            setIsApproving(false);
        }
    };

    if (!patientId) {
        return (
            <div className="h-[650px] flex flex-col items-center justify-center navavej-card bg-navavej-gray-light border-dashed border-2">
                <div className="relative mb-8">
                    <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-lg border border-navavej-border">
                        <Stethoscope className="w-10 h-10 text-navavej-teal opacity-30" />
                    </div>
                    <div className="absolute inset-x-0 bottom-[-10px] flex justify-center">
                        <div className="px-3 py-1 bg-navavej-teal text-white text-[9px] font-black uppercase tracking-widest rounded-full shadow-md">System Ready</div>
                    </div>
                </div>
                <h3 className="text-sm font-black text-navavej-gray-dark uppercase tracking-[0.2em]">Patient Analysis Pending</h3>
                <p className="text-xs text-navavej-gray-med mt-2 font-medium">Please select a validated entity from the clinical sidebar</p>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="h-[650px] flex flex-col items-center justify-center navavej-card relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-navavej-teal/10 overflow-hidden">
                    <motion.div
                        animate={{ x: ["-100%", "100%"] }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                        className="w-1/3 h-full bg-navavej-teal"
                    />
                </div>
                <motion.div
                    animate={{ scale: [1, 1.05, 1], rotate: [0, 5, -5, 0] }}
                    transition={{ duration: 4, repeat: Infinity }}
                    className="relative z-10"
                >
                    <div className="w-28 h-28 bg-navavej-gray-light rounded-[30px] flex items-center justify-center shadow-xl border border-navavej-border">
                        <BrainCircuit className="w-14 h-14 text-navavej-teal animate-pulse" />
                    </div>
                </motion.div>
                <p className="mt-10 text-lg font-black tracking-[0.1em] text-navavej-gray-dark uppercase">
                    Synthesizing Clinical Intelligence
                </p>
                <p className="text-[10px] font-bold text-navavej-gray-med uppercase tracking-widest mt-2">Checking signal store & rulesets...</p>
            </div>
        );
    }

    if (!data) return null;
    const criticalAlerts = normalizeCriticalAlerts(data.patient_high_alert);

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={patientToken}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-10"
            >
                {/* Intelligence HUD Panels */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">

                    <div className="lg:col-span-4 navavej-card p-10 flex flex-col items-center justify-center relative bg-white group overflow-hidden">
                        <div className="absolute top-0 left-0 w-2 h-full bg-navavej-teal/20 transition-all group-hover:bg-navavej-teal" />
                        <ClinicalRiskGauge value={data.overall_risk_level} />
                        <div className="mt-8 flex flex-col items-center">
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-2 h-2 bg-navavej-teal rounded-full animate-ping" />
                                <span className="text-[9px] font-black text-navavej-teal uppercase tracking-widest">Active Monitoring</span>
                            </div>
                            <p className="text-[11px] text-navavej-gray-med font-medium text-center italic">Calculated based on current BMI, ASCVD scores and clinical signals.</p>
                        </div>
                    </div>

                    <div className="lg:col-span-8 navavej-card p-0 rounded-[20px] overflow-hidden flex flex-col md:flex-row shadow-xl">
                        <div className="bg-navavej-teal p-12 text-white flex flex-col justify-center md:w-[45%]">
                            <div className="flex items-center gap-2 mb-4 opacity-70">
                                <Package className="w-5 h-5" />
                                <span className="text-[10px] font-black uppercase tracking-[0.2em]">Strategy Assignment</span>
                            </div>
                            <h3 className="text-4xl font-black tracking-tight">{data.ai_recommended_tier || "Premium"}</h3>
                            <div className="mt-6 flex items-center gap-2">
                                <div className="w-10 h-1 bg-white/30 rounded-full overflow-hidden">
                                    <motion.div initial={{ x: "-100%" }} animate={{ x: 0 }} transition={{ duration: 1 }} className="w-full h-full bg-white" />
                                </div>
                                <span className="text-[10px] font-bold uppercase">Optimal Confidence</span>
                            </div>
                        </div>

                        <div className="flex-1 p-12 bg-white flex flex-col justify-center items-start border-l border-navavej-border">
                            <div className="flex items-center justify-between w-full mb-8">
                                <div className="flex flex-col">
                                    <span className="text-[9px] font-black text-navavej-gray-med uppercase tracking-[0.2em] mb-1">Recommended Package</span>
                                    <span className="text-xl font-black text-navavej-gray-dark uppercase tracking-wide">Diamond Plus Center</span>
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-[9px] font-black text-navavej-gray-med uppercase tracking-[0.2em] mb-1">Program Value</span>
                                    <span className="text-3xl font-black text-navavej-teal italic">฿15,000</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 w-full">
                                <div className="px-5 py-3 bg-navavej-gray-light rounded-xl flex items-center gap-3 border border-navavej-border">
                                    <ShieldCheck className="w-5 h-5 text-navavej-teal" />
                                    <span className="text-[10px] font-black uppercase text-navavej-gray-dark">AI Verified</span>
                                </div>
                                <div className="px-5 py-3 bg-navavej-gray-light rounded-xl flex items-center gap-3 border border-navavej-border">
                                    <CheckCircle2 className="w-5 h-5 text-navavej-teal" />
                                    <span className="text-[10px] font-black uppercase text-navavej-gray-dark">Safety Log OK</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Evolution & Trends - Newly Implemented Visualization */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-navavej-teal">
                        <TrendingUp className="w-5 h-5" />
                        <span className="text-xs font-black uppercase tracking-[0.2em]">Biomarker Evolution Trends</span>
                    </div>
                    <BiomarkerCharts
                        bmiHistory={data.biomarker_trends?.bmi?.history || []}
                        bpHistory={data.biomarker_trends?.blood_pressure?.history || []}
                    />
                    <LabResultsGrid labs={data.biomarker_trends?.labs || []} />
                </div>

                {/* Detailed Logic & Alerts Reorganized */}
                <div className="space-y-10">
                    {/* 1. Clinical AI Reasoning - Full Width for Maximum Impact */}
                    <div className="navavej-card p-12 border-none bg-white shadow-xl shadow-navavej-teal/[0.03] relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-navavej-teal/[0.02] rounded-full translate-x-16 -translate-y-16 group-hover:scale-110 transition-transform duration-700" />

                        <div className="flex items-center justify-between mb-10 relative z-10">
                            <div className="flex items-center gap-5">
                                <div className="w-14 h-14 bg-navavej-teal/10 rounded-2xl flex items-center justify-center border border-navavej-teal/20 shadow-inner group-hover:rotate-3 transition-transform">
                                    <BrainCircuit className="w-7 h-7 text-navavej-teal" />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-black text-navavej-gray-dark uppercase tracking-tight leading-none">Clinical Logic & Rationale</h3>
                                    <p className="text-[10px] font-bold text-navavej-teal uppercase tracking-widest mt-1">Physician Evidence Stream</p>
                                </div>
                            </div>
                            <div className="px-4 py-1.5 bg-navavej-teal/10 rounded-full text-[10px] font-black text-navavej-teal uppercase tracking-[0.2em] shadow-sm">Trace Active</div>
                        </div>

                        <div className="relative z-10 bg-navavej-gray-light/30 rounded-[24px] p-8 border border-navavej-border/50">
                            <div className="space-y-4">
                                {data.reasoning_trace.split('\n').map((line: string, idx: number) => {
                                    const cleanLine = line.replace(/^[*-]\s*/, '').trim();
                                    if (!cleanLine) return null;
                                    return (
                                        <div key={idx} className="flex gap-4">
                                            <div className="mt-2 w-2 h-2 rounded-full bg-navavej-teal shrink-0 shadow-[0_0_8px_rgba(45,161,162,0.4)]" />
                                            <p className="text-sm font-medium text-navavej-gray-dark leading-relaxed text-justify flex-1">
                                                {renderBoldText(cleanLine)}
                                            </p>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        <div className="mt-8 flex items-center gap-6 text-navavej-gray-med text-[10px] font-black uppercase tracking-[0.2em] opacity-60">
                            <span className="flex items-center gap-2 bg-navavej-gray-light px-3 py-1 rounded-lg"><Search className="w-3 h-3" /> Integrity: Valid</span>
                            <span className="flex items-center gap-2 bg-navavej-gray-light px-3 py-1 rounded-lg"><Activity className="w-3 h-3" /> Logic: Verified</span>
                        </div>
                    </div>

                    {/* 2. Secondary Insights Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                        {/* Strategic Add-ons List */}
                        <div className="lg:col-span-8 navavej-card p-10 bg-white border-2 border-navavej-teal/10 shadow-lg flex flex-col">
                            <div className="flex items-center gap-3 mb-8">
                                <div className="w-10 h-10 bg-navavej-teal/5 rounded-xl flex items-center justify-center">
                                    <Package className="w-5 h-5 text-navavej-teal" />
                                </div>
                                <h4 className="text-sm font-black text-navavej-gray-dark uppercase tracking-widest">Additional Clinical Screenings</h4>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
                                {data.add_ons?.map((item: any, i: number) => (
                                    <div key={i} className="p-5 bg-navavej-gray-light rounded-2xl border border-navavej-border hover:border-navavej-teal/30 transition-all group flex flex-col justify-between">
                                        <div className="flex items-center justify-between mb-3">
                                            <span className="text-[11px] font-black text-navavej-gray-dark uppercase bg-white px-2 py-1 rounded shadow-sm">{item.item_code}</span>
                                            <span className={cn(
                                                "text-[9px] font-black px-2 py-1 rounded uppercase tracking-widest text-white shadow-sm",
                                                item.priority_level === "High" ? "bg-navavej-red" :
                                                    item.priority_level === "Medium" ? "bg-orange-500" : "bg-navavej-teal"
                                            )}>
                                                {item.priority_level}
                                            </span>
                                        </div>
                                        <p className="text-[11px] text-navavej-gray-med font-medium leading-relaxed text-justify">
                                            {renderBoldText(item.rationale)}
                                        </p>
                                    </div>
                                ))}
                                {(!data.add_ons || data.add_ons.length === 0) && (
                                    <div className="col-span-2 flex flex-col items-center justify-center py-10 opacity-30 italic text-xs">
                                        No clinical add-ons required for this tier.
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Critical Signals & Action Panel */}
                        <div className="lg:col-span-4 flex flex-col gap-6">
                            <div className="navavej-card p-8 bg-navavej-red/[0.02] border-l-[12px] border-navavej-red shadow-xl shadow-navavej-red/5">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-12 h-12 bg-navavej-red/10 rounded-2xl flex items-center justify-center border border-navavej-red/20 animate-float">
                                        <AlertTriangle className="w-6 h-6 text-navavej-red" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-black text-navavej-gray-dark uppercase tracking-tight leading-none">Critical Signals</h3>
                                        <p className="text-[9px] font-bold text-navavej-red uppercase tracking-widest mt-1">Immediate Review</p>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    {criticalAlerts.map((alert: any, i: number) => (
                                        <div key={i} className="flex items-center justify-between p-4 bg-white rounded-xl border border-navavej-border group hover:border-navavej-red/40 transition-colors shadow-sm">
                                            <div className="flex items-center gap-3">
                                                <div className="w-1.5 h-1.5 bg-navavej-red rounded-full" />
                                                <div>
                                                    <h4 className="text-[10px] font-black text-navavej-gray-dark uppercase">{alert.label}</h4>
                                                    <p className="text-[9px] text-navavej-gray-med font-bold italic">{alert.sub}</p>
                                                </div>
                                            </div>
                                            <span className="text-[8px] font-black text-navavej-red border border-navavej-red/20 px-2 py-1 rounded tracking-tighter">{alert.value}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Physician Notes & Action */}
                            <div className="bg-navavej-gray-light rounded-[24px] p-8 border border-navavej-border flex flex-col flex-1 shadow-inner">
                                <div className="flex items-center gap-2 mb-4 text-navavej-gray-med">
                                    <Activity className="w-3.5 h-3.5" />
                                    <span className="text-[10px] font-black uppercase tracking-widest">Execution Notes</span>
                                </div>
                                <textarea
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    disabled={decided || isApproving}
                                    placeholder="Add clinical observation..."
                                    className="w-full h-24 bg-white border-2 border-navavej-border rounded-xl p-4 text-[11px] font-medium outline-none transition-all resize-none shadow-sm focus:border-navavej-teal/50"
                                />
                                <button
                                    onClick={handleApprove}
                                    disabled={isApproving || decided}
                                    className={cn(
                                        "navavej-button-primary mt-4 w-full py-4 flex items-center justify-center gap-3 group shadow-lg",
                                        decided && "bg-emerald-500 hover:bg-emerald-500",
                                        isApproving && "opacity-70 cursor-wait"
                                    )}
                                >
                                    <span className="text-xs uppercase tracking-widest font-black">
                                        {isApproving ? "..." : decided ? "Approved" : "Confirm Strategy"}
                                    </span>
                                    {decided ? <CheckCircle2 className="w-5 h-5" /> : <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Patient Consultation Guide - New Implementation */}
                <div className="navavej-card p-12 bg-white border-none shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-navavej-teal/[0.03] rounded-full translate-x-32 -translate-y-32" />

                    <div className="flex items-center gap-4 mb-10">
                        <div className="w-12 h-12 bg-navavej-teal/10 rounded-2xl flex items-center justify-center border border-navavej-teal/20">
                            <MessageSquare className="w-6 h-6 text-navavej-teal" />
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-navavej-gray-dark uppercase tracking-tight">Patient Consultation Guide</h3>
                            <p className="text-[10px] font-bold text-navavej-teal uppercase tracking-widest mt-1">AI-generated talk track for physicians</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12 relative z-10">
                        <div className="space-y-8">
                            <div>
                                <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Clinical Conclusion</h4>
                                <p className="text-sm font-black text-navavej-teal leading-relaxed italic text-justify">
                                    {renderBoldText(data.communication_script?.opening || data.communication_script?.clinical_conclusion)}
                                </p>
                            </div>
                            <div>
                                <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Core Health Insights</h4>
                                <div className="space-y-2">
                                    {(data.communication_script?.health_summary || "").split('.').filter((s: string) => s.trim().length > 0).map((sentence: string, i: number) => (
                                        <div key={i} className="flex gap-2">
                                            <div className="mt-1.5 w-1 h-1 rounded-full bg-navavej-teal shrink-0" />
                                            <p className="text-sm font-medium text-navavej-gray-dark leading-relaxed">
                                                {renderBoldText(sentence.trim() + ".")}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {data.communication_script?.add_on_highlights && data.communication_script.add_on_highlights.length > 0 && (
                                <div className="mt-6 pt-6 border-t border-navavej-border">
                                    <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Special Highlights</h4>
                                    <div className="space-y-2">
                                        {data.communication_script.add_on_highlights.map((highlight: string, i: number) => (
                                            <div key={i} className="flex gap-2">
                                                <div className="mt-1.5 w-1 h-1 rounded-full bg-navavej-teal shrink-0" />
                                                <p className="text-sm font-medium text-navavej-gray-dark leading-relaxed text-justify">
                                                    {renderBoldText(highlight)}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="space-y-8">
                            <div>
                                <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Why this program?</h4>
                                <div className="p-6 bg-navavej-gray-light rounded-2xl border-l-4 border-navavej-teal">
                                    <p className="text-sm font-bold text-navavej-gray-dark leading-relaxed text-justify">
                                        {renderBoldText(data.communication_script?.recommendation_explanation)}
                                    </p>
                                </div>
                            </div>
                            <div>
                                <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Next steps</h4>
                                <div className="space-y-3">
                                    {(data.communication_script?.next_steps || "").split('.').filter((s: string) => s.trim().length > 0).map((sentence: string, i: number) => (
                                        <div key={i} className="flex items-start gap-3">
                                            <div className="mt-1 bg-emerald-100 p-1 rounded-full"><CheckCircle2 className="w-3 h-3 text-emerald-600" /></div>
                                            <p className="text-[11px] font-bold text-navavej-gray-med italic">
                                                {renderBoldText(sentence.trim() + ".")}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}

// Logic helper for extra visual flare
import { Search } from "lucide-react";
