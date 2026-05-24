import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { ReactNode } from 'react';
import { getFilm } from '@/features/films/server/getFilm';
import type { Person } from '@/features/films/types';
import messages from '@/../messages/en.json';

type Props = { params: Promise<{ id: string }> };

export default async function FilmDetailPage({ params }: Props) {
  const { id } = await params;
  const film = await getFilm(id);
  if (!film) notFound();

  const t = messages.filmDetail;

  return (
    <article className="mx-auto max-w-screen-xl px-6 py-10 lg:px-[100px]">
      <Link
        href="/films"
        className="inline-flex items-center gap-1 text-sm text-fg-muted transition-colors hover:text-fg-primary"
      >
        ← {t.back}
      </Link>

      <div className="mt-8 grid gap-10 md:grid-cols-[260px_1fr] lg:gap-14">
        <div
          className="relative mx-auto aspect-[2/3] w-full max-w-[220px] overflow-hidden rounded-lg bg-bg-elev shadow-2xl md:mx-0 md:max-w-none"
          style={{
            backgroundImage: `url(${film.posterUrl})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <span className="sr-only">{film.title}</span>
        </div>

        <div className="flex flex-col">
          <h1 className="text-4xl font-extrabold leading-[1.1] tracking-tight sm:text-5xl">
            {film.title}
          </h1>

          <div className="mt-5 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm text-fg-muted">
            <span className="font-semibold text-accent">IMDb {film.rating.toFixed(1)}</span>
            {film.genres.length > 0 ? (
              <>
                <span aria-hidden>·</span>
                <ul className="flex flex-wrap gap-2">
                  {film.genres.map((g) => (
                    <li
                      key={g.uuid}
                      className="rounded-full border border-white/10 bg-bg-elev/60 px-3 py-0.5 text-xs"
                    >
                      {g.name}
                    </li>
                  ))}
                </ul>
              </>
            ) : null}
          </div>

          {film.description ? (
            <p className="mt-6 max-w-prose text-base leading-relaxed text-fg-primary/90">
              {film.description}
            </p>
          ) : (
            <p className="mt-6 text-sm text-fg-muted">{t.noDescription}</p>
          )}
        </div>
      </div>

      <div className="mt-14 grid gap-10 sm:grid-cols-3">
        <PeopleSection heading={t.directors} people={film.directors} empty={t.noDirectors} />
        <PeopleSection heading={t.cast} people={film.actors} empty={t.noActors} />
        <PeopleSection heading={t.writers} people={film.writers} empty={t.noWriters} />
      </div>
    </article>
  );
}

function PeopleSection({
  heading,
  people,
  empty,
}: {
  heading: string;
  people: Person[];
  empty: string;
}): ReactNode {
  return (
    <section>
      <h2 className="text-xs font-semibold uppercase tracking-widest text-accent">{heading}</h2>
      {people.length > 0 ? (
        <ul className="mt-3 flex flex-col gap-1 text-sm text-fg-primary">
          {people.map((p) => (
            <li key={p.uuid}>{p.fullName}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-fg-muted">{empty}</p>
      )}
    </section>
  );
}
