import messages from '@/../messages/en.json';

export function Footer() {
  return (
    <footer className="mt-section border-t border-white/5">
      <div className="mx-auto max-w-screen-xl px-6 py-8 text-sm text-fg-muted">
        {messages.footer.copyright}
      </div>
    </footer>
  );
}
