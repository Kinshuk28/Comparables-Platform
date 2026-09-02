import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ApiError, getFairnessOpinion } from "@/lib/api";
import { formatDate, formatMoney } from "@/lib/format";
import ValuationSummary from "@/components/ValuationSummary";
import FairnessBadge from "@/components/FairnessBadge";

export default async function ReportPage({ params }: { params: { id: string } }) {
  let opinion;
  try {
    opinion = await getFairnessOpinion(params.id);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  const { valuation } = opinion;

  return (
    <div className="space-y-6 print:space-y-4">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-gold-500">Fairness Opinion — Draft Report</p>
            <h1 className="mt-1 font-serif text-2xl font-bold text-navy-900">
              {valuation.target_name}
              {valuation.acquirer_name ? ` / ${valuation.acquirer_name}` : ""}
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Offer price {formatMoney(valuation.offer_price)} per share ({valuation.consideration_type}) · Generated{" "}
              {formatDate(opinion.created_at)}
            </p>
          </div>
          <FairnessBadge status={valuation.results.football_field.fairness_support} />
        </div>
      </div>

      <ValuationSummary results={valuation.results} />

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 font-serif text-lg font-bold text-navy-900">Fairness Opinion Report</h2>
        <div className="report-prose max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{opinion.narrative}</ReactMarkdown>
        </div>
      </div>

      <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
        This report is an AI-generated draft produced for educational and internal discussion purposes only. It has
        not been prepared, reviewed, or approved by a licensed investment bank or valuation professional and does
        not constitute a fairness opinion for any actual transaction, disclosure document, or fiduciary decision.
      </p>
    </div>
  );
}
