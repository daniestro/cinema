'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { TextField } from '@/features/auth/components/TextField';
import { PasswordRequirements } from '@/features/auth/components/PasswordRequirements';
import { AuthError, signIn, signUp } from '@/features/auth/api';
import { signUpSchema } from '@/features/auth/schema';
import messages from '@/../messages/en.json';

type FieldErrors = { email?: string; password?: string };

export function RegisterForm() {
  const router = useRouter();
  const t = messages.auth;
  const tRegister = messages.auth.register;

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);

    const parsed = signUpSchema.safeParse({ email, password });
    if (!parsed.success) {
      const errors: FieldErrors = {};
      for (const issue of parsed.error.issues) {
        const field = issue.path[0];
        if (field === 'email' && !errors.email) errors.email = issue.message;
        if (field === 'password' && !errors.password) errors.password = ' ';
      }
      setFieldErrors(errors);
      return;
    }

    setFieldErrors({});
    setIsSubmitting(true);
    try {
      await signUp(parsed.data);
      await signIn(parsed.data);
      router.push('/');
      router.refresh();
    } catch (error) {
      setFormError(error instanceof AuthError ? error.message : 'Something went wrong');
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5" noValidate>
      <TextField
        label={t.emailLabel}
        name="email"
        type="email"
        autoComplete="email"
        placeholder={t.emailPlaceholder}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={fieldErrors.email}
        required
      />
      <div>
        <TextField
          label={t.passwordLabel}
          name="password"
          type="password"
          autoComplete="new-password"
          placeholder={t.passwordPlaceholder}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fieldErrors.password}
          required
        />
        {password ? <PasswordRequirements password={password} /> : null}
      </div>

      {formError ? <p className="text-sm text-red-400">{formError}</p> : null}

      <button
        type="submit"
        disabled={isSubmitting}
        className="mt-2 inline-flex items-center justify-center rounded-md bg-accent px-6 py-3 text-base font-semibold text-accent-fg transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? t.submitting : tRegister.submit}
      </button>

      <p className="text-center text-sm text-fg-muted">
        {tRegister.hasAccountPrefix}{' '}
        <Link href="/login" className="font-medium text-accent hover:text-accent-hover">
          {tRegister.hasAccountLink}
        </Link>
      </p>
    </form>
  );
}
