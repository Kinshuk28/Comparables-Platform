import Link from "next/link";
import { listFairnessOpinions, listValuations } from "@/lib/api";
import { formatDate, formatMoney } from "@/lib/format";
import FairnessBadge from "@/components/FairnessBadge";

export default async function ReportsListPage() {
  const [opinions, valuations] = await Promise.all([listFairnessOpinions(), listValuations()]);
  const valuationById = new Map(valuations.map((v) => [v.id, v]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-bold text-navy-900">Past Reports</h1>
        <p className="mt-1 text-sm text-slate-500">Previously generated fairness opinion reports.</p>
      </div>

      {opinions.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
          No fairness opinion reports have been generated yet.{" "}
          <Link href="/" className="text-navy-800 underline">
            Start a new analysis
          </Link>
          .
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <th className="px-4 py-3 font-medium">Target / Acquirer</th>
                <th className="px-4 py-3 font-medium">Offer Price</th>
                <th className="px-4 py-3 font-medium">Generated</th>
                <th className="px-4 py-3 font-medium">Fairness Signal</th>
              </tr>
            </thead>
            <tbody>
              {opinions.map((opinion) => {
                const v = valuationById.get(opinion.valuation_id);
                return (
                  <tr key={opinion.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <Link href={`/reports/${opinion.id}`} className="font-medium text-navy-900 hover:underline">
                        {v ? `${v.target_name}${v.acquirer_name ? ` / ${v.acquirer_name}` : ""}` : "Unknown target"}
                      </Link>
                    </td>
                    <td className="px-4 py-3">{v ? formatMoney(v.offer_price) : "—"}</td>
                    <td className="px-4 py-3 text-slate-500">{formatDate(opinion.created_at)}</td>
                    <td className="px-4 py-3">{v?.fairness_support ? <FairnessBadge status={v.fairness_support} /> : "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
