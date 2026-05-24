import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { AuthShell } from '@/features/auth/components/AuthShell';
import { LoginForm } from './LoginForm';
import messages from '@/../messages/en.json';

export default async function LoginPage() {
  const cookieStore = await cookies();
  if (cookieStore.get('access_token')) redirect('/');

  return (
    <AuthShell heading={messages.auth.login.heading} subheading={messages.auth.login.subheading}>
      <LoginForm />
    </AuthShell>
  );
}
