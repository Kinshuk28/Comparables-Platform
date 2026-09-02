import { FAIRNESS_LABELS } from "@/lib/format";
import type { FootballField } from "@/lib/types";

const STYLES: Record<string, string> = {
  supports_fairness: "bg-emerald-100 text-emerald-800 border-emerald-300",
  does_not_support_fairness: "bg-red-100 text-red-800 border-red-300",
  mixed: "bg-amber-100 text-amber-800 border-amber-300",
  insufficient_data: "bg-slate-100 text-slate-700 border-slate-300",
};

export default function FairnessBadge({ status }: { status: FootballField["fairness_support"] }) {
  return (
    <span className={`inline-block rounded-full border px-3 py-1 text-xs font-semibold ${STYLES[status]}`}>
      {FAIRNESS_LABELS[status] ?? status}
    </span>
  );
}
