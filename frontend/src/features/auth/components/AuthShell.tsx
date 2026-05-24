import type { ReactNode } from 'react';

type Props = {
  heading: string;
  subheading?: string;
  footer?: ReactNode;
  children: ReactNode;
};

export function AuthShell({ heading, subheading, footer, children }: Props) {
  return (
    <section className="mx-auto flex max-w-md flex-col px-6 py-section">
      <div
        className="relative overflow-hidden rounded-2xl border border-accent/30 bg-bg-elev/60 px-8 py-10 sm:px-10 sm:py-12"
        style={{ boxShadow: '0 0 80px -20px rgba(255, 106, 44, 0.35)' }}
      >
        <div
          aria-hidden
          className="pointer-events-none absolute -top-32 -right-32 h-80 w-80 rounded-full bg-accent/15 blur-3xl"
        />

        <div className="relative">
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">{heading}</h1>
          {subheading ? <p className="mt-3 text-sm text-fg-muted">{subheading}</p> : null}

          <div className="mt-8">{children}</div>

          {footer ? <div className="mt-6 text-sm text-fg-muted">{footer}</div> : null}
        </div>
      </div>
    </section>
  );
}
