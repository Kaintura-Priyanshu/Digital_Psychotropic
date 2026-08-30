'use client';

import { useRef, useState } from 'react';
import { Search, Mic, ImagePlus, SlidersHorizontal, X, Radio, Loader2, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';
import { searchText, searchFace, SearchHit, ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

interface TopSearchBarProps {
  onResultSelect?: (uipId: string) => void;
  liveAlertCount?: number;
}

export default function TopSearchBar({ onResultSelect, liveAlertCount = 3 }: TopSearchBarProps) {
  const { token } = useAuth();
  const [query, setQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [droppedFile, setDroppedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [searching, setSearching] = useState(false);
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [cypher, setCypher] = useState<string | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const runSearch = async () => {
    if (!token) return;
    if (droppedFile) return runFaceSearch(droppedFile);
    if (!query.trim()) {
      setHits(null);
      return;
    }
    setSearching(true);
    setSearchError(null);
    setCypher(null);
    try {
      const res = await searchText(token, query);
      setHits(res.hits);
      setCypher(res.cypher ?? null);
    } catch (err) {
      setHits(null);
      setSearchError(err instanceof ApiError ? err.message : 'Search failed — is the backend running?');
    } finally {
      setSearching(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runSearch();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setDroppedFile(file);
      runFaceSearch(file);
    }
  };

  const runFaceSearch = async (file: File) => {
    if (!token) return;
    setSearching(true);
    setSearchError(null);
    setCypher(null);
    try {
      const res = await searchFace(token, file);
      setHits(res.hits);
    } catch (err) {
      setHits(null);
      setSearchError(err instanceof ApiError ? err.message : 'Face search failed — is the backend running?');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="border-b border-base-600 bg-base-900/95 backdrop-blur px-4 py-2.5 flex items-center gap-3">
      {/* Brand / system mark */}
      <div className="flex items-center gap-2 pr-3 border-r border-base-600 shrink-0">
        <div className="relative h-7 w-7 rounded-sm bg-base-800 border border-signal/30 flex items-center justify-center">
          <Radio size={14} className="text-signal" />
          <span className="absolute inset-0 rounded-sm border border-signal/40 animate-pulse-slow" />
        </div>
        <div className="leading-tight hidden md:block">
          <p className="font-display font-semibold text-[13px] text-ink-100 tracking-label uppercase">
            MHA Intel Suite
          </p>
          <p className="text-[10px] text-ink-500 font-mono tracking-label">SIH-26189 · TACTICAL</p>
        </div>
      </div>

      {/* Universal search */}
      <form
        onSubmit={handleSubmit}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={clsx(
          'flex-1 flex items-center gap-2 rounded-md border bg-base-800 px-3 py-1.5 transition-colors',
          isDragOver ? 'border-signal ring-1 ring-signal/40' : 'border-base-600 focus-within:border-signal/60'
        )}
      >
        <button type="submit" aria-label="Run search" className="shrink-0 text-ink-500 hover:text-signal transition-colors">
          {searching ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
        </button>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          type="text"
          placeholder='Search suspects, phone numbers, or ask — "Show Rahul&apos;s hawala contacts, last 3 months"'
          disabled={!!droppedFile}
          className="flex-1 bg-transparent text-sm text-ink-100 placeholder:text-ink-700 outline-none font-body min-w-0 disabled:opacity-50"
        />

        {droppedFile && (
          <span className="hidden sm:flex items-center gap-1.5 text-[11px] bg-base-700 text-ink-300 px-2 py-1 rounded font-mono shrink-0">
            {droppedFile.name}
            <button
              type="button"
              aria-label="Remove uploaded photo"
              onClick={() => {
                setDroppedFile(null);
                setHits(null);
              }}
              className="text-ink-500 hover:text-ink-100"
            >
              <X size={12} />
            </button>
          </span>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              setDroppedFile(file);
              runFaceSearch(file);
            }
          }}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          title="Upload a photo for facial search"
          className="shrink-0 p-1.5 rounded text-ink-500 hover:text-signal hover:bg-base-700 transition-colors"
        >
          <ImagePlus size={16} />
        </button>

        <button
          type="button"
          onClick={() => setIsListening((v) => !v)}
          title="Voice query"
          className={clsx(
            'shrink-0 p-1.5 rounded transition-colors',
            isListening ? 'text-threat-kingpin bg-threat-kingpin/10' : 'text-ink-500 hover:text-signal hover:bg-base-700'
          )}
        >
          <Mic size={16} className={isListening ? 'animate-pulse' : ''} />
        </button>

        <button
          type="button"
          onClick={() => setShowFilters((v) => !v)}
          title="Advanced filters"
          className={clsx(
            'shrink-0 p-1.5 rounded transition-colors',
            showFilters ? 'text-signal bg-signal/10' : 'text-ink-500 hover:text-signal hover:bg-base-700'
          )}
        >
          <SlidersHorizontal size={16} />
        </button>
      </form>

      {/* Progressive-disclosure advanced filters — hidden until requested (Hick's Law) */}
      {showFilters && (
        <div className="absolute left-4 right-4 top-[52px] z-30 flex flex-wrap gap-2 rounded-md border border-base-600 bg-base-800 p-3 shadow-panel">
          {['IMEI range', 'Date range', 'IPC / BNS section', 'District', 'Confidence ≥ 85%'].map((f) => (
            <span
              key={f}
              className="text-[11px] font-mono px-2.5 py-1 rounded border border-base-600 text-ink-300 hover:border-signal/50 hover:text-signal cursor-pointer transition-colors"
            >
              {f}
            </span>
          ))}
        </div>
      )}

      {/* Search results — from the live Graph Query Agent (text) or Qdrant face match (photo) */}
      {(hits || searchError) && (
        <div className="absolute left-4 right-4 top-[52px] z-20 rounded-md border border-base-600 bg-base-800 shadow-panel overflow-hidden">
          {searchError && (
            <p className="flex items-center gap-1.5 px-3 py-2 text-[12px] text-threat-kingpin">
              <AlertTriangle size={13} /> {searchError}
            </p>
          )}
          {hits && hits.length === 0 && !searchError && (
            <p className="px-3 py-2 text-[12px] text-ink-500">No matches found.</p>
          )}
          {hits && hits.length > 0 && (
            <ul className="max-h-64 overflow-y-auto">
              {hits.map((hit) => (
                <li key={hit.uip_id}>
                  <button
                    type="button"
                    onClick={() => {
                      onResultSelect?.(hit.uip_id);
                      setHits(null);
                      setDroppedFile(null);
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-base-700 transition-colors"
                  >
                    <span className="text-[13px] text-ink-100">{hit.name}</span>
                    <span className="text-[10px] font-mono text-ink-500">
                      {hit.uip_id} · {(hit.score * 100).toFixed(0)}% · {hit.matched_on}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {cypher && (
            <p className="border-t border-base-600 px-3 py-1.5 text-[10px] font-mono text-ink-500 truncate" title={cypher}>
              Cypher: {cypher}
            </p>
          )}
        </div>
      )}

      {/* Live alert ticker */}
      <div className="hidden lg:flex items-center gap-2 pl-3 border-l border-base-600 shrink-0">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-threat-kingpin opacity-60" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-threat-kingpin" />
        </span>
        <span className="text-[11px] font-mono text-ink-300">
          {liveAlertCount} active watchlist alert{liveAlertCount === 1 ? '' : 's'}
        </span>
      </div>
    </div>
  );
}
