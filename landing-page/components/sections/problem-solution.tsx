'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, Check } from 'lucide-react'

const PROBLEMS = [
  'Non-English speakers struggle with complex Excel operations',
  'Repetitive formatting tasks eat 2-3 hours daily',
  'No voice interface exists for desktop productivity tools',
  'Language barrier blocks 500M+ regional language users from full productivity',
]

const SOLUTIONS = [
  'Speak in Hindi/Marathi — Sarvam AI translates instantly',
  '129 pre-coded Excel actions execute in milliseconds',
  'Global hotkey Alt+. works even when Excel is focused',
  'Built for Bharat — works with any regional language via STT',
]

export function ProblemSolution() {
  return (
    <section
      id="problem"
      className="relative mx-auto max-w-7xl scroll-mt-16 px-4 py-24 sm:px-6 lg:px-8"
    >
      <motion.span
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="block font-mono text-xs uppercase tracking-[0.25em] text-primary"
      >
        02 / Problem &amp; Solution
      </motion.span>

      <div className="relative mt-10 grid grid-cols-1 gap-10 lg:grid-cols-2">
        {/* center divider + VS */}
        <div className="pointer-events-none absolute inset-y-0 left-1/2 hidden -translate-x-1/2 lg:block">
          <div className="h-full w-px bg-border" />
          <span className="absolute left-1/2 top-1/2 flex size-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-border bg-background font-mono text-xs font-bold text-muted-foreground">
            VS
          </span>
        </div>

        {/* problem */}
        <div className="lg:pr-10">
          <h3 className="text-2xl font-bold tracking-tight">
            The Office Productivity Gap
          </h3>
          <div className="mt-6 flex flex-col gap-4">
            {PROBLEMS.map((p, i) => (
              <motion.div
                key={p}
                initial={{ opacity: 0, x: -24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className="flex items-start gap-3 rounded-lg border border-destructive/25 bg-destructive/5 p-4"
              >
                <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-md bg-destructive/15 text-destructive">
                  <AlertTriangle className="size-4" />
                </span>
                <p className="text-sm leading-relaxed text-foreground/90">{p}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* solution */}
        <div className="lg:pl-10">
          <h3 className="text-2xl font-bold tracking-tight text-primary text-glow">
            OFFICE-NATOR
          </h3>
          <div className="mt-6 flex flex-col gap-4">
            {SOLUTIONS.map((s, i) => (
              <motion.div
                key={s}
                initial={{ opacity: 0, x: 24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className="flex items-start gap-3 rounded-lg border border-primary/25 bg-primary/5 p-4"
              >
                <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-md bg-primary/15 text-primary">
                  <Check className="size-4" />
                </span>
                <p className="text-sm leading-relaxed text-foreground/90">{s}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
