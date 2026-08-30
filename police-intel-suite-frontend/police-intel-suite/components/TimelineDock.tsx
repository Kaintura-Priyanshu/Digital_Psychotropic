'use client';

import { useState } from 'react';
import { Clock } from 'lucide-react';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];

export default function TimelineDock() {
  const [range, setRange] = useState<[number, number]>([1, 6]);

  return (
    <div className="h-14 border-t border-base-600 bg-base-900 px-4 flex items-center gap-4">
      <span className="flex items-center gap-1.5 text-[11px] font-mono text-ink-500 tracking-label uppercase shrink-0">
        <Clock size={13} className="text-signal" />
        Timeline
      </span>

      <div className="flex-1 relative h-6 flex items-center">
        <div className="absolute left-0 right-0 h-1 rounded-full bg-base-700" />
        <div
          className="absolute h-1 rounded-full bg-signal/70"
          style={{
            left: `${(range[0] / (MONTHS.length - 1)) * 100}%`,
            right: `${100 - (range[1] / (MONTHS.length - 1)) * 100}%`,
          }}
        />
        <input
          type="range"
          min={0}
          max={MONTHS.length - 1}
          value={range[0]}
          onChange={(e) => setRange([Math.min(Number(e.target.value), range[1]), range[1]])}
          className="absolute w-full appearance-none bg-transparent pointer-events-auto accent-signal h-1"
        />
        <input
          type="range"
          min={0}
          max={MONTHS.length - 1}
          value={range[1]}
          onChange={(e) => setRange([range[0], Math.max(Number(e.target.value), range[0])])}
          className="absolute w-full appearance-none bg-transparent pointer-events-auto accent-signal h-1"
        />
      </div>

      <div className="hidden sm:flex gap-3 text-[11px] font-mono text-ink-500 shrink-0">
        {MONTHS.map((m, i) => (
          <span key={m} className={i >= range[0] && i <= range[1] ? 'text-ink-100' : ''}>
            {m}
          </span>
        ))}
      </div>
    </div>
  );
}
