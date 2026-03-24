"use client";

import "leaflet/dist/leaflet.css";

import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

type Point = { id: number; name: string; latitude?: number | null; longitude?: number | null };

export default function MapClient({ points }: { points: Point[] }) {
  const mapped = points.filter((p) => p.latitude && p.longitude);
  return (
    <MapContainer center={[9.082, 8.6753]} zoom={4} className="h-[460px] w-full rounded-2xl">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {mapped.map((point) => (
        <Marker key={point.id} position={[point.latitude as number, point.longitude as number]}>
          <Popup>{point.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
