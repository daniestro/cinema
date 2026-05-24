'use client';

import { checkPassword } from '@/features/auth/passwordRules';

export function PasswordRequirements({ password }: { password: string }) {
  const rules = checkPassword(password);

  return (
    <ul className="mt-2 flex flex-col gap-1.5">
      {rules.map((rule) => (
        <li
          key={rule.id}
          className={`flex items-center gap-2 text-xs transition-colors ${
            rule.passed ? 'text-green-400' : 'text-fg-muted'
          }`}
        >
          <span
            aria-hidden
            className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full border ${
              rule.passed
                ? 'border-green-400/40 bg-green-400/10'
                : 'border-white/15'
            }`}
          >
            {rule.passed ? <CheckMark /> : null}
          </span>
          <span>{rule.message}</span>
        </li>
      ))}
    </ul>
  );
}

function CheckMark() {
  return (
    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
