// Mock intelligence data for UI development. Replace with live API calls
// to /api/graph, /api/gis, and /api/dossier once the backend is wired up.

export type ThreatTier = 'kingpin' | 'broker' | 'operative' | 'inactive';

export interface SuspectNode {
  id: string;
  label: string;
  tier: ThreatTier;
  type: 'suspect' | 'phone' | 'vehicle' | 'bank';
  centrality: number; // 0-1, drives node size
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: 'CALLED' | 'ACCOMPLICE_OF' | 'HAWALA_TRANSFER' | 'OWNS';
  weight: number;
}

export const graphNodes: SuspectNode[] = [
  { id: 'S-1042', label: 'R. Malhotra', tier: 'kingpin', type: 'suspect', centrality: 0.95 },
  { id: 'S-1103', label: 'V. Iyer', tier: 'broker', type: 'suspect', centrality: 0.72 },
  { id: 'S-1187', label: 'A. Qureshi', tier: 'broker', type: 'suspect', centrality: 0.68 },
  { id: 'S-1224', label: 'D. Fernandes', tier: 'operative', type: 'suspect', centrality: 0.41 },
  { id: 'S-1256', label: 'K. Reddy', tier: 'operative', type: 'suspect', centrality: 0.38 },
  { id: 'S-1299', label: 'P. Sharma', tier: 'operative', type: 'suspect', centrality: 0.33 },
  { id: 'S-1310', label: 'N. Bhatt', tier: 'inactive', type: 'suspect', centrality: 0.19 },
  { id: 'P-7841', label: '+91 98•••41', tier: 'broker', type: 'phone', centrality: 0.55 },
  { id: 'P-7902', label: '+91 87•••02', tier: 'operative', type: 'phone', centrality: 0.3 },
  { id: 'V-2210', label: 'MH-04 KL 2210', tier: 'operative', type: 'vehicle', centrality: 0.27 },
  { id: 'B-5561', label: 'Acct •••5561', tier: 'broker', type: 'bank', centrality: 0.6 },
  { id: 'B-5602', label: 'Acct •••5602', tier: 'inactive', type: 'bank', centrality: 0.22 },
];

export const graphEdges: GraphEdge[] = [
  { id: 'e1', source: 'S-1042', target: 'S-1103', relation: 'ACCOMPLICE_OF', weight: 0.9 },
  { id: 'e2', source: 'S-1042', target: 'S-1187', relation: 'ACCOMPLICE_OF', weight: 0.8 },
  { id: 'e3', source: 'S-1103', target: 'P-7841', relation: 'OWNS', weight: 0.5 },
  { id: 'e4', source: 'S-1187', target: 'B-5561', relation: 'HAWALA_TRANSFER', weight: 0.85 },
  { id: 'e5', source: 'B-5561', target: 'B-5602', relation: 'HAWALA_TRANSFER', weight: 0.4 },
  { id: 'e6', source: 'S-1224', target: 'P-7841', relation: 'CALLED', weight: 0.6 },
  { id: 'e7', source: 'S-1256', target: 'P-7841', relation: 'CALLED', weight: 0.55 },
  { id: 'e8', source: 'S-1299', target: 'P-7902', relation: 'CALLED', weight: 0.3 },
  { id: 'e9', source: 'S-1224', target: 'V-2210', relation: 'OWNS', weight: 0.7 },
  { id: 'e10', source: 'S-1310', target: 'P-7902', relation: 'CALLED', weight: 0.15 },
  { id: 'e11', source: 'S-1103', target: 'S-1224', relation: 'ACCOMPLICE_OF', weight: 0.45 },
  { id: 'e12', source: 'S-1187', target: 'S-1256', relation: 'ACCOMPLICE_OF', weight: 0.4 },
];

export interface CdrTower {
  id: string;
  name: string;
  lat: number;
  lng: number;
  intensity: number; // 0-1, drives heatmap weight
  pings: number;
}

// Sample tower cluster around a metro area — swap for live CDR normalizer output.
export const cdrTowers: CdrTower[] = [
  { id: 'T-01', name: 'Andheri East BTS-14', lat: 19.1197, lng: 72.8697, intensity: 0.9, pings: 214 },
  { id: 'T-02', name: 'Bandra Kurla BTS-08', lat: 19.0662, lng: 72.8697, intensity: 0.75, pings: 168 },
  { id: 'T-03', name: 'Dadar West BTS-22', lat: 19.0186, lng: 72.8437, intensity: 0.6, pings: 122 },
  { id: 'T-04', name: 'Powai BTS-05', lat: 19.1176, lng: 72.9060, intensity: 0.45, pings: 88 },
  { id: 'T-05', name: 'Chembur BTS-11', lat: 19.0522, lng: 72.9006, intensity: 0.3, pings: 54 },
  { id: 'T-06', name: 'Kurla BTS-19', lat: 19.0728, lng: 72.8826, intensity: 0.55, pings: 101 },
];

export interface UipProfile {
  id: string;
  name: string;
  alias: string[];
  tier: ThreatTier;
  faceMatchConfidence: number;
  ipcSections: string[];
  lastKnownLocation: string;
  contacts: { label: string; count: number }[];
  vehicles: string[];
  financialTrails: { account: string; flagged: boolean }[];
}

export const uipProfiles: Record<string, UipProfile> = {
  'S-1042': {
    id: 'S-1042',
    name: 'Rajeev Malhotra',
    alias: ['Raja', 'RM'],
    tier: 'kingpin',
    faceMatchConfidence: 0.94,
    ipcSections: ['BNS 111', 'BNS 61(2)', 'IPC 420'],
    lastKnownLocation: 'Andheri East, Mumbai',
    contacts: [
      { label: 'High-risk contacts', count: 6 },
      { label: 'Verified associates', count: 11 },
    ],
    vehicles: ['MH-02 CX 7743'],
    financialTrails: [
      { account: 'Acct •••5561', flagged: true },
      { account: 'Acct •••9012', flagged: false },
    ],
  },
  'S-1103': {
    id: 'S-1103',
    name: 'Vikram Iyer',
    alias: ['Vicky'],
    tier: 'broker',
    faceMatchConfidence: 0.88,
    ipcSections: ['BNS 61(2)'],
    lastKnownLocation: 'Bandra Kurla Complex, Mumbai',
    contacts: [
      { label: 'High-risk contacts', count: 3 },
      { label: 'Verified associates', count: 7 },
    ],
    vehicles: [],
    financialTrails: [{ account: 'Acct •••5561', flagged: true }],
  },
};

export function getProfileForNode(nodeId: string): UipProfile | null {
  return uipProfiles[nodeId] ?? null;
}
