'use client';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import messages from '@/../messages/en.json';

type Props = {
  page: number;
  totalPages: number;
  hasNext: boolean;
};

export function FilmsPagination({ page, totalPages, hasNext }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const t = messages.films;

  const [pageInput, setPageInput] = useState(String(page));

  useEffect(() => {
    setPageInput(String(page));
  }, [page]);

  const hasPrev = page > 1;
  if (!hasPrev && !hasNext) return null;

  function go(target: number) {
    const next = new URLSearchParams(params.toString());
    if (target <= 1) next.delete('page');
    else next.set('page', String(target));
    const queryString = next.toString();
    router.push(queryString ? `${pathname}?${queryString}` : pathname);
  }

  function submitInput() {
    const parsed = Number(pageInput);
    if (!Number.isFinite(parsed) || parsed < 1) {
      setPageInput(String(page));
      return;
    }
    const target = Math.min(Math.floor(parsed), Math.max(totalPages, 1));
    if (target === page) {
      setPageInput(String(page));
      return;
    }
    go(target);
  }

  return (
    <nav className="flex items-center justify-center gap-4 text-sm" aria-label="Pagination">
      <button
        type="button"
        onClick={() => go(page - 1)}
        disabled={!hasPrev}
        className="rounded-md border border-white/10 bg-bg-elev/70 px-4 py-2 text-fg-primary transition-colors hover:border-accent/50 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-white/10"
      >
        {t.prev}
      </button>

      <div className="flex items-center gap-2 text-fg-muted">
        <label htmlFor="page-input" className="select-none">
          {t.page}
        </label>
        <input
          id="page-input"
          type="number"
          inputMode="numeric"
          min={1}
          max={Math.max(totalPages, 1)}
          value={pageInput}
          onChange={(e) => setPageInput(e.target.value)}
          onBlur={submitInput}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              submitInput();
            }
          }}
          aria-label="Page number"
          className="w-16 rounded-md border border-white/10 bg-bg-elev/70 px-2 py-1.5 text-center text-fg-primary outline-none transition-colors focus:border-accent [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
        />
        {totalPages > 0 ? (
          <span className="select-none">
            {t.of} {totalPages}
          </span>
        ) : null}
      </div>

      <button
        type="button"
        onClick={() => go(page + 1)}
        disabled={!hasNext}
        className="rounded-md border border-white/10 bg-bg-elev/70 px-4 py-2 text-fg-primary transition-colors hover:border-accent/50 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-white/10"
      >
        {t.next}
      </button>
    </nav>
  );
}
