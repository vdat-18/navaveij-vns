"use client";

import React, { useState } from "react";
import Link from "next/link";

import { PatientList } from "@/components/dashboard/PatientList";
import { TrendTimelineScreen } from "@/components/trend-timeline/TrendTimelineScreen";

interface Patient {
  patient_id: string;
  patient_name: string;
  patient_token: string;
}

export default function TrendTimelinePage() {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  return (
    <main className="w-full px-8 lg:px-16 py-10 min-h-screen bg-white">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-black text-navavej-gray-dark uppercase tracking-tighter">
          Screen 2 — Trend & Timeline
        </h1>
        <Link href="/" className="text-xs font-black text-navavej-teal uppercase">
          Back to Summary
        </Link>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        <div className="xl:col-span-3">
          <div className="bg-[#fcfdfe] p-4 rounded-[20px] border border-navavej-border min-h-[640px] shadow-inner">
            <PatientList
              onSelectPatient={setSelectedPatient}
              selectedId={selectedPatient?.patient_id}
            />
          </div>
        </div>
        <div className="xl:col-span-9">
          {selectedPatient ? (
            <TrendTimelineScreen
              patientName={selectedPatient.patient_name}
              patientId={selectedPatient.patient_id}
              patientToken={selectedPatient.patient_token}
            />
          ) : (
            <div className="navavej-card bg-white p-10 text-center">
              <p className="text-sm font-black text-navavej-gray-med uppercase">
                Select a patient to inspect trend and timeline data
              </p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
