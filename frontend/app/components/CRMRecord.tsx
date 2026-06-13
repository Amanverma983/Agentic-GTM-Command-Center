"use client";

import React, { useState } from "react";
import { User, ClipboardCheck, Code, Copy, Check } from "lucide-react";

interface CRMData {
  lead_name: string;
  company: string;
  industry: string;
  lead_score: number;
  deal_stage: string;
  priority: string;
  notes: string;
}

interface CRMRecordProps {
  data: CRMData | null;
}

export default function CRMRecord({ data }: CRMRecordProps) {
  const [showJson, setShowJson] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!data) {
    return (
      <div className="flex items-center justify-center h-[300px] text-slate-500 italic text-sm">
        Awaiting CRM Agent preparation...
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getPriorityStyle = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "high": return "bg-red-500/10 text-red-400 border-red-500/20";
      case "medium": return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      default: return "bg-slate-500/10 text-slate-400 border-slate-800";
    }
  };

  const crmRows = [
    { label: "Lead Contact Name", val: data.lead_name },
    { label: "Company Portal", val: data.company },
    { label: "Industry Vector", val: data.industry },
    { label: "Lead Qualification Score", val: `${data.lead_score}/100` },
    { label: "Deal Ingestion Stage", val: data.deal_stage },
    { 
      label: "Account Priority", 
      val: (
        <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${getPriorityStyle(data.priority)}`}>
          {data.priority}
        </span>
      ) 
    }
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">HubSpot & Salesforce Mapping</h3>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setShowJson(!showJson)}
            className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[10px] font-semibold text-slate-300 hover:text-white transition-colors flex items-center gap-1"
          >
            <Code className="w-3 h-3" />
            <span>{showJson ? "Table View" : "Raw JSON"}</span>
          </button>
          <button 
            onClick={handleCopy}
            className="p-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {showJson ? (
        <pre className="p-4 rounded-xl bg-slate-950/80 border border-slate-900 text-xs text-violet-300 overflow-x-auto max-h-[300px]">
          {JSON.stringify(data, null, 2)}
        </pre>
      ) : (
        <div className="rounded-xl border border-slate-900 bg-slate-950/20 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <tbody>
              {crmRows.map((row, idx) => (
                <tr key={idx} className="border-b border-slate-900 last:border-0 hover:bg-slate-950/40">
                  <td className="px-4 py-3 text-xs font-semibold text-slate-500 w-1/3 bg-slate-950/30">
                    {row.label}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-300 font-medium">
                    {row.val}
                  </td>
                </tr>
              ))}
              <tr>
                <td className="px-4 py-3 text-xs font-semibold text-slate-500 w-1/3 bg-slate-950/30 valign-top">
                  CRM Opportunity Notes
                </td>
                <td className="px-4 py-3 text-xs text-slate-300 leading-relaxed">
                  {data.notes}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
