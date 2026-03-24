import { City, Country, Division, SearchResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1/geo";

async function apiFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const geoApi = {
  countries: () => apiFetch<Country[]>("/countries"),
  countryDivisions: (countryId: number) => apiFetch<Division[]>(`/countries/${countryId}/divisions`),
  divisionChildren: (divisionId: number) => apiFetch<Division[]>(`/divisions/${divisionId}/children`),
  divisionCities: (divisionId: number) => apiFetch<City[]>(`/divisions/${divisionId}/cities`),
  cities: () => apiFetch<City[]>("/cities"),
  search: (q: string) => apiFetch<SearchResult[]>(`/search?q=${encodeURIComponent(q)}`),
  nearby: (lat: number, lng: number, radiusKm = 25) =>
    apiFetch<Array<City & { distance_km: number }>>(
      `/nearby?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}&radius_km=${encodeURIComponent(radiusKm)}`
    ),
  nigeriaLgas: (stateId: number) => apiFetch<Division[]>(`/states/${stateId}/lgas`)
};
