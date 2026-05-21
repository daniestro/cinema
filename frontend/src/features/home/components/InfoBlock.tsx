import Link from 'next/link';
import { cookies } from 'next/headers';
import messages from '@/../messages/en.json';

export async function InfoBlock() {
  const cookieStore = await cookies();
  if (cookieStore.get('access_token')) return null;

  const cards = messages.info.cards;

  return (
    <section className="mx-auto max-w-screen-xl px-[100px] py-section">
      <h2 className="text-3xl font-bold">{messages.info.heading}</h2>
      <p className="mt-3 max-w-2xl text-fg-muted">{messages.info.subheading}</p>

      <ul className="mt-10 grid gap-6 sm:grid-cols-3">
        {(['save', 'rate', 'share'] as const).map((key) => (
          <li key={key} className="rounded-xl border border-white/5 bg-bg-elev p-6">
            <h3 className="text-lg font-semibold text-accent">{cards[key].title}</h3>
            <p className="mt-3 text-sm leading-relaxed text-fg-muted">{cards[key].body}</p>
          </li>
        ))}
      </ul>

      <div className="mt-8">
        <Link
          href="/login"
          className="inline-flex items-center rounded-md bg-accent px-5 py-2 font-semibold text-accent-fg hover:bg-accent-hover"
        >
          {messages.info.cta}
        </Link>
      </div>
    </section>
  );
}
