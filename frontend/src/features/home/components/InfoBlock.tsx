import Link from 'next/link';
import { cookies } from 'next/headers';
import type { ReactNode } from 'react';
import messages from '@/../messages/en.json';

const cardIcons: Record<'save' | 'rate' | 'share', ReactNode> = {
  save: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
    </svg>
  ),
  rate: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  ),
  share: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
      <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
    </svg>
  ),
};

export async function InfoBlock() {
  const cookieStore = await cookies();
  if (cookieStore.get('access_token')) return null;

  const { heading, cards, ctaPrimary, ctaSecondaryPrefix, ctaSecondary } = messages.info;

  return (
    <section className="mx-auto max-w-screen-xl px-[100px] py-section">
      <div
        className="relative overflow-hidden rounded-2xl border border-accent/30 bg-bg-elev/60 px-8 py-10 sm:px-12 sm:py-12"
        style={{ boxShadow: '0 0 80px -20px rgba(255, 106, 44, 0.35)' }}
      >
        <div
          aria-hidden
          className="pointer-events-none absolute -top-32 -right-32 h-80 w-80 rounded-full bg-accent/15 blur-3xl"
        />

        <div className="relative grid gap-12 lg:grid-cols-2 lg:items-center lg:gap-16">
          <div>
            <h2 className="text-5xl/[1.2] font-extrabold tracking-tight sm:text-6xl/[1.2]">
              {heading}
            </h2>
            <div className="mt-10">
              <Link
                href="/register"
                className="inline-flex items-center rounded-md bg-accent px-8 py-3 text-base font-semibold text-accent-fg transition-colors hover:bg-accent-hover"
              >
                {ctaPrimary}
              </Link>
              <p className="mt-4 text-sm text-fg-muted">
                {ctaSecondaryPrefix}{' '}
                <Link href="/login" className="font-medium text-accent hover:text-accent-hover">
                  {ctaSecondary}
                </Link>
              </p>
            </div>
          </div>

          <ul className="flex flex-col gap-4">
            {(['save', 'rate', 'share'] as const).map((key) => (
              <li
                key={key}
                className="flex gap-5 rounded-xl border border-white/10 bg-bg-base/80 p-6 transition-all duration-200 hover:scale-[1.02] hover:border-accent/40 hover:bg-bg-base"
              >
                <div className="h-7 w-7 shrink-0 text-accent">{cardIcons[key]}</div>
                <div>
                  <h3 className="text-lg font-semibold">{cards[key].title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-fg-muted">
                    {cards[key].body}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
