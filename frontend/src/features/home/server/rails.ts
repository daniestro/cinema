import 'server-only';
import { catalogGet } from '@/lib/api/client';

type FilmRow = {
  uuid: string;
  title: string;
  poster_url?: string | null;
  imdb_rating?: number;
};

type GenreRow = {
  uuid: string;
  name: string;
};

export type RailCard = {
  uuid: string;
  title: string;
  posterUrl: string;
  rating: number;
};

export type Rail = {
  genre: string;
  cards: RailCard[];
};

const POSTER_BASE = '/media/posters';
const FALLBACK_POSTER = `${POSTER_BASE}/_default.svg`;
const RAIL_SIZE = 10;
export const RAIL_GENRES = ['Drama', 'Sci-Fi', 'Comedy'] as const;

function buildPosterUrl(value: string | null | undefined): string {
  if (!value) return FALLBACK_POSTER;
  return value.startsWith('http') || value.startsWith('/')
    ? value
    : `${POSTER_BASE}/${value}`;
}

function toCard(raw: FilmRow): RailCard {
  return {
    uuid: raw.uuid,
    title: raw.title,
    posterUrl: buildPosterUrl(raw.poster_url),
    rating: raw.imdb_rating ?? 0,
  };
}

async function fetchRail(genre: string, uuid: string): Promise<Rail> {
  const list = (await catalogGet('/api/v1/films/', {
    query: { genre: uuid, sort: '-imdb_rating', page_size: RAIL_SIZE } as never,
  })) as unknown as FilmRow[];
  return { genre, cards: list.slice(0, RAIL_SIZE).map(toCard) };
}

export async function getRails(): Promise<Rail[]> {
  const genres = (await catalogGet('/api/v1/genres/')) as unknown as GenreRow[];
  const byName = new Map(genres.map((g) => [g.name, g.uuid]));

  const settled = await Promise.allSettled(
    RAIL_GENRES.map((name) => {
      const uuid = byName.get(name);
      if (!uuid) {
        console.warn(`[rails] genre not found in catalog: ${name}`);
        return Promise.resolve<Rail>({ genre: name, cards: [] });
      }
      return fetchRail(name, uuid);
    }),
  );

  const rails: Rail[] = [];
  settled.forEach((r, i) => {
    if (r.status === 'fulfilled') {
      rails.push(r.value);
    } else {
      console.warn(`[rails] failed to load ${RAIL_GENRES[i]}:`, r.reason);
      rails.push({ genre: RAIL_GENRES[i], cards: [] });
    }
  });
  return rails;
}
