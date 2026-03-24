"use client";

import dynamic from "next/dynamic";

import { useCities } from "@/hooks/useGeoQueries";

const MapClient = dynamic(() => import("@/components/MapClient"), { ssr: false });

export default function MapPage() {
  const { data, isLoading, error } = useCities();

  if (isLoading) return <p>Loading map data...</p>;
  if (error) return <p>Failed to load city coordinates.</p>;

  return (
    <section className="card p-6">
      <h2 className="mb-4 font-display text-2xl">Map View</h2>
      <MapClient points={(data || []).filter((city) => city.latitude && city.longitude)} />
    </section>
  );
}
