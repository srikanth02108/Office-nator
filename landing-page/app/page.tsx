import { SiteHeader } from '@/components/site-header'
import { SiteFooter } from '@/components/site-footer'
import { Hero } from '@/components/sections/hero'
import { ProblemSolution } from '@/components/sections/problem-solution'
import { Features } from '@/components/sections/features'
import { Architecture } from '@/components/sections/architecture'
import { Market } from '@/components/sections/market'
import { Roadmap } from '@/components/sections/roadmap'
import { Pricing } from '@/components/sections/pricing'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader />
      <main>
        <Hero />
        <ProblemSolution />
        <Features />
        <Architecture />
        <Market />
        <Roadmap />
        <Pricing />
      </main>
      <SiteFooter />
    </div>
  )
}
