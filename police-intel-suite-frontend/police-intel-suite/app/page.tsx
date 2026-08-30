'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { AlertTriangle, WifiOff } from 'lucide-react';
import TopSearchBar from '@/components/TopSearchBar';
import ProfileDrawer from '@/components/ProfileDrawer';
import TimelineDock from '@/components/TimelineDock';
import LoginScreen from '@/components/LoginScreen';
import { useAuth } from '@/lib/auth-context';
import {
  getGraph,
  getTowers,
  getProfile,
  ApiError,
  GraphNode,
  GraphEdge,
  CdrTower,
  UipProfile,
} from '@/lib/api';
import { graphNodes as mockNodes, graphEdges as mockEdges, cdrTowers as mockTowers } from '@/lib/mockData';

// Cytoscape and Leaflet both touch `window` at import time, so both panels
// are loaded client-only. This also keeps first paint of the shell fast.
const GraphCanvas = dynamic(() => import('@/components/GraphCanvas'), {
  ssr: false,
  loading: () => <PanelSkeleton label="Loading knowledge graph…" />,
});

const GisMap = dynamic(() => import('@/components/GisMap'), {
  ssr: false,
  loading: () => <PanelSkeleton label="Loading geospatial layer…" />,
});

function PanelSkeleton({ label }: { label: string }) {
  return (
    <div className="h-full w-full flex items-center justify-center bg-base-900 text-ink-500 text-xs font-mono tracking-label uppercase">
      {label}
    </div>
  );
}

function Dashboard() {
  const { token, username, signOut } = useAuth();
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [towers, setTowers] = useState<CdrTower[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [profile, setProfile] = useState<UipProfile | null>(null);
  const [offline, setOffline] = useState(false);

  // Load the graph + GIS layers once per session. Falls back to the local
  // demo dataset (lib/mockData.ts) if the backend can't be reached, so the
  // UI is never just a blank screen — it clearly flags that it's showing
  // offline/demo data instead.
  useEffect(() => {
    if (!token) return;
    let cancelled = false;

    (async () => {
      try {
        const [graph, towerList] = await Promise.all([getGraph(token), getTowers(token)]);
        if (cancelled) return;
        setNodes(graph.nodes);
        setEdges(graph.edges);
        setTowers(towerList);
        setOffline(false);
      } catch (err) {
        if (cancelled) return;
        console.error('Failed to load live data, falling back to demo dataset', err);
        setNodes(mockNodes as GraphNode[]);
        setEdges(mockEdges as GraphEdge[]);
        setTowers(mockTowers as CdrTower[]);
        setOffline(true);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  // Fetch the UIP profile for whichever node is selected.
  useEffect(() => {
    if (!selectedNodeId || !token) {
      setProfile(null);
      return;
    }
    let cancelled = false;

    (async () => {
      try {
        const p = await getProfile(token, selectedNodeId);
        if (!cancelled) setProfile(p);
      } catch (err) {
        if (cancelled) return;
        // No dossier on file for this node (e.g. a phone/vehicle/bank node,
        // or the demo backend only seeds two full UIPs) — close the drawer
        // rather than showing a broken one.
        console.warn(`No profile available for ${selectedNodeId}`, err instanceof ApiError ? err.message : err);
        setProfile(null);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [selectedNodeId, token]);

  return (
    <main className="h-full flex flex-col bg-base-900">
      {offline && (
        <div className="flex items-center gap-2 bg-threat-broker/10 border-b border-threat-broker/30 px-4 py-1.5 text-[11px] font-mono text-threat-broker">
          <WifiOff size={13} />
          Backend unreachable — showing local demo data. Start the API (see backend README) and reload.
        </div>
      )}

      <div className="flex items-center justify-end gap-2 px-4 pt-1 text-[10px] font-mono text-ink-500">
        <span>{username}</span>
        <button onClick={signOut} className="underline hover:text-ink-300">
          Sign out
        </button>
      </div>

      <TopSearchBar onResultSelect={setSelectedNodeId} />

      {/* Command-center split-screen: graph (60%) / GIS + dossier (40%) */}
      <div className="flex-1 flex min-h-0">
        <section className="w-[60%] min-w-0 border-r border-base-600">
          <GraphCanvas nodes={nodes} edges={edges} onNodeSelect={setSelectedNodeId} selectedNodeId={selectedNodeId} />
        </section>
        <section className="w-[40%] min-w-0">
          <GisMap towers={towers} />
        </section>
      </div>

      <TimelineDock />

      <ProfileDrawer profile={profile} onClose={() => setSelectedNodeId(null)} />
    </main>
  );
}

export default function DashboardPage() {
  const { token } = useAuth();
  if (!token) return <LoginScreen />;
  return <Dashboard />;
}
