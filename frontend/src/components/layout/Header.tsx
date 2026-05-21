import Link from 'next/link';
import messages from '@/../messages/en.json';

export function Header() {
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
          <Link href="/login" className="hover:text-fg-primary">
            {messages.nav.login}
          </Link>
        </nav>
      </div>
    </header>
  );
}
