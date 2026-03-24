"use client";

import { useMemo, useState } from "react";

import { useCountries, useCountryDivisions, useDivisionChildren, useDivisionCities } from "@/hooks/useGeoQueries";
import { Division } from "@/services/types";

function groupByLevel(divisions: Division[]) {
  return divisions.reduce<Record<number, Division[]>>((acc, item) => {
    if (!acc[item.level]) acc[item.level] = [];
    acc[item.level].push(item);
    return acc;
  }, {});
}

export default function CascadeSelector() {
  const [countryId, setCountryId] = useState<number | undefined>(undefined);
  const [levelOneId, setLevelOneId] = useState<number | undefined>(undefined);
  const [levelTwoId, setLevelTwoId] = useState<number | undefined>(undefined);

  const countries = useCountries();
  const divisions = useCountryDivisions(countryId);
  const levelTwoDivisions = useDivisionChildren(levelOneId);
  const levelThreeDivisions = useDivisionChildren(levelTwoId);
  const cities = useDivisionCities(levelTwoId || levelOneId);

  const grouped = useMemo(() => groupByLevel(divisions.data || []), [divisions.data]);

  return (
    <section className="card p-4 md:p-6">
      <h2 className="mb-4 font-display text-xl">Dynamic Hierarchy Explorer</h2>
      <div className="grid gap-3 md:grid-cols-4">
        <select
          className="rounded-lg border border-brand-200 bg-white px-3 py-2"
          value={countryId ?? ""}
          onChange={(e) => {
            const value = Number(e.target.value);
            setCountryId(Number.isNaN(value) ? undefined : value);
            setLevelOneId(undefined);
            setLevelTwoId(undefined);
          }}
        >
          <option value="">Country</option>
          {(countries.data || []).map((country) => (
            <option key={country.id} value={country.id}>{country.name}</option>
          ))}
        </select>

        <select
          className="rounded-lg border border-brand-200 bg-white px-3 py-2"
          value={levelOneId ?? ""}
          onChange={(e) => {
            const value = Number(e.target.value);
            setLevelOneId(Number.isNaN(value) ? undefined : value);
            setLevelTwoId(undefined);
          }}
        >
          <option value="">Division Level 1</option>
          {(grouped[1] || []).map((division) => (
            <option key={division.id} value={division.id}>{division.name}</option>
          ))}
        </select>

        <select
          className="rounded-lg border border-brand-200 bg-white px-3 py-2"
          value={levelTwoId ?? ""}
          onChange={(e) => {
            const value = Number(e.target.value);
            setLevelTwoId(Number.isNaN(value) ? undefined : value);
          }}
        >
          <option value="">Division Level 2</option>
          {(levelTwoDivisions.data || []).map((division) => (
            <option key={division.id} value={division.id}>{division.name}</option>
          ))}
        </select>

        <select className="rounded-lg border border-brand-200 bg-white px-3 py-2" disabled>
          <option>{(levelThreeDivisions.data || []).length ? `Level 3 found (${(levelThreeDivisions.data || []).length})` : "Division Level 3 (optional)"}</option>
        </select>
      </div>

      <div className="mt-4">
        <h3 className="mb-2 font-semibold">Cities</h3>
        <div className="max-h-56 overflow-auto rounded-lg border border-brand-100 bg-white p-3">
          <ul className="space-y-1 text-sm">
            {(cities.data || []).map((city) => (
              <li key={city.id}>{city.name}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
