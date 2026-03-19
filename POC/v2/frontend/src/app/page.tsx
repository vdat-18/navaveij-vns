"use client";

import React, { useState } from "react";
import { PatientList } from "@/components/dashboard/PatientList";
import { RecommendationPanel } from "@/components/dashboard/RecommendationPanel";
import { Bell, Search, User, Globe, Phone, ShoppingCart, Menu, Info, Activity, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";
import { cn } from "@/shared/utils";

const primaryNavLinks = [
  { label: "Screen 1 Summary", href: "/" },
  { label: "Trend & Timeline", href: "/trend-timeline" },
  { label: "Access Monitoring", href: "/access-monitoring" },
  { label: "Governance", href: "/audit" },
];

const NavavejBrand = () => (
  <div className="flex items-center gap-3">
    <img
      src="/logo-navavej.png"
      alt="Navavej International Hospital"
      className="h-10 w-auto object-contain"
    />
    <div className="h-8 w-[1px] bg-navavej-border mx-1 hidden sm:block" />
    <div className="flex flex-col">
      <h1 className="text-[#00ABC7] font-black text-xl tracking-tighter leading-none uppercase">Clinical Guidance</h1>
      <span className="text-[#666666] text-[8px] font-bold uppercase tracking-[0.2em] mt-1">Strategic Advisory System</span>
    </div>
  </div>
);

export default function DashboardPage() {
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [isRuleBasedForced, setIsRuleBasedForced] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      {/* Top Utility Bar - Inspired by official navavej.com */}
      <div className="bg-navavej-teal py-1.5 px-8 text-white text-[10px] font-bold flex justify-between items-center">
        <div className="flex gap-4">
          <span className="flex items-center gap-1"><Globe className="w-3 h-3" /> TH / EN</span>
          <span className="flex items-center gap-1"><Phone className="w-3 h-3" /> 1507</span>
        </div>
        <div className="flex gap-4 uppercase tracking-widest">
          <span>About Us</span>
          <span>Contact</span>
          <span>Career</span>
        </div>
      </div>

      {/* Main Navbar */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-navavej-border px-8 py-5 shadow-sm flex items-center justify-between">
        <NavavejBrand />

        <nav className="hidden lg:flex items-center gap-10">
          {primaryNavLinks.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="font-bold text-sm text-navavej-gray-dark hover:text-navavej-teal transition-colors uppercase tracking-wider"
            >
              {item.label}
            </Link>
          ))}
          <Link href="/audit" className="font-bold text-sm text-navavej-teal hover:opacity-80 transition-opacity uppercase tracking-wider border-l border-navavej-border pl-6 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />
            Governance
          </Link>
          <Link href="/trend-timeline" className="font-bold text-sm text-navavej-teal hover:opacity-80 transition-opacity uppercase tracking-wider border-l border-navavej-border pl-6 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Trend & Timeline
          </Link>
          <Link href="/access-monitoring" className="font-bold text-sm text-navavej-teal hover:opacity-80 transition-opacity uppercase tracking-wider border-l border-navavej-border pl-6 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />
            Access Monitoring
          </Link>
        </nav>

        <div className="flex items-center gap-5 translate-y-[-2px]">
          <button
            onClick={() => setIsRuleBasedForced((prev) => !prev)}
            className={cn(
              "hidden md:flex items-center gap-2 px-4 py-2 rounded-full font-black text-[10px] uppercase tracking-widest transition-all shadow-md active:scale-95 border-2",
              isRuleBasedForced
                ? "bg-amber-500 text-white border-amber-600 animate-pulse"
                : "bg-white text-navavej-gray-med border-navavej-border hover:border-amber-400"
            )}
          >
            <Activity className="w-4 h-4" />
            {isRuleBasedForced ? "Fallback: Rules" : "Mode: Hybrid AI"}
          </button>
          <button className="p-2 text-navavej-gray-dark hover:text-navavej-teal transition-all"><Search className="w-5 h-5 stroke-[2.5px]" /></button>
          <button className="p-2 text-navavej-gray-dark hover:text-navavej-teal transition-all relative">
            <Bell className="w-5 h-5 stroke-[2.5px]" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-navavej-red rounded-full border-2 border-white shadow-sm"></span>
          </button>
          <div className="h-6 w-[1px] bg-navavej-border mx-1" />
          <button className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-full border-2 border-navavej-teal/20 flex items-center justify-center bg-navavej-gray-light group-hover:border-navavej-teal transition-colors">
              <User className="w-5 h-5 text-navavej-teal" />
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-[10px] font-black text-navavej-gray-med uppercase tracking-tighter leading-none mb-1">Physician</p>
              <p className="text-xs font-black text-navavej-gray-dark leading-none">DR. CLINICIAN</p>
            </div>
          </button>
        </div>
      </header>

      {/* Clinical Workbench Layout */}
      <main className="w-full px-8 lg:px-16 py-10">
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">

          {/* Patient Directory Sidebar */}
          <div className="xl:col-span-2">
            <div className="bg-[#fcfdfe] p-4 rounded-[20px] border border-navavej-border min-h-[600px] shadow-inner">
              <PatientList
                onSelectPatient={setSelectedPatient}
                selectedId={selectedPatient?.patient_id}
              />
            </div>
          </div>

          {/* Core Analysis Area */}
          <div className="xl:col-span-10">
            <div className="mb-10">
              <div className="flex items-center gap-2 text-navavej-teal mb-3">
                <div className="w-6 h-0.5 bg-navavej-teal rounded-full" />
                <span className="text-[10px] font-black uppercase tracking-[0.3em]">Personalized Health Insights</span>
              </div>
              <h2 className="text-4xl font-black text-navavej-gray-dark tracking-tighter uppercase italic leading-none">
                Clinical Checkup <span className="text-navavej-teal">Advisory Center</span>
              </h2>
            </div>

            {selectedPatient && (
              <motion.div
                initial={{ opacity: 0, y: -15 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8 p-8 navavej-card bg-[#F0F9FA] border-navavej-teal/20 flex items-center justify-between"
              >
                <div className="flex items-center gap-8">
                  <div className="relative">
                    <div className="w-20 h-20 bg-white rounded-[20px] flex items-center justify-center shadow-xl border border-navavej-teal/10 group overflow-hidden">
                      <div className="absolute top-0 right-0 w-8 h-8 bg-navavej-teal/10 rounded-bl-[20px]" />
                      <span className="text-4xl font-black text-navavej-teal tracking-tighter relative z-10">
                        {selectedPatient.patient_name.charAt(0)}
                      </span>
                    </div>
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-navavej-teal text-white rounded-full flex items-center justify-center border-4 border-white shadow-lg">
                      <Activity className="w-4 h-4" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-3xl font-black text-navavej-gray-dark tracking-tighter uppercase">
                      {selectedPatient.patient_name}
                    </h3>
                    <div className="flex items-center gap-6 mt-2">
                      <div className="flex flex-col">
                        <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-widest">Medical ID</span>
                        <span className="text-xs font-bold text-navavej-teal">{selectedPatient.patient_id}</span>
                      </div>
                      <div className="w-[1px] h-6 bg-navavej-border" />
                      <div className="flex flex-col">
                        <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-widest">Demographics</span>
                        <span className="text-xs font-bold text-navavej-gray-dark">35 Yrs / Male / Asian</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="px-6 py-3 bg-white/60 border border-white rounded-2xl flex flex-col justify-center">
                    <span className="text-[8px] font-black text-navavej-gray-med uppercase tracking-widest mb-1">Last Analysis Run</span>
                    <span className="text-xs font-black text-navavej-gray-dark uppercase tracking-tighter">16 MAR 2026 • 18:43</span>
                  </div>
                </div>
              </motion.div>
            )}

            <RecommendationPanel
              patientId={selectedPatient?.patient_id || null}
              patientToken={selectedPatient?.patient_token || null}
              isRuleBasedForced={isRuleBasedForced}
            />
          </div>
        </div>
      </main>

      {/* Official-style Footer Highlight */}
      <footer className="mt-20 border-t border-navavej-border py-20 px-8 lg:px-16 bg-navavej-gray-light overflow-hidden relative">
        <div className="absolute top-0 right-0 w-96 h-96 bg-navavej-teal/5 rounded-full blur-[100px] translate-x-1/2 -translate-y-1/2" />
        <div className="w-full grid grid-cols-1 md:grid-cols-4 gap-12">
          <div>
            <NavavejBrand />
            <p className="text-xs text-navavej-gray-med mt-6 leading-relaxed font-medium">
              Official Clinical Orchestration Platform for Navavej International Hospital.
              Providing precision medicine powered by advanced AI architecture.
            </p>
          </div>
          {['Healthcare Info', 'Our Services', 'Contact Us'].map((col) => (
            <div key={col}>
              <h4 className="font-black text-navavej-gray-dark text-sm uppercase tracking-widest mb-6">{col}</h4>
              <ul className="space-y-3">
                {[1, 2, 3].map(i => (
                  <li key={i} className="text-xs font-bold text-navavej-gray-med hover:text-navavej-teal cursor-pointer">Sample Link {i}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </footer>
    </div>
  );
}
