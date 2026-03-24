"use client";

import { useCities } from "@/hooks/useGeoQueries";

export default function CitiesPage() {
  const { data, isLoading, error } = useCities();

  if (isLoading) return <p>Loading cities...</p>;
  if (error) return <p>Failed to load cities.</p>;

  return (
    <section className="card p-6">
      <h2 className="mb-4 font-display text-2xl">City Explorer</h2>
      <div className="max-h-[70vh] overflow-auto rounded-xl border border-brand-100 bg-white p-4">
        <ul className="grid gap-2 md:grid-cols-4">
          {(data || []).map((city) => (
            <li key={city.id} className="rounded-lg border border-brand-100 p-2">{city.name}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
