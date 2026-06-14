'use client'

import { motion } from 'framer-motion'
import {
  Brain,
  CheckCircle2,
  Cpu,
  FileSpreadsheet,
  Languages,
  type LucideIcon,
  MemoryStick,
  Mic,
  MousePointerClick,
  Waves,
} from 'lucide-react'
import { SectionHeading } from '@/components/section-heading'

type Node = { icon: LucideIcon; label: string; tech: string; detail: string }

const PIPELINE: Node[] = [
  { icon: Mic, label: 'Microphone', tech: 'PyAudio', detail: 'Captures raw audio input from the user.' },
  { icon: Waves, label: 'Voice Detection', tech: 'Silero VAD', detail: 'Detects speech boundaries, ignores silence.' },
  { icon: Languages, label: 'Speech-to-Text', tech: 'Sarvam AI', detail: 'Transcribes & translates Indian languages.' },
  { icon: MemoryStick, label: 'Memory Context', tech: 'Local JSON', detail: 'Injects learned user preferences.' },
  { icon: Brain, label: 'LLM Brain', tech: 'Groq / Gemini', detail: 'Maps intent to a deterministic action.' },
  { icon: Cpu, label: 'Action Library', tech: '129 Actions', detail: 'Resolves the exact Excel operation.' },
  { icon: MousePointerClick, label: 'Executor', tech: 'PyAutoGUI', detail: 'Performs hotkeys & UI actions on desktop.' },
  { icon: CheckCircle2, label: 'Excel', tech: 'Result ✓', detail: 'Action completes inside Microsoft Excel.' },
]

const BACKEND = ['FastAPI', 'PyAudio', 'Silero VAD', 'PyAutoGUI', 'edge-tts', 'keyboard']
const FRONTEND = ['Next.js', 'TypeScript', 'Framer Motion', 'Groq', 'Gemini', 'Sarvam AI']

export function Architecture() {
  return (
    <section id="architecture" className="scroll-mt-16 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="04 / System Architecture"
          title="From voice to executed action in milliseconds"
          description="A streaming pipeline that turns a spoken phrase into a deterministic desktop action."
        />

        <div className="relative mt-14">
          <svg
            className="pointer-events-none absolute inset-x-0 top-1/2 hidden h-2 w-full -translate-y-1/2 lg:block"
            aria-hidden
            preserveAspectRatio="none"
          >
            <line
              x1="0"
              y1="4"
              x2="100%"
              y2="4"
              stroke="var(--primary)"
              strokeWidth="2"
              className="animate-dash opacity-60"
            />
          </svg>

          <div className="relative grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-8">
            {PIPELINE.map((node, i) => (
              <motion.div
                key={node.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.35, delay: i * 0.08 }}
                className="group relative"
              >
                <div className="glass flex flex-col items-center gap-2 rounded-xl p-4 text-center transition-all duration-300 hover:border-primary/50 hover:shadow-glow">
                  <span className="flex size-10 items-center justify-center rounded-lg border border-primary/30 bg-background text-primary">
                    <node.icon className="size-5" />
                  </span>
                  <span className="text-xs font-semibold leading-tight">
                    {node.label}
                  </span>
                  <span className="font-mono text-[10px] tracking-wide text-muted-foreground">
                    {node.tech}
                  </span>
                </div>
                <span className="pointer-events-none absolute -top-2 left-1/2 z-10 w-44 -translate-x-1/2 -translate-y-full rounded-md border border-border bg-popover p-2 text-center text-[11px] leading-snug text-popover-foreground opacity-0 shadow-hard transition-opacity duration-200 group-hover:opacity-100">
                  {node.detail}
                </span>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-6 md:grid-cols-2">
          <StackCard title="Python Backend" items={BACKEND} />
          <StackCard title="Frontend / AI" items={FRONTEND} />
        </div>
      </div>
    </section>
  )
}

function StackCard({ title, items }: { title: string; items: string[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.4 }}
      className="glass rounded-xl p-6"
    >
      <h3 className="font-mono text-xs uppercase tracking-[0.2em] text-primary">
        {title}
      </h3>
      <div className="mt-4 flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={item}
            className="rounded-md border border-border bg-secondary px-3 py-1.5 text-sm text-secondary-foreground"
          >
            {item}
          </span>
        ))}
      </div>
    </motion.div>
  )
}
