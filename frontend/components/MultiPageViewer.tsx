"use client";

import { useState, useEffect } from "react";

interface DrawingPage {
  page_number: number;
  width: number;
  height: number;
  image_data?: string;
}

interface MultiPageViewerProps {
  pages: DrawingPage[];
  currentPage: number;
  onPageChange: (pageNumber: number) => void;
  children?: React.ReactNode;
}

export function MultiPageViewer({
  pages,
  currentPage,
  onPageChange,
  children,
}: MultiPageViewerProps) {
  const [zoomLevel, setZoomLevel] = useState(100);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });

  if (!pages || pages.length === 0) {
    return (
      <div className="rounded-lg border border-slate-700 bg-slate-900/50 p-8 text-center text-slate-400">
        No pages available
      </div>
    );
  }

  const current = pages[currentPage - 1];
  if (!current) {
    return (
      <div className="rounded-lg border border-slate-700 bg-slate-900/50 p-8 text-center text-slate-400">
        Invalid page
      </div>
    );
  }

  const handleZoomIn = () => setZoomLevel(Math.min(zoomLevel + 10, 300));
  const handleZoomOut = () => setZoomLevel(Math.max(zoomLevel - 10, 50));
  const handleZoomReset = () => {
    setZoomLevel(100);
    setPanX(0);
    setPanY(0);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 1 || (e.button === 0 && e.ctrlKey)) {
      // Middle click or Ctrl+left click for panning
      setIsPanning(true);
      setPanStart({ x: e.clientX - panX, y: e.clientY - panY });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanning) return;
    setPanX(e.clientX - panStart.x);
    setPanY(e.clientY - panStart.y);
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const goToPrevious = () => {
    if (currentPage > 1) onPageChange(currentPage - 1);
  };

  const goToNext = () => {
    if (currentPage < pages.length) onPageChange(currentPage + 1);
  };

  const goToPage = (pageNum: number) => {
    if (pageNum >= 1 && pageNum <= pages.length) onPageChange(pageNum);
  };

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Controls */}
      <div className="flex flex-wrap gap-3 items-center rounded-lg border border-slate-700 bg-slate-900/50 p-3">
        {/* Navigation */}
        <div className="flex items-center gap-2">
          <button
            onClick={goToPrevious}
            disabled={currentPage === 1}
            className="px-3 py-2 rounded bg-slate-800 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 transition text-sm"
          >
            ← Previous
          </button>

          <div className="flex items-center gap-2 px-3 py-2 rounded bg-slate-800">
            <label className="text-sm text-slate-400">Page:</label>
            <input
              type="number"
              min="1"
              max={pages.length}
              value={currentPage}
              onChange={(e) => goToPage(parseInt(e.target.value))}
              className="w-12 px-2 py-1 rounded bg-slate-700 text-slate-100 text-sm text-center border border-slate-600"
            />
            <span className="text-sm text-slate-400">of {pages.length}</span>
          </div>

          <button
            onClick={goToNext}
            disabled={currentPage === pages.length}
            className="px-3 py-2 rounded bg-slate-800 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 transition text-sm"
          >
            Next →
          </button>
        </div>

        <div className="flex-1" />

        {/* Zoom Controls */}
        <div className="flex items-center gap-2 px-3 py-2 rounded bg-slate-800">
          <button
            onClick={handleZoomOut}
            className="px-2 py-1 rounded text-sm text-slate-300 hover:bg-slate-700 transition"
            title="Zoom out"
          >
            −
          </button>
          <span className="w-16 text-center text-sm text-slate-300">{zoomLevel}%</span>
          <button
            onClick={handleZoomIn}
            className="px-2 py-1 rounded text-sm text-slate-300 hover:bg-slate-700 transition"
            title="Zoom in"
          >
            +
          </button>
          <button
            onClick={handleZoomReset}
            className="px-2 py-1 rounded text-sm text-slate-400 hover:bg-slate-700 transition border border-slate-600"
          >
            Reset
          </button>
        </div>

        {/* Dimensions */}
        <div className="text-xs text-slate-400 px-3">
          {current.width}×{current.height}px
        </div>
      </div>

      {/* Page Thumbnails */}
      {pages.length > 1 && (
        <div className="flex gap-2 pb-3 rounded-lg border border-slate-700 bg-slate-900/30 p-2 overflow-x-auto">
          {pages.map((page) => (
            <button
              key={page.page_number}
              onClick={() => goToPage(page.page_number)}
              className={`flex-shrink-0 px-3 py-2 rounded text-sm font-medium transition ${
                currentPage === page.page_number
                  ? "bg-cyan-600 text-white border border-cyan-500"
                  : "bg-slate-800 text-slate-300 border border-slate-600 hover:bg-slate-700"
              }`}
            >
              Page {page.page_number}
            </button>
          ))}
        </div>
      )}

      {/* Viewer */}
      <div
        className="flex-1 rounded-lg border border-slate-700 bg-slate-950 overflow-hidden flex items-center justify-center cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={(e) => {
          e.preventDefault();
          const delta = e.deltaY > 0 ? -10 : 10;
          setZoomLevel(Math.max(50, Math.min(300, zoomLevel + delta)));
        }}
      >
        <div
          style={{
            transform: `translate(${panX}px, ${panY}px) scale(${zoomLevel / 100})`,
            transformOrigin: "center",
            transition: isPanning ? "none" : "transform 0.1s ease-out",
          }}
        >
          {children}
        </div>
      </div>

      {/* Info */}
      <div className="text-xs text-slate-500 p-2 rounded-lg bg-slate-900/20">
        💡 Use scroll wheel to zoom, middle click to pan, or drag while holding Ctrl
      </div>
    </div>
  );
}
