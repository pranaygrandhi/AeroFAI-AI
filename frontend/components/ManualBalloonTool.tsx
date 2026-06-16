"use client";

import { useState, useRef, useEffect } from "react";

interface BalloonData {
  id: number | string;
  number: number;
  cx: number;
  cy: number;
  radius: number;
  leader_x?: number;
  leader_y?: number;
  requirement: string;
  type: string;
  status: string;
}

interface ManualBalloonToolProps {
  pageWidth: number;
  pageHeight: number;
  onBalloonCreate: (balloon: Partial<BalloonData>) -> void;
  onBalloonUpdate: (balloonId: string | number, updates: Partial<BalloonData>) => void;
  existingBalloons: BalloonData[];
  imageData?: string;
}

export function ManualBalloonTool({
  pageWidth,
  pageHeight,
  onBalloonCreate,
  onBalloonUpdate,
  existingBalloons,
  imageData,
}: ManualBalloonToolProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [mode, setMode] = useState<"view" | "create" | "edit">("view");
  const [selectedBalloonId, setSelectedBalloonId] = useState<number | string | null>(null);
  const [temporaryBalloon, setTemporaryBalloon] = useState<Partial<BalloonData> | null>(null);
  const [draggingBalloon, setDraggingBalloon] = useState<{ id: number | string; startX: number; startY: number } | null>(null);
  const [nextNumber, setNextNumber] = useState(1);

  // Calculate next balloon number
  useEffect(() => {
    if (existingBalloons.length > 0) {
      const max = Math.max(...existingBalloons.map((b) => b.number || 0));
      setNextNumber(max + 1);
    } else {
      setNextNumber(1);
    }
  }, [existingBalloons]);

  const handleSvgClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (mode !== "create") return;

    const svg = svgRef.current;
    if (!svg) return;

    const rect = svg.getBoundingClientRect();
    const scaleX = pageWidth / rect.width;
    const scaleY = pageHeight / rect.height;

    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;

    // Check if clicked on existing balloon
    const clicked = existingBalloons.find((b) => {
      const dist = Math.sqrt((b.cx - clickX) ** 2 + (b.cy - clickY) ** 2);
      return dist < b.radius * 1.5;
    });

    if (clicked) {
      setSelectedBalloonId(clicked.id);
      setMode("edit");
      return;
    }

    // Create new balloon at click location
    const newBalloon: Partial<BalloonData> = {
      number: nextNumber,
      cx: clickX,
      cy: clickY,
      radius: 15,
      requirement: "",
      type: "dimension",
      status: "pending",
    };

    setTemporaryBalloon(newBalloon);
    onBalloonCreate(newBalloon);
    setNextNumber(nextNumber + 1);

    // Auto-switch to view after creation
    setTimeout(() => setMode("view"), 500);
  };

  const handleBalloonMouseDown = (
    e: React.MouseEvent,
    balloonId: number | string,
    balloonData: BalloonData
  ) => {
    e.preventDefault();
    if (mode === "view") {
      setSelectedBalloonId(balloonId);
      setMode("edit");
      return;
    }

    const svg = svgRef.current;
    if (!svg) return;

    const rect = svg.getBoundingClientRect();
    const scaleX = pageWidth / rect.width;
    const scaleY = pageHeight / rect.height;

    const startX = (e.clientX - rect.left) * scaleX;
    const startY = (e.clientY - rect.top) * scaleY;

    setDraggingBalloon({
      id: balloonId,
      startX: startX - balloonData.cx,
      startY: startY - balloonData.cy,
    });
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!draggingBalloon || !selectedBalloonId) return;

    const svg = svgRef.current;
    if (!svg) return;

    const rect = svg.getBoundingClientRect();
    const scaleX = pageWidth / rect.width;
    const scaleY = pageHeight / rect.height;

    const moveX = (e.clientX - rect.left) * scaleX;
    const moveY = (e.clientY - rect.top) * scaleY;

    const newCx = moveX - draggingBalloon.startX;
    const newCy = moveY - draggingBalloon.startY;

    // Constrain to page boundaries
    const constrainedCx = Math.max(20, Math.min(newCx, pageWidth - 20));
    const constrainedCy = Math.max(20, Math.min(newCy, pageHeight - 20));

    onBalloonUpdate(selectedBalloonId, {
      cx: constrainedCx,
      cy: constrainedCy,
    });
  };

  const handleMouseUp = () => {
    setDraggingBalloon(null);
  };

  const handleDeleteBalloon = () => {
    if (selectedBalloonId !== null) {
      onBalloonUpdate(selectedBalloonId, { status: "deleted" });
      setSelectedBalloonId(null);
      setMode("view");
    }
  };

  const handleRenumberBalloon = () => {
    if (selectedBalloonId !== null) {
      const newNumber = prompt("Enter new balloon number:", String(nextNumber));
      if (newNumber) {
        onBalloonUpdate(selectedBalloonId, { number: parseInt(newNumber) });
      }
    }
  };

  const selectedBalloon = existingBalloons.find((b) => b.id === selectedBalloonId);

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap gap-2 rounded-lg border border-slate-700 bg-slate-900/50 p-3">
        <button
          onClick={() => setMode("view")}
          className={`px-3 py-2 rounded text-sm font-medium transition ${
            mode === "view"
              ? "bg-cyan-600 text-white"
              : "bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
        >
          View
        </button>
        <button
          onClick={() => {
            setMode("create");
            setSelectedBalloonId(null);
          }}
          className={`px-3 py-2 rounded text-sm font-medium transition ${
            mode === "create"
              ? "bg-cyan-600 text-white"
              : "bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
        >
          Create Balloon
        </button>
        <button
          onClick={() => setMode("edit")}
          className={`px-3 py-2 rounded text-sm font-medium transition ${
            mode === "edit"
              ? "bg-cyan-600 text-white"
              : "bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
          disabled={selectedBalloonId === null}
        >
          Edit Selected
        </button>

        <div className="flex-1" />

        {selectedBalloon && (
          <>
            <button
              onClick={handleRenumberBalloon}
              className="px-3 py-2 rounded text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition"
            >
              Renumber
            </button>
            <button
              onClick={handleDeleteBalloon}
              className="px-3 py-2 rounded text-sm font-medium bg-red-900/50 text-red-300 hover:bg-red-900 transition"
            >
              Delete
            </button>
          </>
        )}

        <div className="text-xs text-slate-400 px-3 py-2">
          {mode === "create" ? "Click on drawing to place balloon" : mode === "edit" && selectedBalloon ? "Drag to move balloon" : "Select to edit"}
        </div>
      </div>

      {/* Canvas */}
      <div className="rounded-lg border border-slate-700 bg-slate-950/50 overflow-hidden">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${pageWidth} ${pageHeight}`}
          preserveAspectRatio="xMidYMid meet"
          className="w-full cursor-crosshair bg-slate-900"
          onClick={handleSvgClick}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {/* Background image if available */}
          {imageData && (
            <image
              href={imageData}
              x={0}
              y={0}
              width={pageWidth}
              height={pageHeight}
              preserveAspectRatio="none"
              opacity={0.3}
            />
          )}

          {/* Balloons */}
          {existingBalloons.map((balloon) => {
            const isSelected = balloon.id === selectedBalloonId;
            const isHovered = mode !== "view" && isSelected;

            return (
              <g key={balloon.id}>
                {/* Leader line if exists */}
                {balloon.leader_x !== undefined && balloon.leader_y !== undefined && (
                  <line
                    x1={balloon.cx}
                    y1={balloon.cy}
                    x2={balloon.leader_x}
                    y2={balloon.leader_y}
                    stroke={isSelected ? "#06b6d4" : "#94a3b8"}
                    strokeWidth={isHovered ? 3 : 2}
                    pointerEvents="none"
                  />
                )}

                {/* Balloon circle */}
                <circle
                  cx={balloon.cx}
                  cy={balloon.cy}
                  r={balloon.radius}
                  fill={isSelected ? "#0891b2" : "#06b6d4"}
                  stroke={isHovered ? "#ffffff" : "#0891b2"}
                  strokeWidth={isHovered ? 3 : 2}
                  opacity={0.9}
                  onMouseDown={(e) => handleBalloonMouseDown(e, balloon.id, balloon)}
                  style={{ cursor: mode !== "view" ? "grab" : "pointer" }}
                  className="transition hover:opacity-100"
                />

                {/* Balloon number/label */}
                <text
                  x={balloon.cx}
                  y={balloon.cy}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="white"
                  fontSize={Math.max(10, balloon.radius * 0.6)}
                  fontWeight="bold"
                  pointerEvents="none"
                  className="select-none"
                >
                  {balloon.number}
                </text>

                {/* Selection indicator */}
                {isSelected && (
                  <circle
                    cx={balloon.cx}
                    cy={balloon.cy}
                    r={balloon.radius + 8}
                    fill="none"
                    stroke="#06b6d4"
                    strokeWidth={1}
                    strokeDasharray="5,5"
                    pointerEvents="none"
                  />
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Properties panel */}
      {selectedBalloon && (
        <div className="rounded-lg border border-slate-700 bg-slate-900/50 p-4">
          <h3 className="text-sm font-semibold text-white mb-3">Balloon #{selectedBalloon.number}</h3>
          <div className="space-y-3 text-sm">
            <div>
              <label className="text-slate-400">Position (X, Y)</label>
              <div className="text-slate-200">
                {Math.round(selectedBalloon.cx)}, {Math.round(selectedBalloon.cy)}
              </div>
            </div>
            <div>
              <label className="text-slate-400">Requirement</label>
              <div className="text-slate-200 text-xs">{selectedBalloon.requirement || "Not set"}</div>
            </div>
            <div>
              <label className="text-slate-400">Type</label>
              <div className="text-slate-200 text-xs capitalize">{selectedBalloon.type}</div>
            </div>
            <div>
              <label className="text-slate-400">Status</label>
              <div className="text-slate-200 text-xs capitalize">{selectedBalloon.status}</div>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="text-xs text-slate-400 p-3 rounded-lg bg-slate-900/50">
        {existingBalloons.length} balloons • Next: #{nextNumber}
      </div>
    </div>
  );
}
