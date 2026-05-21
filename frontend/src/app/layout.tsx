import type { Metadata } from 'next';
import { Footer } from '@/components/layout/Footer';
import { Header } from '@/components/layout/Header';
import messages from '@/../messages/en.json';
import './globals.css';

export const metadata: Metadata = {
  title: messages.site.name,
  description: messages.site.tagline,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-bg-base text-fg-primary">
      <body className="flex min-h-screen flex-col font-sans antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
