import 'server-only';
import { catalogGet } from '@/lib/api/client';
import type { Genre } from '@/features/films/types';

type RawGenre = { uuid: string; name: string };

export async function listGenres(): Promise<Genre[]> {
  const raw = (await catalogGet('/api/v1/genres/')) as unknown as RawGenre[];
  return raw
    .map((g) => ({ uuid: g.uuid, name: g.name }))
    .sort((a, b) => a.name.localeCompare(b.name));
}
