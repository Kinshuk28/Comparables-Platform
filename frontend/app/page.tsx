import ValuationForm from "@/components/ValuationForm";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-bold text-navy-900">New Fairness Opinion Analysis</h1>
        <p className="mt-1 max-w-3xl text-sm text-slate-500">
          Enter the deal terms, DCF assumptions, comparable companies, and precedent transactions below. The
          analysis runs all three valuation methodologies, plots them on a football field against the offer
          price, and can draft a fairness opinion narrative from the results.
        </p>
      </div>
      <ValuationForm />
    </div>
  );
}
