"use client";

import React from "react";
import { Building2, Landmark, CheckCircle, Lightbulb } from "lucide-react";

interface ResearchData {
  company_name: string;
  industry: string;
  business_model: string;
  summary: string;
  pain_points: string[];
  opportunities: string[];
  strategic_insights: string[];
}

interface ResearchCardProps {
  data: ResearchData | null;
}

export default function ResearchCard({ data }: ResearchCardProps) {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-[300px] text-slate-500 italic text-sm">
        Awaiting Research Agent execution...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-950/40 border border-slate-900">
          <Building2 className="w-5 h-5 text-violet-400" />
          <div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Industry</p>
            <p className="text-sm font-semibold text-slate-200">{data.industry}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-950/40 border border-slate-900">
          <Landmark className="w-5 h-5 text-indigo-400" />
          <div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Business Model</p>
            <p className="text-sm font-semibold text-slate-200">{data.business_model}</p>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div>
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Company Overview</h3>
        <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/20 border border-slate-900 p-4 rounded-xl">
          {data.summary}
        </p>
      </div>

      {/* Pain Points & Opportunities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <CheckCircle className="w-4 h-4 text-red-400" />
            <span>Target Pain Points</span>
          </h3>
          <ul className="space-y-2">
            {data.pain_points.map((pt, idx) => (
              <li key={idx} className="text-xs text-slate-400 bg-slate-950/30 border border-slate-900/50 p-2.5 rounded-lg flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0 mt-1.5" />
                <span>{pt}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Lightbulb className="w-4 h-4 text-green-400" />
            <span>Growth Opportunities</span>
          </h3>
          <ul className="space-y-2">
            {data.opportunities.map((op, idx) => (
              <li key={idx} className="text-xs text-slate-400 bg-slate-950/30 border border-slate-900/50 p-2.5 rounded-lg flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0 mt-1.5" />
                <span>{op}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Strategic Insights */}
      {data.strategic_insights && data.strategic_insights.length > 0 && (
        <div>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Strategic GTM Insights</h3>
          <div className="bg-violet-950/10 border border-violet-900/30 p-4 rounded-xl space-y-2">
            {data.strategic_insights.map((ins, idx) => (
              <p key={idx} className="text-xs text-slate-300 flex items-start gap-2 leading-relaxed">
                <span className="text-violet-400 font-bold">0{idx + 1}.</span>
                <span>{ins}</span>
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
