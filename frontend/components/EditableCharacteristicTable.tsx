"use client";

import { useState } from "react";

interface Characteristic {
  id: number | string;
  balloon_no: number;
  requirement: string;
  type: string;
  nominal?: number;
  upper_tolerance?: number;
  lower_tolerance?: number;
  upper_limit?: number;
  lower_limit?: number;
  unit: string;
  measured_value?: number;
  status: "pending" | "pass" | "fail";
  tool?: string;
  notes?: string;
}

interface EditableCharacteristicTableProps {
  characteristics: Characteristic[];
  onUpdate: (id: string | number, updates: Partial<Characteristic>) => void;
  onDelete: (id: string | number) => void;
  onBulkUpdate: (characteristics: Characteristic[]) => void;
}

export function EditableCharacteristicTable({
  characteristics,
  onUpdate,
  onDelete,
  onBulkUpdate,
}: EditableCharacteristicTableProps) {
  const [editingId, setEditingId] = useState<string | number | null>(null);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  const filtered = filterStatus
    ? characteristics.filter((c) => c.status === filterStatus)
    : characteristics;

  const handleCellEdit = (
    id: string | number,
    field: string,
    value: any
  ) => {
    const char = characteristics.find((c) => c.id === id);
    if (!char) return;

    // Parse numeric fields
    let parsedValue = value;
    if (["nominal", "upper_tolerance", "lower_tolerance", "upper_limit", "lower_limit", "measured_value"].includes(field)) {
      parsedValue = value === "" ? undefined : parseFloat(value) || 0;
    }

    onUpdate(id, { [field]: parsedValue });
  };

  const handleStatusChange = (id: string | number, status: "pending" | "pass" | "fail") => {
    onUpdate(id, { status });
  };

  const statuses: Array<"pending" | "pass" | "fail"> = ["pending", "pass", "fail"];
  const statusColors = {
    pending: "bg-yellow-900/30 text-yellow-200 border-yellow-700",
    pass: "bg-green-900/30 text-green-200 border-green-700",
    fail: "bg-red-900/30 text-red-200 border-red-700",
  };

  const passCount = characteristics.filter((c) => c.status === "pass").length;
  const failCount = characteristics.filter((c) => c.status === "fail").length;
  const pendingCount = characteristics.filter((c) => c.status === "pending").length;

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap gap-3 items-center p-4 rounded-lg border border-slate-700 bg-slate-900/50">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">Filter:</span>
          <select
            value={filterStatus || ""}
            onChange={(e) => setFilterStatus(e.target.value || null)}
            className="px-2 py-1 rounded text-sm bg-slate-800 text-slate-200 border border-slate-600"
          >
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="pass">Passed</option>
            <option value="fail">Failed</option>
          </select>
        </div>

        <div className="flex-1" />

        {/* Stats */}
        <div className="flex gap-4 text-sm">
          <div className="text-slate-400">
            <span className="font-semibold text-cyan-400">{characteristics.length}</span> total
          </div>
          <div className="text-green-400">
            <span className="font-semibold">{passCount}</span> passed
          </div>
          <div className="text-red-400">
            <span className="font-semibold">{failCount}</span> failed
          </div>
          <div className="text-yellow-400">
            <span className="font-semibold">{pendingCount}</span> pending
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-slate-700 bg-slate-900/30 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-slate-700 bg-slate-900/50">
            <tr>
              <th className="px-4 py-3 text-left text-slate-300 font-semibold">Balloon</th>
              <th className="px-4 py-3 text-left text-slate-300 font-semibold">Requirement</th>
              <th className="px-4 py-3 text-center text-slate-300 font-semibold">Type</th>
              <th className="px-4 py-3 text-center text-slate-300 font-semibold">Nominal</th>
              <th className="px-4 py-3 text-center text-slate-300 font-semibold">Upper</th>
              <th className="px-4 py-3 text-center text-slate-300 font-semibold">Lower</th>
              <th className="px-4 py-3 text-center text-slate-300 font-semibold">Measured</th>
              <th className="px-4 py-3 text-center text-slate-300 font-semibold">Status</th>
              <th className="px-4 py-3 text-center text-slate-300 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {filtered.map((char) => (
              <tr
                key={char.id}
                className="hover:bg-slate-800/50 transition"
                onMouseEnter={() => setEditingId(char.id)}
                onMouseLeave={() => {
                  setEditingId(null);
                  setEditingField(null);
                }}
              >
                {/* Balloon Number */}
                <td className="px-4 py-3">
                  <span className="inline-block px-2 py-1 rounded bg-cyan-900/30 text-cyan-300 font-semibold">
                    {char.balloon_no}
                  </span>
                </td>

                {/* Requirement - Editable */}
                <td className="px-4 py-3 max-w-xs">
                  {editingId === char.id && editingField === "requirement" ? (
                    <input
                      autoFocus
                      type="text"
                      value={char.requirement || ""}
                      onChange={(e) => handleCellEdit(char.id, "requirement", e.target.value)}
                      onBlur={() => setEditingField(null)}
                      className="w-full px-2 py-1 rounded bg-slate-800 text-slate-100 border border-cyan-500"
                    />
                  ) : (
                    <div
                      onClick={() => {
                        setEditingId(char.id);
                        setEditingField("requirement");
                      }}
                      className="cursor-pointer hover:text-cyan-300 text-slate-300 text-xs truncate"
                      title={char.requirement}
                    >
                      {char.requirement || "—"}
                    </div>
                  )}
                </td>

                {/* Type */}
                <td className="px-4 py-3 text-center">
                  <select
                    value={char.type || ""}
                    onChange={(e) => handleCellEdit(char.id, "type", e.target.value)}
                    className="px-2 py-1 rounded bg-slate-800 text-slate-200 border border-slate-600 text-xs"
                  >
                    <option value="dimension">Dimension</option>
                    <option value="gdt">GD&T</option>
                    <option value="note">Note</option>
                  </select>
                </td>

                {/* Nominal - Editable */}
                <td className="px-4 py-3 text-center">
                  {editingId === char.id && editingField === "nominal" ? (
                    <input
                      autoFocus
                      type="number"
                      step="0.001"
                      value={char.nominal || ""}
                      onChange={(e) => handleCellEdit(char.id, "nominal", e.target.value)}
                      onBlur={() => setEditingField(null)}
                      className="w-full px-2 py-1 rounded bg-slate-800 text-slate-100 border border-cyan-500 text-center"
                    />
                  ) : (
                    <div
                      onClick={() => {
                        setEditingId(char.id);
                        setEditingField("nominal");
                      }}
                      className="cursor-pointer hover:text-cyan-300 text-slate-300"
                    >
                      {char.nominal !== undefined ? char.nominal.toFixed(3) : "—"}
                    </div>
                  )}
                </td>

                {/* Upper Limit - Editable */}
                <td className="px-4 py-3 text-center">
                  {editingId === char.id && editingField === "upper_limit" ? (
                    <input
                      autoFocus
                      type="number"
                      step="0.001"
                      value={char.upper_limit || ""}
                      onChange={(e) => handleCellEdit(char.id, "upper_limit", e.target.value)}
                      onBlur={() => setEditingField(null)}
                      className="w-full px-2 py-1 rounded bg-slate-800 text-slate-100 border border-cyan-500 text-center"
                    />
                  ) : (
                    <div
                      onClick={() => {
                        setEditingId(char.id);
                        setEditingField("upper_limit");
                      }}
                      className="cursor-pointer hover:text-cyan-300 text-slate-300"
                    >
                      {char.upper_limit !== undefined ? char.upper_limit.toFixed(3) : "—"}
                    </div>
                  )}
                </td>

                {/* Lower Limit - Editable */}
                <td className="px-4 py-3 text-center">
                  {editingId === char.id && editingField === "lower_limit" ? (
                    <input
                      autoFocus
                      type="number"
                      step="0.001"
                      value={char.lower_limit || ""}
                      onChange={(e) => handleCellEdit(char.id, "lower_limit", e.target.value)}
                      onBlur={() => setEditingField(null)}
                      className="w-full px-2 py-1 rounded bg-slate-800 text-slate-100 border border-cyan-500 text-center"
                    />
                  ) : (
                    <div
                      onClick={() => {
                        setEditingId(char.id);
                        setEditingField("lower_limit");
                      }}
                      className="cursor-pointer hover:text-cyan-300 text-slate-300"
                    >
                      {char.lower_limit !== undefined ? char.lower_limit.toFixed(3) : "—"}
                    </div>
                  )}
                </td>

                {/* Measured Value - Editable */}
                <td className="px-4 py-3 text-center">
                  {editingId === char.id && editingField === "measured_value" ? (
                    <input
                      autoFocus
                      type="number"
                      step="0.001"
                      value={char.measured_value || ""}
                      onChange={(e) => handleCellEdit(char.id, "measured_value", e.target.value)}
                      onBlur={() => setEditingField(null)}
                      className="w-full px-2 py-1 rounded bg-slate-800 text-slate-100 border border-cyan-500 text-center"
                    />
                  ) : (
                    <div
                      onClick={() => {
                        setEditingId(char.id);
                        setEditingField("measured_value");
                      }}
                      className="cursor-pointer hover:text-cyan-300 text-slate-300"
                    >
                      {char.measured_value !== undefined ? char.measured_value.toFixed(3) : "—"}
                    </div>
                  )}
                </td>

                {/* Status - Dropdown */}
                <td className="px-4 py-3 text-center">
                  <select
                    value={char.status}
                    onChange={(e) => handleStatusChange(char.id, e.target.value as any)}
                    className={`px-2 py-1 rounded text-xs font-semibold border transition ${statusColors[char.status]}`}
                  >
                    {statuses.map((s) => (
                      <option key={s} value={s}>
                        {s.charAt(0).toUpperCase() + s.slice(1)}
                      </option>
                    ))}
                  </select>
                </td>

                {/* Actions */}
                <td className="px-4 py-3 text-center">
                  {editingId === char.id && (
                    <button
                      onClick={() => {
                        onDelete(char.id);
                      }}
                      className="px-2 py-1 rounded text-xs bg-red-900/30 text-red-300 hover:bg-red-900/50 border border-red-700 transition"
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <div className="p-8 text-center text-slate-400">
            {filterStatus ? `No ${filterStatus} characteristics` : "No characteristics"}
          </div>
        )}
      </div>

      {/* Notes */}
      <div className="text-xs text-slate-500 p-3 rounded-lg bg-slate-900/20">
        💡 <strong>Tip:</strong> Click on any cell to edit. Use the dropdown menus to change types and status. Delete button appears on hover.
      </div>
    </div>
  );
}
