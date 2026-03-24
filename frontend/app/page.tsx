import Link from "next/link";

export default function HomePage() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <section className="card p-6">
        <h2 className="font-display text-2xl text-brand-700">Global + Africa-First Geo Infrastructure</h2>
        <p className="mt-3 text-sm text-accent-ink">
          Explore country-level and dynamic multi-level administrative divisions without hardcoded hierarchy assumptions.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link className="rounded-lg bg-brand-600 px-4 py-2 text-white" href="/explorer">Open Explorer</Link>
          <Link className="rounded-lg bg-accent-ink px-4 py-2 text-white" href="/search">Search Places</Link>
        </div>
      </section>
      <section className="card p-6">
        <h3 className="font-display text-xl">Nigeria LGA Coverage</h3>
        <p className="mt-3 text-sm">
          The backend explicitly maps Nigeria as State -&gt; LGA -&gt; City/Town and exposes convenience APIs for state-to-LGA and LGA-to-city retrieval.
        </p>
      </section>
    </div>
  );
}
