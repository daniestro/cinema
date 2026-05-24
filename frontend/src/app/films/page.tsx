import { listFilms } from '@/features/films/server/listFilms';
import { listGenres } from '@/features/films/server/listGenres';
import { FilmGrid } from '@/features/films/components/FilmGrid';
import { FilmsToolbar } from '@/features/films/components/FilmsToolbar';
import { FilmsPagination } from '@/features/films/components/FilmsPagination';
import messages from '@/../messages/en.json';

type SearchParams = Promise<{
  q?: string;
  genre?: string;
  sort?: string;
  page?: string;
}>;

function parsePage(value: string | undefined): number {
  const n = Number(value);
  return Number.isFinite(n) && n >= 1 ? Math.floor(n) : 1;
}

export default async function FilmsPage({ searchParams }: { searchParams: SearchParams }) {
  const sp = await searchParams;
  const query = {
    search: sp.q?.trim() ?? '',
    genre: sp.genre || null,
    sort: (sp.sort === 'asc' ? 'asc' : 'desc') as 'asc' | 'desc',
    page: parsePage(sp.page),
  };

  const [{ films, hasNext, totalPages }, genres] = await Promise.all([
    listFilms(query),
    listGenres(),
  ]);

  return (
    <section className="mx-auto max-w-screen-xl px-6 py-12 lg:px-[100px]">
      <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">{messages.films.heading}</h1>

      <div className="mt-8">
        <FilmsToolbar genres={genres} />
      </div>

      <div className="mt-10">
        <FilmGrid films={films} />
      </div>

      {films.length > 0 ? (
        <div className="mt-12">
          <FilmsPagination page={query.page} totalPages={totalPages} hasNext={hasNext} />
        </div>
      ) : null}
    </section>
  );
}
