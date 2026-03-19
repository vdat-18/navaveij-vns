"use client";

import React from "react";
import Link from "next/link";
import { AccessMonitoringScreen } from "@/components/access-monitoring/AccessMonitoringScreen";

export default function AccessMonitoringPage() {
  const configuredRole = (process.env.NEXT_PUBLIC_AUTH_ROLE || "admin").toLowerCase();
  const role: "admin" | "dpo" = configuredRole === "dpo" ? "dpo" : "admin";

  return (
    <main className="w-full px-8 lg:px-16 py-10 min-h-screen bg-white space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-navavej-gray-dark uppercase tracking-tighter">
            Screen 3 — Access Monitoring
          </h1>
          <p className="text-xs font-bold text-navavej-gray-med mt-2">
            Admin / DPO dashboard for monitoring, anomaly review, audit forensics, and governance evidence.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="border border-navavej-border rounded-lg px-3 py-2 text-xs font-black uppercase">
            {role}
          </span>
          <Link href="/" className="text-xs font-black text-navavej-teal uppercase">
            Back to Summary
          </Link>
        </div>
      </div>

      <AccessMonitoringScreen role={role} />
    </main>
  );
}
