import Link from 'next/link';
import type { Film } from '@/features/films/types';

export function FilmCard({ film }: { film: Film }) {
  return (
    <Link href={`/films/${film.uuid}`} className="group flex flex-col">
      <div
        className="relative aspect-[2/3] overflow-hidden rounded-md bg-bg-elev shadow-md transition-transform duration-200 group-hover:scale-[1.03]"
        style={{
          backgroundImage: `url(${film.posterUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <span className="sr-only">{film.title}</span>
      </div>
      <p className="mt-3 line-clamp-2 text-sm font-medium text-fg-primary transition-colors group-hover:text-accent">
        {film.title}
      </p>
      <p className="mt-0.5 text-xs text-fg-muted">IMDb {film.rating.toFixed(1)}</p>
    </Link>
  );
}
