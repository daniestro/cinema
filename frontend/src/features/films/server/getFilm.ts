import 'server-only';
import { catalogGet } from '@/lib/api/client';
import { CatalogHttpError } from '@/lib/api/errors';
import type { FilmDetail } from '@/features/films/types';

type RawPerson = { uuid: string; full_name: string };
type RawGenre = { uuid: string; name: string };
type RawDetail = {
  uuid: string;
  title: string;
  imdb_rating?: number;
  poster_url?: string | null;
  description?: string | null;
  genre: RawGenre[];
  directors: RawPerson[];
  actors: RawPerson[];
  writers: RawPerson[];
};

const POSTER_BASE = '/media/posters';
const FALLBACK_POSTER = `${POSTER_BASE}/_default.svg`;

function buildPosterUrl(value: string | null | undefined): string {
  if (!value) return FALLBACK_POSTER;
  return value.startsWith('http') || value.startsWith('/') ? value : `${POSTER_BASE}/${value}`;
}

function toPerson(raw: RawPerson) {
  return { uuid: raw.uuid, fullName: raw.full_name };
}

export async function getFilm(id: string): Promise<FilmDetail | null> {
  let raw: RawDetail;
  try {
    raw = (await catalogGet('/api/v1/films/{film_id}', {
      pathParams: { film_id: id },
    })) as unknown as RawDetail;
  } catch (error) {
    if (error instanceof CatalogHttpError && error.status === 404) return null;
    throw error;
  }

  return {
    uuid: raw.uuid,
    title: raw.title,
    posterUrl: buildPosterUrl(raw.poster_url),
    rating: raw.imdb_rating ?? 0,
    description: raw.description ?? null,
    genres: raw.genre.map((g) => ({ uuid: g.uuid, name: g.name })),
    directors: raw.directors.map(toPerson),
    actors: raw.actors.map(toPerson),
    writers: raw.writers.map(toPerson),
  };
}
