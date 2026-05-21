import 'server-only';
import { catalogGet } from '@/lib/api/client';
import { getFeatured, type FeaturedEntry } from '@/lib/featured';

type FilmRow = {
  uuid: string;
  title: string;
  poster_url?: string | null;
  imdb_rating?: number;
};

export type HeroSlide = {
  uuid: string;
  title: string;
  posterUrl: string;
  posterPosition: string;
  rating: number;
};

const POSTER_BASE = '/media/posters';
const FALLBACK_POSTER = `${POSTER_BASE}/_default.svg`;
const DEFAULT_FOCUS = { x: 50, y: 20 };

function buildPosterUrl(value: string | null | undefined): string {
  if (!value) return FALLBACK_POSTER;
  return value.startsWith('http') || value.startsWith('/')
    ? value
    : `${POSTER_BASE}/${value}`;
}

function formatPosition(focus: { x: number; y: number } | undefined): string {
  const { x, y } = focus ?? DEFAULT_FOCUS;
  return `${x}% ${y}%`;
}

function toSlide(raw: FilmRow, entry: FeaturedEntry | undefined): HeroSlide {
  return {
    uuid: raw.uuid,
    title: raw.title,
    posterUrl: buildPosterUrl(raw.poster_url),
    posterPosition: formatPosition(entry?.focus),
    rating: raw.imdb_rating ?? 0,
  };
}

async function fetchFromFeatured(entries: readonly FeaturedEntry[]): Promise<HeroSlide[]> {
  const settled = await Promise.allSettled(
    entries.map((entry) =>
      catalogGet('/api/v1/films/{film_id}', { pathParams: { film_id: entry.id } }),
    ),
  );
  const slides: HeroSlide[] = [];
  settled.forEach((result, i) => {
    if (result.status === 'fulfilled') {
      slides.push(toSlide(result.value as unknown as FilmRow, entries[i]));
    }
  });
  return slides;
}

async function fetchTopRated(): Promise<HeroSlide[]> {
  const list = (await catalogGet('/api/v1/films/', {
    query: { sort: '-imdb_rating', page_size: 3 } as never,
  })) as unknown as FilmRow[];
  return list.slice(0, 3).map((raw) => toSlide(raw, undefined));
}

export async function getHeroSlides(): Promise<HeroSlide[]> {
  const featured = await getFeatured();
  if (featured?.films.length) {
    const slides = await fetchFromFeatured(featured.films);
    if (slides.length) return slides;
  }
  return fetchTopRated();
}
