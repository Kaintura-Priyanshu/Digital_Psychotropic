'use client';

import { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, NodeSingular } from 'cytoscape';
import { GraphNode, GraphEdge, ThreatTier } from '@/lib/api';
import { ZoomIn, ZoomOut, Maximize2, GitBranch } from 'lucide-react';

const TIER_COLOR: Record<ThreatTier, string> = {
  kingpin: '#EF4444',
  broker: '#F59E0B',
  operative: '#06B6D4',
  inactive: '#64748B',
};

const TYPE_SHAPE: Record<string, string> = {
  suspect: 'ellipse',
  vehicle: 'round-rectangle',
  bank: 'diamond',
  phone: 'hexagon',
};

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeSelect: (nodeId: string) => void;
  selectedNodeId?: string | null;
}

export default function GraphCanvas({ nodes, edges, onNodeSelect, selectedNodeId }: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map((n) => ({
          data: {
            id: n.id,
            label: n.label,
            tier: n.tier,
            type: n.type,
            centrality: n.centrality,
          },
        })),
        ...edges.map((e) => ({
          data: { id: e.id, source: e.source, target: e.target, relation: e.relation, weight: e.weight },
        })),
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele: NodeSingular) => TIER_COLOR[ele.data('tier') as ThreatTier],
            shape: (ele: NodeSingular) => TYPE_SHAPE[ele.data('type') as string] as any,
            width: (ele: NodeSingular) => 28 + ele.data('centrality') * 46,
            height: (ele: NodeSingular) => 28 + ele.data('centrality') * 46,
            label: 'data(label)',
            color: '#EAF0FB',
            'font-family': 'IBM Plex Mono, monospace',
            'font-size': 10,
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'text-outline-width': 2,
            'text-outline-color': '#0F172A',
            'border-width': 2,
            'border-color': '#0A0F1C',
            'border-opacity': 0.6,
            'transition-property': 'opacity, background-color, border-color, border-width',
            'transition-duration': 150,
          },
        },
        {
          selector: 'edge',
          style: {
            width: (ele: any) => 1 + ele.data('weight') * 3,
            'line-color': '#3D5075',
            'target-arrow-color': '#3D5075',
            'target-arrow-shape': 'triangle',
            'arrow-scale': 0.7,
            'curve-style': 'bezier',
            opacity: 0.55,
            'transition-property': 'opacity, line-color',
            'transition-duration': 150,
          },
        },
        {
          selector: 'edge[relation = "HAWALA_TRANSFER"]',
          style: { 'line-style': 'dashed', 'line-color': '#F59E0B', 'target-arrow-color': '#F59E0B' },
        },
        {
          selector: '.dimmed',
          style: { opacity: 0.12 },
        },
        {
          selector: '.selected-node',
          style: {
            'border-width': 3,
            'border-color': '#3DD9C2',
            'border-opacity': 1,
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 600,
        nodeRepulsion: () => 9000,
        idealEdgeLength: () => 90,
        padding: 40,
      } as any,
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.25,
    });

    cyRef.current = cy;

    // Hover de-cluttering — Gestalt / focal attention: dim everything not directly connected
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target as NodeSingular;
      setHoveredId(node.id());
      const neighborhood = node.closedNeighborhood();
      cy.elements().difference(neighborhood).addClass('dimmed');
    });

    cy.on('mouseout', 'node', () => {
      setHoveredId(null);
      cy.elements().removeClass('dimmed');
    });

    // Click to select + double-click to expand (multi-hop) neighborhood
    cy.on('tap', 'node', (evt) => {
      const node = evt.target as NodeSingular;
      cy.nodes().removeClass('selected-node');
      node.addClass('selected-node');
      onNodeSelect(node.id());
    });

    cy.on('dbltap', 'node', (evt) => {
      const node = evt.target as NodeSingular;
      const hop = node.closedNeighborhood();
      cy.animate({ fit: { eles: hop, padding: 60 }, duration: 400 } as any);
    });

    return () => {
      cy.destroy();
    };
    // Rebuilds when live data arrives (nodes/edges start empty while the
    // initial fetch is in flight, then populate once).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, edges]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !selectedNodeId) return;
    cy.nodes().removeClass('selected-node');
    cy.getElementById(selectedNodeId).addClass('selected-node');
  }, [selectedNodeId]);

  return (
    <div className="relative h-full w-full graph-canvas-root">
      <div ref={containerRef} className="h-full w-full" />

      {/* Panel chrome */}
      <div className="pointer-events-none absolute top-3 left-3 flex items-center gap-2">
        <span className="pointer-events-auto flex items-center gap-1.5 rounded bg-base-800/90 border border-base-600 px-2.5 py-1 text-[11px] font-mono text-ink-300 tracking-label uppercase">
          <GitBranch size={12} className="text-signal" />
          Knowledge Graph
        </span>
        {hoveredId && (
          <span className="pointer-events-auto rounded bg-base-800/90 border border-base-600 px-2.5 py-1 text-[11px] font-mono text-ink-300">
            {hoveredId}
          </span>
        )}
      </div>

      <div className="absolute bottom-3 left-3 flex items-center gap-1.5">
        <button
          onClick={() => cyRef.current?.zoom({ level: cyRef.current.zoom() * 1.25, renderedPosition: { x: 300, y: 200 } })}
          className="p-1.5 rounded bg-base-800/90 border border-base-600 text-ink-300 hover:text-signal hover:border-signal/50 transition-colors"
          aria-label="Zoom in"
        >
          <ZoomIn size={14} />
        </button>
        <button
          onClick={() => cyRef.current?.zoom({ level: cyRef.current.zoom() * 0.8, renderedPosition: { x: 300, y: 200 } })}
          className="p-1.5 rounded bg-base-800/90 border border-base-600 text-ink-300 hover:text-signal hover:border-signal/50 transition-colors"
          aria-label="Zoom out"
        >
          <ZoomOut size={14} />
        </button>
        <button
          onClick={() => cyRef.current?.fit(undefined, 40)}
          className="p-1.5 rounded bg-base-800/90 border border-base-600 text-ink-300 hover:text-signal hover:border-signal/50 transition-colors"
          aria-label="Fit graph to view"
        >
          <Maximize2 size={14} />
        </button>
      </div>

      {/* Legend — Gestalt similarity mapping (color = threat tier) */}
      <div className="absolute bottom-3 right-3 flex items-center gap-3 rounded bg-base-800/90 border border-base-600 px-3 py-1.5 text-[10px] font-mono text-ink-300 tracking-label uppercase">
        {(['kingpin', 'broker', 'operative', 'inactive'] as ThreatTier[]).map((tier) => (
          <span key={tier} className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: TIER_COLOR[tier] }} />
            {tier}
          </span>
        ))}
      </div>
    </div>
  );
}
