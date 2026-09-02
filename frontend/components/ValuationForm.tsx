"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createValuation, generateFairnessOpinion, ApiError } from "@/lib/api";
import type { ConsiderationType, ValuationRequest, Valuation } from "@/lib/types";
import { NumberField, Section, SelectField, TextField } from "./fields";
import YearArrayInput from "./YearArrayInput";
import CompsTable from "./CompsTable";
import PrecedentTable from "./PrecedentTable";
import ValuationSummary from "./ValuationSummary";

const DEFAULT_REQUEST: ValuationRequest = {
  target_name: "Aster Analytics Inc.",
  acquirer_name: "Meridian Holdings",
  offer_price: 27.5,
  current_share_price: 21.0,
  consideration_type: "cash",
  shares_outstanding: 20,
  net_debt: 50,
  ltm_revenue: 100,
  ltm_ebitda: 20,
  dcf: {
    revenue_growth_rates: [0.1, 0.08, 0.06, 0.05, 0.04],
    ebitda_margins: [0.2, 0.21, 0.22, 0.22, 0.22],
    tax_rate: 0.25,
    capex_pct_revenue: 0.04,
    da_pct_revenue: 0.035,
    nwc_pct_revenue_change: 0.1,
    wacc: 0.1,
    terminal_growth_rate: 0.025,
  },
  comps: [
    { name: "Peer A", ev_revenue_multiple: 3.0, ev_ebitda_multiple: 12.0 },
    { name: "Peer B", ev_revenue_multiple: 3.5, ev_ebitda_multiple: 13.0 },
    { name: "Peer C", ev_revenue_multiple: 2.8, ev_ebitda_multiple: 11.0 },
    { name: "Peer D", ev_revenue_multiple: 4.0, ev_ebitda_multiple: 14.5 },
  ],
  precedent_transactions: [
    { target_name: "Deal A", acquirer_name: "Buyer 1", announced_date: null, ev_revenue_multiple: 3.8, ev_ebitda_multiple: 14.0 },
    { target_name: "Deal B", acquirer_name: "Buyer 2", announced_date: null, ev_revenue_multiple: 4.2, ev_ebitda_multiple: 15.5 },
    { target_name: "Deal C", acquirer_name: "Buyer 3", announced_date: null, ev_revenue_multiple: 3.5, ev_ebitda_multiple: 13.0 },
  ],
};

export default function ValuationForm() {
  const router = useRouter();
  const [form, setForm] = useState<ValuationRequest>(DEFAULT_REQUEST);
  const [valuation, setValuation] = useState<Valuation | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [opinionError, setOpinionError] = useState<string | null>(null);
  const [generatingOpinion, setGeneratingOpinion] = useState(false);

  function updateForm<K extends keyof ValuationRequest>(key: K, value: ValuationRequest[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function updateDcf<K extends keyof ValuationRequest["dcf"]>(key: K, value: ValuationRequest["dcf"][K]) {
    setForm((f) => ({ ...f, dcf: { ...f.dcf, [key]: value } }));
  }

  async function runAnalysis(e: React.FormEvent) {
    e.preventDefault();
    setRunning(true);
    setRunError(null);
    setValuation(null);
    try {
      const result = await createValuation(form);
      setValuation(result);
    } catch (err) {
      setRunError(err instanceof ApiError ? err.message : "Something went wrong running the analysis.");
    } finally {
      setRunning(false);
    }
  }

  async function handleGenerateOpinion() {
    if (!valuation) return;
    setGeneratingOpinion(true);
    setOpinionError(null);
    try {
      const opinion = await generateFairnessOpinion(valuation.id);
      router.push(`/reports/${opinion.id}`);
    } catch (err) {
      setOpinionError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong generating the fairness opinion."
      );
    } finally {
      setGeneratingOpinion(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={runAnalysis} className="space-y-6">
        <Section title="Deal Overview" subtitle="Basic transaction terms and target capitalization">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <TextField label="Target company" value={form.target_name} onChange={(v) => updateForm("target_name", v)} />
            <TextField
              label="Acquirer"
              value={form.acquirer_name ?? ""}
              onChange={(v) => updateForm("acquirer_name", v || null)}
            />
            <SelectField
              label="Consideration"
              value={form.consideration_type}
              onChange={(v) => updateForm("consideration_type", v as ConsiderationType)}
              options={[
                { value: "cash", label: "Cash" },
                { value: "stock", label: "Stock" },
                { value: "mixed", label: "Cash & Stock" },
              ]}
            />
            <NumberField label="Offer price per share" value={form.offer_price} onChange={(v) => updateForm("offer_price", v)} step={0.01} suffix="$" />
            <NumberField
              label="Current share price"
              value={form.current_share_price ?? NaN}
              onChange={(v) => updateForm("current_share_price", Number.isNaN(v) ? null : v)}
              step={0.01}
              suffix="$"
            />
            <NumberField label="Shares outstanding" value={form.shares_outstanding} onChange={(v) => updateForm("shares_outstanding", v)} suffix="mm" />
            <NumberField label="Net debt" value={form.net_debt} onChange={(v) => updateForm("net_debt", v)} suffix="$mm" />
            <NumberField label="LTM revenue" value={form.ltm_revenue} onChange={(v) => updateForm("ltm_revenue", v)} suffix="$mm" />
            <NumberField label="LTM EBITDA" value={form.ltm_ebitda} onChange={(v) => updateForm("ltm_ebitda", v)} suffix="$mm" />
          </div>
        </Section>

        <Section title="DCF Assumptions" subtitle="Explicit forecast period, discounted at WACC with a Gordon Growth terminal value">
          <div className="space-y-4">
            <YearArrayInput label="Revenue growth by year" values={form.dcf.revenue_growth_rates} onChange={(v) => updateDcf("revenue_growth_rates", v)} />
            <YearArrayInput label="EBITDA margin by year" values={form.dcf.ebitda_margins} onChange={(v) => updateDcf("ebitda_margins", v)} />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <NumberField label="Tax rate" value={form.dcf.tax_rate * 100} onChange={(v) => updateDcf("tax_rate", v / 100)} step={0.5} suffix="%" />
              <NumberField label="Capex (% revenue)" value={form.dcf.capex_pct_revenue * 100} onChange={(v) => updateDcf("capex_pct_revenue", v / 100)} step={0.5} suffix="%" />
              <NumberField label="D&A (% revenue)" value={form.dcf.da_pct_revenue * 100} onChange={(v) => updateDcf("da_pct_revenue", v / 100)} step={0.5} suffix="%" />
              <NumberField
                label="Δ NWC (% of Δ revenue)"
                value={form.dcf.nwc_pct_revenue_change * 100}
                onChange={(v) => updateDcf("nwc_pct_revenue_change", v / 100)}
                step={0.5}
                suffix="%"
              />
              <NumberField label="WACC" value={form.dcf.wacc * 100} onChange={(v) => updateDcf("wacc", v / 100)} step={0.25} suffix="%" />
              <NumberField
                label="Terminal growth rate"
                value={form.dcf.terminal_growth_rate * 100}
                onChange={(v) => updateDcf("terminal_growth_rate", v / 100)}
                step={0.25}
                suffix="%"
              />
            </div>
          </div>
        </Section>

        <Section title="Comparable Company Analysis" subtitle="Trading multiples of public peer companies (optional but recommended)">
          <CompsTable comps={form.comps} onChange={(comps) => updateForm("comps", comps)} />
        </Section>

        <Section title="Precedent Transaction Analysis" subtitle="Multiples paid in comparable historical M&A deals (optional but recommended)">
          <PrecedentTable transactions={form.precedent_transactions} onChange={(t) => updateForm("precedent_transactions", t)} />
        </Section>

        {runError ? <p className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{runError}</p> : null}

        <button
          type="submit"
          disabled={running}
          className="rounded-md bg-navy-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-navy-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {running ? "Running valuation…" : "Run Valuation Analysis"}
        </button>
      </form>

      {valuation ? (
        <div className="space-y-4">
          <ValuationSummary results={valuation.results} />

          {opinionError ? <p className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{opinionError}</p> : null}

          <button
            type="button"
            onClick={handleGenerateOpinion}
            disabled={generatingOpinion}
            className="rounded-md bg-gold-500 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-gold-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {generatingOpinion ? "Drafting fairness opinion…" : "Generate Fairness Opinion Report"}
          </button>
        </div>
      ) : null}
    </div>
  );
}
