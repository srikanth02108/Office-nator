'use client'

import { motion } from 'framer-motion'
import { ArrowUpRight } from 'lucide-react'
import { CountUp } from '@/components/count-up'
import { SectionHeading } from '@/components/section-heading'

const STATS = [
  { value: 500, suffix: 'M+', label: 'Regional language office workers in India alone' },
  { value: 2.3, decimals: 1, suffix: 'hrs', label: 'Average daily time lost to repetitive Excel tasks' },
  { value: 4.2, decimals: 1, prefix: '$', suffix: 'B', label: 'Voice AI productivity market size by 2027' },
]

const RINGS = [
  { label: 'TAM', value: '1.2B', note: 'Microsoft Office users globally', size: 'size-64', tone: 'border-border' },
  { label: 'SAM', value: '200M', note: 'Non-English enterprise users', size: 'size-44', tone: 'border-primary/40' },
  { label: 'SOM', value: '5M', note: 'Indian SME power users (Yr 1)', size: 'size-24', tone: 'border-primary' },
]

const TRENDS = [
  'AI assistant adoption +340% YoY in enterprise',
  'India office software market growing 18% annually',
  'Voice interface for productivity: 0 direct competitors',
  'Government push for vernacular digital tools',
]

export function Market() {
  return (
    <section id="market" className="scroll-mt-16 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="05 / Market & Impact"
          title="A massive, underserved opportunity"
          description="Hundreds of millions of regional-language workers are locked out of full desktop productivity. We unlock them with voice."
        />

        <div className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {STATS.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="glass rounded-xl p-6 text-center"
            >
              <CountUp
                to={s.value}
                decimals={s.decimals ?? 0}
                prefix={s.prefix}
                suffix={s.suffix}
                className="text-4xl font-extrabold tracking-tight text-primary sm:text-5xl"
              />
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {s.label}
              </p>
            </motion.div>
          ))}
        </div>

        <div className="mt-12 grid grid-cols-1 gap-10 lg:grid-cols-2">
          {/* concentric rings */}
          <div className="glass rounded-xl p-8">
            <h3 className="text-lg font-semibold">Market Sizing</h3>
            <div className="mt-6 flex flex-col items-center gap-8 sm:flex-row sm:gap-10">
              <div className="relative flex size-64 items-center justify-center">
                {RINGS.map((r) => (
                  <div
                    key={r.label}
                    className={`absolute flex items-center justify-center rounded-full border ${r.size} ${r.tone}`}
                  />
                ))}
                <span className="font-mono text-xs text-muted-foreground">
                  TAM · SAM · SOM
                </span>
              </div>
              <div className="flex flex-col gap-4">
                {RINGS.map((r) => (
                  <div key={r.label} className="flex items-baseline gap-3">
                    <span className="font-mono text-xs uppercase tracking-widest text-primary">
                      {r.label}
                    </span>
                    <span className="text-xl font-bold">{r.value}</span>
                    <span className="text-sm text-muted-foreground">
                      {r.note}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* trends */}
          <div className="glass rounded-xl p-8">
            <h3 className="text-lg font-semibold">Tailwinds</h3>
            <div className="mt-6 flex flex-col gap-3">
              {TRENDS.map((t, i) => (
                <motion.div
                  key={t}
                  initial={{ opacity: 0, x: 24 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.4, delay: i * 0.08 }}
                  className="flex items-start gap-3 border-b border-border pb-3 last:border-0"
                >
                  <ArrowUpRight className="mt-0.5 size-4 shrink-0 text-primary" />
                  <span className="text-sm leading-relaxed text-foreground/90">
                    {t}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
