import { FilmCard } from '@/features/films/components/FilmCard';
import type { Film } from '@/features/films/types';
import messages from '@/../messages/en.json';

export function FilmGrid({ films }: { films: Film[] }) {
  if (films.length === 0) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-center text-fg-muted">
        {messages.films.empty}
      </div>
    );
  }

  return (
    <ul className="grid grid-cols-2 gap-x-6 gap-y-10 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {films.map((film) => (
        <li key={film.uuid}>
          <FilmCard film={film} />
        </li>
      ))}
    </ul>
  );
}
