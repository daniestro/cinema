import 'server-only';
import { cookies } from 'next/headers';
import { env } from '@/lib/env';

export type CurrentUser = {
  id: string;
  email: string;
};

export async function getCurrentUser(): Promise<CurrentUser | null> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;
  if (!accessToken) return null;

  try {
    const response = await fetch(`${env.INTERNAL_AUTH_URL}/api/v1/auth/me/`, {
      headers: { Cookie: `access_token=${accessToken}` },
      cache: 'no-store',
    });
    if (!response.ok) return null;
    const data = (await response.json()) as Partial<CurrentUser>;
    if (typeof data.id !== 'string' || typeof data.email !== 'string') return null;
    return { id: data.id, email: data.email };
  } catch {
    return null;
  }
}
