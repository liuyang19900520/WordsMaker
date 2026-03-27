"use client";

import { useState } from "react";
import EudicPanel from "@/components/EudicPanel";
import PdfUploadPanel from "@/components/PdfUploadPanel";

export default function Home() {
  const [cookie, setCookie] = useState("");

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Top intro bar */}
      <div className="bg-white border-b border-gray-200 px-8 py-4">
        <h1 className="text-base font-semibold text-gray-800 mb-1">WordsMaker</h1>
        <p className="text-xs text-gray-500 leading-relaxed max-w-3xl">
          Upload a PDF (e.g. a textbook or article), and WordsMaker will OCR each page, extract
          meaningful English words, cross-check them against your existing Eudic study list, and
          automatically import only the <em>new</em> ones — so you never add duplicates and always
          stay on top of unfamiliar vocabulary.
        </p>
        <div className="flex items-center gap-6 mt-3">
          {[
            { step: "1", label: "Sign in to Eudic", desc: "Authenticate so we can read & write your study list" },
            { step: "2", label: "Upload a PDF", desc: "Select the file and page range to process" },
            { step: "3", label: "Words imported", desc: "New vocabulary is added to Eudic automatically" },
          ].map(({ step, label, desc }) => (
            <div key={step} className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center shrink-0 mt-0.5">{step}</span>
              <div>
                <p className="text-xs font-medium text-gray-700">{label}</p>
                <p className="text-xs text-gray-400">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Panels */}
      <div className="flex flex-1 min-h-0">
        {/* Left panel — Eudic */}
        <div className="w-1/2 flex flex-col border-r border-gray-200 bg-white shadow-sm">
          <EudicPanel onCookieChange={setCookie} />
        </div>

        {/* Right panel — PDF upload */}
        <div className="w-1/2 flex flex-col bg-white">
          <PdfUploadPanel cookie={cookie} />
        </div>
      </div>
    </div>
  );
}
