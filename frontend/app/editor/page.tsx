"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";

export default function BalloonEditor() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const drawingId = searchParams.get("id");
  const [apiBase, setApiBase] = useState<string>("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [scale, setScale] = useState(1);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [localChars, setLocalChars] = useState<any[] | null>(null);
  const dragRef = useRef<{ id: number | string | null; offset?: [number, number] } | null>(null);
  const [selectedId, setSelectedId] = useState<number | string | null>(null);

  useEffect(() => {
    if (result?.characteristics) {
      setLocalChars(JSON.parse(JSON.stringify(result.characteristics)));
    } else {
      setLocalChars([]);
    }
  }, [result]);

  useEffect(() => {
    const base =
      typeof window !== "undefined"
        ? process.env.NEXT_PUBLIC_API_URL ||
          (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
            ? "http://localhost:8000"
            : `${window.location.protocol}//${window.location.hostname}:8000`)
        : "http://localhost:8000";
    setApiBase(base);
  }, []);

  useEffect(() => {
    if (!drawingId || !apiBase) return;
    const fetchResult = async () => {
      try {
        const r = await fetch(`${apiBase}/api/drawings/${drawingId}/result`);
        if (!r.ok) throw new Error("no result");
        const data = await r.json();
        setResult(data);
      } catch (e) {
        console.error("Failed to fetch result:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
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

  if (!drawingId) {
    return (
      <main className="relative overflow-hidden bg-slate-950 text-slate-100 min-h-screen">
        <div className="mx-auto max-w-[1480px] px-4 py-6 sm:px-6 lg:px-8">
          <div className="rounded-[2rem] border border-slate-800 bg-slate-950/95 p-6 shadow-xl">
            <h1 className="text-4xl font-semibold text-white mb-4">Auto-Ballooning Editor</h1>
            <p className="text-slate-300 mb-6">No drawing selected. Please upload a drawing first.</p>
            <button
              onClick={() => router.push("/")}
              className="rounded-[1.4rem] bg-cyan-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-cyan-500"
            >
              Back to Upload
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="relative overflow-hidden bg-slate-950 text-slate-100 min-h-screen">
        <div className="mx-auto max-w-[1480px] px-4 py-6 sm:px-6 lg:px-8">
          <div className="rounded-[1.8rem] border border-slate-800 bg-slate-900/90 p-6 text-slate-200">
            Loading editor...
          </div>
        </div>
      </main>
    );
  }

  if (!result) {
    return (
      <main className="relative overflow-hidden bg-slate-950 text-slate-100 min-h-screen">
        <div className="mx-auto max-w-[1480px] px-4 py-6 sm:px-6 lg:px-8">
          <div className="rounded-[1.8rem] border border-slate-800 bg-slate-900/90 p-6 text-slate-200">
            No results available.
          </div>
        </div>
      </main>
    );
  }

  const balloons = (localChars || result.characteristics || []).filter((c: any) => c.type === "balloon");

  return (
    <main className="relative overflow-hidden bg-slate-950 text-slate-100 min-h-screen">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-80 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.14),transparent_34%)]" />
      <div className="mx-auto max-w-[1800px] px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-8 flex items-center justify-between rounded-[2rem] border border-slate-800 bg-slate-950/95 p-6 shadow-xl">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-cyan-300">Interactive Editor</p>
            <h1 className="text-3xl font-semibold text-white sm:text-4xl">Auto-Ballooning Review</h1>
            <p className="mt-2 text-sm text-slate-400">{result.filename} — {balloons.length} balloons detected</p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400 hover:text-white"
          >
            Back
          </button>
        </header>

        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          {/* Diagram with Balloons */}
          <figure ref={containerRef} className="rounded-[2rem] border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white">Live Drawing Preview</h2>
                <p className="mt-1 text-sm text-slate-400">Interactive balloon diagram with leader lines.</p>
              </div>
              <div className="text-sm text-slate-400">Scale: {Math.round(scale * 100)}%</div>
            </div>
            {result.pages && result.pages.length ? (
              <div className="overflow-hidden rounded-[1.6rem] bg-slate-950 p-2">
                <svg
                  ref={svgRef}
                  viewBox={`0 0 ${result.pages[0].width || 1000} ${result.pages[0].height || 1000}`}
                  preserveAspectRatio="xMinYMin meet"
                  className="w-full bg-white/5"
                  onPointerDown={(e) => {
                    // if user clicks background and a balloon is selected, set target
                    const svg = svgRef.current;
                    if (!svg || !selectedId) return;
                    const target = e.target as Element;
                    if (target && target.nodeName.toLowerCase() !== "svg") return;
                    const rect = svg.getBoundingClientRect();
                    const svgX = ((e.clientX - rect.left) / rect.width) * (result.pages?.[0]?.width || 1000);
                    const svgY = ((e.clientY - rect.top) / rect.height) * (result.pages?.[0]?.height || 1000);
                    setLocalChars((prev) => {
                      if (!prev) return prev;
                      return prev.map((item: any) => {
                        if ((item.id ?? null) === selectedId) {
                          const copy = { ...item };
                          if (!copy.value) copy.value = {};
                          copy.value.target = [svgX, svgY];
                          return copy;
                        }
                        return item;
                      });
                    });
                    // persist
                    (async () => {
                      try {
                        if (!localChars) return;
                        await fetch(`${process.env.NEXT_PUBLIC_API_URL || apiBase}/api/drawings/${drawingId}/characteristics`, {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ characteristics: localChars }),
                        });
                      } catch (err) {
                        console.error("Failed to save target", err);
                      }
                    })();
                  }}
                >
                  {/* Page background image if available */}
                  {result.pages[0].image && (
                    <image
                      href={result.pages[0].image}
                      x={0}
                      y={0}
                      width={result.pages[0].width || 1000}
                      height={result.pages[0].height || 1000}
                      preserveAspectRatio="none"
                    />
                  )}

                  {/* Background shapes */}
                  {result.pages[0].shapes?.map((s: any, i: number) => {
                    if (s.type === "circle") {
                      return <circle key={i} cx={s.center[0]} cy={s.center[1]} r={s.radius} fill="transparent" stroke="#94a3b8" />;
                    }
                    return null;
                  })}

                  {/* Balloons with leader lines */}
                  {(localChars || balloons)
                    .filter((c: any) => c.type === "balloon")
                    .map((ch: any, idx: number) => {
                      const balloon = ch.value || {};
                      const labelPos = balloon.position || balloon.value?.position || null;
                      const targetPos = balloon.target || balloon.value?.target || null;

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
                        setLocalChars((prev) => {
                          if (!prev) return prev;
                          return prev.map((item: any) => {
                            if ((item.id ?? null) === (ch.id ?? idx + 1) || item === ch) {
                              const copy = { ...item };
                              if (!copy.value) copy.value = {};
                              copy.value.position = [nx, ny];
                              return copy;
                            }
                            return item;
                          });
                        });
                      };

                      const onPointerUp = async (e: React.PointerEvent) => {
                        try {
                          (e.target as Element).releasePointerCapture(e.pointerId);
                        } catch {}
                        dragRef.current = { id: null };
                        // persist
                        try {
                          if (!localChars) return;
                          await fetch(`${process.env.NEXT_PUBLIC_API_URL || apiBase}/api/drawings/${drawingId}/characteristics`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ characteristics: localChars }),
                          });
                        } catch (err) {
                          console.error("Failed to save balloon positions", err);
                        }
                      };

                      return (
                        <g key={idx}>
                          {targetPos ? (
                            <>
                              <circle
                                cx={targetPos[0]}
                                cy={targetPos[1]}
                                r={8}
                                fill={selectedId === (ch.id ?? idx + 1) ? "#fb7185" : "#fb7185"}
                                opacity={0.95}
                                role="button"
                                onPointerDown={(e) => {
                                  const svg = svgRef.current;
                                  if (!svg) return;
                                  const rect = svg.getBoundingClientRect();
                                  const svgX = ((e.clientX - rect.left) / rect.width) * (result.pages?.[0]?.width || 1000);
                                  const svgY = ((e.clientY - rect.top) / rect.height) * (result.pages?.[0]?.height || 1000);
                                  dragRef.current = { id: `target-${ch.id ?? idx + 1}`, offset: [svgX - targetPos[0], svgY - targetPos[1]] };
                                  (e.target as Element).setPointerCapture(e.pointerId);
                                  e.stopPropagation();
                                }}
                                onPointerMove={(e) => {
                                  if (!dragRef.current || !dragRef.current.id) return;
                                  if (String(dragRef.current.id) !== `target-${ch.id ?? idx + 1}`) return;
                                  const svg = svgRef.current;
                                  if (!svg) return;
                                  const rect = svg.getBoundingClientRect();
                                  const svgX = ((e.clientX - rect.left) / rect.width) * (result.pages?.[0]?.width || 1000);
                                  const svgY = ((e.clientY - rect.top) / rect.height) * (result.pages?.[0]?.height || 1000);
                                  const [offX, offY] = dragRef.current.offset || [0, 0];
                                  const nx = svgX - offX;
                                  const ny = svgY - offY;
                                  setLocalChars((prev) => {
                                    if (!prev) return prev;
                                    return prev.map((item: any) => {
                                      if ((item.id ?? null) === (ch.id ?? idx + 1)) {
                                        const copy = { ...item };
                                        if (!copy.value) copy.value = {};
                                        copy.value.target = [nx, ny];
                                        return copy;
                                      }
                                      return item;
                                    });
                                  });
                                }}
                                onPointerUp={async (e) => {
                                  try {
                                    (e.target as Element).releasePointerCapture(e.pointerId);
                                  } catch {}
                                  dragRef.current = { id: null };
                                  // persist
                                  try {
                                    if (!localChars) return;
                                    await fetch(`${process.env.NEXT_PUBLIC_API_URL || apiBase}/api/drawings/${drawingId}/characteristics`, {
                                      method: "POST",
                                      headers: { "Content-Type": "application/json" },
                                      body: JSON.stringify({ characteristics: localChars }),
                                    });
                                  } catch (err) {
                                    console.error("Failed to save target", err);
                                  }
                                }}
                              />
                              <line
                                x1={targetPos[0]}
                                y1={targetPos[1]}
                                x2={x}
                                y2={y}
                                stroke="#38bdf8"
                                strokeWidth={1.6}
                                strokeLinecap="round"
                                opacity={0.8}
                              />
                            </>
                          ) : null}
                          <g
                            transform={`translate(${x}, ${y})`}
                            role="button"
                            onPointerDown={(e) => {
                              setSelectedId(ch.id ?? idx + 1);
                              onPointerDown(e as any);
                            }}
                            onPointerMove={onPointerMove}
                            onPointerUp={onPointerUp}
                            style={{ cursor: "grab" }}
                          >
                            <circle r={20} fill="#0ea5a9" stroke="#083344" strokeWidth={2} />
                            <text x={0} y={6} textAnchor="middle" fontWeight={700} fontSize={14} fill="#001219">
                              {label}
                            </text>
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

          {/* Balloons List Panel */}
          <aside className="rounded-[2rem] border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white">Detected Balloons</h3>
              <p className="mt-1 text-sm text-slate-400">{balloons.length} features identified</p>
            </div>

            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {balloons.length > 0 ? (
                balloons.map((ch: any, idx: number) => {
                  const balloon = ch.value || {};
                  const label = balloon.label ?? ch.id ?? idx + 1;
                  const text = balloon.text || balloon.value?.text || "—";
                  return (
                    <div key={idx} className="rounded-[1.4rem] border border-slate-700 bg-slate-950/80 p-4 hover:border-cyan-400/50 transition">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-500 text-xs font-bold text-black">
                          {label}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-white truncate">{ch.type}</p>
                          <p className="text-xs text-slate-400 truncate">{String(text).substring(0, 30)}</p>
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-slate-400 text-sm">No balloons detected.</p>
              )}
            </div>

            <div className="mt-6 space-y-3">
              <button
                onClick={async () => {
                  try {
                    const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || apiBase}/api/drawings/${drawingId}/export`);
                    if (!r.ok) throw new Error("export failed");
                    const blob = await r.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `AS9102_export_${drawingId}.csv`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    URL.revokeObjectURL(url);
                  } catch (err) {
                    console.error("Export failed", err);
                  }
                }}
                className="w-full rounded-[1.4rem] bg-cyan-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-cyan-500"
              >
                Export AS9102
              </button>
              <button
                onClick={() => router.push(`/editor?id=${drawingId}`)}
                className="w-full rounded-[1.4rem] border border-slate-700 bg-slate-950/90 px-4 py-3 text-sm font-medium text-white transition hover:border-cyan-400"
              >
                Edit Balloons
              </button>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}

