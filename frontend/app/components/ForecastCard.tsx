"use client";

import React from "react";
import { AlertCircle, ArrowUpRight, TrendingUp } from "lucide-react";

interface ForecastData {
  close_probability: number;
  estimated_revenue: number;
  deal_risk: string;
  risk_factors: string[];
  recommended_next_step: string;
}

interface ForecastCardProps {
  data: ForecastData | null;
}

export default function ForecastCard({ data }: ForecastCardProps) {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-[300px] text-slate-500 italic text-sm">
        Awaiting Forecast Agent calculation...
      </div>
    );
  }

  const getRiskStyle = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "low": return "bg-green-500/10 text-green-400 border-green-500/25";
      case "medium": return "bg-amber-500/10 text-amber-400 border-amber-500/25";
      default: return "bg-red-500/10 text-red-400 border-red-500/25";
    }
  };

  return (
    <div className="space-y-6">
      {/* Probability Gauge & Contract Value Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* close probability */}
        <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-900 flex flex-col justify-between h-full">
          <div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">Close Probability</p>
            <h3 className="text-3xl font-extrabold text-white tracking-tight">{data.close_probability}%</h3>
          </div>
          {/* Progress Slider */}
          <div className="w-full bg-slate-900 rounded-full h-1.5 mt-4 overflow-hidden">
            <div 
              className="bg-violet-500 h-1.5 rounded-full transition-all duration-500" 
              style={{ width: `${data.close_probability}%` }}
            />
          </div>
        </div>

        {/* contract size */}
        <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-900 flex flex-col justify-between h-full">
          <div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">Estimated ACV</p>
            <h3 className="text-3xl font-extrabold text-emerald-400 tracking-tight">
              ${data.estimated_revenue.toLocaleString()}
            </h3>
          </div>
          <div className="flex items-center gap-1 text-[10px] text-slate-500 mt-4">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            <span>Projected Annual Contract Size</span>
          </div>
        </div>
      </div>

      {/* Deal Risk Section */}
      <div className="p-4 rounded-xl bg-slate-950/20 border border-slate-900 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Deal Risk Tier</span>
          <span className={`px-2.5 py-0.5 text-[10px] font-bold rounded-full border ${getRiskStyle(data.deal_risk)}`}>
            {data.deal_risk} Risk
          </span>
        </div>
        <hr className="border-slate-900" />
        <div className="space-y-1.5">
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Identified Risk Drivers</p>
          {data.risk_factors.map((factor, idx) => (
            <div key={idx} className="flex items-start gap-2 text-xs text-slate-400">
              <AlertCircle className="w-4 h-4 text-red-400/80 flex-shrink-0 mt-0.5" />
              <span>{factor}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Playbook */}
      <div className="p-4 rounded-xl bg-violet-950/10 border border-violet-900/30 space-y-2">
        <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider flex items-center gap-1">
          <ArrowUpRight className="w-4 h-4" />
          <span>Recommended Next Action Play</span>
        </span>
        <p className="text-xs text-slate-200 leading-relaxed font-semibold">
          {data.recommended_next_step}
        </p>
      </div>
    </div>
  );
}
