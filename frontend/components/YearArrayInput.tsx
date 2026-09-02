"use client";

export default function YearArrayInput({
  label,
  values,
  onChange,
  asPercent = true,
}: {
  label: string;
  values: number[];
  onChange: (values: number[]) => void;
  asPercent?: boolean;
}) {
  function update(index: number, raw: string) {
    const next = [...values];
    const parsed = parseFloat(raw);
    next[index] = raw === "" ? NaN : asPercent ? parsed / 100 : parsed;
    onChange(next);
  }

  function addYear() {
    onChange([...values, values[values.length - 1] ?? 0]);
  }

  function removeYear() {
    if (values.length > 1) onChange(values.slice(0, -1));
  }

  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-600">{label}</span>
        <div className="flex gap-1">
          <button type="button" onClick={removeYear} className="rounded border border-slate-300 px-1.5 text-xs text-slate-500 hover:bg-slate-50">
            −
          </button>
          <button type="button" onClick={addYear} className="rounded border border-slate-300 px-1.5 text-xs text-slate-500 hover:bg-slate-50">
            +
          </button>
        </div>
      </div>
      <div className="flex gap-2">
        {values.map((v, i) => (
          <div key={i} className="flex-1">
            <span className="mb-0.5 block text-center text-[10px] text-slate-400">Y{i + 1}</span>
            <input
              type="number"
              step="0.1"
              value={Number.isFinite(v) ? (asPercent ? +(v * 100).toFixed(4) : v) : ""}
              onChange={(e) => update(i, e.target.value)}
              className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-center text-sm focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
