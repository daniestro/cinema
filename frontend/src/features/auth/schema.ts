import { z } from 'zod';
import { validatePassword } from './passwordRules';

const email = z.string().trim().min(1, 'Email is required').email('Enter a valid email');

export const signInSchema = z.object({
  email,
  password: z.string().min(1, 'Password is required'),
});

export const signUpSchema = z.object({
  email,
  password: z.string().superRefine((value, ctx) => {
    for (const message of validatePassword(value)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message });
    }
  }),
});

export type Credentials = z.infer<typeof signInSchema>;
