"use client";

import React from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area,
} from "recharts";
import { cn } from "@/shared/utils";

interface HistoryEntry {
    date: string;
    value?: number;
    sbp?: number;
    dbp?: number;
}

interface BiomarkerChartsProps {
    bmiHistory: HistoryEntry[];
    bpHistory: HistoryEntry[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white p-3 border border-navavej-border rounded-xl shadow-xl">
                <p className="text-[10px] font-black text-navavej-gray-med uppercase tracking-tighter mb-1">{label}</p>
                {payload.map((entry: any, index: number) => (
                    <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                        <span className="text-xs font-black text-navavej-gray-dark italic">
                            {entry.name}: {entry.value}
                        </span>
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

export function BiomarkerCharts({ bmiHistory, bpHistory }: BiomarkerChartsProps) {
    const hasBP = bpHistory && bpHistory.length > 0;
    const hasBMI = bmiHistory && bmiHistory.length > 0;

    if (!hasBP && !hasBMI) return null;

    return (
        <div className={cn(
            "grid gap-6 mt-10",
            hasBP && hasBMI ? "grid-cols-1 md:grid-cols-3" : "grid-cols-1"
        )}>
            {/* Blood Pressure Trend */}
            {hasBP && (
                <div className="navavej-card p-6 bg-white">
                    <div className="flex items-center justify-between mb-6">
                        <h4 className="text-[11px] font-black text-navavej-gray-dark uppercase tracking-widest leading-none">Blood Pressure Trend</h4>
                        <div className="flex gap-3">
                            <div className="flex items-center gap-1">
                                <div className="w-1.5 h-1.5 rounded-full bg-navavej-red" />
                                <span className="text-[8px] font-black text-navavej-gray-med uppercase">SBP</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <div className="w-1.5 h-1.5 rounded-full bg-navavej-teal" />
                                <span className="text-[8px] font-black text-navavej-gray-med uppercase">DBP</span>
                            </div>
                        </div>
                    </div>
                    <div className="h-[160px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={bpHistory}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E9ECEF" />
                                <XAxis
                                    dataKey="date"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 9, fontWeight: 700, fill: '#666' }}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 9, fontWeight: 700, fill: '#666' }}
                                    domain={['dataMin - 10', 'dataMax + 10']}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Line
                                    name="Systolic"
                                    type="monotone"
                                    dataKey="sbp"
                                    stroke="#9D0A31"
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#9D0A31', strokeWidth: 2, stroke: '#fff' }}
                                    activeDot={{ r: 6 }}
                                />
                                <Line
                                    name="Diastolic"
                                    type="monotone"
                                    dataKey="dbp"
                                    stroke="#00ABC7"
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#00ABC7', strokeWidth: 2, stroke: '#fff' }}
                                    activeDot={{ r: 6 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* BMI Trend */}
            {hasBMI && (
                <div className="navavej-card p-6 bg-white">
                    <div className="flex items-center justify-between mb-6">
                        <h4 className="text-[11px] font-black text-navavej-gray-dark uppercase tracking-widest leading-none">BMI Progression</h4>
                        <span className="bg-navavej-teal/10 text-navavej-teal text-[8px] font-black px-2 py-0.5 rounded-full uppercase">Target: &lt; 23.0</span>
                    </div>
                    <div className="h-[160px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={bmiHistory}>
                                <defs>
                                    <linearGradient id="colorBmi" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#00ABC7" stopOpacity={0.2} />
                                        <stop offset="95%" stopColor="#00ABC7" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E9ECEF" />
                                <XAxis
                                    dataKey="date"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 9, fontWeight: 700, fill: '#666' }}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 9, fontWeight: 700, fill: '#666' }}
                                    domain={['dataMin - 2', 'dataMax + 2']}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Area
                                    name="BMI"
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#00ABC7"
                                    fillOpacity={1}
                                    fill="url(#colorBmi)"
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#00ABC7', strokeWidth: 2, stroke: '#fff' }}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
}
