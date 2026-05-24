import type { Credentials } from './schema';

export class AuthError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = 'AuthError';
  }
}

async function postJson(path: string, body: unknown): Promise<Response> {
  return fetch(path, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

async function readError(response: Response, fallback: string): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: unknown };
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail) && data.detail[0]?.msg) return String(data.detail[0].msg);
  } catch {
    // body wasn't JSON
  }
  return fallback;
}

export async function signIn(credentials: Credentials): Promise<void> {
  const response = await postJson('/auth/api/v1/auth/signin/', credentials);
  if (!response.ok) {
    throw new AuthError(await readError(response, 'Invalid email or password'), response.status);
  }
}

export async function signUp(credentials: Credentials): Promise<void> {
  const response = await postJson('/auth/api/v1/auth/signup/', credentials);
  const body = await response.clone().text();
  console.log('[signUp]', response.status, response.statusText, body);
  if (!response.ok) {
    throw new AuthError(await readError(response, 'Could not create account'), response.status);
  }
}
