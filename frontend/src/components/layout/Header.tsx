import Link from 'next/link';
import { getCurrentUser } from '@/features/auth/server/me';
import messages from '@/../messages/en.json';

export async function Header() {
  const user = await getCurrentUser();

  return (
    <header className="border-b border-white/5 bg-bg-base/70 backdrop-blur supports-[backdrop-filter]:bg-bg-base/60">
      <div className="mx-auto flex max-w-screen-xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-xl font-bold tracking-tight text-accent">
          {messages.site.name}
        </Link>
        <nav className="flex items-center gap-6 text-sm text-fg-muted">
          <Link href="/films" className="hover:text-fg-primary">
            {messages.nav.films}
          </Link>

          {user ? (
            <span className="flex items-center gap-2 text-fg-primary">
              <UserGlyph />
              <span className="font-medium">{displayName(user.email)}</span>
            </span>
          ) : (
            <>
              <Link href="/login" className="hover:text-fg-primary">
                {messages.nav.login}
              </Link>
              <Link
                href="/register"
                className="inline-flex items-center rounded-md bg-accent px-4 py-2 font-semibold text-accent-fg transition-colors hover:bg-accent-hover"
              >
                {messages.nav.register}
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

function displayName(email: string): string {
  const localPart = email.split('@')[0];
  return localPart || email;
}

function UserGlyph() {
  return (
    <span
      aria-hidden
      className="flex h-7 w-7 items-center justify-center rounded-full bg-accent/15 text-accent"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    </span>
  );
}
