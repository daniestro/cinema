'use client';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import type { Genre } from '@/features/films/types';
import messages from '@/../messages/en.json';

const SEARCH_DEBOUNCE_MS = 300;

export function FilmsToolbar({ genres }: { genres: Genre[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const t = messages.films;

  const initialSearch = params.get('q') ?? '';
  const currentGenre = params.get('genre') ?? '';
  const currentSort = (params.get('sort') === 'asc' ? 'asc' : 'desc') as 'asc' | 'desc';

  const [search, setSearch] = useState(initialSearch);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      if (search === initialSearch) return;
      pushParams({ q: search || null, page: null });
    }, SEARCH_DEBOUNCE_MS);
    return () => window.clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  function pushParams(updates: Record<string, string | null>) {
    const next = new URLSearchParams(params.toString());
    for (const [key, value] of Object.entries(updates)) {
      if (value === null || value === '') next.delete(key);
      else next.set(key, value);
    }
    const queryString = next.toString();
    router.push(queryString ? `${pathname}?${queryString}` : pathname);
  }

  const isSearching = search.length > 0;

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder={t.searchPlaceholder}
        className="w-full rounded-md border border-white/10 bg-bg-elev/70 px-4 py-2.5 text-sm text-fg-primary outline-none transition-colors placeholder:text-fg-muted focus:border-accent sm:max-w-sm"
      />

      <div className="flex flex-1 items-center justify-end gap-3">
        <select
          value={currentGenre}
          onChange={(e) => pushParams({ genre: e.target.value || null, page: null })}
          disabled={isSearching}
          aria-label={t.genreLabel}
          className="rounded-md border border-white/10 bg-bg-elev/70 px-3 py-2 text-sm text-fg-primary outline-none transition-colors focus:border-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          <option value="">{t.allGenres}</option>
          {genres.map((g) => (
            <option key={g.uuid} value={g.uuid}>
              {g.name}
            </option>
          ))}
        </select>

        <button
          type="button"
          onClick={() => pushParams({ sort: currentSort === 'desc' ? 'asc' : 'desc', page: null })}
          aria-pressed={currentSort === 'asc'}
          className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-bg-elev/70 px-3 py-2 text-sm text-fg-primary transition-colors hover:border-accent/50"
        >
          {t.sortLabel}
          <span aria-hidden className="text-accent">
            {currentSort === 'desc' ? '↓' : '↑'}
          </span>
        </button>
      </div>
    </div>
  );
}
