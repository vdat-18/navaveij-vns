"use client";

import React from "react";
import { CLINICAL_DICTIONARY } from "@/shared/clinical-dictionary";

interface ClinicalReportProps {
    patient: any;
    data: any;
}

export function ClinicalReport({ patient, data }: ClinicalReportProps) {
    if (!data || !patient) return null;

    const translate = (key: string) => CLINICAL_DICTIONARY[key] || key;

    return (
        <div id="clinical-report-container" className="hidden print:block font-serif text-navavej-gray-dark bg-white">
            {/* Header */}
            <div className="flex justify-between items-start border-b-2 border-navavej-teal pb-6 mb-8">
                <div>
                    <h1 className="text-3xl font-black text-navavej-teal tracking-tighter uppercase leading-none">
                        Navavej <span className="text-navavej-gray-dark">International Hospital</span>
                    </h1>
                    <p className="text-[10px] font-bold text-navavej-gray-med mt-2 uppercase tracking-widest leading-none">Clinical Strategy Advisory Report</p>
                </div>
                <div className="text-right">
                    <p className="text-[10px] font-bold text-navavej-gray-med uppercase">Official Report Date</p>
                    <p className="text-sm font-black">{new Date().toLocaleDateString("en-GB", { day: '2-digit', month: 'long', year: 'numeric' })}</p>
                </div>
            </div>

            {/* Patient Info */}
            <div className="bg-navavej-gray-light/50 p-6 rounded-xl border border-navavej-border mb-8">
                <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-navavej-teal mb-4">Patient Demographics</h2>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                    <div>
                        <p className="text-[9px] font-bold text-navavej-gray-med uppercase">Patient Name</p>
                        <p className="text-sm font-black uppercase">{patient.patient_name || "N/A"}</p>
                    </div>
                    <div>
                        <p className="text-[9px] font-bold text-navavej-gray-med uppercase">Medical ID (MRN)</p>
                        <p className="text-sm font-black">{patient.patient_id || patient.mrn}</p>
                    </div>
                    <div>
                        <p className="text-[9px] font-bold text-navavej-gray-med uppercase">Age / Gender</p>
                        <p className="text-sm font-black">{patient.age} Yrs / {patient.gender}</p>
                    </div>
                    <div>
                        <p className="text-[9px] font-bold text-navavej-gray-med uppercase">Ethnicity</p>
                        <p className="text-sm font-black capitalize">{patient.ethnicity}</p>
                    </div>
                </div>
            </div>

            {/* Biomarker Table */}
            <div className="mb-8">
                <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-navavej-teal mb-4">Current Clinical Indicators</h2>
                <table className="w-full border-collapse">
                    <thead>
                        <tr className="bg-navavej-gray-light border-y border-navavej-border">
                            <th className="px-4 py-3 text-[9px] font-black text-left uppercase text-navavej-gray-med">Indicator</th>
                            <th className="px-4 py-3 text-[9px] font-black text-left uppercase text-navavej-gray-med">Current Value</th>
                            <th className="px-4 py-3 text-[9px] font-black text-left uppercase text-navavej-gray-med">Previous (Last Visit)</th>
                            <th className="px-4 py-3 text-[9px] font-black text-left uppercase text-navavej-gray-med">Clinical status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-navavej-border">
                        <tr>
                            <td className="px-4 py-4 text-xs font-bold">Body Mass Index (BMI)</td>
                            <td className="px-4 py-4 text-xs font-black">{data.biomarker_trends?.bmi?.history?.[0]?.value || "N/A"} kg/m²</td>
                            <td className="px-4 py-4 text-xs font-medium text-navavej-gray-med">{data.biomarker_trends?.bmi?.history?.[1]?.value || "--"}</td>
                            <td className="px-4 py-4 text-xs font-black text-navavej-teal uppercase tracking-tighter">Monitored</td>
                        </tr>
                        <tr>
                            <td className="px-4 py-4 text-xs font-bold">Systolic BP</td>
                            <td className="px-4 py-4 text-xs font-black">{data.biomarker_trends?.blood_pressure?.history?.[0]?.sbp || "N/A"} mmHg</td>
                            <td className="px-4 py-4 text-xs font-medium text-navavej-gray-med">{data.biomarker_trends?.blood_pressure?.history?.[1]?.sbp || "--"}</td>
                            <td className="px-4 py-4 text-xs font-black text-navavej-red uppercase tracking-tighter">Review High</td>
                        </tr>
                        <tr>
                            <td className="px-4 py-4 text-xs font-bold">Diastolic BP</td>
                            <td className="px-4 py-4 text-xs font-black">{data.biomarker_trends?.blood_pressure?.history?.[0]?.dbp || "N/A"} mmHg</td>
                            <td className="px-4 py-4 text-xs font-medium text-navavej-gray-med">{data.biomarker_trends?.blood_pressure?.history?.[1]?.dbp || "--"}</td>
                            <td className="px-4 py-4 text-xs font-black text-navavej-teal uppercase tracking-tighter">Normal range</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* Recommendation Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div className="border-2 border-navavej-teal p-8 rounded-2xl bg-navavej-teal/5">
                    <p className="text-[10px] font-black text-navavej-teal uppercase tracking-widest mb-4">Recommended Strategy</p>
                    <h3 className="text-4xl font-black text-navavej-teal mb-4 uppercase leading-none tracking-tighter">
                        {data.package_name || data.ai_recommended_tier}
                    </h3>
                    <p className="text-xl font-black italic text-navavej-gray-dark">Value: ฿{data.price_thb?.toLocaleString()}</p>
                </div>
                <div className="border border-navavej-border p-8 rounded-2xl flex flex-col justify-center">
                    <p className="text-[10px] font-black text-navavej-gray-med uppercase tracking-widest mb-4">Clinical Logic Summary</p>
                    <p className="text-xs font-medium leading-relaxed italic text-justify">
                        "{data.communication_script?.clinical_conclusion || "Finalized after comprehensive review of 3-year history and biomarker trends."}"
                    </p>
                </div>
            </div>

            {/* Add-ons & Gaps */}
            <div className="grid grid-cols-2 gap-10 mb-8 p-6 border border-navavej-border rounded-2xl">
                <div>
                    <h4 className="text-[10px] font-black text-navavej-teal uppercase tracking-[0.2em] mb-4">Added Screenings</h4>
                    <ul className="space-y-4">
                        {data.add_ons?.map((item: any, i: number) => (
                            <li key={i} className="flex gap-4">
                                <div className="mt-1 w-1.5 h-1.5 rounded-full bg-navavej-teal shrink-0" />
                                <div>
                                    <p className="text-xs font-black text-navavej-gray-dark uppercase">{item.item_code}</p>
                                    <p className="text-[10px] font-medium text-navavej-gray-med italic">{item.rationale}</p>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
                <div>
                    <h4 className="text-[10px] font-black text-navavej-red uppercase tracking-[0.2em] mb-4">Preventive Alerts</h4>
                    {data.clinical_signals?.screening_gaps?.map((gap: any, i: number) => (
                        <div key={i} className="mb-4 border-l-2 border-navavej-red pl-4 py-1">
                            <p className="text-xs font-black text-navavej-gray-dark uppercase">{gap.label}</p>
                            <p className="text-[10px] font-medium text-navavej-red italic">{gap.note}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Physician Notes */}
            <div className="p-8 border-2 border-navavej-gray-med/20 rounded-2xl mb-12">
                <p className="text-[10px] font-black text-navavej-gray-med uppercase tracking-[0.2em] mb-4">Physician Observation & Confirmation</p>
                <div className="min-h-[100px] text-sm font-medium italic text-navavej-gray-dark leading-relaxed">
                    {data.physician_notes || "Confirmed implementation of personalized health program. Risk profiling validated against baseline data."}
                </div>
                <div className="mt-10 flex border-t border-navavej-border pt-6 items-end justify-between">
                    <div>
                        <p className="text-[9px] font-black text-navavej-gray-med uppercase mb-8">Physician Digital Signature</p>
                        <p className="text-sm font-black border-t-2 border-navavej-gray-dark pt-2 px-10">DR. CLINICIAN</p>
                    </div>
                    <div className="text-right">
                        <p className="text-[8px] font-bold text-navavej-gray-med uppercase mb-1">Audit Reference</p>
                        <p className="font-mono text-[8px] text-navavej-gray-med uppercase">{data.recommendation_hash || "LOG_TRACE_001X"}</p>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="border-t border-navavej-border pt-6 text-center">
                <p className="text-[8px] font-bold text-navavej-gray-med uppercase tracking-widest leading-loose">
                    Navavej International Hospital • 9 Ratchadaphisek Rd, Bangkok, Thailand • Tel: 1507
                </p>
                <p className="text-[7px] text-navavej-gray-med italic">
                    This document is a clinical advisory generated for hospital internal use and patient counseling. Final medical decision rests with the attending physician.
                </p>
            </div>
        </div>
    );
}
