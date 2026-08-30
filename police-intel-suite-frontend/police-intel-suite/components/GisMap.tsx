'use client';

import { useEffect, useRef, useState } from 'react';
import { MapPin, Layers, Radar } from 'lucide-react';
import { CdrTower } from '@/lib/api';

// Leaflet touches `window` on import, so this component must only ever
// run on the client — it's dynamically imported (ssr: false) from page.tsx.

interface GisMapProps {
  towers: CdrTower[];
}

export default function GisMap({ towers }: GisMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const heatLayerRef = useRef<any>(null);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showTowers, setShowTowers] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function init() {
      const L = (await import('leaflet')).default;
      await import('leaflet.heat');

      if (!mounted || !containerRef.current) return;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }

      const map = L.map(containerRef.current, {
        zoomControl: true,
        attributionControl: true,
      }).setView([19.076, 72.877], 12);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;

      // Tower markers
      const towerIcon = L.divIcon({
        className: '',
        html: `<div style="width:12px;height:12px;border-radius:9999px;background:#3DD9C2;box-shadow:0 0 8px rgba(61,217,194,0.8);border:2px solid #0A0F1C;"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6],
      });

      const towerLayer = L.layerGroup();
      towers.forEach((t) => {
        L.marker([t.lat, t.lng], { icon: towerIcon })
          .bindPopup(
            `<div style="font-family: 'IBM Plex Mono', monospace; font-size: 12px;">
              <strong>${t.name}</strong><br/>
              ${t.pings} CDR pings · intensity ${(t.intensity * 100).toFixed(0)}%
            </div>`
          )
          .addTo(towerLayer);
      });
      towerLayer.addTo(map);
      (map as any)._towerLayer = towerLayer;

      // Heatmap
      const heatPoints: [number, number, number][] = towers.map((t) => [t.lat, t.lng, t.intensity]);
      const heat = (L as any).heatLayer(heatPoints, {
        radius: 45,
        blur: 35,
        maxZoom: 15,
        gradient: { 0.2: '#1F8A79', 0.5: '#F59E0B', 0.8: '#EF4444' },
      });
      heat.addTo(map);
      heatLayerRef.current = heat;
    }

    init();

    return () => {
      mounted = false;
      mapRef.current?.remove();
      mapRef.current = null;
    };
    // Rebuilds when live tower data arrives (starts empty while the initial
    // fetch is in flight, then populates once).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [towers]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !heatLayerRef.current) return;
    if (showHeatmap) heatLayerRef.current.addTo(map);
    else map.removeLayer(heatLayerRef.current);
  }, [showHeatmap]);

  useEffect(() => {
    const map = mapRef.current;
    const towerLayer = map?._towerLayer;
    if (!map || !towerLayer) return;
    if (showTowers) towerLayer.addTo(map);
    else map.removeLayer(towerLayer);
  }, [showTowers]);

  return (
    <div className="relative h-full w-full">
      <div ref={containerRef} className="h-full w-full" />

      <div className="pointer-events-none absolute top-3 left-3 flex items-center gap-2">
        <span className="pointer-events-auto flex items-center gap-1.5 rounded bg-base-800/90 border border-base-600 px-2.5 py-1 text-[11px] font-mono text-ink-300 tracking-label uppercase">
          <MapPin size={12} className="text-signal" />
          Geospatial · CDR
        </span>
      </div>

      {/* Layer control — reduces clutter per Hick's Law: toggle, don't overwhelm */}
      <div className="absolute top-3 right-3 flex flex-col gap-1.5 rounded bg-base-800/90 border border-base-600 p-2 text-[11px] font-mono text-ink-300">
        <span className="flex items-center gap-1.5 text-ink-500 text-[10px] tracking-label uppercase pb-1 border-b border-base-600">
          <Layers size={11} /> Layers
        </span>
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={showTowers}
            onChange={(e) => setShowTowers(e.target.checked)}
            className="accent-signal"
          />
          CDR towers
        </label>
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={showHeatmap}
            onChange={(e) => setShowHeatmap(e.target.checked)}
            className="accent-signal"
          />
          Density heatmap
        </label>
      </div>

      <div className="absolute bottom-3 left-3 flex items-center gap-1.5 rounded bg-base-800/90 border border-base-600 px-2.5 py-1 text-[10px] font-mono text-ink-500 tracking-label uppercase">
        <Radar size={12} className="text-signal" />
        {towers.length} towers in view
      </div>
    </div>
  );
}
