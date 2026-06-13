"use client";

import React from "react";
import { DollarSign, ShieldAlert, Award, Star } from "lucide-react";

interface MetricSummaryProps {
  score: number;
  confidence: number;
  revenue: number;
  probability: number;
}

export default function MetricSummary({ score, confidence, revenue, probability }: MetricSummaryProps) {
  
  const metrics = [
    {
      label: "Qualified Lead Score",
      val: score > 0 ? `${score}/100` : "0/100",
      desc: score >= 70 ? "High Fit ICP Target" : score >= 50 ? "Medium Fit Prospect" : "Low Fit Prospect",
      icon: Award,
      color: "text-green-400 bg-green-950/25 border-green-500/20"
    },
    {
      label: "Forecast Contract Value (ACV)",
      val: revenue > 0 ? `$${revenue.toLocaleString()}` : "$0",
      desc: "Annual Contract Prediction",
      icon: DollarSign,
      color: "text-violet-400 bg-violet-950/25 border-violet-500/20"
    },
    {
      label: "Deal Close Probability",
      val: probability > 0 ? `${probability}%` : "0%",
      desc: probability >= 70 ? "Likely to Close" : probability >= 40 ? "Needs Nurturing" : "High Risk Prospect",
      icon: Star,
      color: "text-amber-400 bg-amber-950/25 border-amber-500/20"
    },
    {
      label: "Model Orchestration Confidence",
      val: confidence > 0 ? `${confidence.toFixed(0)}%` : "0%",
      desc: "System Telemetry Precision",
      icon: ShieldAlert,
      color: "text-cyan-400 bg-cyan-950/25 border-cyan-500/20"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {metrics.map((m, idx) => {
        const Icon = m.icon;
        return (
          <div key={idx} className="glass-panel rounded-2xl p-5 border-slate-800 flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 mb-1">{m.label}</p>
              <h3 className="text-2xl font-bold tracking-tight text-white mb-1">{m.val}</h3>
              <p className="text-[10px] text-slate-500">{m.desc}</p>
            </div>
            <div className={`p-2.5 rounded-xl border ${m.color}`}>
              <Icon className="w-5 h-5" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
