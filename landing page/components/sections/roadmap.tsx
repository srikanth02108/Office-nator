'use client'

import { motion } from 'framer-motion'
import { SectionHeading } from '@/components/section-heading'
import { cn } from '@/lib/utils'

const MILESTONES = [
  { period: 'Q3 2026 · NOW', title: 'Excel Automation Live', desc: '129 actions, Hindi & Marathi support, real-time web dashboard.', now: true },
  { period: 'Q4 2026', title: 'Word + PowerPoint', desc: 'Microsoft Word & PowerPoint support, 15 more Indian languages.' },
  { period: 'Q1 2027', title: 'Google Workspace', desc: 'Sheets, Docs, and Slides integration via voice.' },
  { period: 'Q2 2027', title: 'Total Desktop Automation', desc: 'Control any Windows application through voice.' },
  { period: 'Q3 2027', title: 'Mobile + Offline LLM', desc: 'Mobile companion app and offline local LLM mode.' },
  { period: 'Q4 2027', title: 'Enterprise API', desc: 'White-label SDK and API for other companies.' },
  { period: '2028+', title: 'OS-Level Voice Control', desc: 'Full operating-system voice control — the complete Terminator era.' },
]

export function Roadmap() {
  return (
    <section id="roadmap" className="scroll-mt-16 py-24">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="06 / Future Roadmap"
          title="The path to total voice automation"
        />

        <div className="relative mt-16">
          <div className="absolute left-4 top-0 h-full w-px bg-border md:left-1/2 md:-translate-x-1/2" />

          <div className="flex flex-col gap-10">
            {MILESTONES.map((m, i) => {
              const left = i % 2 === 0
              return (
                <div
                  key={m.title}
                  className="relative md:grid md:grid-cols-2 md:gap-8"
                >
                  <motion.div
                    initial={{ opacity: 0, scale: 0 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true, margin: '-80px' }}
                    transition={{ type: 'spring', stiffness: 260, damping: 18 }}
                    className={cn(
                      'absolute left-4 top-2 z-10 size-4 -translate-x-1/2 rounded-full border-2 border-primary bg-background md:left-1/2',
                      m.now && 'bg-primary shadow-glow',
                    )}
                  />

                  <motion.div
                    initial={{ opacity: 0, x: left ? -40 : 40 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, margin: '-60px' }}
                    transition={{ duration: 0.45 }}
                    className={cn(
                      'glass ml-10 rounded-xl p-5 md:ml-0',
                      left
                        ? 'md:col-start-1 md:text-right'
                        : 'md:col-start-2',
                    )}
                  >
                    <span
                      className={cn(
                        'font-mono text-xs uppercase tracking-[0.2em]',
                        m.now ? 'text-primary text-glow' : 'text-primary',
                      )}
                    >
                      {m.period}
                    </span>
                    <h3 className="mt-2 text-lg font-semibold">{m.title}</h3>
                    <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                      {m.desc}
                    </p>
                  </motion.div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
