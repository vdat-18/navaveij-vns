"use client";

import React from "react";
import { Beaker, ArrowUpRight, ArrowDownRight, Minus, AlertCircle } from "lucide-react";
import { cn } from "@/shared/utils";
import { translateIdentifier } from "@/shared/clinical-dictionary";

interface LabResult {
    lab_id: string;
    label: string;
    current_value: number;
    unit: string;
    interpretation: string;
    category: string;
    trend_direction: string;
    reference_range: any;
}

interface LabResultsGridProps {
    labs: LabResult[];
}

const getStatusColor = (interpretation: string) => {
    switch (interpretation) {
        case "N": return "text-emerald-500 bg-emerald-50 border-emerald-100";
        case "H": return "text-navavej-red bg-navavej-red/5 border-navavej-red/10";
        case "L": return "text-blue-500 bg-blue-50 border-blue-100";
        default: return "text-navavej-gray-med bg-navavej-gray-light border-navavej-border";
    }
};

const TrendIcon = ({ direction }: { direction: string }) => {
    switch (direction) {
        case "increasing": return <ArrowUpRight className="w-3 h-3 text-navavej-red" />;
        case "decreasing": return <ArrowDownRight className="w-3 h-3 text-emerald-500" />;
        case "stable": return <Minus className="w-3 h-3 text-navavej-gray-med" />;
        default: return null;
    }
};

export function LabResultsGrid({ labs }: LabResultsGridProps) {
    if (!labs || labs.length === 0) return null;

    return (
        <div className="space-y-6 mt-10">
            <div className="flex items-center gap-2 text-navavej-teal">
                <Beaker className="w-5 h-5" />
                <span className="text-xs font-black uppercase tracking-[0.2em]">Comprehensive metabolic Profile</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-4">
                {labs.map((lab) => (
                    <div key={lab.lab_id} className="navavej-card p-5 bg-white flex flex-col justify-between group hover:scale-[1.02] transition-all cursor-default">
                        <div>
                            <div className="flex justify-between items-start mb-3">
                                <span className="text-[9px] font-black text-navavej-gray-med uppercase tracking-wider truncate mr-2">
                                    {lab.label}
                                </span>
                                <div className={cn(
                                    "px-2 py-0.5 rounded text-[8px] font-black uppercase border",
                                    getStatusColor(lab.interpretation)
                                )}>
                                    {translateIdentifier(lab.category)}
                                </div>
                            </div>

                            <div className="flex items-baseline gap-1">
                                <span className="text-2xl font-black text-navavej-gray-dark tracking-tighter">
                                    {lab.current_value}
                                </span>
                                <span className="text-[10px] font-bold text-navavej-gray-med italic">
                                    {lab.unit}
                                </span>
                                <div className="ml-auto">
                                    <TrendIcon direction={lab.trend_direction} />
                                </div>
                            </div>
                        </div>

                        <div className="mt-4 pt-3 border-t border-navavej-border flex justify-between items-center">
                            <div className="flex flex-col">
                                <span className="text-[7px] font-black text-navavej-gray-med uppercase tracking-widest">Ref Range</span>
                                <span className="text-[9px] font-bold text-navavej-gray-dark">
                                    {lab.reference_range?.low ?? "--"} - {lab.reference_range?.high ?? lab.reference_range?.optimal ?? "--"}
                                </span>
                            </div>
                            {lab.interpretation !== "N" && (
                                <AlertCircle className="w-3.5 h-3.5 text-navavej-red animate-pulse" />
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
