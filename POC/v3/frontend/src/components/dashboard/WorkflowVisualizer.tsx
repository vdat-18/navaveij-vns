"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Database,
    Zap,
    TrendingUp,
    Cpu,
    CheckCircle2,
    Loader2
} from "lucide-react";
import { cn } from "@/shared/utils";

const STEPS = [
    { id: "baseline", label: "Baseline", desc: "Retrieving patient medical history (3yr)", icon: Database },
    { id: "signals", label: "Signals", desc: "Identifying clinical red flags", icon: Zap },
    { id: "trends", label: "Trends", desc: "Analyzing biomarker longitudinal history", icon: TrendingUp },
    { id: "inference", label: "Inference", desc: "AI Agents synthesis & reasoning", icon: Cpu },
    { id: "finalize", label: "Finalize", desc: "Validating safety & clinical drift", icon: CheckCircle2 },
];

export function WorkflowVisualizer() {
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
        }, 1500); // Progress every 1.5s for demo effect
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full bg-white rounded-[32px] p-10 border-2 border-navavej-border shadow-2xl relative overflow-hidden">
            {/* Background Decor */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-navavej-teal/5 rounded-full -mr-32 -mt-32 blur-3xl" />

            <div className="relative z-10">
                <div className="flex items-center gap-4 mb-10">
                    <div className="bg-navavej-teal/10 p-3 rounded-2xl">
                        <Loader2 className="w-6 h-6 text-navavej-teal animate-spin" />
                    </div>
                    <div>
                        <h2 className="text-xl font-black text-navavej-gray-dark uppercase tracking-tight">Clinical Reasoning Engine</h2>
                        <p className="text-xs font-bold text-navavej-gray-med uppercase tracking-widest mt-1">Multi-phase Agentic Orchestration</p>
                    </div>
                </div>

                <div className="grid grid-cols-5 gap-4 relative">
                    {/* Connecting Line */}
                    <div className="absolute top-7 left-[10%] right-[10%] h-0.5 bg-navavej-border z-0">
                        <motion.div
                            className="h-full bg-navavej-teal"
                            initial={{ width: "0%" }}
                            animate={{ width: `${(currentStep / (STEPS.length - 1)) * 100}%` }}
                            transition={{ duration: 0.5 }}
                        />
                    </div>

                    {STEPS.map((step, i) => {
                        const Icon = step.icon;
                        const isCompleted = currentStep > i;
                        const isActive = currentStep === i;

                        return (
                            <div key={step.id} className="flex flex-col items-center relative z-10">
                                <motion.div
                                    className={cn(
                                        "w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-500 border-2 shadow-lg",
                                        isCompleted ? "bg-navavej-teal border-navavej-teal text-white" :
                                            isActive ? "bg-white border-navavej-teal text-navavej-teal scale-110" :
                                                "bg-white border-navavej-border text-navavej-gray-med"
                                    )}
                                    animate={isActive ? { y: -5 } : { y: 0 }}
                                >
                                    <Icon className={cn("w-6 h-6", isActive && "animate-pulse")} />
                                    {isCompleted && (
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            className="absolute -top-1 -right-1 bg-emerald-500 text-white rounded-full p-1"
                                        >
                                            <CheckCircle2 className="w-3 h-3" />
                                        </motion.div>
                                    )}
                                </motion.div>
                                <div className="mt-4 text-center">
                                    <p className={cn(
                                        "text-[10px] font-black uppercase tracking-widest transition-colors",
                                        isActive || isCompleted ? "text-navavej-teal" : "text-navavej-gray-med"
                                    )}>
                                        {step.label}
                                    </p>
                                    <AnimatePresence mode="wait">
                                        {isActive && (
                                            <motion.p
                                                initial={{ opacity: 0, y: 5 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -5 }}
                                                className="text-[9px] font-bold text-navavej-gray-med italic mt-1 max-w-[120px]"
                                            >
                                                {step.desc}
                                            </motion.p>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Bottom Progress Bar */}
            <div className="mt-12 w-full h-1 bg-navavej-gray-light rounded-full overflow-hidden">
                <motion.div
                    className="h-full bg-navavej-teal/30"
                    animate={{ width: ["0%", "100%"] }}
                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                />
            </div>
        </div>
    );
}
