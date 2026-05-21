'use client';

import { useEffect, useRef, useState } from 'react';
import type { Rail } from '@/features/home/server/rails';

const VISIBLE = 4;
const GAP = 48;
const ROW_LEFT_PADDING = 20;
const MIN_CARD_WIDTH = 160;
const MAX_CARD_WIDTH = 240;
const FALLBACK_CARD_WIDTH = 224;

function Chevron({ direction }: { direction: 'left' | 'right' }) {
  return (
    <svg
      viewBox="0 0 12 32"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-16 w-6"
      style={direction === 'left' ? { transform: 'scaleX(-1)' } : undefined}
      aria-hidden
    >
      <polyline points="3,4 9,16 3,28" />
    </svg>
  );
}

export function NumberedRail({ rail }: { rail: Rail }) {
  const [start, setStart] = useState(0);
  const clipRef = useRef<HTMLDivElement>(null);
  const [cardWidth, setCardWidth] = useState(FALLBACK_CARD_WIDTH);

  useEffect(() => {
    const el = clipRef.current;
    if (!el) return;
    const measure = () => {
      const available = el.clientWidth - ROW_LEFT_PADDING - (VISIBLE - 1) * GAP - 4;
      const cw = Math.floor(available / VISIBLE);
      setCardWidth(Math.max(MIN_CARD_WIDTH, Math.min(MAX_CARD_WIDTH, cw)));
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const step = cardWidth + GAP;

  if (!rail.cards.length) {
    return (
      <section className="mx-auto max-w-screen-xl px-20">
        <h2 className="mb-6 text-2xl font-bold" style={{ paddingLeft: `${ROW_LEFT_PADDING}px` }}>
          Top in {rail.genre}
        </h2>
        <p className="text-fg-muted" style={{ paddingLeft: `${ROW_LEFT_PADDING}px` }}>
          Nothing here yet.
        </p>
      </section>
    );
  }

  const maxStart = Math.max(0, rail.cards.length - VISIBLE);
  const hasPrev = start > 0;
  const hasNext = start < maxStart;
  const offset = start * step;

  return (
    <section className="mx-auto max-w-screen-xl px-20">
      <h2 className="mb-6 text-2xl font-bold" style={{ paddingLeft: `${ROW_LEFT_PADDING}px` }}>
        Top in {rail.genre}
      </h2>
      <div className="relative">
        <button
          type="button"
          aria-label="Previous"
          onClick={() => setStart((s) => Math.max(0, s - 1))}
          disabled={!hasPrev}
          className={`absolute -left-16 top-1/2 z-10 -translate-y-1/2 p-2 text-fg-muted transition hover:text-accent ${
            hasPrev ? 'opacity-100' : 'pointer-events-none opacity-0'
          }`}
        >
          <Chevron direction="left" />
        </button>

        <div ref={clipRef} className="overflow-hidden">
          <ul
            className="flex transition-transform duration-500 ease-out"
            style={{
              gap: `${GAP}px`,
              paddingLeft: `${ROW_LEFT_PADDING}px`,
              transform: `translateX(-${offset}px)`,
            }}
          >
            {rail.cards.map((card, i) => (
              <li
                key={card.uuid}
                className="shrink-0"
                style={{ width: `${cardWidth}px` }}
              >
                <div className="relative">
                  <span
                    aria-hidden
                    className="pointer-events-none absolute select-none font-black leading-none text-bg-base"
                    style={{
                      left: '-16px',
                      bottom: '-16px',
                      fontSize: '120px',
                      WebkitTextStroke: '3px #FF6A2C',
                      zIndex: 2,
                    }}
                  >
                    {i + 1}
                  </span>
                  <div
                    className="relative z-[1] aspect-[2/3] overflow-hidden rounded-md bg-bg-elev shadow-lg"
                    style={{
                      backgroundImage: `url(${card.posterUrl})`,
                      backgroundSize: 'cover',
                      backgroundPosition: 'center',
                    }}
                  >
                    <span className="sr-only">{card.title}</span>
                  </div>
                </div>
                <p className="relative z-[3] mt-6 line-clamp-2 text-sm font-medium">{card.title}</p>
                <p className="relative z-[3] text-xs text-fg-muted">IMDb {card.rating.toFixed(1)}</p>
              </li>
            ))}
          </ul>
        </div>

        <button
          type="button"
          aria-label="Next"
          onClick={() => setStart((s) => Math.min(maxStart, s + 1))}
          disabled={!hasNext}
          className={`absolute -right-16 top-1/2 z-10 -translate-y-1/2 p-2 text-fg-muted transition hover:text-accent ${
            hasNext ? 'opacity-100' : 'pointer-events-none opacity-0'
          }`}
        >
          <Chevron direction="right" />
        </button>
      </div>
    </section>
  );
}
