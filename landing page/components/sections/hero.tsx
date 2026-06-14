'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, Code2, Play, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

const TITLE = 'OFFICE-NATOR'

const TERMINAL_LINES = [
  { text: '> sutra --listen --lang=hi', tone: 'cmd' },
  { text: '[19:42:11] Heard: "bold karo"', tone: 'muted' },
  { text: '[19:42:12] Plan: Toggle bold formatting', tone: 'accent' },
  { text: '[19:42:12] Executing: hotkey ctrl+b ✓', tone: 'accent' },
  { text: '[19:42:13] Done!', tone: 'success' },
] as const

const TRUST = ['129 Excel Actions', '4 AI Providers', 'Hindi · Marathi · English']

export function Hero() {
  const [showDemo, setShowDemo] = useState(false)

  return (
    <section
      id="hero"
      className="relative flex min-h-screen items-center overflow-hidden pt-16"
    >
      <div className="absolute inset-0 grid-bg opacity-60" aria-hidden />
      <div
        className="pointer-events-none absolute -right-20 top-1/3 size-[420px] rounded-full bg-primary/10 blur-3xl"
        aria-hidden
      />

      <div className="relative mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-12 px-4 py-20 sm:px-6 lg:grid-cols-2 lg:px-8">
        <div>
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center rounded-full border border-primary/40 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.2em] text-primary"
          >
            [ Voice AI · Desktop Automation ]
          </motion.span>

          <h1 className="mt-6 flex flex-wrap text-5xl font-extrabold tracking-tight sm:text-6xl xl:text-7xl">
            {TITLE.split('').map((char, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 + i * 0.04 }}
                className={char === '-' ? 'text-primary text-glow' : undefined}
              >
                {char}
              </motion.span>
            ))}
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="mt-4 text-balance text-xl font-medium text-foreground/90 sm:text-2xl"
          >
            The beginning of the terminator era for your office tools
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            className="mt-5 max-w-xl text-pretty leading-relaxed text-muted-foreground"
          >
            Control Microsoft Excel with your voice in Hindi, Marathi, or
            English. No mouse. No keyboard. Just speak — Sutra translates,
            plans, and executes.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.9 }}
            className="mt-8 flex flex-col gap-3 sm:flex-row"
          >
            <Button
              size="lg"
              onClick={() => setShowDemo(true)}
              className="border-l-2 border-primary-foreground/40 shadow-glow"
            >
              <Play className="size-4 fill-current" />
              Watch Demo
            </Button>
            <Button asChild size="lg" variant="outline">
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer noopener"
              >
                <Code2 className="size-4" />
                View on GitHub
              </a>
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.1 }}
            className="mt-8 flex flex-wrap gap-x-6 gap-y-2"
          >
            {TRUST.map((t) => (
              <span
                key={t}
                className="flex items-center gap-2 font-mono text-xs text-muted-foreground"
              >
                <span className="size-1.5 rounded-full bg-primary" />
                {t}
              </span>
            ))}
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="relative"
        >
          <div className="animate-float">
            <div className="glass rounded-xl shadow-hard">
              <div className="flex items-center gap-2 border-b border-border px-4 py-3">
                <span className="size-3 rounded-full bg-destructive/80" />
                <span className="size-3 rounded-full bg-chart-4/80" />
                <span className="size-3 rounded-full bg-success/80" />
                <span className="ml-2 font-mono text-xs text-muted-foreground">
                  sutra — live session
                </span>
              </div>
              <div className="space-y-2 p-5 font-mono text-sm">
                {TERMINAL_LINES.map((line, i) => (
                  <motion.p
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 1 + i * 0.25 }}
                    className={
                      line.tone === 'cmd'
                        ? 'text-foreground'
                        : line.tone === 'accent'
                          ? 'text-primary'
                          : line.tone === 'success'
                            ? 'text-success'
                            : 'text-muted-foreground'
                    }
                  >
                    {line.text}
                  </motion.p>
                ))}
                <span className="inline-block h-4 w-2 animate-pulse bg-primary align-middle" />
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      <button
        onClick={() =>
          document
            .getElementById('problem')
            ?.scrollIntoView({ behavior: 'smooth' })
        }
        aria-label="Scroll to next section"
        className="absolute bottom-6 left-1/2 -translate-x-1/2 text-muted-foreground"
      >
        <ChevronDown className="size-6 animate-bounce-chevron" />
      </button>

      {showDemo ? (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center bg-background/90 p-4 backdrop-blur-sm"
          onClick={() => setShowDemo(false)}
        >
          <div
            className="relative w-full max-w-3xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setShowDemo(false)}
              aria-label="Close demo"
              className="absolute -top-10 right-0 flex size-9 items-center justify-center rounded-md border border-border text-foreground"
            >
              <X className="size-4" />
            </button>
            <div className="aspect-video overflow-hidden rounded-xl border border-border shadow-hard">
              <iframe
                className="size-full"
                src="https://www.youtube.com/embed/dQw4w9WgXcQ"
                title="OFFICE-NATOR demo"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      ) : null}
    </section>
  )
}
