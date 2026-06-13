"use client";

import React, { useState } from "react";
import { Play, Loader2, Sparkles } from "lucide-react";

interface LeadFormProps {
  onWorkflowTriggered: (leadId: string) => void;
  isProcessing: boolean;
}

export default function LeadForm({ onWorkflowTriggered, isProcessing }: LeadFormProps) {
  const [companyName, setCompanyName] = useState("");
  const [website, setWebsite] = useState("");
  const [productSold, setProductSold] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!companyName.trim() || !website.trim() || !productSold.trim()) {
      setError("Please fill out all lead intake fields.");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/leads/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: companyName,
          website: website,
          product_sold: productSold,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to trigger GTM Command Center workflow.");
      }

      const data = await response.json();
      if (data && data.lead_id) {
        onWorkflowTriggered(data.lead_id);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred. Check backend connectivity.");
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border-slate-800 h-full">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-violet-400" />
        <h2 className="text-lg font-bold text-slate-100">Prospect Intake Command</h2>
      </div>
      <p className="text-xs text-slate-400 mb-6">
        Specify details about the company and product below to execute the multi-agent orchestration.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="companyName" className="block text-xs font-semibold text-slate-400 mb-1">
            Company Name
          </label>
          <input
            id="companyName"
            type="text"
            className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500 transition-colors"
            placeholder="e.g. Acme Corp"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            disabled={isProcessing}
            required
          />
        </div>

        <div>
          <label htmlFor="website" className="block text-xs font-semibold text-slate-400 mb-1">
            Company Website
          </label>
          <input
            id="website"
            type="text"
            className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500 transition-colors"
            placeholder="e.g. acme.com"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            disabled={isProcessing}
            required
          />
        </div>

        <div>
          <label htmlFor="productSold" className="block text-xs font-semibold text-slate-400 mb-1">
            Product Being Sold
          </label>
          <textarea
            id="productSold"
            rows={3}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500 transition-colors resize-none"
            placeholder="e.g. Enterprise Cyber-Threat Intelligence Dashboard with automated incident mitigation"
            value={productSold}
            onChange={(e) => setProductSold(e.target.value)}
            disabled={isProcessing}
            required
          />
        </div>

        {error && (
          <div className="p-3 bg-red-950/20 border border-red-500/30 rounded-xl text-xs text-red-400">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isProcessing}
          className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold py-2.5 px-4 rounded-xl text-sm transition-all duration-200 shadow-lg shadow-violet-500/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Orchestrating Agents...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Execute GTM Center</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
