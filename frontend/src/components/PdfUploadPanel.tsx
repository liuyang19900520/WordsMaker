"use client";

import { useRef, useState } from "react";

interface PdfUploadPanelProps {
  cookie: string;
}

type JobStatus = "idle" | "uploading" | "processing" | "done" | "error";

interface PipelineResult {
  pages_processed: number;
  words_extracted: number;
  words_new_to_eudic: number;
  words_imported: number;
  words_imported_list?: string[];
  fallback_file?: string;
}

export default function PdfUploadPanel({ cookie }: PdfUploadPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [startPage, setStartPage] = useState("1");
  const [endPage, setEndPage] = useState("15");
  const [status, setStatus] = useState<JobStatus>("idle");
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null;
    setFile(f);
    setStatus("idle");
    setResult(null);
    setErrorMsg("");
  }

  async function handleSubmit() {
    if (!file) return;
    if (!cookie) {
      setErrorMsg("Please set your Eudic cookie on the left first.");
      return;
    }

    setStatus("uploading");
    setResult(null);
    setErrorMsg("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("start_page", startPage);
      formData.append("end_page", endPage);
      formData.append("eudic_cookie", cookie);

      setStatus("processing");

      const res = await fetch("/api/process-pdf", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.error ?? "Server error");
      }

      const data: PipelineResult = await res.json();
      setResult(data);
      setStatus("done");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Unknown error");
      setStatus("error");
    }
  }

  const canSubmit = !!file && !!cookie && status !== "processing" && status !== "uploading";

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-white">
        <h2 className="font-semibold text-gray-700">PDF Parser</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Cookie status hint */}
        {!cookie && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-amber-50 border border-amber-200">
            <span className="text-amber-500">⚠️</span>
            <p className="text-xs text-amber-700">
              Set your Eudic cookie on the left panel first.
            </p>
          </div>
        )}

        {/* File upload */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            Select PDF file
          </label>
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            {file ? (
              <div className="space-y-1">
                <div className="text-2xl">📄</div>
                <p className="text-sm font-medium text-gray-700">{file.name}</p>
                <p className="text-xs text-gray-400">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-3xl text-gray-300">📂</div>
                <p className="text-sm text-gray-400">Click to select a PDF file</p>
              </div>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>

        {/* Page range */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            Page range
          </label>
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <label className="block text-xs text-gray-400 mb-1">Start page</label>
              <input
                type="number"
                min="1"
                value={startPage}
                onChange={(e) => setStartPage(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-400"
              />
            </div>
            <span className="text-gray-300 mt-5">—</span>
            <div className="flex-1">
              <label className="block text-xs text-gray-400 mb-1">End page</label>
              <input
                type="number"
                min="1"
                value={endPage}
                onChange={(e) => setEndPage(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-400"
              />
            </div>
          </div>
        </div>

        {/* Submit button */}
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="w-full py-3 rounded-xl text-sm font-semibold bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {status === "uploading" && "Uploading..."}
          {status === "processing" && "Processing..."}
          {(status === "idle" || status === "done" || status === "error") && "Start"}
        </button>

        {/* Processing indicator */}
        {(status === "uploading" || status === "processing") && (
          <div className="flex items-center justify-center gap-3 p-4 rounded-xl bg-blue-50">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-blue-600">
              {status === "uploading" ? "Uploading file..." : "Processing via Lambda, please wait..."}
            </p>
          </div>
        )}

        {/* Error */}
        {status === "error" && errorMsg && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200">
            <p className="text-sm text-red-600">❌ {errorMsg}</p>
          </div>
        )}

        {/* Result */}
        {status === "done" && result && (
          <div className="p-4 rounded-xl bg-green-50 border border-green-200 space-y-3">
            <p className="text-sm font-semibold text-green-700">✅ Done</p>
            <div className="grid grid-cols-2 gap-2">
              <Stat label="Pages processed" value={result.pages_processed} />
              <Stat label="Words extracted" value={result.words_extracted} />
              <Stat label="New words" value={result.words_new_to_eudic} />
              <Stat label="Imported to Eudic" value={result.words_imported} />
            </div>
            {result.fallback_file && (
              <p className="text-xs text-amber-600">
                ⚠️ Some words imported via fallback file: {result.fallback_file}
              </p>
            )}
            {result.words_imported_list && result.words_imported_list.length > 0 && (
              <div>
                <p className="text-xs font-medium text-green-700 mb-1.5">Words imported:</p>
                <div className="max-h-48 overflow-y-auto bg-white rounded-lg p-2 border border-green-100">
                  <div className="flex flex-wrap gap-1.5">
                    {result.words_imported_list.map((word) => (
                      <span
                        key={word}
                        className="px-2 py-0.5 rounded-full bg-green-100 text-green-800 text-xs font-mono"
                      >
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-lg p-3 text-center">
      <p className="text-xl font-bold text-gray-800">{value}</p>
      <p className="text-xs text-gray-400 mt-0.5">{label}</p>
    </div>
  );
}
