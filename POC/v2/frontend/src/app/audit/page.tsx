"use client";

import React from "react";
import Link from "next/link";
import { AccessMonitoringScreen } from "@/components/access-monitoring/AccessMonitoringScreen";

export default function AuditPage() {
  return (
    <main className="w-full px-8 lg:px-16 py-10 min-h-screen bg-white space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-black text-navavej-gray-dark uppercase tracking-tighter">Screen 3 — Access Monitoring</h1>
        <Link href="/" className="text-xs font-black text-navavej-teal uppercase">
          Back to Summary
        </Link>
      </div>
      <AccessMonitoringScreen role="admin" />
    </main>
  );
}
