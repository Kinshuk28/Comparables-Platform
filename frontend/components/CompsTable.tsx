"use client";

import type { ComparableCompany } from "@/lib/types";

export default function CompsTable({
  comps,
  onChange,
}: {
  comps: ComparableCompany[];
  onChange: (comps: ComparableCompany[]) => void;
}) {
  function update(index: number, patch: Partial<ComparableCompany>) {
    const next = [...comps];
    next[index] = { ...next[index], ...patch };
    onChange(next);
  }

  function addRow() {
    onChange([...comps, { name: "", ev_revenue_multiple: null, ev_ebitda_multiple: null }]);
  }

  function removeRow(index: number) {
    onChange(comps.filter((_, i) => i !== index));
  }

  return (
    <div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
            <th className="py-1.5 font-medium">Company</th>
            <th className="py-1.5 font-medium">EV / Revenue</th>
            <th className="py-1.5 font-medium">EV / EBITDA</th>
            <th className="py-1.5"></th>
          </tr>
        </thead>
        <tbody>
          {comps.map((c, i) => (
            <tr key={i} className="border-b border-slate-100 last:border-0">
              <td className="py-1.5 pr-2">
                <input
                  type="text"
                  value={c.name}
                  onChange={(e) => update(i, { name: e.target.value })}
                  placeholder="Peer company"
                  className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
                />
              </td>
              <td className="py-1.5 pr-2">
                <input
                  type="number"
                  step="0.1"
                  value={c.ev_revenue_multiple ?? ""}
                  onChange={(e) => update(i, { ev_revenue_multiple: e.target.value === "" ? null : parseFloat(e.target.value) })}
                  placeholder="3.0x"
                  className="w-24 rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
                />
              </td>
              <td className="py-1.5 pr-2">
                <input
                  type="number"
                  step="0.1"
                  value={c.ev_ebitda_multiple ?? ""}
                  onChange={(e) => update(i, { ev_ebitda_multiple: e.target.value === "" ? null : parseFloat(e.target.value) })}
                  placeholder="12.0x"
                  className="w-24 rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
                />
              </td>
              <td className="py-1.5 text-right">
                <button type="button" onClick={() => removeRow(i)} className="text-xs text-slate-400 hover:text-red-600">
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button
        type="button"
        onClick={addRow}
        className="mt-2 rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
      >
        + Add comparable company
      </button>
    </div>
  );
}
