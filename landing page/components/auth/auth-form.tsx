'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Bot, Loader2, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { FloatingInput } from '@/components/auth/floating-input'
import { OAuthButtons } from '@/components/auth/oauth-buttons'

type AuthFormProps = {
  mode: 'login' | 'register'
}

const MAIN_APP_URL = process.env.NEXT_PUBLIC_MAIN_APP_URL ?? 'http://localhost:3000'

export function AuthForm({ mode }: AuthFormProps) {
  const [loading, setLoading]     = useState(false)
  const [demoLoading, setDemo]    = useState(false)
  const [error, setError]         = useState('')
  const isRegister                = mode === 'register'

  // ── Normal submit ───────────────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const form  = e.currentTarget
    const data  = new FormData(form)
    const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login'

    const body = isRegister
      ? {
          username: data.get('username'),
          email:    data.get('email'),
          password: data.get('password'),
        }
      : {
          email:    data.get('email'),
          password: data.get('password'),
        }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const json = await res.json()

      if (!res.ok) {
        setError(json.error ?? 'Something went wrong.')
        setLoading(false)
        return
      }

      // Success → redirect to main app
      window.location.href = MAIN_APP_URL
    } catch {
      setError('Network error. Is the server running?')
      setLoading(false)
    }
  }

  // ── Demo login ──────────────────────────────────────────────────────
  const handleDemo = async () => {
    setError('')
    setDemo(true)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ demo: true }),
      })
      const json = await res.json()
      if (!res.ok) {
        setError(json.error ?? 'Demo login failed.')
        setDemo(false)
        return
      }
      window.location.href = MAIN_APP_URL
    } catch {
      setError('Network error.')
      setDemo(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-16">
      <div className="absolute inset-0 grid-bg opacity-50" aria-hidden />
      <div
        className="pointer-events-none absolute left-1/2 top-1/3 size-[360px] -translate-x-1/2 rounded-full bg-primary/10 blur-3xl"
        aria-hidden
      />

      <div className="relative w-full max-w-md">
        <Link
          href="/"
          className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          Back to home
        </Link>

        <div className="glass rounded-2xl p-8 shadow-hard">
          {/* Header */}
          <div className="flex flex-col items-center text-center">
            <span className="flex size-11 items-center justify-center rounded-md border border-primary/40 bg-primary/10 text-primary shadow-glow">
              <Bot className="size-5" />
            </span>
            <h1 className="mt-4 text-xl font-bold tracking-tight">OFFICE-NATOR</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {isRegister
                ? 'Create your account to get early access'
                : 'Welcome back — sign in to continue'}
            </p>
          </div>

          {/* Demo login button (login page only) */}
          {!isRegister && (
            <button
              type="button"
              onClick={handleDemo}
              disabled={demoLoading || loading}
              className="mt-6 flex w-full items-center justify-center gap-2.5 rounded-xl border border-primary/40 bg-primary/10 px-4 py-3 text-sm font-semibold text-primary transition-all hover:border-primary/70 hover:bg-primary/20 hover:shadow-[0_0_20px_-4px_var(--primary)] disabled:opacity-50"
            >
              {demoLoading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Zap className="size-4" />
              )}
              {demoLoading ? 'Signing in…' : 'Try Demo — instant access'}
            </button>
          )}

          {/* Divider after demo button */}
          {!isRegister && (
            <div className="my-5 flex items-center gap-3">
              <span className="h-px flex-1 bg-border" />
              <span className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
                or sign in with email
              </span>
              <span className="h-px flex-1 bg-border" />
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
              {error}
            </div>
          )}

          {/* Form */}
          <form
            onSubmit={handleSubmit}
            className={`flex flex-col gap-4 ${isRegister ? 'mt-8' : ''}`}
          >
            {isRegister && (
              <FloatingInput
                name="username"
                label="Username"
                autoComplete="username"
                required
              />
            )}
            <FloatingInput
              name="email"
              type="email"
              label="Email"
              autoComplete="email"
              required
            />
            <FloatingInput
              name="password"
              type="password"
              label="Password"
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              required
            />
            {isRegister && (
              <FloatingInput
                name="confirmPassword"
                type="password"
                label="Confirm Password"
                autoComplete="new-password"
                required
              />
            )}

            {isRegister && (
              <label className="flex items-start gap-2.5 text-xs text-muted-foreground">
                <input
                  type="checkbox"
                  required
                  className="mt-0.5 size-4 rounded border-border accent-primary"
                />
                <span>
                  I agree to the{' '}
                  <a href="#" className="text-primary hover:underline">Terms of Service</a>
                  {' '}and{' '}
                  <a href="#" className="text-primary hover:underline">Privacy Policy</a>.
                </span>
              </label>
            )}

            <Button
              type="submit"
              disabled={loading || demoLoading}
              className="mt-2 h-11 shadow-glow"
            >
              {loading ? (
                <><Loader2 className="size-4 animate-spin" /> Please wait</>
              ) : (
                isRegister ? 'Create Account' : 'Sign In'
              )}
            </Button>
          </form>

          {/* OAuth */}
          <div className="my-6 flex items-center gap-3">
            <span className="h-px flex-1 bg-border" />
            <span className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
              or continue with
            </span>
            <span className="h-px flex-1 bg-border" />
          </div>
          <OAuthButtons />

          {/* Switch link */}
          <p className="mt-8 text-center text-sm text-muted-foreground">
            {isRegister ? (
              <>Already have an account?{' '}
                <Link href="/login" className="text-primary hover:underline">Login</Link>
              </>
            ) : (
              <>Don&apos;t have an account?{' '}
                <Link href="/register" className="text-primary hover:underline">Register</Link>
              </>
            )}
          </p>
        </div>
      </div>
    </main>
  )
}
