'use client'

import { motion } from 'framer-motion'
import {
  Brain,
  Database,
  Gauge,
  KeyRound,
  type LucideIcon,
  MonitorSmartphone,
  Mic,
  Plug,
  ShieldCheck,
  Zap,
} from 'lucide-react'
import { SectionHeading } from '@/components/section-heading'

type Feature = { icon: LucideIcon; title: string; desc: string }

const FEATURES: Feature[] = [
  {
    icon: Mic,
    title: 'Voice in Any Language',
    desc: 'Hindi, Marathi, English via Sarvam AI speech-to-text.',
  },
  {
    icon: Zap,
    title: '129 Deterministic Actions',
    desc: 'Pre-coded Excel operations with zero hallucination.',
  },
  {
    icon: Brain,
    title: 'Multi-Provider Brain',
    desc: 'Switch between Groq, Gemini, OpenAI, Custom at runtime.',
  },
  {
    icon: Database,
    title: 'Stateful Memory',
    desc: 'Learns your preferences across sessions — local JSON, no cloud.',
  },
  {
    icon: MonitorSmartphone,
    title: 'Web Dashboard',
    desc: 'Real-time transcript, execution plan, and memory viewer.',
  },
  {
    icon: KeyRound,
    title: 'Global Hotkey',
    desc: 'Alt+. triggers from anywhere, even when Excel is focused.',
  },
  {
    icon: ShieldCheck,
    title: 'Confirmation Guard',
    desc: 'Destructive actions always ask "Haan/Nahi" first.',
  },
  {
    icon: Gauge,
    title: 'Usage Meter',
    desc: 'Live token and request tracking per provider.',
  },
  {
    icon: Plug,
    title: 'Extensible',
    desc: 'OpenAI-compatible custom providers — Ollama, Together, Mistral.',
  },
]

const TECH = [
  'Sarvam AI',
  'Groq',
  'Gemini',
  'PyAutoGUI',
  'Silero VAD',
  'edge-tts',
  'FastAPI',
  'Next.js',
  'Framer Motion',
  'Python',
  'WebSocket',
]

export function Features() {
  return (
    <section
      id="features"
      className="relative scroll-mt-16 overflow-hidden py-24"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="03 / Features & Capabilities"
          title="Everything you need to talk to your tools"
          description="A deterministic action engine wrapped in a multilingual voice layer — built for speed, safety, and Bharat."
        />

        <div className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: (i % 3) * 0.08 }}
              className="group glass rounded-xl p-6 transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-glow"
            >
              <span className="flex size-11 items-center justify-center rounded-lg border border-border bg-primary/10 text-primary transition-shadow duration-300 group-hover:shadow-glow">
                <f.icon className="size-5" />
              </span>
              <h3 className="mt-4 text-base font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {f.desc}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="relative mt-16 flex overflow-hidden border-y border-border py-4">
        <div className="flex shrink-0 animate-ticker">
          {[...TECH, ...TECH].map((t, i) => (
            <span
              key={i}
              className="flex items-center gap-6 px-6 font-mono text-sm text-muted-foreground"
            >
              {t}
              <span className="size-1 rounded-full bg-primary/60" />
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
