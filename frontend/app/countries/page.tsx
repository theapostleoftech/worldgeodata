"use client";

import { useCountries } from "@/hooks/useGeoQueries";

export default function CountriesPage() {
  const { data, isLoading, error } = useCountries();

  if (isLoading) return <p>Loading countries...</p>;
  if (error) return <p>Failed to load countries.</p>;

  return (
    <section className="card p-6">
      <h2 className="mb-4 font-display text-2xl">Countries</h2>
      <div className="grid gap-2 md:grid-cols-3">
        {(data || []).map((country) => (
          <article key={country.id} className="rounded-xl border border-brand-100 bg-white p-3">
            <h3 className="font-semibold">{country.name}</h3>
            <p className="text-sm text-gray-600">{country.iso2} / {country.iso3}</p>
            <p className="text-sm text-gray-600">Capital: {country.capital || "N/A"}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
