"use client";

import { useEffect, useRef, useState } from "react";

type Result = {
  drawing_id: number;
  filename: string;
  uploaded_at: string;
  status: string;
  confidence_score: number;
  pages: Array<{
    width?: number;
    height?: number;
    shapes?: Array<{ type?: string; center?: [number, number]; radius?: number }>;
  }>;
  characteristics: Array<{
    id?: number | string;
    status?: string;
    type?: string;
    nominal?: string;
    tol?: string;
    min?: string;
    max?: string;
    units?: string;
    comments?: string;
    value?: {
      position?: [number, number];
      label?: string | number;
      id?: string | number;
      type?: string;
      value?: string | number;
      symbol?: string;
      unit?: string;
    };
  }>;
};

export default function ResultsViewer({ apiBase, drawingId }: { apiBase: string; drawingId: number | null }) {
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [scale, setScale] = useState(1);
  const [localChars, setLocalChars] = useState<any[] | null>(null);
  const dragRef = useRef<{ id: number | string | null; offset?: [number, number] } | null>(null);

  const stringifyCell = (cell: any) => {
    if (cell === null || cell === undefined) return "";
    return typeof cell === "object" ? JSON.stringify(cell) : String(cell);
  };

  const exportRows = () => {
    const headers = ["Balloon", "Status", "Type", "Nominal", "Tolerance", "Min", "Max", "Units", "Comments", "Value"];
    const rows = (result?.characteristics || []).map((ch) => [
      ch.id ?? "",
      ch.status ?? "",
      ch.type ?? "",
      stringifyCell(ch.nominal ?? ch.value?.nominal ?? ""),
      stringifyCell(ch.tol ?? ch.value?.tolerance ?? ""),
      stringifyCell(ch.min ?? ""),
      stringifyCell(ch.max ?? ""),
      stringifyCell(ch.units ?? ch.value?.unit ?? ""),
      stringifyCell(ch.comments ?? ""),
      stringifyCell(ch.value?.value ?? ch.value?.symbol ?? ch.value ?? ""),
    ]);
    return [headers, ...rows]
      .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\n");
  };

  const downloadCsv = () => {
    const csv = exportRows();
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${result?.filename || "inspection"}_AS9102.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadExcel = () => {
    const csv = exportRows();
    const blob = new Blob([csv], { type: "application/vnd.ms-excel;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${result?.filename || "inspection"}_AS9102.xls`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (!drawingId) return;
    let mounted = true;
    let pollId: any = null;

    const fetchResult = async () => {
      try {
        const r = await fetch(`${apiBase}/api/drawings/${drawingId}/result`);
        if (!r.ok) throw new Error("no result");
        const data = await r.json();
        if (!mounted) return;
        setResult(data);
        // initialize editable local copy of characteristics
        setLocalChars(data.characteristics ? JSON.parse(JSON.stringify(data.characteristics)) : []);
      } catch (e) {
        if (!mounted) return;
      } finally {
        if (mounted) setLoading(false);
      }
    };

    setLoading(true);
    fetchResult();
    pollId = setInterval(fetchResult, 1500);

    return () => {
      mounted = false;
      if (pollId) clearInterval(pollId);
    };
  }, [drawingId, apiBase]);

  useEffect(() => {
    const resize = () => {
      const el = containerRef.current;
      if (!el || !result?.pages?.length) return;
      const page = result.pages[0];
      const width = el.clientWidth;
      setScale(width / (page.width || 1));
    };

    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [result]);

    if (!drawingId) return null;
  if (loading) return <div className="rounded-[1.8rem] border border-slate-800 bg-slate-900/90 p-6 text-slate-200">Loading results…</div>;
  if (!result) return <div className="rounded-[1.8rem] border border-slate-800 bg-slate-900/90 p-6 text-slate-200">No results available.</div>;

  return (
    <article className="rounded-[2rem] border border-slate-800 bg-slate-950/95 p-6 shadow-xl shadow-slate-950/30">
      <header className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-300">Inspection result</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">{result.filename}</h3>
          <p className="mt-2 text-sm text-slate-400">
            Status: <span className="font-semibold text-white">{result.status}</span> · Confidence: <span className="font-semibold text-white">{result.confidence_score}</span>
          </p>
        </div>
        <section className="rounded-[1.6rem] border border-slate-800 bg-slate-900/90 p-4 text-slate-300">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Report metrics</p>
              <dl className="mt-4 grid gap-3 text-sm">
                <div className="flex items-center justify-between rounded-[1.4rem] bg-slate-950/80 p-3">
                  <dt className="font-semibold text-white">Pages</dt>
                  <dd>{result.pages?.length || 0}</dd>
                </div>
                <div className="flex items-center justify-between rounded-[1.4rem] bg-slate-950/80 p-3">
                  <dt className="font-semibold text-white">Characteristics</dt>
                  <dd>{result.characteristics?.length || 0}</dd>
                </div>
                <div className="flex items-center justify-between rounded-[1.4rem] bg-slate-950/80 p-3">
                  <dt className="font-semibold text-white">Uploaded</dt>
                  <dd>{new Date(result.uploaded_at).toLocaleString()}</dd>
                </div>
              </dl>
            </div>
            <div className="grid gap-3 sm:justify-end">
              <button
                type="button"
                className="rounded-[1.4rem] bg-cyan-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-cyan-500"
                onClick={downloadCsv}
              >
                Export AS9102 CSV
              </button>
              <button
                type="button"
                className="rounded-[1.4rem] bg-slate-950/90 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-900"
                onClick={downloadExcel}
              >
                Export AS9102 Excel
              </button>
            </div>
          </div>
        </section>
      </header>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_1fr]">
        <figure ref={containerRef} className="relative overflow-hidden rounded-[1.8rem] border border-slate-800 bg-slate-900/90 p-4 shadow-inner shadow-slate-950/20">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h4 className="text-base font-semibold text-white">Live preview</h4>
              <p className="text-sm text-slate-400">Interactive page preview with balloon markers.</p>
            </div>
            <div className="text-sm text-slate-400">Scale: {Math.round(scale * 100)}%</div>
          </div>

          {result.pages && result.pages.length ? (
            <div className="w-full overflow-hidden rounded-[1.6rem] bg-slate-950 p-2">
              <svg
                ref={svgRef}
                viewBox={`0 0 ${result.pages[0].width || 1000} ${result.pages[0].height || 1000}`}
                preserveAspectRatio="xMinYMin meet"
                className="w-full h-[420px] bg-white/5"
              >
                {result.pages[0].shapes?.map((s: any, i: number) => {
                  if (s.type === "circle") {
                    return <circle key={i} cx={s.center[0]} cy={s.center[1]} r={s.radius} fill="transparent" stroke="#94a3b8" />;
                  }
                  return null;
                })}

                {(localChars || result.characteristics)
                  .filter((c: any) => c.type === "balloon")
                  .map((ch: any, idx: number) => {
                    const balloon = ch.value || {};

                    const labelPos =
                      balloon.position ||
                      balloon.value?.position ||
                      balloon.value?.value?.position ||
                      balloon.value?.target ||
                      balloon.target ||
                      null;

                    const targetPos =
                      (balloon.target && Array.isArray(balloon.target) && balloon.target) ||
                      (balloon.value?.target && Array.isArray(balloon.value.target) && balloon.value.target) ||
                      null;

                    if (!labelPos) return null;

                    const [x, y] = labelPos;
                    const label = balloon.label ?? balloon.value?.label ?? ch.id ?? idx + 1;

                    const onPointerDown = (e: React.PointerEvent) => {
                      const svg = svgRef.current;
                      if (!svg) return;
                      const rect = svg.getBoundingClientRect();
                      const svgX = ((e.clientX - rect.left) / rect.width) * (result.pages?.[0]?.width || 1000);
                      const svgY = ((e.clientY - rect.top) / rect.height) * (result.pages?.[0]?.height || 1000);
                      dragRef.current = { id: ch.id ?? idx + 1, offset: [svgX - x, svgY - y] };
                      (e.target as Element).setPointerCapture(e.pointerId);
                    };

                    const onPointerMove = (e: React.PointerEvent) => {
                      if (!dragRef.current || dragRef.current.id == null) return;
                      if (dragRef.current.id !== (ch.id ?? idx + 1)) return;
                      const svg = svgRef.current;
                      if (!svg) return;
                      const rect = svg.getBoundingClientRect();
                      const svgX = ((e.clientX - rect.left) / rect.width) * (result.pages?.[0]?.width || 1000);
                      const svgY = ((e.clientY - rect.top) / rect.height) * (result.pages?.[0]?.height || 1000);
                      const [offX, offY] = dragRef.current.offset || [0, 0];
                      const nx = svgX - offX;
                      const ny = svgY - offY;
                      // update localChars
                      setLocalChars((prev) => {
                        if (!prev) return prev;
                        return prev.map((item: any) => {
                          if ((item.id ?? (null)) === (ch.id ?? idx + 1) || item === ch) {
                            const copy = { ...item };
                            if (!copy.value) copy.value = {};
                            copy.value.position = [nx, ny];
                            return copy;
                          }
                          return item;
                        });
                      });
                    };

                    const onPointerUp = (e: React.PointerEvent) => {
                      try {
                        (e.target as Element).releasePointerCapture(e.pointerId);
                      } catch {}
                                      dragRef.current = { id: null };
                    
                                      // Persist updated localChars to backend
                                      (async () => {
                                        try {
                                          if (!localChars) return;
                                          await fetch(`${apiBase}/api/drawings/${drawingId}/characteristics`, {
                                            method: "POST",
                                            headers: { "Content-Type": "application/json" },
                                            body: JSON.stringify({ characteristics: localChars }),
                                          });
                                        } catch (err) {
                                          // ignore for now
                                        }
                                      })();
                    };

                    return (
                      <g key={idx}>
                        {targetPos ? (
                          <line
                            x1={targetPos[0]}
                            y1={targetPos[1]}
                            x2={x}
                            y2={y}
                            stroke="#38bdf8"
                            strokeWidth={1.6}
                            strokeLinecap="round"
                            opacity={0.9}
                          />
                        ) : null}

                        <g
                          transform={`translate(${x}, ${y})`}
                          role="button"
                          aria-label={`Balloon ${label}`}
                          onPointerDown={onPointerDown}
                          onPointerMove={onPointerMove}
                          onPointerUp={onPointerUp}
                          style={{ cursor: "grab" }}
                        >
                          <circle r={18} fill="#0ea5a9" stroke="#083344" strokeWidth={2} />
                          <text x={0} y={6} textAnchor="middle" fontWeight={700} fontSize={12} fill="#001219">{label}</text>
                        </g>
                      </g>
                    );
                  })}
              </svg>
            </div>
          ) : (
            <figcaption className="rounded-2xl bg-slate-950/80 p-6 text-slate-400">No preview available.</figcaption>
          )}
        </figure>

        <section className="overflow-hidden rounded-[1.8rem] border border-slate-800 bg-slate-900/90 p-4 shadow-sm shadow-cyan-500/5">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-base font-semibold text-white">Feature table</h4>
              <p className="mt-2 text-sm text-slate-400">Balloon count, inspection status, and export readiness all in one panel.</p>
            </div>
          </div>

          <div className="mt-4 overflow-auto">
            <table className="min-w-full text-left text-sm text-slate-300">
              <thead className="text-slate-400">
                <tr>
                  <th className="px-3 py-2">#</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Type</th>
                  <th className="px-3 py-2">Value</th>
                  <th className="px-3 py-2">Units</th>
                </tr>
              </thead>
              <tbody>
                {result.characteristics && result.characteristics.length ? (
                  result.characteristics.map((ch, i) => (
                    <tr key={i} className="border-t border-slate-800 hover:bg-slate-950/80">
                      <td className="px-3 py-2 font-semibold text-white">{ch.id ?? i + 1}</td>
                      <td className="px-3 py-2 text-slate-300">{ch.type}</td>
                      <td className="px-3 py-2 text-slate-300">{ch.value?.type || "—"}</td>
                      <td className="px-3 py-2 text-slate-300">
                        {(() => {
                          const rawValue = ch.value?.value ?? ch.value?.symbol ?? ch.value;
                          if (rawValue === undefined || rawValue === null) return "—";
                          return typeof rawValue === "object" ? JSON.stringify(rawValue) : rawValue;
                        })()}
                      </td>
                      <td className="px-3 py-2 text-slate-300">{ch.value?.unit || "—"}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="px-3 py-6 text-slate-400" colSpan={5}>
                      No characteristics extracted.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </article>
  );
}
