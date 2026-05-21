'use client';

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <section className="mx-auto max-w-screen-xl px-6 py-section">
      <h1 className="text-hero">Something broke.</h1>
      <p className="mt-6 text-lg text-fg-muted">An unexpected error occurred.</p>
      <button
        type="button"
        onClick={reset}
        className="mt-8 rounded-md bg-accent px-5 py-2 font-semibold text-accent-fg hover:bg-accent-hover"
      >
        Try again
      </button>
    </section>
  );
}
