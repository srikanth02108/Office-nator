'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Bot, Menu, Moon, Sun, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/lib/use-theme'
import { cn } from '@/lib/utils'

const NAV = [
  { id: 'hero', label: 'Hero' },
  { id: 'problem', label: 'Problem' },
  { id: 'features', label: 'Features' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'market', label: 'Market' },
  { id: 'roadmap', label: 'Roadmap' },
  { id: 'pricing', label: 'Pricing' },
]

export function SiteHeader() {
  const { theme, toggleTheme, mounted } = useTheme()
  const [scrolled, setScrolled] = useState(false)
  const [active, setActive] = useState('hero')
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActive(entry.target.id)
        })
      },
      { rootMargin: '-45% 0px -50% 0px', threshold: 0 },
    )
    NAV.forEach(({ id }) => {
      const el = document.getElementById(id)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [])

  const handleNav = (id: string) => {
    setOpen(false)
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <header
      className={cn(
        'fixed inset-x-0 top-0 z-50 transition-all duration-300',
        scrolled
          ? 'border-b border-border bg-background/80 backdrop-blur-xl'
          : 'border-b border-transparent',
      )}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => handleNav('hero')}
          className="flex items-center gap-2.5"
          aria-label="OFFICE-NATOR home"
        >
          <span className="flex size-9 items-center justify-center rounded-md border border-primary/40 bg-primary/10 text-primary shadow-glow">
            <Bot className="size-5" />
          </span>
          <span className="flex flex-col leading-none">
            <span className="text-sm font-bold tracking-tight">
              OFFICE-NATOR
            </span>
            <span className="font-mono text-[10px] tracking-[0.2em] text-muted-foreground">
              v1.0 · BETA
            </span>
          </span>
        </button>

        <nav className="hidden items-center gap-1 lg:flex">
          {NAV.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => handleNav(id)}
              className={cn(
                'group relative px-3 py-2 text-sm font-medium transition-colors',
                active === id
                  ? 'text-foreground'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {label}
              <span
                className={cn(
                  'absolute inset-x-3 -bottom-0.5 h-px origin-left bg-primary transition-transform duration-300',
                  active === id
                    ? 'scale-x-100'
                    : 'scale-x-0 group-hover:scale-x-100',
                )}
              />
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="flex size-9 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:text-foreground"
          >
            {mounted && theme === 'dark' ? (
              <Sun className="size-4" />
            ) : (
              <Moon className="size-4" />
            )}
          </button>
          <Button
            asChild
            variant="ghost"
            className="hidden sm:inline-flex"
            size="sm"
          >
            <Link href="/login">Login</Link>
          </Button>
          <Button
            asChild
            size="sm"
            className="hidden shadow-glow sm:inline-flex"
          >
            <Link href="/register">Get Early Access</Link>
          </Button>
          <button
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
            className="flex size-9 items-center justify-center rounded-md border border-border text-foreground lg:hidden"
          >
            {open ? <X className="size-4" /> : <Menu className="size-4" />}
          </button>
        </div>
      </div>

      {open ? (
        <div className="border-t border-border bg-background/95 backdrop-blur-xl lg:hidden">
          <nav className="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-4">
            {NAV.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => handleNav(id)}
                className={cn(
                  'rounded-md px-3 py-2 text-left text-sm font-medium transition-colors',
                  active === id
                    ? 'bg-accent text-foreground'
                    : 'text-muted-foreground hover:bg-accent/60 hover:text-foreground',
                )}
              >
                {label}
              </button>
            ))}
            <div className="mt-2 flex gap-2">
              <Button asChild variant="outline" className="flex-1" size="sm">
                <Link href="/login">Login</Link>
              </Button>
              <Button asChild className="flex-1 shadow-glow" size="sm">
                <Link href="/register">Get Early Access</Link>
              </Button>
            </div>
          </nav>
        </div>
      ) : null}
    </header>
  )
}
