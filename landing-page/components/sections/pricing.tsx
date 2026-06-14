'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { SectionHeading } from '@/components/section-heading'
import { cn } from '@/lib/utils'

const TIERS = [
  {
    name: 'Free',
    price: '₹0',
    period: '/month',
    cta: 'Get Started',
    variant: 'outline' as const,
    featured: false,
    features: ['50 commands/day', 'Groq free tier', 'Hindi + Marathi', 'Web dashboard'],
  },
  {
    name: 'Pro',
    price: '₹499',
    period: '/month',
    cta: 'Start Free Trial',
    variant: 'default' as const,
    featured: true,
    features: ['Unlimited commands', 'All 4 AI providers', 'Priority voice processing', 'Memory across sessions', 'Email support'],
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    cta: 'Contact Sales',
    variant: 'outline' as const,
    featured: false,
    features: ['Everything in Pro', 'Custom LLM endpoints', 'On-premise deployment', 'Multi-language expansion', 'Dedicated support + SLA'],
  },
]

const REVENUE = [
  { year: 'Year 1', label: '₹42L', height: 14 },
  { year: 'Year 2', label: '₹1.8Cr', height: 34 },
  { year: 'Year 3', label: '₹8.4Cr', height: 64 },
  { year: 'Year 4', label: '₹24Cr', height: 100 },
]

export function Pricing() {
  return (
    <section id="pricing" className="scroll-mt-16 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="07 / Pricing & Revenue"
          title="Simple pricing, built to scale"
          description="Start free, upgrade when you are ready. Enterprise plans for teams deploying across the organization."
        />

        <div className="mt-14 grid grid-cols-1 gap-6 lg:grid-cols-3">
          {TIERS.map((tier, i) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className={cn(
                'glass relative flex flex-col rounded-xl p-8',
                tier.featured &&
                  'border-primary shadow-glow lg:-translate-y-3 lg:scale-[1.02]',
              )}
            >
              {tier.featured ? (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-primary-foreground">
                  Most Popular
                </span>
              ) : null}
              <h3 className="text-lg font-semibold">{tier.name}</h3>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold tracking-tight">
                  {tier.price}
                </span>
                <span className="text-sm text-muted-foreground">
                  {tier.period}
                </span>
              </div>
              <ul className="mt-6 flex flex-1 flex-col gap-3">
                {tier.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5 text-sm">
                    <Check className="mt-0.5 size-4 shrink-0 text-primary" />
                    <span className="text-foreground/90">{f}</span>
                  </li>
                ))}
              </ul>
              <Button
                asChild
                variant={tier.variant}
                className={cn('mt-8', tier.featured && 'shadow-glow')}
              >
                <Link href="/register">{tier.cta}</Link>
              </Button>
            </motion.div>
          ))}
        </div>

        {/* revenue bar chart */}
        <div className="glass mt-12 rounded-xl p-8">
          <h3 className="text-lg font-semibold">Projected Revenue</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Conservative growth across the first four years.
          </p>
          <div className="mt-8 flex h-64 items-end justify-around gap-4">
            {REVENUE.map((bar, i) => (
              <div
                key={bar.year}
                className="flex h-full flex-1 flex-col items-center justify-end gap-3"
              >
                <span className="font-mono text-sm font-bold text-primary">
                  {bar.label}
                </span>
                <motion.div
                  initial={{ height: 0 }}
                  whileInView={{ height: `${bar.height}%` }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.8, delay: i * 0.12, ease: 'easeOut' }}
                  className="w-full max-w-20 rounded-t-md border border-primary/50 bg-primary/30"
                />
                <span className="font-mono text-xs text-muted-foreground">
                  {bar.year}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
