import 'server-only';
import { catalogGet } from '@/lib/api/client';
import { DEFAULT_PAGE_SIZE, type Film, type FilmsQuery } from '@/features/films/types';

type RawFilm = {
  uuid: string;
  title: string;
  poster_url?: string | null;
  imdb_rating?: number;
};

const POSTER_BASE = '/media/posters';
const FALLBACK_POSTER = `${POSTER_BASE}/_default.svg`;

function buildPosterUrl(value: string | null | undefined): string {
  if (!value) return FALLBACK_POSTER;
  return value.startsWith('http') || value.startsWith('/') ? value : `${POSTER_BASE}/${value}`;
}

function toFilm(raw: RawFilm): Film {
  return {
    uuid: raw.uuid,
    title: raw.title,
    posterUrl: buildPosterUrl(raw.poster_url),
    rating: raw.imdb_rating ?? 0,
  };
}

export type FilmsPage = {
  films: Film[];
  total: number;
  totalPages: number;
  hasNext: boolean;
};

export async function listFilms(query: FilmsQuery): Promise<FilmsPage> {
  const sort = query.sort === 'asc' ? 'imdb_rating' : '-imdb_rating';
  const pageSize = DEFAULT_PAGE_SIZE;

  const baseParams = {
    sort,
    page_number: query.page,
    page_size: pageSize,
  };

  let total = 0;
  const captureTotal = (response: Response) => {
    const header = response.headers.get('x-total-count');
    const parsed = header ? Number(header) : NaN;
    if (Number.isFinite(parsed) && parsed >= 0) total = parsed;
  };

  let raw: RawFilm[];
  if (query.search) {
    raw = (await catalogGet('/api/v1/films/search/', {
      query: { ...baseParams, query: query.search } as never,
      onResponse: captureTotal,
    })) as unknown as RawFilm[];
  } else {
    raw = (await catalogGet('/api/v1/films/', {
      query: { ...baseParams, ...(query.genre ? { genre: query.genre } : {}) } as never,
      onResponse: captureTotal,
    })) as unknown as RawFilm[];
  }

  const totalPages = total > 0 ? Math.ceil(total / pageSize) : 0;

  return {
    films: raw.map(toFilm),
    total,
    totalPages,
    hasNext: query.page < totalPages,
  };
}
