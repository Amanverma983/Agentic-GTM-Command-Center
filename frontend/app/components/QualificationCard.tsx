"use client";

import React from "react";
import { Check, ShieldAlert, Award } from "lucide-react";

interface QualificationData {
  qualification_score: number;
  confidence_score: number;
  icp_fit: string;
  reasoning: string;
  strengths: string[];
  weaknesses: string[];
}

interface QualificationCardProps {
  data: QualificationData | null;
}

export default function QualificationCard({ data }: QualificationCardProps) {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-[300px] text-slate-500 italic text-sm">
        Awaiting Lead Qualification Agent evaluation...
      </div>
    );
  }

  // Determine styles based on ICP Fit
  const getFitStyle = (fit: string) => {
    switch (fit.toLowerCase()) {
      case "high":
        return "bg-green-500/10 text-green-400 border-green-500/20";
      case "medium":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      default:
        return "bg-red-500/10 text-red-400 border-red-500/20";
    }
  };

  return (
    <div className="space-y-6">
      {/* Score Telemetry Header */}
      <div className="flex flex-col sm:flex-row items-center gap-6 p-4 rounded-xl bg-slate-950/40 border border-slate-900">
        
        {/* Radial Score Indicator */}
        <div className="relative w-24 h-24 flex items-center justify-center flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            {/* Background Circle */}
            <circle 
              cx="50" cy="50" r="40" 
              className="stroke-slate-800" 
              strokeWidth="8" fill="transparent" 
            />
            {/* Progress Circle */}
            <circle 
              cx="50" cy="50" r="40" 
              className="stroke-violet-500" 
              strokeWidth="8" fill="transparent" 
              strokeDasharray={251.2}
              strokeDashoffset={251.2 - (251.2 * data.qualification_score) / 100}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-xl font-bold text-white">{data.qualification_score}</span>
            <span className="text-[9px] font-semibold text-slate-500 uppercase">Score</span>
          </div>
        </div>

        {/* Info Badges */}
        <div className="flex-1 space-y-3 text-center sm:text-left">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
            <span className={`px-3 py-1 text-xs font-bold rounded-full border ${getFitStyle(data.icp_fit)}`}>
              {data.icp_fit} ICP Fit
            </span>
            <span className="px-3 py-1 text-xs font-bold rounded-full border border-slate-800 bg-slate-900 text-slate-400">
              Confidence: {data.confidence_score}%
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {data.reasoning}
          </p>
        </div>
      </div>

      {/* Strengths & Weaknesses Checklist */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Award className="w-4 h-4 text-green-400" />
            <span>Target Match Strengths</span>
          </h3>
          <ul className="space-y-2">
            {data.strengths.map((str, idx) => (
              <li key={idx} className="text-xs text-slate-300 bg-slate-950/20 border border-slate-900/50 p-2.5 rounded-lg flex items-start gap-2.5">
                <div className="p-0.5 rounded-full bg-green-500/10 text-green-400 flex-shrink-0 mt-0.5">
                  <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                </div>
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Risk Factors & Gaps</span>
          </h3>
          <ul className="space-y-2">
            {data.weaknesses.map((weak, idx) => (
              <li key={idx} className="text-xs text-slate-300 bg-slate-950/20 border border-slate-900/50 p-2.5 rounded-lg flex items-start gap-2.5">
                <div className="p-0.5 rounded-full bg-amber-500/10 text-amber-400 flex-shrink-0 mt-0.5">
                  <ShieldAlert className="w-3.5 h-3.5" />
                </div>
                <span>{weak}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
