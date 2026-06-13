"use client";

import React from "react";
import { 
  Search, ShieldCheck, Users, Mail, MessageSquare, 
  Database, TrendingUp, Cpu, Check, Loader2, AlertTriangle 
} from "lucide-react";

interface WorkflowVisualizerProps {
  currentNode: string;
  status: string;
}

const AGENTS = [
  { id: "research", name: "Research Agent", desc: "Company Summary & Web Scraping", icon: Search },
  { id: "qualification", name: "Qualification Agent", desc: "ICP Evaluation & Scoring", icon: ShieldCheck },
  { id: "personas", name: "Persona Agent", desc: "Buyer Decision Profiles", icon: Users },
  { id: "outreach", name: "Outreach Agent", desc: "Email & LinkedIn Scripts", icon: Mail },
  { id: "objections", name: "Objection Agent", desc: "Sales Rebuttal Matrix", icon: MessageSquare },
  { id: "crm", name: "CRM Agent", desc: "Structured Salesforce JSON", icon: Database },
  { id: "forecast", name: "Forecast Agent", desc: " ACV & Close Probability", icon: TrendingUp },
  { id: "manager", name: "Manager Agent", desc: "Final Briefing & Report", icon: Cpu }
];

export default function WorkflowVisualizer({ currentNode, status }: WorkflowVisualizerProps) {
  
  // Determine if a node is completed, running, or pending
  const getNodeState = (nodeId: string, index: number) => {
    const activeIndex = AGENTS.findIndex(a => a.id === currentNode);
    
    if (status === "FAILED" && nodeId === currentNode) {
      return "failed";
    }
    
    if (status === "COMPLETE") {
      return "success";
    }
    
    if (nodeId === currentNode && status === "RUNNING") {
      return "running";
    }
    
    if (activeIndex === -1) {
      return "pending";
    }
    
    if (index < activeIndex) {
      return "success";
    }
    
    return "pending";
  };

  return (
    <div className="w-full glass-panel rounded-2xl p-6 mb-8 border-slate-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-glow-purple text-violet-400">Agentic Workflow HUD</h2>
          <p className="text-xs text-slate-400">Real-time telemetry and task state transitions of the multi-agent graph</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold glass-panel border-slate-700">
          <span className={`w-2 h-2 rounded-full ${
            status === "RUNNING" ? "bg-purple-500 animate-pulse" :
            status === "COMPLETE" ? "bg-green-500" :
            status === "FAILED" ? "bg-red-500" : "bg-slate-500"
          }`} />
          <span className="capitalize">{status ? status.toLowerCase() : "Idle"}</span>
        </div>
      </div>

      {/* Grid of Agent Nodes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 relative">
        {AGENTS.map((agent, index) => {
          const Icon = agent.icon;
          const nodeState = getNodeState(agent.id, index);
          
          return (
            <div 
              key={agent.id}
              className={`p-4 rounded-xl border transition-all duration-300 relative ${
                nodeState === "success" ? "border-green-500/30 bg-green-950/10" :
                nodeState === "running" ? "border-violet-500 active-pulse-purple bg-violet-950/20" :
                nodeState === "failed" ? "border-red-500 bg-red-950/15" :
                "border-slate-800 bg-slate-900/30"
              }`}
            >
              {/* Connector Line indicator (Visual only) */}
              {index < AGENTS.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-2.5 w-5 h-[1px] bg-slate-800 z-10" />
              )}
              
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  nodeState === "success" ? "bg-green-500/20 text-green-400" :
                  nodeState === "running" ? "bg-violet-500/20 text-violet-400" :
                  nodeState === "failed" ? "bg-red-500/20 text-red-400" :
                  "bg-slate-800 text-slate-500"
                }`}>
                  <Icon className="w-5 h-5" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className={`text-sm font-semibold truncate ${
                    nodeState === "running" ? "text-violet-300" : 
                    nodeState === "success" ? "text-slate-200" : "text-slate-400"
                  }`}>
                    {agent.name}
                  </h3>
                  <p className="text-[11px] text-slate-500 truncate">{agent.desc}</p>
                </div>

                <div className="flex-shrink-0">
                  {nodeState === "success" && (
                    <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center text-green-400">
                      <Check className="w-3 h-3 stroke-[3]" />
                    </div>
                  )}
                  {nodeState === "running" && (
                    <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
                  )}
                  {nodeState === "failed" && (
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
