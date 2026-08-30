'use client';

import { useState } from 'react';
import clsx from 'clsx';
import {
  X,
  ScanFace,
  Users,
  Car,
  Landmark,
  FileDown,
  ShieldAlert,
  ChevronDown,
  CheckCircle2,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { UipProfile, ThreatTier, exportDossier, dossierDownloadUrl, ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

const TIER_STYLE: Record<ThreatTier, { bg: string; text: string; ring: string; label: string }> = {
  kingpin: { bg: 'bg-threat-kingpin/10', text: 'text-threat-kingpin', ring: 'ring-threat-kingpin/30', label: 'Kingpin' },
  broker: { bg: 'bg-threat-broker/10', text: 'text-threat-broker', ring: 'ring-threat-broker/30', label: 'Broker' },
  operative: { bg: 'bg-threat-operative/10', text: 'text-threat-operative', ring: 'ring-threat-operative/30', label: 'Operative' },
  inactive: { bg: 'bg-threat-inactive/10', text: 'text-threat-inactive', ring: 'ring-threat-inactive/30', label: 'Inactive' },
};

interface ProfileDrawerProps {
  profile: UipProfile | null;
  onClose: () => void;
}

// Chunked sections (Miller's Law: 4–5 groups, not a flat wall of data)
function Section({
  icon,
  title,
  count,
  children,
  defaultOpen = false,
}: {
  icon: React.ReactNode;
  title: string;
  count?: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border-b border-base-600 last:border-b-0">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between py-3 text-left group"
      >
        <span className="flex items-center gap-2 text-[13px] font-medium text-ink-100">
          <span className="text-ink-500 group-hover:text-signal transition-colors">{icon}</span>
          {title}
          {typeof count === 'number' && (
            <span className="text-[10px] font-mono text-ink-500 bg-base-700 rounded px-1.5 py-0.5">{count}</span>
          )}
        </span>
        <ChevronDown
          size={15}
          className={clsx('text-ink-500 transition-transform', open && 'rotate-180')}
        />
      </button>
      {open && <div className="pb-3 text-[12.5px] text-ink-300 space-y-1.5">{children}</div>}
    </div>
  );
}

export default function ProfileDrawer({ profile, onClose }: ProfileDrawerProps) {
  const { token } = useAuth();
  const [exportState, setExportState] = useState<'idle' | 'hashing' | 'done' | 'error'>('idle');
  const [exportError, setExportError] = useState<string | null>(null);

  const handleExport = async () => {
    if (!profile || !token) return;
    setExportState('hashing');
    setExportError(null);
    try {
      // Step 1: backend renders the PDF and returns its SHA-256 digest —
      // the chain-of-custody proof shown in the UI.
      await exportDossier(token, profile.id);
      setExportState('done');
      // Step 2: trigger the actual file download via a plain browser nav —
      // the endpoint streams the PDF bytes with a Content-Disposition header.
      const link = document.createElement('a');
      link.href = dossierDownloadUrl(profile.id);
      // Auth: the download endpoint also requires a bearer token, which a
      // plain <a> can't attach — fetch the bytes instead and hand them to
      // the browser as a blob download.
      const res = await fetch(dossierDownloadUrl(profile.id), {
        headers: { Authorization: `Bearer ${token}` },
      });
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      link.href = blobUrl;
      link.download = `dossier_${profile.id}.pdf`;
      link.click();
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setExportState('error');
      setExportError(err instanceof ApiError ? err.message : 'Export failed — is the backend running?');
    } finally {
      setTimeout(() => setExportState('idle'), 3000);
    }
  };

  const isOpen = !!profile;
  const tier = profile ? TIER_STYLE[profile.tier] : null;

  return (
    <div
      className={clsx(
        'fixed inset-y-0 right-0 z-40 w-full max-w-sm bg-base-800 border-l border-base-600 shadow-panel transition-transform duration-300 ease-out flex flex-col',
        isOpen ? 'translate-x-0' : 'translate-x-full'
      )}
      aria-hidden={!isOpen}
    >
      {!profile ? null : (
        <>
          {/* Header */}
          <div className="flex items-start justify-between p-4 border-b border-base-600">
            <div>
              <p className="text-[10px] font-mono text-ink-500 tracking-label uppercase mb-1">
                Unified Intelligence Profile · {profile.id}
              </p>
              <h2 className="font-display font-semibold text-lg text-ink-100">{profile.name}</h2>
              {profile.alias.length > 0 && (
                <p className="text-[12px] text-ink-500 mt-0.5">
                  aka {profile.alias.join(', ')}
                </p>
              )}
              <span
                className={clsx(
                  'inline-flex items-center gap-1 mt-2 text-[10px] font-mono uppercase tracking-label px-2 py-0.5 rounded ring-1',
                  tier?.bg,
                  tier?.text,
                  tier?.ring
                )}
              >
                <ShieldAlert size={11} />
                {tier?.label}
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded text-ink-500 hover:text-ink-100 hover:bg-base-700 transition-colors"
              aria-label="Close profile drawer"
            >
              <X size={18} />
            </button>
          </div>

          {/* Face match card */}
          <div className="mx-4 mt-4 rounded-md border border-base-600 bg-base-700/60 p-3 flex items-center gap-3">
            <div className="h-14 w-14 rounded bg-base-900 border border-base-600 flex items-center justify-center shrink-0">
              <ScanFace size={26} className="text-signal" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[12px] text-ink-100 font-medium">ArcFace biometric match</p>
              <div className="mt-1 h-1.5 rounded-full bg-base-900 overflow-hidden">
                <div
                  className="h-full rounded-full bg-signal"
                  style={{ width: `${profile.face_match_confidence * 100}%` }}
                />
              </div>
              <p className="text-[11px] font-mono text-ink-500 mt-1">
                {(profile.face_match_confidence * 100).toFixed(1)}% confidence · Qdrant 512D
              </p>
            </div>
          </div>

          {/* Chunked profile sections */}
          <div className="flex-1 overflow-y-auto px-4 mt-2">
            <Section icon={<Users size={15} />} title="High-risk contacts" count={profile.contacts[0]?.count} defaultOpen>
              {profile.contacts.map((c) => (
                <div key={c.label} className="flex justify-between">
                  <span>{c.label}</span>
                  <span className="font-mono text-ink-500">{c.count}</span>
                </div>
              ))}
            </Section>

            <Section icon={<ShieldAlert size={15} />} title="IPC / BNS sections" count={profile.ipc_sections.length}>
              <div className="flex flex-wrap gap-1.5">
                {profile.ipc_sections.map((s) => (
                  <span key={s} className="font-mono text-[11px] bg-base-900 border border-base-600 rounded px-1.5 py-0.5">
                    {s}
                  </span>
                ))}
              </div>
            </Section>

            <Section icon={<Car size={15} />} title="Linked vehicles" count={profile.vehicles.length}>
              {profile.vehicles.length === 0 ? (
                <p className="text-ink-500 italic">No vehicles linked.</p>
              ) : (
                profile.vehicles.map((v) => <p key={v} className="font-mono">{v}</p>)
              )}
            </Section>

            <Section icon={<Landmark size={15} />} title="Financial trails" count={profile.financial_trails.length}>
              {profile.financial_trails.map((f) => (
                <div key={f.account} className="flex items-center justify-between">
                  <span className="font-mono">{f.account}</span>
                  {f.flagged && (
                    <span className="text-[10px] uppercase tracking-label text-threat-broker bg-threat-broker/10 rounded px-1.5 py-0.5">
                      Flagged
                    </span>
                  )}
                </div>
              ))}
            </Section>

            <p className="text-[11px] text-ink-500 py-3">
              Last known location: <span className="text-ink-300">{profile.last_known_location}</span>
            </p>
          </div>

          {/* Export */}
          <div className="p-4 border-t border-base-600">
            <button
              onClick={handleExport}
              disabled={exportState !== 'idle'}
              className={clsx(
                'w-full flex items-center justify-center gap-2 rounded-md py-2.5 text-[13px] font-medium transition-colors',
                exportState === 'idle' && 'bg-signal text-base-950 hover:bg-signal/90',
                exportState === 'hashing' && 'bg-base-700 text-ink-300 cursor-wait',
                exportState === 'done' && 'bg-signal/20 text-signal ring-1 ring-signal/40',
                exportState === 'error' && 'bg-threat-kingpin/20 text-threat-kingpin ring-1 ring-threat-kingpin/40'
              )}
            >
              {exportState === 'idle' && (
                <>
                  <FileDown size={16} /> Export verified dossier
                </>
              )}
              {exportState === 'hashing' && (
                <>
                  <Loader2 size={16} className="animate-spin" /> Hashing evidence (SHA-256)…
                </>
              )}
              {exportState === 'done' && (
                <>
                  <CheckCircle2 size={16} /> Dossier downloaded
                </>
              )}
              {exportState === 'error' && (
                <>
                  <AlertTriangle size={16} /> Export failed
                </>
              )}
            </button>
            {exportState === 'error' && exportError && (
              <p className="mt-2 text-[11px] text-threat-kingpin">{exportError}</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
