"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { geoApi } from "@/services/api";

export default function SearchPage() {
  const [q, setQ] = useState("lagos");
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["search", q],
    queryFn: () => geoApi.search(q),
    enabled: false
  });

  return (
    <section className="card p-6">
      <h2 className="mb-4 font-display text-2xl">Weighted Search</h2>
      <div className="mb-4 flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="w-full rounded-lg border border-brand-200 px-3 py-2"
          placeholder="Search by city, LGA, state, country"
        />
        <button onClick={() => refetch()} className="rounded-lg bg-brand-600 px-4 py-2 text-white">Search</button>
      </div>
      {isLoading ? <p>Searching...</p> : null}
      <div className="space-y-2">
        {(data || []).map((row) => (
          <article key={`${row.entity_type}-${row.id}`} className="rounded-lg border border-brand-100 bg-white p-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">{row.name}</h3>
              <span className="rounded-full bg-brand-100 px-2 py-1 text-xs uppercase">{row.entity_type}</span>
            </div>
            <p className="text-xs text-gray-600">Score: {row.score}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
