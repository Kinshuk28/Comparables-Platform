import type { ValuationResults } from "@/lib/types";
import { formatMoney, formatMultiple, formatPercent } from "@/lib/format";
import FootballFieldChart from "./FootballFieldChart";
import FairnessBadge from "./FairnessBadge";

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-3 font-serif text-base font-bold text-navy-900">{title}</h3>
      {children}
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-slate-100 py-1.5 text-sm last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium text-navy-900">{value}</span>
    </div>
  );
}

export default function ValuationSummary({ results }: { results: ValuationResults }) {
  const { dcf, comparable_company_analysis, precedent_transaction_analysis, football_field } = results;

  return (
    <div className="space-y-6">
      <Card title="Valuation Summary — Football Field">
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Implied per-share value ranges vs. offer price of {formatMoney(football_field.offer_price)}
            {football_field.premium_to_current !== null
              ? ` (${formatPercent(football_field.premium_to_current / 100)} premium to current price)`
              : ""}
          </p>
          <FairnessBadge status={football_field.fairness_support} />
        </div>
        <FootballFieldChart footballField={football_field} />
      </Card>

      <div className="grid gap-6 md:grid-cols-3">
        <Card title="Discounted Cash Flow">
          <StatRow label="Enterprise value" value={formatMoney(dcf.enterprise_value)} />
          <StatRow label="Equity value" value={formatMoney(dcf.equity_value)} />
          <StatRow label="Value per share" value={formatMoney(dcf.value_per_share)} />
          <StatRow label="Implied range" value={`${formatMoney(dcf.implied_range.low)} – ${formatMoney(dcf.implied_range.high)}`} />
          <StatRow label="Terminal value (PV)" value={formatMoney(dcf.pv_terminal_value)} />
        </Card>

        <Card title="Comparable Companies">
          {comparable_company_analysis ? (
            <>
              <StatRow label="Value per share" value={formatMoney(comparable_company_analysis.value_per_share)} />
              <StatRow
                label="Implied range"
                value={`${formatMoney(comparable_company_analysis.implied_range.low)} – ${formatMoney(comparable_company_analysis.implied_range.high)}`}
              />
              {comparable_company_analysis.ev_ebitda.stats ? (
                <StatRow
                  label="EV/EBITDA (25th–75th pct)"
                  value={`${formatMultiple(comparable_company_analysis.ev_ebitda.stats.p25)} – ${formatMultiple(comparable_company_analysis.ev_ebitda.stats.p75)}`}
                />
              ) : null}
              {comparable_company_analysis.ev_revenue.stats ? (
                <StatRow
                  label="EV/Revenue (25th–75th pct)"
                  value={`${formatMultiple(comparable_company_analysis.ev_revenue.stats.p25)} – ${formatMultiple(comparable_company_analysis.ev_revenue.stats.p75)}`}
                />
              ) : null}
            </>
          ) : (
            <p className="text-sm text-slate-400">No comparable companies supplied.</p>
          )}
        </Card>

        <Card title="Precedent Transactions">
          {precedent_transaction_analysis ? (
            <>
              <StatRow label="Value per share" value={formatMoney(precedent_transaction_analysis.value_per_share)} />
              <StatRow
                label="Implied range"
                value={`${formatMoney(precedent_transaction_analysis.implied_range.low)} – ${formatMoney(precedent_transaction_analysis.implied_range.high)}`}
              />
              {precedent_transaction_analysis.ev_ebitda.stats ? (
                <StatRow
                  label="EV/EBITDA (25th–75th pct)"
                  value={`${formatMultiple(precedent_transaction_analysis.ev_ebitda.stats.p25)} – ${formatMultiple(precedent_transaction_analysis.ev_ebitda.stats.p75)}`}
                />
              ) : null}
              {precedent_transaction_analysis.ev_revenue.stats ? (
                <StatRow
                  label="EV/Revenue (25th–75th pct)"
                  value={`${formatMultiple(precedent_transaction_analysis.ev_revenue.stats.p25)} – ${formatMultiple(precedent_transaction_analysis.ev_revenue.stats.p75)}`}
                />
              ) : null}
            </>
          ) : (
            <p className="text-sm text-slate-400">No precedent transactions supplied.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
