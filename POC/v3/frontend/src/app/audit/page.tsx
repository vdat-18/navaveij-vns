"use client";

import React, { useEffect, useState } from "react";
import { clinicalService } from "@/services/api";
import {
    ShieldCheck,
    Search,
    ArrowLeft,
    Clock,
    User,
    FileText,
    ExternalLink,
    ChevronRight,
    Hash,
    Database
} from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/shared/utils";

const NavavejBrand = () => (
    <div className="flex items-center gap-4">
        <div className="relative">
            <div className="w-10 h-10 bg-navavej-teal rounded-lg flex items-center justify-center text-white font-black text-xl shadow-lg shadow-navavej-teal/20">
                N
            </div>
        </div>
        <div className="flex flex-col">
            <h1 className="text-[#00ABC7] font-black text-lg tracking-tighter leading-none uppercase">NAVAVEJ</h1>
            <span className="text-[#666666] text-[7px] font-bold uppercase tracking-[0.2em] mt-0.5">Audit Governance</span>
        </div>
    </div>
);

export default function AuditPage() {
    const [logs, setLogs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const data = await clinicalService.getAuditLogs();
                // Reverse to show latest first
                setLogs([...data].reverse());
            } catch (error) {
                console.error("Failed to fetch logs:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchLogs();
    }, []);

    const filteredLogs = logs.filter(log =>
        log.who.patient_id.toLowerCase().includes(search.toLowerCase()) ||
        log.current_hash.toLowerCase().includes(search.toLowerCase()) ||
        log.why.decision?.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-[#F8F9FA]">
            {/* Header */}
            <header className="bg-white border-b border-navavej-border px-8 py-4 sticky top-0 z-50 backdrop-blur-md bg-white/90">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="p-2 hover:bg-navavej-gray-light rounded-full transition-colors">
                            <ArrowLeft className="w-5 h-5 text-navavej-gray-med" />
                        </Link>
                        <NavavejBrand />
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="relative w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navavej-gray-med" />
                            <input
                                type="text"
                                placeholder="Search hashes or IDs..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="w-full bg-navavej-gray-light border-none rounded-xl py-2 pl-10 pr-4 text-xs font-bold focus:ring-2 focus:ring-navavej-teal/20 outline-none transition-all"
                            />
                        </div>
                        <div className="px-4 py-2 bg-navavej-teal text-white rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
                            <ShieldCheck className="w-4 h-4" />
                            Immutable Ledger Active
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto p-8">
                <div className="mb-8">
                    <div className="flex items-center gap-2 text-navavej-teal mb-2">
                        <Database className="w-4 h-4" />
                        <span className="text-[10px] font-black uppercase tracking-[0.3em]">Governance & Compliance</span>
                    </div>
                    <h2 className="text-3xl font-black text-navavej-gray-dark tracking-tighter uppercase leading-none">
                        Clinical Decision <span className="text-navavej-teal">Audit Logs</span>
                    </h2>
                    <p className="text-navavej-gray-med text-xs font-medium mt-2">
                        Viewing {filteredLogs.length} verified immutable records in the Navavej ROC ecosystem.
                    </p>
                </div>

                {loading ? (
                    <div className="space-y-4">
                        {[1, 2, 3, 4, 5].map(i => (
                            <div key={i} className="h-20 bg-white rounded-2xl animate-pulse border border-navavej-border" />
                        ))}
                    </div>
                ) : (
                    <div className="bg-white rounded-[20px] border border-navavej-border overflow-hidden shadow-sm">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-navavej-gray-light/50 border-b border-navavej-border">
                                    <th className="px-6 py-4 text-[10px] font-black text-navavej-gray-med uppercase tracking-widest">Timestamp / Event</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-navavej-gray-med uppercase tracking-widest">Entity & Actor</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-navavej-gray-med uppercase tracking-widest">Decision Hash</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-navavej-gray-med uppercase tracking-widest">Status</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-navavej-gray-med uppercase tracking-widest">Notes</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-navavej-border">
                                {filteredLogs.map((log) => (
                                    <tr key={log.current_hash} className="hover:bg-[#FDFDFD] transition-colors group">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-1.5 text-navavej-gray-dark font-bold text-xs uppercase tracking-tighter">
                                                    <Clock className="w-3 h-3 text-navavej-teal" />
                                                    {new Date(log.timestamp).toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                                </div>
                                                <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-[0.2em]">{log.what.event || "RECOMMENDATION"}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-1.5 text-xs font-black text-navavej-teal tracking-tight">
                                                    <User className="w-3 h-3" />
                                                    {log.who.patient_id}
                                                </div>
                                                {log.who.physician_id && (
                                                    <span className="text-[8px] font-bold text-navavej-gray-med uppercase">Actor: {log.who.physician_id}</span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-2">
                                                <div className="bg-navavej-gray-light p-1.5 rounded-lg border border-navavej-border">
                                                    <Hash className="w-3 h-3 text-navavej-gray-med" />
                                                </div>
                                                <span className="text-[9px] font-mono text-navavej-gray-med italic truncate max-w-[120px]">
                                                    {log.current_hash}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className={cn(
                                                "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest",
                                                log.why.decision === "Approve" ? "bg-emerald-50 text-emerald-600 border border-emerald-100" :
                                                    log.why.decision === "Reject" ? "bg-navavej-red/5 text-navavej-red border border-navavej-red/10" :
                                                        "bg-navavej-teal/5 text-navavej-teal border border-navavej-teal/10"
                                            )}>
                                                {log.why.decision || log.why.event || "ANALYZED"}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <p className="text-[10px] font-medium text-navavej-gray-med line-clamp-2 max-w-[200px] italic">
                                                {log.why.notes || "--"}
                                            </p>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {!loading && filteredLogs.length === 0 && (
                            <div className="p-20 flex flex-col items-center justify-center text-navavej-gray-med opacity-40">
                                <FileText className="w-12 h-12 mb-4" />
                                <p className="text-sm font-black uppercase tracking-widest">No audit traces found</p>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
