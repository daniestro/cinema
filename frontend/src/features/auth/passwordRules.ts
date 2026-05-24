const ALLOWED_PATTERN = /^[A-Za-z\d@$!%*#?&"']+$/;
const SPECIAL_DISPLAY = '@ $ ! % * # ? & " \'';

type Rule = {
  id: string;
  check: (password: string) => boolean;
  message: string;
};

export const passwordRules: Rule[] = [
  {
    id: 'length',
    check: (p) => p.length >= 6 && p.length <= 50,
    message: 'Must be between 6 and 50 characters',
  },
  {
    id: 'lowercase',
    check: (p) => /[a-z]/.test(p),
    message: 'Must include a lowercase letter',
  },
  {
    id: 'uppercase',
    check: (p) => /[A-Z]/.test(p),
    message: 'Must include an uppercase letter',
  },
  {
    id: 'digit',
    check: (p) => /\d/.test(p),
    message: 'Must include a digit',
  },
  {
    id: 'special',
    check: (p) => /[@$!%*#?&"']/.test(p),
    message: `Must include one special character: ${SPECIAL_DISPLAY}`,
  },
  {
    id: 'allowed',
    check: (p) => p === '' || ALLOWED_PATTERN.test(p),
    message: `Only letters, digits and ${SPECIAL_DISPLAY} are allowed`,
  },
];

export type PasswordRuleStatus = { id: string; message: string; passed: boolean };

export function checkPassword(password: string): PasswordRuleStatus[] {
  return passwordRules.map((rule) => ({
    id: rule.id,
    message: rule.message,
    passed: rule.check(password),
  }));
}

export function validatePassword(password: string): string[] {
  return passwordRules.filter((rule) => !rule.check(password)).map((rule) => rule.message);
}
