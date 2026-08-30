# MHA Police Intelligence Suite — Tactical Console (Frontend)

Next.js 14 / React / TypeScript / Tailwind CSS dashboard shell for the Command
Center Workbench described in the SIH-26189 brief. This is the **frontend
only**, wired to mock data in `lib/mockData.ts` — swap in real API calls
where noted once the FastAPI backend is available.

## Run it

```bash
npm install
npm run dev
```

Then open http://localhost:3000.

## Structure

```
app/
  layout.tsx        Root HTML shell, dark theme, fonts
  globals.css        Tailwind layers + Leaflet/Cytoscape overrides
  page.tsx           Assembles the split-screen dashboard
components/
  TopSearchBar.tsx    Universal search — text / voice / photo, progressive filters
  GraphCanvas.tsx     Cytoscape.js knowledge graph (left panel, 60%)
  GisMap.tsx          Leaflet GIS map with CDR towers + heatmap (right panel, 40%)
  ProfileDrawer.tsx   Slide-out UIP profile, face match card, PDF export
  TimelineDock.tsx    Bottom date-range dock
lib/
  mockData.ts         Sample graph nodes/edges, CDR towers, UIP profiles
```

## Design notes

- **Palette**: `#0F172A` slate-dark baseline with a single teal accent
  (`#3DD9C2`) for live/system state, plus the four fixed threat-tier colors
  from the brief (red / amber / cyan / gray).
- **Type**: IBM Plex Sans Condensed for display headings, Inter for body UI,
  IBM Plex Mono for data-dense labels (IDs, coordinates, hashes) — mirrors
  how ops consoles separate "read this" from "reference this."
- **Interaction**: hovering a graph node dims unrelated elements (focal
  de-cluttering); advanced search filters stay hidden until requested
  (Hick's Law); the UIP drawer groups data into ~5 collapsible sections
  (Miller's Law) instead of one long list.

## Wiring to a real backend

- `GraphCanvas` expects `{ nodes, edges }` shaped like `lib/mockData.ts` —
  point it at `/api/graph` (Neo4j-backed).
- `GisMap` expects CDR tower points `{ lat, lng, intensity }` — point it at
  `/api/gis/towers`.
- `ProfileDrawer` expects a `UipProfile` per node id — point it at
  `/api/dossier/:uipId`.
- `TopSearchBar`'s `onQuery` callback is where a Text-to-Cypher call to the
  Graph Query Agent would be dispatched.
