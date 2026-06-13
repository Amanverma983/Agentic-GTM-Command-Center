"use client";

import React, { useState, useEffect, useRef } from "react";
import { UploadCloud, FileText, Trash2, Loader2, BookOpen } from "lucide-react";

interface SalesFile {
  id: str;
  filename: str;
  file_type: str;
  file_size: number;
  uploaded_at: str;
}

export default function CollateralUploader() {
  const [files, setFiles] = useState<SalesFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/files/");
      if (response.ok) {
        const data = await response.json();
        setFiles(data);
      }
    } catch (err) {
      console.error("Failed to fetch files:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setError("");
    setUploading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/api/files/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Upload failed.");
      }

      await fetchFiles();
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err: any) {
      setError(err.message || "Failed to upload file. Ensure it is .txt or .md format.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/files/${id}`, {
        method: "DELETE",
      });
      if (response.ok) {
        setFiles(prev => prev.filter(f => f.id !== id));
      }
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border-slate-800 h-full flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-bold text-slate-100">RAG Sales Playbooks</h2>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          Upload product documentation, pricing sheets, or playbooks (.txt, .md) to ground qualification and outreach.
        </p>

        {/* Upload Trigger Area */}
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="border border-dashed border-slate-800 hover:border-violet-500/50 hover:bg-slate-900/30 rounded-xl p-5 text-center cursor-pointer transition-all duration-200 mb-4 flex flex-col items-center justify-center gap-2"
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleUpload}
            accept=".txt,.md,.json" 
            className="hidden" 
          />
          {uploading ? (
            <>
              <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
              <span className="text-xs font-medium text-slate-300">Chunking & Indexing Vectors...</span>
            </>
          ) : (
            <>
              <UploadCloud className="w-8 h-8 text-slate-500" />
              <span className="text-xs font-semibold text-slate-300">Click to upload collateral</span>
              <span className="text-[10px] text-slate-500">Supports .txt, .md, .json</span>
            </>
          )}
        </div>

        {error && (
          <div className="p-2.5 bg-red-950/20 border border-red-500/30 rounded-lg text-[10px] text-red-400 mb-4">
            {error}
          </div>
        )}
      </div>

      {/* Files List */}
      <div className="flex-1 overflow-y-auto max-h-[140px] pr-1">
        <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">Active Grounding Files</h3>
        {loading ? (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="w-4 h-4 animate-spin text-slate-600" />
          </div>
        ) : files.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-2">No documents indexed in ChromaDB collection.</p>
        ) : (
          <div className="space-y-2">
            {files.map(file => (
              <div 
                key={file.id} 
                className="flex items-center justify-between p-2 rounded-lg bg-slate-950/40 border border-slate-900 text-xs"
              >
                <div className="flex items-center gap-2 truncate">
                  <FileText className="w-4 h-4 text-violet-400 flex-shrink-0" />
                  <div className="truncate">
                    <p className="font-medium text-slate-300 truncate">{file.filename}</p>
                    <p className="text-[10px] text-slate-500">{formatSize(file.file_size)}</p>
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(file.id)}
                  className="p-1 text-slate-500 hover:text-red-400 rounded-lg hover:bg-slate-900 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
