'use client';

import { useEffect, useState } from 'react';
import type { HeroSlide } from '@/features/home/server/heroData';

const ROTATION_MS = 6000;

export function HeroRotator({ slides }: { slides: HeroSlide[] }) {
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused || slides.length <= 1) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % slides.length);
    }, ROTATION_MS);
    return () => window.clearInterval(id);
  }, [paused, slides.length]);

  if (!slides.length) {
    return (
      <div className="flex h-[70vh] items-center justify-center text-fg-muted">
        No featured films yet.
      </div>
    );
  }

  const current = slides[index];

  return (
    <div className="relative h-[70vh] min-h-[480px] w-full overflow-hidden bg-bg-elev">
      {slides.map((slide, i) => (
        <div
          key={slide.uuid}
          aria-hidden={i !== index}
          className={`absolute inset-0 transition-opacity duration-700 ${
            i === index ? 'opacity-100' : 'opacity-0'
          }`}
          style={{
            backgroundImage: `url(${slide.posterUrl})`,
            backgroundSize: 'cover',
            backgroundPosition: slide.posterPosition,
          }}
        />
      ))}

      <div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-t from-bg-base via-bg-base/60 to-transparent"
      />
      <div
        aria-hidden
        className="absolute inset-y-0 left-0 w-1/2 bg-gradient-to-r from-bg-base/90 to-transparent"
      />

      <div className="relative z-10 mx-auto flex h-full max-w-screen-xl flex-col justify-end px-10 pb-16">
        <p className="text-sm font-semibold uppercase tracking-widest text-accent">
          Featured
        </p>
        <h1 className="mt-3 max-w-2xl text-hero">{current.title}</h1>
        <p className="mt-3 text-lg text-fg-muted">
          IMDb {current.rating.toFixed(1)}
        </p>

        {slides.length > 1 && (
          <div className="mt-8 flex items-center gap-3">
            {slides.map((slide, i) => (
              <button
                key={slide.uuid}
                type="button"
                aria-label={`Show ${slide.title}`}
                onClick={() => {
                  setIndex(i);
                  setPaused(true);
                }}
                className={`h-1.5 rounded-full transition-all ${
                  i === index
                    ? 'w-10 bg-accent'
                    : 'w-6 bg-fg-muted/40 hover:bg-fg-muted'
                }`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
