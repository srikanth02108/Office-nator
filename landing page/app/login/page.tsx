import type { Metadata } from 'next'
import { AuthForm } from '@/components/auth/auth-form'

export const metadata: Metadata = {
  title: 'Login — OFFICE-NATOR',
  description: 'Sign in to your OFFICE-NATOR account.',
}

export default function LoginPage() {
  return <AuthForm mode="login" />
}
