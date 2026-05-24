export type Film = {
  uuid: string;
  title: string;
  posterUrl: string;
  rating: number;
};

export type Genre = {
  uuid: string;
  name: string;
};

export type FilmsQuery = {
  search: string;
  genre: string | null;
  sort: 'asc' | 'desc';
  page: number;
};

export const DEFAULT_PAGE_SIZE = 24;
