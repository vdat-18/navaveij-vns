"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { clinicalService } from "@/services/api";
import { BiomarkerSeries, ScreeningGapRow, TimelinePayload } from "@/types/timeline";
import { BiomarkerTrendGrid } from "./BiomarkerTrendGrid";
import { ClinicalEventTimeline } from "./ClinicalEventTimeline";
import { ScreeningGapStatus } from "./ScreeningGapStatus";

interface TrendTimelineScreenProps {
  patientName: string;
  patientId: string;
  patientToken: string;
}

export function TrendTimelineScreen({ patientName, patientId, patientToken }: TrendTimelineScreenProps) {
  const [timeline, setTimeline] = useState<TimelinePayload | null>(null);
  const [biomarkers, setBiomarkers] = useState<any>(null);
  const [screeningGaps, setScreeningGaps] = useState<ScreeningGapRow[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [rangeYears, setRangeYears] = useState(5);

  useEffect(() => {
    let active = true;
    const run = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const [timelineData, biomarkerData, screeningData] = await Promise.all([
          clinicalService.getTimeline(patientToken),
          clinicalService.getBiomarkerTrends(patientToken),
          clinicalService.getScreeningGaps(patientToken),
        ]);
        if (!active) {
          return;
        }
        setTimeline(timelineData);
        setBiomarkers(biomarkerData);
        setScreeningGaps([
          ...(screeningData.screening_gaps || []),
          ...(screeningData.vaccination_gaps || []),
        ]);
      } catch (error) {
        if (!active) {
          return;
        }
        const message = error instanceof Error ? error.message : "Unable to load trend and timeline data.";
        setErrorMessage(message);
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };
    run();
    return () => {
      active = false;
    };
  }, [patientToken]);

  const startYear = useMemo(() => {
    const latest = timeline?.timeline_span?.latest_event_date?.slice(0, 4);
    const latestYear = latest ? Number(latest) : new Date().getFullYear();
    return latestYear - rangeYears + 1;
  }, [timeline, rangeYears]);

  const chartSeries = useMemo<BiomarkerSeries[]>(() => {
    if (!biomarkers) return [];
    const getLab = (labId: string) => (biomarkers.labs || []).find((item: any) => item.lab_id === labId);
    const filterHistory = (history: any[] = []) =>
      history.filter((h) => Number((h.date || "").slice(0, 4)) >= startYear);

    const fbs = getLab("fbs");
    const hba1c = getLab("hba1c");
    const ldl = getLab("ldl");
    const bmi = biomarkers.bmi;
    const bp = biomarkers.blood_pressure;
    const egfr = biomarkers.egfr;
    return [
      {
        label: "FBS",
        loinc_code: fbs?.loinc_code || "1558-6",
        unit: fbs?.unit || "mg/dL",
        trend_direction: fbs?.trend_direction || "unknown",
        slope_per_year: fbs?.velocity_per_year ?? null,
        reference: fbs?.reference_range?.high,
        current: fbs?.current_value || 0,
        history: filterHistory(fbs?.history || []),
      },
      {
        label: "HbA1c",
        loinc_code: hba1c?.loinc_code || "4548-4",
        unit: hba1c?.unit || "%",
        trend_direction: hba1c?.trend_direction || "unknown",
        slope_per_year: hba1c?.velocity_per_year ?? null,
        reference: hba1c?.reference_range?.high,
        current: hba1c?.current_value || 0,
        history: filterHistory(hba1c?.history || []),
      },
      {
        label: "LDL",
        loinc_code: ldl?.loinc_code || "2089-1",
        unit: ldl?.unit || "mg/dL",
        trend_direction: ldl?.trend_direction || "unknown",
        slope_per_year: ldl?.velocity_per_year ?? null,
        reference: ldl?.reference_range?.borderline_high_low || 130,
        current: ldl?.current_value || 0,
        history: filterHistory(ldl?.history || []),
      },
      {
        label: "BMI",
        loinc_code: "39156-5",
        unit: bmi?.unit || "kg/m²",
        trend_direction: bmi?.trend_direction || "unknown",
        slope_per_year: bmi?.slope_per_year ?? null,
        reference: 23,
        current: bmi?.current || 0,
        history: filterHistory(bmi?.history || []),
      },
      {
        label: "BP Systolic",
        loinc_code: "55284-4",
        unit: "mmHg",
        trend_direction: bp?.trend_direction || "unknown",
        slope_per_year: bp?.sbp_slope_per_year ?? null,
        reference: 120,
        current: bp?.latest?.sbp || 0,
        history: filterHistory((bp?.history || []).map((item: any) => ({ date: item.date, value: item.sbp }))),
      },
      {
        label: "eGFR",
        loinc_code: egfr?.loinc_code || "62238-1",
        unit: egfr?.unit || "mL/min/1.73m2",
        trend_direction: egfr?.trend_direction || "unknown",
        slope_per_year: egfr?.annual_slope ?? null,
        reference: 60,
        current: egfr?.current || 0,
        history: filterHistory(egfr?.history || []),
      },
    ];
  }, [biomarkers, startYear]);

  return (
    <div className="space-y-6">
      <div className="navavej-card bg-[#F0F9FA] border-navavej-teal/20 p-5 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-black text-navavej-gray-dark uppercase tracking-tighter">
            Trend & Timeline
          </h2>
          <p className="text-xs text-navavej-gray-med font-bold mt-2">
            {patientName} • {patientId} • {patientToken}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={rangeYears}
            onChange={(e) => setRangeYears(Number(e.target.value))}
            className="border border-navavej-border rounded-lg px-2 py-1 text-xs font-bold"
          >
            <option value={1}>1 year</option>
            <option value={3}>3 years</option>
            <option value={5}>5 years</option>
            <option value={10}>10 years</option>
          </select>
          <Link href="/" className="text-xs font-black text-navavej-teal uppercase">
            Back to Summary
          </Link>
        </div>
      </div>

      <BiomarkerTrendGrid series={chartSeries} />

      {isLoading && (
        <div className="navavej-card bg-white p-4 border border-navavej-border">
          <p className="text-xs font-black text-navavej-gray-med uppercase">
            Loading trend and timeline data...
          </p>
        </div>
      )}

      {errorMessage && (
        <div className="navavej-card bg-[#fff5f5] p-4 border border-navavej-red/30">
          <p className="text-xs font-black text-navavej-red uppercase">
            Data load warning
          </p>
          <p className="text-xs font-bold text-navavej-gray-dark mt-2">{errorMessage}</p>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <ClinicalEventTimeline timeline={timeline} startYear={startYear} />
        <ScreeningGapStatus screeningGaps={screeningGaps} />
      </div>
    </div>
  );
}
