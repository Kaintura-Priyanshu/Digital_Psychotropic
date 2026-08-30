// Thin fetch wrapper around the FastAPI backend (see
// police-intel-suite-backend/app/api/*). Base URL is configurable via
// NEXT_PUBLIC_API_URL so this points at localhost in dev and a real host
// in production without code changes.

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, detail.detail || `Request to ${path} failed (${res.status})`);
  }

  const contentType = res.headers.get('content-type') || '';
  return (contentType.includes('application/json') ? res.json() : res.blob()) as Promise<T>;
}

// ---- Auth ----
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username, password });
  return request<TokenResponse>('/api/auth/token', { method: 'POST', body });
}

// ---- Graph ----
export type ThreatTier = 'kingpin' | 'broker' | 'operative' | 'inactive';
export type NodeType = 'suspect' | 'phone' | 'vehicle' | 'bank';
export type RelationType = 'CALLED' | 'ACCOMPLICE_OF' | 'HAWALA_TRANSFER' | 'OWNS';

export interface GraphNode {
  id: string;
  label: string;
  tier: ThreatTier;
  type: NodeType;
  centrality: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: RelationType;
  weight: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export async function getGraph(token: string): Promise<GraphResponse> {
  return request<GraphResponse>('/api/graph', {}, token);
}

export async function getNeighborhood(token: string, nodeId: string, hops = 1): Promise<GraphResponse> {
  return request<GraphResponse>(`/api/graph/node/${encodeURIComponent(nodeId)}/neighborhood?hops=${hops}`, {}, token);
}

// ---- GIS ----
export interface CdrTower {
  id: string;
  name: string;
  lat: number;
  lng: number;
  intensity: number;
  pings: number;
}

export async function getTowers(token: string): Promise<CdrTower[]> {
  return request<CdrTower[]>('/api/gis/towers', {}, token);
}

// ---- Dossier / UIP ----
export interface ContactSummary {
  label: string;
  count: number;
}

export interface FinancialTrail {
  account: string;
  flagged: boolean;
}

export interface UipProfile {
  id: string;
  name: string;
  alias: string[];
  tier: ThreatTier;
  face_match_confidence: number;
  ipc_sections: string[];
  last_known_location: string;
  contacts: ContactSummary[];
  vehicles: string[];
  financial_trails: FinancialTrail[];
}

export async function getProfile(token: string, uipId: string): Promise<UipProfile> {
  return request<UipProfile>(`/api/dossier/${encodeURIComponent(uipId)}`, {}, token);
}

export interface DossierExportResult {
  uip_id: string;
  sha256: string;
  filename: string;
  generated_at: string;
}

export async function exportDossier(token: string, uipId: string): Promise<DossierExportResult> {
  return request<DossierExportResult>(`/api/dossier/${encodeURIComponent(uipId)}/export`, { method: 'POST' }, token);
}

export function dossierDownloadUrl(uipId: string): string {
  return `${API_URL}/api/dossier/${encodeURIComponent(uipId)}/export/download`;
}

// ---- Search ----
export interface SearchHit {
  uip_id: string;
  name: string;
  score: number;
  matched_on: string;
}

export interface SearchResponse {
  query_echo: string;
  hits: SearchHit[];
  cypher?: string | null;
}

export async function searchText(token: string, q: string): Promise<SearchResponse> {
  return request<SearchResponse>(`/api/search?q=${encodeURIComponent(q)}`, {}, token);
}

export async function searchFace(token: string, file: File): Promise<SearchResponse> {
  const form = new FormData();
  form.append('file', file);
  return request<SearchResponse>('/api/search/face', { method: 'POST', body: form }, token);
}
