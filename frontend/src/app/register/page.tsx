import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { AuthShell } from '@/features/auth/components/AuthShell';
import { RegisterForm } from './RegisterForm';
import messages from '@/../messages/en.json';

export default async function RegisterPage() {
  const cookieStore = await cookies();
  if (cookieStore.get('access_token')) redirect('/');

  return (
    <AuthShell heading={messages.auth.register.heading} subheading={messages.auth.register.subheading}>
      <RegisterForm />
    </AuthShell>
  );
}
