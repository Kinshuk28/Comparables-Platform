"use client";

import type { PrecedentTransaction } from "@/lib/types";

export default function PrecedentTable({
  transactions,
  onChange,
}: {
  transactions: PrecedentTransaction[];
  onChange: (transactions: PrecedentTransaction[]) => void;
}) {
  function update(index: number, patch: Partial<PrecedentTransaction>) {
    const next = [...transactions];
    next[index] = { ...next[index], ...patch };
    onChange(next);
  }

  function addRow() {
    onChange([
      ...transactions,
      { target_name: "", acquirer_name: null, announced_date: null, ev_revenue_multiple: null, ev_ebitda_multiple: null },
    ]);
  }

  function removeRow(index: number) {
    onChange(transactions.filter((_, i) => i !== index));
  }

  return (
    <div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
            <th className="py-1.5 font-medium">Target</th>
            <th className="py-1.5 font-medium">Acquirer</th>
            <th className="py-1.5 font-medium">EV / Revenue</th>
            <th className="py-1.5 font-medium">EV / EBITDA</th>
            <th className="py-1.5"></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t, i) => (
            <tr key={i} className="border-b border-slate-100 last:border-0">
              <td className="py-1.5 pr-2">
                <input
                  type="text"
                  value={t.target_name}
                  onChange={(e) => update(i, { target_name: e.target.value })}
                  placeholder="Deal target"
                  className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
                />
              </td>
              <td className="py-1.5 pr-2">
                <input
                  type="text"
                  value={t.acquirer_name ?? ""}
                  onChange={(e) => update(i, { acquirer_name: e.target.value || null })}
                  placeholder="Acquirer"
                  className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
                />
              </td>
              <td className="py-1.5 pr-2">
                <input
                  type="number"
                  step="0.1"
                  value={t.ev_revenue_multiple ?? ""}
                  onChange={(e) => update(i, { ev_revenue_multiple: e.target.value === "" ? null : parseFloat(e.target.value) })}
                  placeholder="3.8x"
                  className="w-24 rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
                />
              </td>
              <td className="py-1.5 pr-2">
                <input
                  type="number"
                  step="0.1"
                  value={t.ev_ebitda_multiple ?? ""}
                  onChange={(e) => update(i, { ev_ebitda_multiple: e.target.value === "" ? null : parseFloat(e.target.value) })}
                  placeholder="14.0x"
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
        + Add precedent transaction
      </button>
    </div>
  );
}
