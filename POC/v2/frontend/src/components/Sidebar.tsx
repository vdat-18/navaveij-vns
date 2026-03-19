"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    LineChart,
    ShieldCheck,
    HelpCircle,
    FileSearch
} from "lucide-react";
import { cn } from "@/shared/utils";

const menuItems = [
    { icon: LayoutDashboard, label: "Screen 1", id: "dashboard", href: "/" },
    { icon: LineChart, label: "Screen 2", id: "timeline", href: "/trend-timeline" },
    { icon: ShieldCheck, label: "Screen 3", id: "monitoring", href: "/access-monitoring" },
    { icon: FileSearch, label: "Governance", id: "audit", href: "/audit" },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 glass-sidebar h-screen flex flex-col p-6 fixed left-0 top-0 z-50">
            <div className="flex flex-col mb-12">
                <img
                    src="/logo-navavej.png"
                    alt="Navavej"
                    className="h-12 w-auto object-contain mb-2 self-start"
                />
                <div className="flex items-center gap-2 px-1">
                    <div className="h-4 w-[2px] bg-teal-accent/40" />
                    <h1 className="text-xs font-black tracking-[0.3em] uppercase opacity-70">
                        Clinical <span className="text-teal-accent">Intelligence</span>
                    </h1>
                </div>
            </div>

            <nav className="flex-1 space-y-2">
                <p className="text-xs uppercase tracking-widest text-slate-500 font-semibold mb-4 px-2">
                    Management
                </p>
                {menuItems.map((item) => (
                    <Link
                        key={item.id}
                        href={item.href}
                        className={cn(
                            "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group",
                            pathname === item.href
                                ? "bg-teal-accent/10 text-teal-accent"
                                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                        )}
                    >
                        <item.icon className={cn("w-5 h-5", pathname === item.href ? "text-teal-accent" : "text-slate-500 group-hover:text-slate-300")} />
                        <span className="font-medium">{item.label}</span>
                    </Link>
                ))}
            </nav>

            <div className="mt-auto space-y-2">
                <Link href="/audit" className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 transition-all">
                    <HelpCircle className="w-5 h-5 text-slate-500" />
                    <span className="font-medium">Support</span>
                </Link>
            </div>
        </aside>
    );
}
