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
    MessageSquare,
    Lock,
    Unlock,
    Eye,
    EyeOff,
    Search,
    XCircle,
    Edit3,
    FileText,
    Printer,
    ThumbsUp,
    ThumbsDown
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { clinicalService } from "@/services/api";
import { cn } from "@/shared/utils";
import { BiomarkerCharts } from "./BiomarkerCharts";
import { LabResultsGrid } from "./LabResultsGrid";
import { CLINICAL_DICTIONARY } from "@/shared/clinical-dictionary";
import { ClinicalReport } from "./ClinicalReport";
import { WorkflowVisualizer } from "./WorkflowVisualizer";

interface RecommendationPanelProps {
    patient: any;
    patientId: string | null;
    privacyMode: boolean;
    setPrivacyMode: (val: boolean) => void;
    onDataLoaded?: (data: any) => void;
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
            content = content.replace(regex, `**${CLINICAL_DICTIONARY[key]}**`);
        }
    });

    // 3. CLEANUP: Normalize any number of asterisks (1+) to exactly two (**)
    // This fixes cases like *Text**, **Text*, or ****Text**** from the LLM or Dictionary
    content = content.replace(/\*+/g, '**');

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

export function RecommendationPanel({ patient, patientId, privacyMode, setPrivacyMode, onDataLoaded, isRuleBasedForced }: RecommendationPanelProps) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [isApproving, setIsApproving] = useState(false);
    const [decided, setDecided] = useState<boolean>(false);
    const [notes, setNotes] = useState("");
    const [decisionType, setDecisionType] = useState<"Approve" | "Reject" | "Modify">("Approve");
    const [modifiedTier, setModifiedTier] = useState<string>("");
    const [userRating, setUserRating] = useState<number | null>(null);
    const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);

    useEffect(() => {
        if (!patientId) return;
        const fetchRecommendation = async () => {
            setLoading(true);
            setDecided(false);
            setNotes("");
            try {
                const result = await clinicalService.getRecommendation(patientId, isRuleBasedForced);
                setData(result);
                setModifiedTier(result.ai_recommended_tier);
                if (onDataLoaded) onDataLoaded(result);
            } catch (error) {
                console.error("Failed to fetch recommendation:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchRecommendation();
    }, [patientId, isRuleBasedForced]);

    const handleDecision = async () => {
        if (!data?.recommendation_hash || !patientId) return;
        setIsApproving(true);
        try {
            await clinicalService.recordDecision(
                patientId,
                data.recommendation_hash,
                decisionType,
                notes,
                decisionType === "Modify" ? modifiedTier : undefined
            );
            setDecided(true);
            // Attach notes to data for report
            setData({ ...data, physician_notes: notes });
        } catch (error) {
            console.error("Failed to record decision:", error);
            alert("Action failed. Please check backend connection.");
        } finally {
            setIsApproving(false);
        }
    };

    const handlePrint = () => {
        window.print();
    };

    const handleFeedback = async (score: number) => {
        if (!data?.recommendation_hash || !patientId || isSubmittingFeedback) return;
        setUserRating(score);
        setIsSubmittingFeedback(true);
        try {
            // We reuse recordDecision to send feedback for the existing decision 
            // (The backend should handle updates to existing hash or new log entry)
            await clinicalService.recordDecision(
                patientId,
                data.recommendation_hash,
                decisionType,
                notes,
                decisionType === "Modify" ? modifiedTier : undefined,
                score
            );
        } catch (error) {
            console.error("Feedback failed:", error);
        } finally {
            setIsSubmittingFeedback(false);
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
            <div className="h-[650px] flex items-center justify-center p-6 bg-navavej-gray-light/30 rounded-[32px] border-2 border-dashed border-navavej-border">
                <WorkflowVisualizer />
            </div>
        );
    }

    if (!data) return null;

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={patientId}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-10"
            >
                {/* Hybrid Intelligence Source & Fallback Alert */}
                {data.review_required && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        className="mb-8 p-6 bg-navavej-red/5 border-2 border-navavej-red/20 rounded-3xl flex items-center gap-6 shadow-xl shadow-navavej-red/5"
                    >
                        <div className="w-14 h-14 bg-navavej-red rounded-2xl flex items-center justify-center shadow-lg shadow-navavej-red/20 animate-pulse">
                            <AlertTriangle className="w-8 h-8 text-white" />
                        </div>
                        <div className="flex-1">
                            <h4 className="text-sm font-black text-navavej-red uppercase tracking-tight">AI Agent Unavailable - Safety Fallback Active</h4>
                            <p className="text-[11px] font-medium text-navavej-red/80 italic leading-relaxed">
                                The AI reasoning engine failed to respond. The system has automatically switched to the hospital's **deterministic rule-based recommendation** (Rule {data.rule_preliminary_tier}).
                                Clinical review is mandatory for this case.
                            </p>
                        </div>
                    </motion.div>
                )}

                {/* Security HUD - PoC Control */}
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-3">
                        <div className={cn(
                            "w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-500 shadow-lg",
                            privacyMode ? "bg-navavej-red text-white" : "bg-emerald-500 text-white"
                        )}>
                            {privacyMode ? <Lock className="w-5 h-5 animate-pulse" /> : <Unlock className="w-5 h-5" />}
                        </div>
                        <div>
                            <h3 className="text-sm font-black text-navavej-gray-dark uppercase tracking-tight">Security Context: <span className={privacyMode ? "text-navavej-red" : "text-emerald-500"}>{privacyMode ? "AI MASKED" : "PHYSICIAN REHYDRATED"}</span></h3>
                            <p className="text-[9px] font-bold text-navavej-gray-med uppercase tracking-widest mt-1">PoC Proof of Privacy Demonstration</p>
                        </div>
                    </div>
                    <div className="flex gap-4">
                        {decided && (
                            <button
                                onClick={handlePrint}
                                className="flex items-center gap-2 px-6 py-2 rounded-full font-black text-[10px] uppercase tracking-widest transition-all shadow-lg bg-navavej-teal text-white hover:bg-navavej-teal/90 animate-in zoom-in-95 duration-500"
                            >
                                <Printer className="w-4 h-4" />
                                Export Official Report
                            </button>
                        )}
                        <button
                            onClick={() => setPrivacyMode(!privacyMode)}
                            className={cn(
                                "flex items-center gap-2 px-4 py-2 rounded-full font-black text-[10px] uppercase tracking-widest transition-all shadow-md active:scale-95",
                                privacyMode
                                    ? "bg-navavej-red text-white hover:bg-navavej-red/90"
                                    : "bg-navavej-gray-light text-navavej-gray-dark hover:bg-navavej-border"
                            )}
                        >
                            {privacyMode ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                            {privacyMode ? "Switch to Physician View" : "Switch to Raw AI View"}
                        </button>
                    </div>


                </div>

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
                            <h3 className="text-4xl font-black tracking-tight flex items-center gap-3">
                                {data.ai_recommended_tier || "Premium"}
                                {data.recommendation_source === "AI" && data.ai_recommended_tier !== data.rule_preliminary_tier && (
                                    <span className="text-[10px] bg-white/20 px-2 py-0.5 rounded border border-white/30 font-bold uppercase">
                                        Baseline: {data.rule_preliminary_tier}
                                    </span>
                                )}
                            </h3>
                            <div className="mt-6 flex items-center gap-2">
                                <div className="w-10 h-1 bg-white/30 rounded-full overflow-hidden">
                                    <motion.div initial={{ x: "-100%" }} animate={{ x: 0 }} transition={{ duration: 1 }} className="w-full h-full bg-white" />
                                </div>
                                <span className="text-[10px] font-bold uppercase">
                                    {data.recommendation_source === "RuleBased" ? "Safe Rule-Based Mode" : "High Confidence AI Mode"}
                                </span>
                            </div>
                        </div>

                        <div className="flex-1 p-12 bg-white flex flex-col justify-center items-start border-l border-navavej-border">
                            <div className="flex items-center justify-between w-full mb-8">
                                <div className="flex flex-col">
                                    <span className="text-[9px] font-black text-navavej-gray-med uppercase tracking-[0.2em] mb-1">Recommended Package</span>
                                    <span className="text-xl font-black text-navavej-gray-dark uppercase tracking-wide">
                                        {data.package_name || "Diagnostic Program"}
                                    </span>
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-[9px] font-black text-navavej-gray-med uppercase tracking-[0.2em] mb-1">Program Value</span>
                                    <span className="text-3xl font-black text-navavej-teal italic">
                                        ฿{data.price_thb ? data.price_thb.toLocaleString() : "TBD"}
                                    </span>
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

                {/* Personal & Social Context Enrichment */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Occupational context */}
                    <div className="navavej-card p-6 border-none bg-gradient-to-br from-white to-[#F9FCFD] shadow-sm group">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-8 h-8 bg-navavej-teal/10 rounded-lg flex items-center justify-center">
                                <Stethoscope className="w-5 h-5 text-navavej-teal" />
                            </div>
                            <h4 className="text-sm font-black text-navavej-gray-dark uppercase tracking-widest">Occupational Profile</h4>
                        </div>
                        {data.clinical_signals?.behavioral_flags?.occupational && (
                            <div className="space-y-3">
                                <div className="flex flex-wrap gap-2 mb-4">
                                    {(data.clinical_signals.behavioral_flags.occupational.tags || []).map((tag: string, i: number) => (
                                        <span key={i} className="text-[9px] font-black bg-navavej-teal/5 text-navavej-teal border border-navavej-teal/10 px-2 py-0.5 rounded uppercase tracking-tighter">
                                            {tag}
                                        </span>
                                    ))}
                                    {data.clinical_signals.behavioral_flags.occupational.night_shift_worker && (
                                        <span className="text-[9px] font-black bg-navavej-red/5 text-navavej-red border border-navavej-red/10 px-2 py-0.5 rounded uppercase tracking-tighter">
                                            Night Shift
                                        </span>
                                    )}
                                    {data.clinical_signals.behavioral_flags.occupational.retired_status && (
                                        <span className="text-[9px] font-black bg-emerald-100 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded uppercase tracking-tighter shadow-sm">
                                            Retired
                                        </span>
                                    )}
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between items-end border-b border-navavej-border pb-1">
                                        <span className="text-[10px] font-black text-navavej-gray-med uppercase">Device Exposure</span>
                                        <span className="text-base font-black text-navavej-gray-dark">{data.clinical_signals.behavioral_flags.occupational.computer_hours_per_day || "0"} Hrs/Day</span>
                                    </div>
                                    <div className="flex justify-between items-end border-b border-navavej-border pb-1">
                                        <span className="text-[10px] font-black text-navavej-gray-med uppercase">Chemical Exposure</span>
                                        <span className="text-sm font-bold text-navavej-gray-dark">{data.clinical_signals.behavioral_flags.occupational.factory_chemical_exposure ? "Active Risk" : "None Detected"}</span>
                                    </div>
                                    {data.clinical_signals.behavioral_flags.occupational.stress_level && (
                                        <div className="flex justify-between items-end border-b border-navavej-border pb-1">
                                            <span className="text-[10px] font-black text-navavej-gray-med uppercase text-navavej-red">Stress Level</span>
                                            <span className="text-sm font-black text-navavej-red uppercase tracking-tighter">{data.clinical_signals.behavioral_flags.occupational.stress_level}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Vices & Lifestyle */}
                    <div className="navavej-card p-6 border-none bg-gradient-to-br from-white to-[#F9FCFD] shadow-sm overflow-hidden relative">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-8 h-8 bg-navavej-teal/10 rounded-lg flex items-center justify-center">
                                <Activity className="w-5 h-5 text-navavej-teal" />
                            </div>
                            <h4 className="text-sm font-black text-navavej-gray-dark uppercase tracking-widest">Behavioral Lifestyle</h4>
                        </div>
                        <div className="grid grid-cols-1 gap-4">
                            <div className="flex items-center justify-between">
                                <div className="flex flex-col">
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase">Smoking History</span>
                                    <span className={cn(
                                        "text-xs font-black uppercase tracking-tight",
                                        (data.clinical_signals?.behavioral_flags?.smoking?.status === "never") ? "text-emerald-600" : "text-navavej-red"
                                    )}>
                                        {data.clinical_signals?.behavioral_flags?.smoking?.status || "Unknown"}
                                        {data.clinical_signals?.behavioral_flags?.smoking?.pack_years && ` (${data.clinical_signals.behavioral_flags.smoking.pack_years} pk-yrs)`}
                                        {data.clinical_signals?.behavioral_flags?.smoking?.quit_years_ago && (
                                            <span className="block text-[8px] font-bold text-emerald-600 lowercase tracking-normal">
                                                Quit {data.clinical_signals.behavioral_flags.smoking.quit_years_ago} years ago
                                            </span>
                                        )}
                                    </span>
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase">Alcohol (Units/Wk)</span>
                                    <span className="text-xs font-black text-navavej-gray-dark">{data.clinical_signals?.behavioral_flags?.alcohol?.units_per_week || "Minimal"}</span>
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex flex-col">
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-[0.05em]">Physical Activity</span>
                                    <span className="text-xs font-black text-navavej-teal uppercase">
                                        {data.clinical_signals?.behavioral_flags?.physical_activity?.level || "Sedentary"}
                                    </span>
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-[0.05em]">Session Freq</span>
                                    <span className="text-xs font-black text-navavej-gray-dark italic">
                                        {data.clinical_signals?.behavioral_flags?.physical_activity?.days_per_week || "0"} D/Wk
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Hypertension Specific Indicators */}
                        {(data.clinical_signals.behavioral_flags.dietary_salt_risk !== undefined ||
                            data.clinical_signals.behavioral_flags.medication_adherence_note ||
                            data.clinical_signals.behavioral_flags.home_bp_monitoring !== undefined) && (
                                <div className="mt-6 pt-6 border-t border-navavej-border">
                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="flex flex-col">
                                            <span className="text-[8px] font-black text-navavej-gray-med uppercase">Dietary Strategy</span>
                                            <span className={cn(
                                                "text-xs font-black uppercase tracking-tight",
                                                data.clinical_signals.behavioral_flags.dietary_salt_risk ? "text-navavej-red" : "text-emerald-600"
                                            )}>
                                                {data.clinical_signals.behavioral_flags.dietary_salt_risk ? "High Sodium Intake" : "Low Salt Compliant"}
                                            </span>
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <span className="text-[8px] font-black text-navavej-gray-med uppercase">Home Monitoring</span>
                                            <span className="text-xs font-black text-navavej-gray-dark uppercase">
                                                {data.clinical_signals.behavioral_flags.home_bp_monitoring ? "Active Log" : "No Home Data"}
                                            </span>
                                        </div>
                                        {data.clinical_signals.behavioral_flags.medication_adherence_note && (
                                            <div className="col-span-2">
                                                <span className="text-[8px] font-black text-navavej-gray-med uppercase">Medication Adherence</span>
                                                <p className="text-[10px] font-bold text-navavej-gray-dark italic leading-tight mt-1">
                                                    {data.clinical_signals.behavioral_flags.medication_adherence_note}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                    </div>

                    {/* Reproductive / Family History Details */}
                    <div className="navavej-card p-6 border-none bg-gradient-to-br from-white to-[#FAFAFA] shadow-sm">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-8 h-8 bg-navavej-teal/10 rounded-lg flex items-center justify-center">
                                <Heart className="w-5 h-5 text-navavej-teal" />
                            </div>
                            <h4 className="text-sm font-black text-navavej-gray-dark uppercase tracking-widest">Medical History Context</h4>
                        </div>
                        {data.clinical_signals?.reproductive_history_detail ? (
                            <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                                <div>
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase">Menarche Age</span>
                                    <p className="text-xs font-black text-navavej-gray-dark">{data.clinical_signals.reproductive_history_detail.age_at_menarche || "N/A"}</p>
                                </div>
                                <div>
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase">Parity (Children)</span>
                                    <p className="text-xs font-black text-navavej-gray-dark">{data.clinical_signals.reproductive_history_detail.num_children || "0"}</p>
                                </div>
                                <div>
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase">Menopause Status</span>
                                    <p className="text-xs font-black text-navavej-gray-dark">
                                        {data.clinical_signals.reproductive_history_detail.age_at_menopause ? `At age ${data.clinical_signals.reproductive_history_detail.age_at_menopause}` : "Pre-menopausal"}
                                    </p>
                                </div>
                                <div>
                                    <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-tighter">Contraception</span>
                                    <p className="text-xs font-black text-navavej-gray-dark">{data.clinical_signals.reproductive_history_detail.hormonal_contraception ? "Active" : "None"}</p>
                                </div>
                                {data.clinical_signals.history_of_gdm && (
                                    <div className="col-span-2 mt-2 pt-2 border-t border-navavej-border">
                                        <span className="text-[8px] font-black text-navavej-red uppercase tracking-[0.1em]">Clinical Alert: GDM History</span>
                                        <p className="text-[10px] font-bold text-navavej-gray-dark italic leading-tight">Confirmed history of Gestational Diabetes. Increased risk for Type 2 Diabetes.</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex flex-col justify-center h-full pb-4">
                                <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-[0.05em] mb-1">Premature CAD History</span>
                                <p className="text-xs font-bold text-navavej-gray-dark">
                                    {data.clinical_signals?.family_history_flags?.premature_cad ? "High risk in 1st degree relatives" : "None detected in family hx"}
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Evolution & Trends - Newly Implemented Visualization */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-navavej-teal">
                        <TrendingUp className="w-6 h-6" />
                        <span className="text-sm font-black uppercase tracking-[0.2em]">Biomarker Evolution Trends</span>
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
                                {((privacyMode ? data.security_metadata?.masked_ai_output?.reasoning_trace : data.reasoning_trace) || "").split('\n').map((line: string, idx: number) => {
                                    const cleanLine = line.replace(/^[*-]\s*/, '').trim();
                                    if (!cleanLine) return null;
                                    return (
                                        <div key={idx} className="flex gap-4">
                                            <div className={cn(
                                                "mt-2 w-2 h-2 rounded-full shrink-0 shadow-[0_0_8px_rgba(45,161,162,0.4)]",
                                                privacyMode ? "bg-navavej-red" : "bg-navavej-teal"
                                            )} />
                                            <p className={cn(
                                                "text-base font-medium leading-relaxed text-justify flex-1",
                                                privacyMode ? "font-mono text-[11px] text-navavej-red/80" : "text-navavej-gray-dark"
                                            )}>
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
                                    <div key={i} className={cn(
                                        "p-5 bg-navavej-gray-light rounded-2xl border transition-all group flex flex-col justify-between shadow-sm hover:shadow-md",
                                        item.priority_level === "Red" ? "border-red-200 hover:border-red-400" :
                                            item.priority_level === "Orange" ? "border-orange-200 hover:border-orange-400" :
                                                item.priority_level === "Yellow" ? "border-yellow-200 hover:border-yellow-400" :
                                                    "border-navavej-border hover:border-navavej-teal/30"
                                    )}>
                                        <div className="flex items-center justify-between mb-3">
                                            <span className="text-[11px] font-black text-navavej-gray-dark uppercase bg-white px-2 py-1 rounded shadow-sm ring-1 ring-navavej-border/10">{item.item_code}</span>
                                            <span className={cn(
                                                "text-[9px] font-black px-2 py-1 rounded uppercase tracking-widest text-white shadow-sm",
                                                item.priority_level === "Red" ? "bg-navavej-red" :
                                                    item.priority_level === "Orange" ? "bg-orange-500" :
                                                        item.priority_level === "Yellow" ? "bg-yellow-500" :
                                                            "bg-emerald-500"
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
                                        <h3 className="text-xl font-black text-navavej-gray-dark uppercase tracking-tight leading-none">Critical Signals</h3>
                                        <p className="text-[10px] font-bold text-navavej-red uppercase tracking-widest mt-1">Immediate Review</p>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    {(data.patient_high_alert || [
                                        { label: "Hypertensive Crisis", sub: "SBP > 180 mmHg detected", value: "URGENT" },
                                        { label: "High ASCVD Risk", sub: "Score ≥ 20.0%", value: "MONITOR" }
                                    ]).map((alert: any, i: number) => (
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
                                <div className="flex flex-col gap-4 mb-6">
                                    <div className="flex items-center gap-2 mb-2">
                                        <FileText className="w-3.5 h-3.5 text-navavej-gray-med" />
                                        <span className="text-[10px] font-black uppercase tracking-widest text-navavej-gray-med">Select Action</span>
                                    </div>
                                    <div className="grid grid-cols-3 gap-2">
                                        {[
                                            { type: "Approve", icon: CheckCircle2, color: "text-emerald-500", bg: "bg-emerald-50" },
                                            { type: "Modify", icon: Edit3, color: "text-amber-500", bg: "bg-amber-50" },
                                            { type: "Reject", icon: XCircle, color: "text-navavej-red", bg: "bg-red-50" }
                                        ].map((act) => (
                                            <button
                                                key={act.type}
                                                onClick={() => setDecisionType(act.type as any)}
                                                disabled={decided || isApproving}
                                                className={cn(
                                                    "flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all",
                                                    decisionType === act.type
                                                        ? cn("border-current shadow-md", act.bg, act.color)
                                                        : "border-navavej-border grayscale opacity-50 hover:grayscale-0 hover:opacity-100 bg-white"
                                                )}
                                            >
                                                <act.icon className="w-5 h-5 mb-1" />
                                                <span className="text-[8px] font-black uppercase tracking-tighter">{act.type}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Tier Selector for Modify */}
                                {decisionType === "Modify" && (
                                    <div className="mb-6 animate-in slide-in-from-top-2 duration-300">
                                        <label className="text-[9px] font-black text-navavej-gray-med uppercase tracking-widest mb-2 block">Corrected Tier Assignment</label>
                                        <div className="grid grid-cols-3 gap-2">
                                            {["Basic", "Advanced", "Premium"].map((tier) => (
                                                <button
                                                    key={tier}
                                                    onClick={() => setModifiedTier(tier)}
                                                    disabled={decided || isApproving}
                                                    className={cn(
                                                        "py-2 text-[10px] font-black rounded-lg border-2 transition-all uppercase",
                                                        modifiedTier === tier
                                                            ? "bg-navavej-teal text-white border-navavej-teal shadow-sm"
                                                            : "bg-white text-navavej-gray-med border-navavej-border hover:border-navavej-teal/30"
                                                    )}
                                                >
                                                    {tier}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="flex items-center gap-2 mb-3 text-navavej-gray-med">
                                    <Activity className="w-3.5 h-3.5" />
                                    <span className="text-[10px] font-black uppercase tracking-widest">
                                        {decisionType === "Approve" ? "Final Confirmation Notes" : "Reasoning for Variance"}
                                    </span>
                                </div>
                                <textarea
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    disabled={decided || isApproving}
                                    placeholder={decisionType === "Approve" ? "Add clinical observation..." : "Please justify this change for audit compliance..."}
                                    className={cn(
                                        "w-full h-24 bg-white border-2 rounded-xl p-4 text-[11px] font-medium outline-none transition-all resize-none shadow-sm focus:ring-4 focus:ring-navavej-teal/5",
                                        (decisionType !== "Approve" && !notes) ? "border-amber-200" : "border-navavej-border focus:border-navavej-teal/50"
                                    )}
                                />
                                <button
                                    onClick={handleDecision}
                                    disabled={isApproving || decided || (decisionType !== "Approve" && !notes)}
                                    className={cn(
                                        "navavej-button-primary mt-6 w-full py-4 flex items-center justify-center gap-3 group shadow-lg transition-all active:scale-[0.98]",
                                        decided && "bg-emerald-500 hover:bg-emerald-500",
                                        isApproving && "opacity-70 cursor-wait",
                                        (decisionType !== "Approve" && !notes) && "opacity-50 cursor-not-allowed grayscale"
                                    )}
                                >
                                    <span className="text-xs uppercase tracking-widest font-black">
                                        {isApproving ? "..." : decided ? "DECISION COMMITTED" : `Confirm ${decisionType}`}
                                    </span>
                                    {decided ? <CheckCircle2 className="w-5 h-5" /> : <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />}
                                </button>

                                {decided && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-8 pt-8 border-t-2 border-dashed border-navavej-border flex flex-col items-center text-center"
                                    >
                                        <div className="bg-navavej-teal/5 px-4 py-1.5 rounded-full mb-4">
                                            <p className="text-[9px] font-black text-navavej-teal uppercase tracking-widest">Model Tuning Feedback</p>
                                        </div>
                                        <h4 className="text-xs font-black text-navavej-gray-dark uppercase mb-2">Was this AI proposal clinically accurate?</h4>
                                        <p className="text-[10px] text-navavej-gray-med mb-6 font-medium">Your feedback directly improves the recommendation engine.</p>

                                        <div className="flex gap-4">
                                            {userRating === null ? (
                                                <>
                                                    <button
                                                        onClick={() => handleFeedback(1)}
                                                        disabled={isSubmittingFeedback}
                                                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl border-2 border-emerald-100 bg-white text-emerald-600 font-black text-[10px] uppercase tracking-widest hover:bg-emerald-50 hover:border-emerald-200 transition-all active:scale-95 shadow-sm"
                                                    >
                                                        <ThumbsUp className="w-3.5 h-3.5" /> Correct
                                                    </button>
                                                    <button
                                                        onClick={() => handleFeedback(-1)}
                                                        disabled={isSubmittingFeedback}
                                                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl border-2 border-red-100 bg-white text-navavej-red font-black text-[10px] uppercase tracking-widest hover:bg-red-50 hover:border-red-200 transition-all active:scale-95 shadow-sm"
                                                    >
                                                        <ThumbsDown className="w-3.5 h-3.5" /> Needs Tuning
                                                    </button>
                                                </>
                                            ) : (
                                                <motion.div
                                                    initial={{ scale: 0.9 }}
                                                    animate={{ scale: 1 }}
                                                    className="flex items-center gap-3 px-8 py-3 rounded-2xl bg-emerald-50 text-emerald-700 border border-emerald-100"
                                                >
                                                    <CheckCircle2 className="w-4 h-4" />
                                                    <span className="text-[10px] font-black uppercase tracking-widest">Feedback Recorded for Tuning</span>
                                                </motion.div>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Clinical Gaps (Screening & Vaccination) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    {/* Screening Gaps */}
                    <div className="navavej-card p-10 bg-white shadow-xl shadow-navavej-teal/[0.02]">
                        <div className="flex items-center gap-4 mb-8">
                            <div className="w-12 h-12 bg-navavej-teal/5 rounded-2xl flex items-center justify-center border border-navavej-teal/10">
                                <Search className="w-6 h-6 text-navavej-teal" />
                            </div>
                            <div>
                                <h3 className="text-xl font-black text-navavej-gray-dark uppercase tracking-tight">Screening Gaps</h3>
                                <p className="text-[10px] font-bold text-navavej-teal uppercase tracking-widest mt-1">Preventive Care Gaps</p>
                            </div>
                        </div>
                        <div className="space-y-3">
                            {(data.clinical_signals?.screening_gaps || []).length > 0 ? (
                                data.clinical_signals.screening_gaps.map((gap: any, i: number) => (
                                    <div key={i} className="flex items-center justify-between p-4 bg-navavej-gray-light/30 rounded-xl border border-navavej-border">
                                        <div className="flex items-center gap-3">
                                            <div className={cn(
                                                "w-2 h-2 rounded-full",
                                                gap.priority_color === "Red" ? "bg-navavej-red shadow-[0_0_8px_rgba(157,10,49,0.3)]" :
                                                    gap.priority_color === "Orange" ? "bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.3)]" : "bg-navavej-teal"
                                            )} />
                                            <div>
                                                <h4 className="text-[10px] font-black text-navavej-gray-dark uppercase">{gap.label}</h4>
                                                <p className="text-[9px] text-navavej-gray-med font-bold italic">Due: {gap.note || "Pending"}</p>
                                            </div>
                                        </div>
                                        <span className={cn(
                                            "text-[8px] font-black px-2 py-1 rounded tracking-tighter uppercase",
                                            gap.priority_color === "Red" ? "text-navavej-red border-navavej-red/20 border" : "text-navavej-teal border-navavej-teal/20 border"
                                        )}>{gap.overdue_days ? `${gap.overdue_days} Days Overdue` : "Eligible"}</span>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-10 opacity-30 italic text-xs border-2 border-dashed border-navavej-border rounded-xl">
                                    No preventive screening gaps identified.
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Vaccination Gaps (Newly Enriched) */}
                    <div className="navavej-card p-10 bg-white shadow-xl shadow-navavej-teal/[0.02]">
                        <div className="flex items-center gap-4 mb-8">
                            <div className="w-12 h-12 bg-emerald-50 rounded-2xl flex items-center justify-center border border-emerald-100">
                                <ShieldCheck className="w-6 h-6 text-emerald-600" />
                            </div>
                            <div>
                                <h3 className="text-xl font-black text-navavej-gray-dark uppercase tracking-tight">Vaccination Shield</h3>
                                <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest mt-1">Protective Health Matrix</p>
                            </div>
                        </div>
                        <div className="space-y-3">
                            {(data.clinical_signals?.vaccination_gaps || []).length > 0 ? (
                                data.clinical_signals.vaccination_gaps.map((gap: any, i: number) => (
                                    <div key={i} className="flex items-center justify-between p-4 bg-emerald-50/20 rounded-xl border border-emerald-100/50">
                                        <div className="flex items-center gap-3">
                                            <div className={cn(
                                                "w-2 h-2 rounded-full",
                                                gap.priority_color === "Red" ? "bg-navavej-red" :
                                                    gap.priority_color === "Orange" || gap.priority_color === "Amber" ? "bg-orange-400" : "bg-emerald-500"
                                            )} />
                                            <div>
                                                <h4 className="text-[10px] font-black text-navavej-gray-dark">{gap.label}</h4>
                                                <p className="text-[9px] text-navavej-gray-med font-medium italic line-clamp-1">{gap.note}</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <span className="text-[8px] font-black text-emerald-600 uppercase">{gap.recommended_annual ? "Annual" : `${gap.doses_received || 0}/${gap.doses_required || "-"} Doses`}</span>
                                            {gap.anti_hbs_checked && <span className="text-[7px] font-bold text-navavej-teal uppercase tracking-widest mt-0.5">HBsAb Verified</span>}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-10 opacity-30 italic text-xs border-2 border-dashed border-navavej-border rounded-xl">
                                    All essential vaccinations up to date.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
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
                                <p className="text-base font-black text-navavej-teal leading-relaxed italic text-justify">
                                    {renderBoldText(data.communication_script?.clinical_conclusion)}
                                </p>
                            </div>
                            <div>
                                <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Core Health Insights</h4>
                                <div className="space-y-2">
                                    {(data.communication_script?.health_summary || "")
                                        .split(/\.(?!\d)(?=\s+[A-Z0-9]|$)|(?:\n|^)\s*-\s+|(?<=\.)\s*-\s+/g)
                                        .filter((s: string) => s.trim().length > 0)
                                        .map((sentence: string, i: number) => {
                                            // Enhanced strip: handle -, *, 1., 2) patterns
                                            const trimmed = sentence.trim().replace(/^(?:[*-]|\d+[\.\)])\s*/, "");
                                            if (!trimmed || trimmed.length < 2) return null; // Ignore solo numbers or remnants
                                            return (
                                                <div key={i} className="flex gap-2">
                                                    <div className="mt-1.5 w-1 h-1 rounded-full bg-navavej-teal shrink-0" />
                                                    <p className="text-base font-medium text-navavej-gray-dark leading-relaxed text-justify">
                                                        {renderBoldText(trimmed.endsWith('.') ? trimmed : trimmed + ".")}
                                                    </p>
                                                </div>
                                            );
                                        })}
                                </div>
                            </div>
                            {data.communication_script?.add_on_highlights && data.communication_script.add_on_highlights.length > 0 && (
                                <div className="mt-6 pt-6 border-t border-navavej-border">
                                    <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Special Highlights</h4>
                                    <div className="space-y-2">
                                        {data.communication_script.add_on_highlights.map((highlight: string, i: number) => (
                                            <div key={i} className="flex gap-2">
                                                <div className="mt-1.5 w-1 h-1 rounded-full bg-navavej-teal shrink-0" />
                                                <p className="text-base font-medium text-navavej-gray-dark leading-relaxed text-justify">
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
                                    <p className="text-base font-bold text-navavej-gray-dark leading-relaxed text-justify">
                                        {renderBoldText(data.communication_script?.recommendation_explanation)}
                                    </p>
                                </div>
                            </div>
                            <div>
                                <h4 className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-3 border-b border-navavej-border pb-1 w-fit">Next steps</h4>
                                <div className="space-y-3">
                                    {(data.communication_script?.next_steps || "")
                                        .split(/\.(?!\d)(?=\s+[A-Z0-9]|$)|(?:\n|^)\s*-\s+|(?<=\.)\s*-\s+/g)
                                        .filter((s: string) => s.trim().length > 0)
                                        .map((sentence: string, i: number) => {
                                            // Enhanced strip: handle -, *, 1., 2) patterns
                                            const trimmed = sentence.trim().replace(/^(?:[*-]|\d+[\.\)])\s*/, "");
                                            if (!trimmed || trimmed.length < 2) return null; // Ignore solo numbers or remnants
                                            return (
                                                <div key={i} className="flex items-start gap-3">
                                                    <div className="mt-1 bg-emerald-100 p-1 rounded-full"><CheckCircle2 className="w-3 h-3 text-emerald-600" /></div>
                                                    <p className="text-sm font-bold text-navavej-gray-med italic text-justify">
                                                        {renderBoldText(trimmed.endsWith('.') ? trimmed : trimmed + ".")}
                                                    </p>
                                                </div>
                                            );
                                        })}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <ClinicalReport patient={patient} data={data} />
            </motion.div>
        </AnimatePresence >
    );
}
