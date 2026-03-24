export type Country = {
  id: number;
  name: string;
  iso2: string;
  iso3: string;
  capital?: string | null;
  currency?: string | null;
  latitude?: number | null;
  longitude?: number | null;
};

export type Division = {
  id: number;
  name: string;
  level: number;
  type: string;
  parent_id?: number | null;
  country_id: number;
};

export type City = {
  id: number;
  name: string;
  admin_division_id?: number | null;
  country_id: number;
  latitude?: number | null;
  longitude?: number | null;
};

export type SearchResult = {
  entity_type: "city" | "division" | "country";
  id: number;
  name: string;
  score: number;
  country_id?: number | null;
  parent_id?: number | null;
};
