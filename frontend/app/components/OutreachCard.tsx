"use client";

import React, { useState, useEffect } from "react";
import { Copy, Check, Mail, MessageSquare, Mic, ListCollapse, Send, Loader2, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";

interface OutreachData {
  cold_email_subject: string;
  cold_email_body: string;
  linkedin_message: string;
  sales_pitch: string;
  follow_up_sequence: string[];
}

interface OutreachCardProps {
  data: OutreachData | null;
  leadId: string | null;
}

type TabType = "email" | "linkedin" | "pitch" | "followups";
type SendStatus = "idle" | "sending" | "success" | "error";

export default function OutreachCard({ data, leadId }: OutreachCardProps) {
  const [activeTab, setActiveTab] = useState<TabType>("email");
  const [copied, setCopied] = useState(false);

  // Email sending state
  const [toEmail, setToEmail] = useState("");
  const [prospectName, setProspectName] = useState("");
  const [sendStatus, setSendStatus] = useState<SendStatus>("idle");
  const [sendMessage, setSendMessage] = useState("");
  const [smtpConfigured, setSmtpConfigured] = useState<boolean | null>(null);

  // Check SMTP status on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/leads/smtp-status")
      .then((r) => r.json())
      .then((d) => setSmtpConfigured(d.configured))
      .catch(() => setSmtpConfigured(false));
  }, []);

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

  const handleSendEmail = async () => {
    if (!toEmail.trim()) {
      setSendMessage("Please enter the prospect's email address.");
      setSendStatus("error");
      return;
    }
    if (!leadId) {
      setSendMessage("No active lead found.");
      setSendStatus("error");
      return;
    }

    setSendStatus("sending");
    setSendMessage("");

    try {
      const response = await fetch(`http://localhost:8000/api/leads/${leadId}/send-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to_email: toEmail.trim(),
          prospect_name: prospectName.trim() || null,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Email sending failed.");
      }

      setSendStatus("success");
      setSendMessage(`✅ Email sent to ${toEmail}`);
    } catch (err: any) {
      setSendStatus("error");
      setSendMessage(err.message || "Failed to send email.");
    }
  };

  const tabs = [
    { id: "email", name: "Cold Email", icon: Mail },
    { id: "linkedin", name: "LinkedIn Message", icon: MessageSquare },
    { id: "pitch", name: "Elevator Pitch", icon: Mic },
    { id: "followups", name: "Follow-up Sequence", icon: ListCollapse },
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

      {/* ── SEND EMAIL PANEL ── */}
      <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Send className="w-4 h-4 text-violet-400" />
            <span className="text-sm font-bold text-slate-200">Send Cold Email</span>
          </div>
          {/* SMTP status pill */}
          {smtpConfigured === true && (
            <span className="flex items-center gap-1 text-[10px] font-semibold text-green-400 bg-green-950/30 border border-green-500/20 px-2 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse inline-block" />
              Gmail Ready
            </span>
          )}
          {smtpConfigured === false && (
            <span className="flex items-center gap-1 text-[10px] font-semibold text-amber-400 bg-amber-950/30 border border-amber-500/20 px-2 py-0.5 rounded-full">
              <AlertTriangle className="w-3 h-3" />
              SMTP Not Set
            </span>
          )}
        </div>

        {smtpConfigured === false && (
          <div className="text-[11px] text-amber-400/80 bg-amber-950/10 border border-amber-900/30 rounded-lg p-2.5 leading-relaxed">
            <strong>Setup needed:</strong> Add <code className="bg-slate-900 px-1 rounded">SMTP_EMAIL</code> and <code className="bg-slate-900 px-1 rounded">SMTP_APP_PASSWORD</code> to <code className="bg-slate-900 px-1 rounded">backend/.env</code> to enable live email sending.
            <br />
            <span className="text-slate-500">Gmail → My Account → Security → App Passwords</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div>
            <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block mb-1">
              Prospect Email *
            </label>
            <input
              type="email"
              value={toEmail}
              onChange={(e) => { setToEmail(e.target.value); setSendStatus("idle"); }}
              placeholder="cto@prospect.com"
              className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-violet-500 transition-colors placeholder:text-slate-600"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block mb-1">
              Prospect Name (optional)
            </label>
            <input
              type="text"
              value={prospectName}
              onChange={(e) => setProspectName(e.target.value)}
              placeholder="e.g. John Smith"
              className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-violet-500 transition-colors placeholder:text-slate-600"
            />
          </div>
        </div>

        <button
          onClick={handleSendEmail}
          disabled={sendStatus === "sending" || !smtpConfigured}
          className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-xs font-bold transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-violet-500/10"
        >
          {sendStatus === "sending" ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Sending via Gmail SMTP...
            </>
          ) : (
            <>
              <Send className="w-3.5 h-3.5" />
              Send AI Cold Email Now
            </>
          )}
        </button>

        {/* Send Status Feedback */}
        {sendStatus === "success" && (
          <div className="flex items-center gap-2 text-xs text-green-400 bg-green-950/20 border border-green-500/20 rounded-lg p-2.5">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{sendMessage}</span>
          </div>
        )}
        {sendStatus === "error" && (
          <div className="flex items-start gap-2 text-xs text-red-400 bg-red-950/20 border border-red-500/20 rounded-lg p-2.5">
            <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{sendMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
}
