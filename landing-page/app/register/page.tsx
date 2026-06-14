import type { Metadata } from 'next'
import { AuthForm } from '@/components/auth/auth-form'

export const metadata: Metadata = {
  title: 'Register — OFFICE-NATOR',
  description: 'Create your OFFICE-NATOR account and get early access.',
}

export default function RegisterPage() {
  return <AuthForm mode="register" />
}
