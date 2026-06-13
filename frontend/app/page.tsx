"use client";

import React, { useState, useEffect } from "react";
import { 
  Building2, Users, FileText, Cpu, Mail, Sliders, 
  ShieldAlert, BookOpen, Clock, RefreshCw, BarChart2 
} from "lucide-react";
import LeadForm from "./components/LeadForm";
import CollateralUploader from "./components/CollateralUploader";
import WorkflowVisualizer from "./components/WorkflowVisualizer";
import MetricSummary from "./components/MetricSummary";
import ResearchCard from "./components/ResearchCard";
import QualificationCard from "./components/QualificationCard";
import OutreachCard from "./components/OutreachCard";
import CRMRecord from "./components/CRMRecord";
import ForecastCard from "./components/ForecastCard";

type TabType = "brief" | "research" | "qualification" | "personas" | "outreach" | "crm" | "forecast";

export default function Home() {
  const [leads, setLeads] = useState<any[]>([]);
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const [selectedLead, setSelectedLead] = useState<any | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("brief");
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Polling state variables
  const [pollIntervalId, setPollIntervalId] = useState<NodeJS.Timeout | null>(null);

  // Load leads list on load
  const loadLeads = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/leads/");
      if (response.ok) {
        const data = await response.json();
        setLeads(data);
      }
    } catch (err) {
      console.error("Failed to load leads list:", err);
    }
  };

  useEffect(() => {
    loadLeads();
  }, []);

  // Fetch individual lead details
  const fetchLeadDetails = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/leads/${id}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedLead(data);
        
        // Stop polling if complete or failed
        if (data.status === "COMPLETE" || data.status === "FAILED") {
          setIsProcessing(false);
          if (pollIntervalId) {
            clearInterval(pollIntervalId);
            setPollIntervalId(null);
          }
          loadLeads(); // Reload historical list
        } else {
          setIsProcessing(true);
        }
      }
    } catch (err) {
      console.error("Error fetching lead detail:", err);
    }
  };

  // Triggered when lead form triggers a new execution
  const handleWorkflowTriggered = (leadId: string) => {
    setSelectedLeadId(leadId);
    setSelectedLead(null);
    setIsProcessing(true);
    setActiveTab("brief");
    
    // Begin Polling every 2.5 seconds
    const interval = setInterval(() => {
      fetchLeadDetails(leadId);
    }, 2500);
    setPollIntervalId(interval);
  };

  // Select a lead from the sidebar
  const handleSelectLead = (id: string) => {
    // Clear any active polling
    if (pollIntervalId) {
      clearInterval(pollIntervalId);
      setPollIntervalId(null);
    }
    setSelectedLeadId(id);
    setIsProcessing(false);
    fetchLeadDetails(id);
  };

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalId) clearInterval(pollIntervalId);
    };
  }, [pollIntervalId]);

  // Extract variables for metrics display
  const getSelectedLeadMetrics = () => {
    if (!selectedLead) return { score: 0, confidence: 0, revenue: 0, probability: 0 };
    
    const score = selectedLead.qualification_data?.qualification_score || 0;
    const confidence = selectedLead.qualification_data?.confidence_score || 0;
    const revenue = selectedLead.forecast_data?.estimated_revenue || 0;
    const probability = selectedLead.forecast_data?.close_probability || 0;
    
    return { score, confidence, revenue, probability };
  };

  const metrics = getSelectedLeadMetrics();

  return (
    <div className="min-h-screen bg-slate-950 p-4 sm:p-6 lg:p-8 flex flex-col gap-6">
      
      {/* Platform Header */}
      <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-900 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2.5 h-2.5 rounded-full bg-violet-500 animate-ping" />
            <h1 className="text-2xl font-black tracking-tight text-white uppercase sm:text-3xl">
              Agentic GTM <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">Command Center</span>
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Enterprise Go-To-Market Multi-Agent SDR Orchestrator grounded via ChromaDB RAG.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={loadLeads}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh Leads History"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <div className="text-xs text-slate-500 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl font-semibold">
            V1.0.0 Stable
          </div>
        </div>
      </header>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 items-start">
        
        {/* Left Hand side inputs & history (1 column) */}
        <div className="lg:col-span-1 space-y-6">
          <LeadForm onWorkflowTriggered={handleWorkflowTriggered} isProcessing={isProcessing} />
          
          <CollateralUploader />
          
          {/* History Panel */}
          <div className="glass-panel rounded-2xl p-5 border-slate-800">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-slate-500" />
              <span>GTM Audits Log</span>
            </h3>
            <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
              {leads.length === 0 ? (
                <p className="text-xs text-slate-500 italic py-2">No past executions found.</p>
              ) : (
                leads.map((l) => (
                  <div
                    key={l.id}
                    onClick={() => handleSelectLead(l.id)}
                    className={`p-2.5 rounded-xl border text-xs cursor-pointer transition-all duration-200 ${
                      selectedLeadId === l.id 
                        ? "border-violet-500 bg-violet-950/15 text-white" 
                        : "border-slate-900 bg-slate-950/20 text-slate-400 hover:border-slate-800 hover:text-slate-200"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold truncate max-w-[100px]">{l.company_name}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold ${
                        l.status === "COMPLETE" ? "bg-green-500/10 text-green-400 border border-green-500/20" :
                        l.status === "FAILED" ? "bg-red-500/10 text-red-400 border border-red-500/20" :
                        "bg-violet-500/10 text-violet-400 border border-violet-500/20 animate-pulse"
                      }`}>
                        {l.status}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 truncate">{l.product_sold}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Hand side HUD & Results (3 columns) */}
        <div className="lg:col-span-3 space-y-6">
          {/* Workflow HUD */}
          <WorkflowVisualizer 
            currentNode={selectedLead ? selectedLead.current_node : "start"} 
            status={selectedLead ? selectedLead.status : isProcessing ? "RUNNING" : "PENDING"} 
          />

          {/* Metrics summary */}
          {selectedLead && selectedLead.status === "COMPLETE" && (
            <MetricSummary 
              score={metrics.score}
              confidence={metrics.confidence}
              revenue={metrics.revenue}
              probability={metrics.probability}
            />
          )}

          {/* Results Cards Tabs */}
          {selectedLead ? (
            <div className="glass-panel rounded-2xl p-6 border-slate-800 min-h-[400px]">
              
              {/* Output Tab Selection */}
              <div className="flex items-center gap-1.5 overflow-x-auto border-b border-slate-900 pb-3 mb-6 scrollbar-thin">
                <button
                  onClick={() => setActiveTab("brief")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    activeTab === "brief" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Briefing Report
                </button>
                <button
                  onClick={() => setActiveTab("research")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    activeTab === "research" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                  disabled={!selectedLead.research_data}
                >
                  Research
                </button>
                <button
                  onClick={() => setActiveTab("qualification")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    activeTab === "qualification" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                  disabled={!selectedLead.qualification_data}
                >
                  Qualification
                </button>
                <button
                  onClick={() => setActiveTab("personas")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    activeTab === "personas" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                  disabled={!selectedLead.persona_data}
                >
                  Personas
                </button>
                <button
                  onClick={() => setActiveTab("outreach")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    activeTab === "outreach" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                  disabled={!selectedLead.outreach_data}
                >
                  Outreach
                </button>
                <button
                  onClick={() => setActiveTab("crm")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    activeTab === "crm" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                  disabled={!selectedLead.crm_data}
                >
                  CRM Mapping
                </button>
                <button
                  onClick={() => setActiveTab("forecast")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    activeTab === "forecast" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                  disabled={!selectedLead.forecast_data}
                >
                  Forecast
                </button>
              </div>

              {/* Panels */}
              <div className="flex-1">
                {activeTab === "brief" && (
                  <div className="space-y-4">
                    <h2 className="text-lg font-bold text-slate-200">GTM Account Briefing</h2>
                    <div className="p-5 rounded-xl bg-slate-950/60 border border-slate-900/60 max-h-[500px] overflow-y-auto pr-2 scrollbar-thin">
                      {selectedLead.final_report ? (
                        <div className="prose prose-invert max-w-none text-xs leading-relaxed space-y-4 font-mono text-slate-300 whitespace-pre-wrap">
                          {selectedLead.final_report}
                        </div>
                      ) : (
                        <div className="flex flex-col items-center justify-center py-20 text-slate-500 italic gap-2 text-xs">
                          <Cpu className="w-8 h-8 text-violet-400/50 animate-pulse" />
                          <span>Manager Agent compiling final briefing document...</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === "research" && (
                  <ResearchCard data={selectedLead.research_data} />
                )}

                {activeTab === "qualification" && (
                  <QualificationCard data={selectedLead.qualification_data} />
                )}

                {activeTab === "personas" && (
                  <div className="space-y-6">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Generated Buyer Personas</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {selectedLead.persona_data?.map((p: any, idx: number) => (
                        <div key={idx} className="p-4 rounded-xl bg-slate-950/30 border border-slate-900/60 space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-violet-400">{p.title}</span>
                          </div>
                          <hr className="border-slate-950" />
                          <div className="space-y-2 text-[11px]">
                            <div>
                              <span className="font-semibold text-slate-500 block">Goals:</span>
                              <p className="text-slate-300">{p.goals?.join(", ")}</p>
                            </div>
                            <div>
                              <span className="font-semibold text-slate-500 block">Challenges:</span>
                              <p className="text-slate-300">{p.challenges?.join(", ")}</p>
                            </div>
                            <div>
                              <span className="font-semibold text-slate-500 block">Decision factors:</span>
                              <p className="text-slate-300">{p.decision_factors?.join(", ")}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === "outreach" && (
                  <OutreachCard data={selectedLead.outreach_data} />
                )}

                {activeTab === "crm" && (
                  <CRMRecord data={selectedLead.crm_data} />
                )}

                {activeTab === "forecast" && (
                  <ForecastCard data={selectedLead.forecast_data} />
                )}
              </div>

            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-6 border-slate-800 h-[300px] flex flex-col items-center justify-center text-center gap-4">
              <BarChart2 className="w-12 h-12 text-slate-700" />
              <div>
                <h3 className="text-sm font-bold text-slate-400">Select a Prospect to Begin</h3>
                <p className="text-xs text-slate-600 max-w-[300px] mt-1">
                  Specify intake details in the left pane or choose a completed execution from the audits logs.
                </p>
              </div>
            </div>
          )}

        </div>

      </div>
      
    </div>
  );
}
