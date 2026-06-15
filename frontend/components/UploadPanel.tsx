"use client";

import { useState } from "react";

export default function UploadPanel() {
  const [fileName, setFileName] = useState<string>("");
  const [status, setStatus] = useState<string>("");

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const files = event.target.files;
    if (!files?.length) return;

    const file = files[0];
    setFileName(file.name);
    setStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/drawings/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const result = await response.json();
      setStatus(`Processed drawing ${result.filename} with confidence ${result.confidence_score}%`);
    } catch (error) {
      setStatus("Upload failed. Check backend status and file format.");
    }
  }

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-xl shadow-slate-900/20">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold text-white">Upload a PDF Drawing</h2>
          <p className="text-slate-400">Supports multi-page engineering drawings and revision-aware processing.</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-[1fr_auto]">
          <label className="flex cursor-pointer items-center justify-center rounded-2xl border border-slate-700 bg-slate-950 px-5 py-4 text-center text-slate-200 transition hover:border-slate-500">
            <input type="file" accept="application/pdf" className="hidden" onChange={handleUpload} />
            Select PDF Drawing
          </label>
          <div className="rounded-2xl border border-slate-700 bg-slate-950 p-4 text-slate-300">
            <p className="text-sm">Selected File</p>
            <p className="mt-2 font-medium text-white">{fileName || "None"}</p>
          </div>
        </div>

        <p className="rounded-2xl border border-slate-800 bg-slate-950 p-4 text-slate-300">{status || "Upload a drawing to begin processing."}</p>
      </div>
    </section>
  );
}
