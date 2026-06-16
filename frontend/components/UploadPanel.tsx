"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import ResultsViewer from "./ResultsViewer";

const statusLabels: Record<string, string> = {
  idle: "Ready",
  uploading: "Processing",
  success: "Complete",
  error: "Error",
};

function getStatusColor(status: string) {
  switch (status) {
    case "success":
      return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
    case "error":
      return "bg-rose-500/15 text-rose-300 border-rose-500/30";
    case "uploading":
      return "bg-sky-500/15 text-sky-300 border-sky-500/30";
    default:
      return "bg-slate-700/80 text-slate-200 border-slate-600";
  }
}

export default function UploadPanel() {
  const router = useRouter();
  const [fileName, setFileName] = useState<string>("");
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string>("Upload a drawing to begin processing.");
  const [drawingId, setDrawingId] = useState<number | null>(null);
  const [serverStage, setServerStage] = useState<string | null>(null);

  const apiBase =
    typeof window !== "undefined"
      ? process.env.NEXT_PUBLIC_API_URL ||
        (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
          ? "http://localhost:8000"
          : `${window.location.protocol}//${window.location.hostname}:8000`)
      : "http://localhost:8000";

  const scrollToResults = () => {
    if (!drawingId) {
      setMessage("Upload a drawing first to access auto-ballooning results.");
      return;
    }
    router.push(`/editor?id=${drawingId}`);
  };

  const scrollToFeatureTable = () => {
    if (!drawingId) {
      setMessage("Upload a drawing first to view the feature table.");
      return;
    }
    const tableElement = document.querySelector("table");
    if (tableElement) {
      tableElement.scrollIntoView({ behavior: "smooth", block: "center" });
      setMessage("Scrolled to the feature table.");
    } else {
      setMessage("Feature table not yet available. Wait for processing to complete.");
    }
  };

  const scrollToExport = () => {
    if (!drawingId) {
      setMessage("Upload a drawing first to export results.");
      return;
    }
    const exportButtons = document.querySelector("button[class*='Export']");
    if (exportButtons) {
      exportButtons.scrollIntoView({ behavior: "smooth", block: "center" });
      setMessage("Scrolled to export options.");
    } else {
      setMessage("Export buttons not yet available. Wait for processing to complete.");
    }
  };

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const files = event.target.files;
    if (!files?.length) return;

    const file = files[0];
    setFileName(file.name);
    setStatus("uploading");
    setMessage("Uploading your drawing for automated inspection analysis...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${apiBase}/api/drawings/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(err.detail || "Upload failed");
      }

      const result = await response.json();
      setDrawingId(result.drawing_id);
      setMessage("Upload accepted. Waiting for processing to complete...");

      const statusUrl = `${apiBase}/api/drawings/${result.drawing_id}/status`;
      const poll = async () => {
        try {
          const r = await fetch(statusUrl);
          if (!r.ok) throw new Error("status not found");
          const body = await r.json();
          const stage = body.status || "processing";
          setServerStage(stage);

          switch (stage) {
            case "processing":
              setMessage("Processing has started and is initializing the pipeline...");
              break;
            case "parsing":
              setMessage("Parsing PDF pages...");
              break;
            case "ocr":
              setMessage("Running OCR and extracting text...");
              break;
            case "extracting":
              setMessage("Detecting dimensions and annotations...");
              break;
            case "ballooning":
              setMessage("Auto-placing balloons...");
              break;
            case "processed":
              setStatus("success");
              setMessage(`Processing complete — confidence ${body.confidence_score}.`);
              break;
            case "error":
              setStatus("error");
              setMessage(`Processing error: ${body.error || "Unknown processing failure."}`);
              break;
            default:
              setMessage("Processing...");
          }

          if (stage !== "processed" && stage !== "error") {
            setTimeout(poll, 900);
          }
        } catch (e) {
          setStatus("error");
          setMessage("Unable to fetch status from server. Check the backend or network connection.");
        }
      };

      setTimeout(poll, 700);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Upload failed. Check backend status and file format.");
    }
  }

  return (
    <section className="rounded-[2rem] border border-slate-800 bg-slate-950/95 p-6 shadow-xl shadow-slate-950/30">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-[0.28em] text-cyan-300">Upload & inspect</p>
        <h2 className="text-3xl font-semibold text-white sm:text-4xl">Streamlined PDF inspection workflow</h2>
        <p className="max-w-xl text-sm leading-7 text-slate-400">
          Upload your drawing, get automated ballooning analysis, and export the inspection report in one polished interface.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <label className="group relative flex cursor-pointer items-center justify-center overflow-hidden rounded-[1.6rem] border border-slate-800 bg-gradient-to-r from-cyan-500 via-sky-500 to-violet-500 px-6 py-8 text-center text-white shadow-xl shadow-cyan-500/20 transition hover:-translate-y-0.5 hover:shadow-cyan-500/30">
          <input type="file" accept="application/pdf" className="absolute inset-0 h-full w-full cursor-pointer opacity-0" onChange={handleUpload} aria-label="Upload PDF drawing" />
          <div className="relative space-y-3">
            <p className="text-xl font-semibold">Select PDF drawing</p>
            <p className="text-sm text-slate-100/80">Choose a file to begin automated inspection analysis.</p>
          </div>
        </label>

        <div className="rounded-[1.6rem] border border-slate-800 bg-slate-900/90 p-6 shadow-inner shadow-slate-950/20">
          <p className="text-sm uppercase tracking-[0.22em] text-slate-500">Selected file</p>
          <p className="mt-4 text-base font-semibold text-white">{fileName || "No file selected"}</p>
          <div
            role="status"
            className={`mt-6 flex items-center justify-between rounded-[1.4rem] border px-4 py-3 text-sm ${getStatusColor(status)} border-opacity-80`}
          >
            <span className="font-medium">Status</span>
            <span>{statusLabels[status]}</span>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-400">{message}</p>

          {/* Stepper showing backend stages */}
          <div className="mt-4">
            <div className="flex items-center gap-3 text-[13px] text-slate-300">
              {[
                { key: "parsing", label: "Parsing" },
                { key: "ocr", label: "OCR" },
                { key: "extracting", label: "Extract" },
                { key: "ballooning", label: "Ballooning" },
                { key: "processed", label: "Done" },
              ].map((step, i) => {
                const steps = ["parsing", "ocr", "extracting", "ballooning", "processed"];
                const currentIndex = serverStage ? Math.max(0, steps.indexOf(serverStage)) : -1;
                const completed = currentIndex >= i && currentIndex !== -1;
                const isCurrent = serverStage === step.key;
                return (
                  <div key={step.key} className="flex items-center gap-2">
                    <div className={`h-7 w-7 flex items-center justify-center rounded-full ${completed ? "bg-cyan-500 text-black" : "bg-slate-800 text-slate-400"}`}>{i + 1}</div>
                    <div className={`${isCurrent ? "text-white font-semibold" : "text-slate-400"}`}>{step.label}</div>
                    {i < 4 ? <div className="mx-2 h-px w-6 bg-slate-700" /> : null}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <article className="rounded-[1.6rem] border border-slate-800 bg-slate-900/90 p-6 shadow-slate-950/10">
          <p className="text-sm uppercase tracking-[0.22em] text-slate-500">Upload history</p>
          <div className="mt-4 space-y-3 text-sm text-slate-400">
            <div className="rounded-[1.4rem] bg-slate-950/90 p-4">
              <p className="font-medium text-white">Last uploaded</p>
              <p className="mt-1">{fileName || "No uploads yet"}</p>
            </div>
            <div className="rounded-[1.4rem] bg-slate-950/90 p-4">
              <p className="font-medium text-white">Next action</p>
              <p className="mt-1">{drawingId ? "View or export results" : "Upload a PDF to start"}</p>
            </div>
          </div>
        </article>

        <article className="rounded-[1.6rem] border border-slate-800 bg-slate-900/90 p-6 shadow-slate-950/10">
          <p className="text-sm uppercase tracking-[0.22em] text-slate-500">Quick actions</p>
          <div className="mt-4 grid gap-3">
            <button
              className="rounded-[1.4rem] bg-slate-950/90 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-900"
              type="button"
              onClick={scrollToResults}
            >
              Auto ballooning
            </button>
            <button
              className="rounded-[1.4rem] bg-slate-950/90 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-900"
              type="button"
              onClick={scrollToFeatureTable}
            >
              View feature table
            </button>
            <button
              className="rounded-[1.4rem] bg-slate-950/90 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-900"
              type="button"
              onClick={scrollToExport}
            >
              Export AS9102
            </button>
          </div>
        </article>
      </div>

      {drawingId ? (
        <div id="results" className="mt-8">
          <ResultsViewer
            apiBase={
              typeof window !== "undefined"
                ? process.env.NEXT_PUBLIC_API_URL ||
                  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
                    ? "http://localhost:8000"
                    : `${window.location.protocol}//${window.location.hostname}:8000`)
                : "http://localhost:8000"
            }
            drawingId={drawingId}
          />
        </div>
      ) : null}
    </section>
  );
}
