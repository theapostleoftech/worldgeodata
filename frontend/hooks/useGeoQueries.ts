"use client";

import { useQuery } from "@tanstack/react-query";

import { geoApi } from "@/services/api";

export const useCountries = () => useQuery({ queryKey: ["countries"], queryFn: geoApi.countries });

export const useCountryDivisions = (countryId?: number) =>
  useQuery({
    queryKey: ["divisions", countryId],
    queryFn: () => geoApi.countryDivisions(countryId as number),
    enabled: !!countryId
  });

export const useDivisionChildren = (divisionId?: number) =>
  useQuery({
    queryKey: ["division-children", divisionId],
    queryFn: () => geoApi.divisionChildren(divisionId as number),
    enabled: !!divisionId
  });

export const useDivisionCities = (divisionId?: number) =>
  useQuery({
    queryKey: ["division-cities", divisionId],
    queryFn: () => geoApi.divisionCities(divisionId as number),
    enabled: !!divisionId
  });

export const useCities = () => useQuery({ queryKey: ["cities"], queryFn: geoApi.cities });
