import Link from 'next/link';

export default function NotFound() {
  return (
    <section className="mx-auto max-w-screen-xl px-6 py-section">
      <h1 className="text-hero">404</h1>
      <p className="mt-6 text-lg text-fg-muted">This page does not exist.</p>
      <Link href="/" className="mt-8 inline-block text-accent hover:text-accent-hover">
        Back to home →
      </Link>
    </section>
  );
}
