import Link from 'next/link';
import type { ReactNode } from 'react';
import messages from '@/../messages/en.json';

export function Footer() {
  const t = messages.footer;

  return (
    <footer className="mt-section border-t border-white/5 bg-bg-base/70">
      <div className="mx-auto max-w-screen-xl px-6 py-12">
        <div className="grid gap-10 sm:grid-cols-[2fr_1fr_1fr]">
          <div>
            <Link href="/" className="text-xl font-bold tracking-tight text-accent">
              {messages.site.name}
            </Link>
            <p className="mt-3 max-w-xs text-sm text-fg-muted">{messages.site.tagline}</p>
          </div>

          <FooterColumn heading={t.browseHeading}>
            <FooterLink href="/films">{messages.nav.films}</FooterLink>
          </FooterColumn>

          <FooterColumn heading={t.accountHeading}>
            <FooterLink href="/login">{messages.nav.login}</FooterLink>
            <FooterLink href="/register">{t.register}</FooterLink>
          </FooterColumn>
        </div>

        <div className="mt-10 border-t border-white/5 pt-6 text-xs text-fg-muted">
          {t.copyright}
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({ heading, children }: { heading: string; children: ReactNode }) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-widest text-fg-primary">{heading}</h3>
      <ul className="mt-4 flex flex-col gap-2 text-sm text-fg-muted">{children}</ul>
    </div>
  );
}

function FooterLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <li>
      <Link href={href} className="transition-colors hover:text-fg-primary">
        {children}
      </Link>
    </li>
  );
}
