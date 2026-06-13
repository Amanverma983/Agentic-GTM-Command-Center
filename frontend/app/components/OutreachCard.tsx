"use client";

import React, { useState } from "react";
import { Copy, Check, Mail, MessageSquare, Mic, ListCollapse } from "lucide-react";

interface OutreachData {
  cold_email_subject: string;
  cold_email_body: string;
  linkedin_message: string;
  sales_pitch: string;
  follow_up_sequence: string[];
}

interface OutreachCardProps {
  data: OutreachData | null;
}

type TabType = "email" | "linkedin" | "pitch" | "followups";

export default function OutreachCard({ data }: OutreachCardProps) {
  const [activeTab, setActiveTab] = useState<TabType>("email");
  const [copied, setCopied] = useState(false);

  if (!data) {
    return (
      <div className="flex items-center justify-center h-[300px] text-slate-500 italic text-sm">
        Awaiting Outreach Agent execution...
      </div>
    );
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tabs = [
    { id: "email", name: "Cold Email", icon: Mail },
    { id: "linkedin", name: "LinkedIn Message", icon: MessageSquare },
    { id: "pitch", name: "Elevator Pitch", icon: Mic },
    { id: "followups", name: "Follow-up Sequence", icon: ListCollapse }
  ];

  return (
    <div className="space-y-4">
      {/* Tab Selectors */}
      <div className="flex flex-wrap border-b border-slate-800">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as TabType);
                setCopied(false);
              }}
              className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold border-b-2 transition-all duration-200 ${
                activeTab === tab.id
                  ? "border-violet-500 text-violet-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.name}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      <div className="relative p-4 rounded-xl bg-slate-950/50 border border-slate-900 min-h-[200px]">
        {/* Copy Button */}
        <button
          onClick={() => {
            if (activeTab === "email") {
              handleCopy(`Subject: ${data.cold_email_subject}\n\n${data.cold_email_body}`);
            } else if (activeTab === "linkedin") {
              handleCopy(data.linkedin_message);
            } else if (activeTab === "pitch") {
              handleCopy(data.sales_pitch);
            } else if (activeTab === "followups") {
              handleCopy(data.follow_up_sequence.join("\n\n"));
            }
          }}
          className="absolute top-4 right-4 p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5 text-[10px] font-semibold"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-green-400" />
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>

        {activeTab === "email" && (
          <div className="space-y-4 pr-16 text-sm text-slate-300 leading-relaxed font-sans">
            <div>
              <span className="text-xs text-slate-500 font-bold uppercase tracking-wider block mb-1">Subject</span>
              <p className="font-semibold text-slate-200">{data.cold_email_subject}</p>
            </div>
            <hr className="border-slate-900" />
            <div>
              <span className="text-xs text-slate-500 font-bold uppercase tracking-wider block mb-1">Body</span>
              <pre className="whitespace-pre-wrap font-sans text-xs text-slate-300">{data.cold_email_body}</pre>
            </div>
          </div>
        )}

        {activeTab === "linkedin" && (
          <div className="pr-16 space-y-2">
            <span className="text-xs text-slate-500 font-bold uppercase tracking-wider block mb-1">InMail / DM Script</span>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/20 p-3 rounded-lg border border-slate-900 italic">
              &quot;{data.linkedin_message}&quot;
            </p>
            <span className="text-[10px] text-slate-500 block">Character Count: {data.linkedin_message.length}</span>
          </div>
        )}

        {activeTab === "pitch" && (
          <div className="pr-16 space-y-2">
            <span className="text-xs text-slate-500 font-bold uppercase tracking-wider block mb-1">30-Second Elevator Pitch</span>
            <p className="text-sm text-slate-300 leading-relaxed bg-violet-950/10 p-4 rounded-lg border border-violet-900/20 font-medium">
              &quot;{data.sales_pitch}&quot;
            </p>
          </div>
        )}

        {activeTab === "followups" && (
          <div className="pr-16 space-y-4">
            {data.follow_up_sequence.map((msg, idx) => (
              <div key={idx} className="space-y-2">
                <span className="text-xs text-slate-500 font-bold uppercase tracking-wider block">Follow-up {idx + 1}</span>
                <pre className="whitespace-pre-wrap font-sans text-xs text-slate-300 bg-slate-950/30 p-3 rounded-lg border border-slate-900/50">
                  {msg}
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
